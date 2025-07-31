#!/usr/bin/env python3

import re
import json
import sys
import os
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

try:
    from google import genai
except ImportError:
    genai = None

from .tdd_prompts import (
    TDDCorePrompt,
    EditAnalysisPrompt,
    WriteAnalysisPrompt,
    MultiEditAnalysisPrompt,
    TDDContextFormatter,
)
from .config import GEMINI_MODEL
from .streaming_processors import (  # type: ignore[attr-defined]
    TDDValidationProcessor,
    FileCategorizationProcessor,
    ProcessorPart,
    extract_json_from_part,
)


class TDDValidationResponse(BaseModel):  # type: ignore[misc]
    """TDD-specific validation response model"""

    approved: bool
    violation_type: Optional[str] = (
        None  # "multiple_tests", "over_implementation", "premature_implementation"
    )
    test_count: Optional[int] = None
    affected_files: List[str] = []
    tdd_phase: str = "unknown"  # "red", "green", "refactor", "unknown"
    reason: str = ""
    suggestions: List[str] = []
    detailed_analysis: Optional[str] = None
    # Language validation fields
    target_language: Optional[str] = None  # Language of file being validated
    response_language: Optional[str] = None  # Language used in response examples


class FileCategorizationResponse(BaseModel):  # type: ignore[misc]
    """Response model for file categorization"""

    category: str  # "structural", "config", "docs", "data", "test", "implementation"
    reason: str
    requires_tdd: bool


class TDDValidator:
    """
    TDDValidator enforces Test-Driven Development principles through:
    - Operation-specific validation (Edit, Write, MultiEdit)
    - Red-Green-Refactor cycle enforcement
    - New test count detection
    - Over-implementation prevention
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key) if api_key and genai else None
        self.model_name = GEMINI_MODEL
        self.processor = TDDValidationProcessor(api_key)
        self.file_categorization_processor = FileCategorizationProcessor(api_key)

    def _is_minimal_init_file(self, file_path: str, content: str) -> bool:
        """Check if __init__.py file is minimal (structural)"""
        if not file_path.endswith("__init__.py"):
            return False

        # Empty file is structural
        if not content.strip():
            return True

        # Simple imports only (no logic)
        lines = [line.strip() for line in content.split("\n") if line.strip()]

        # Check if all lines are comments, imports, or simple assignments
        for line in lines:
            if line.startswith("#"):  # Comment
                continue
            if line.startswith(
                ("import ", "from ", "__version__", "__author__", "__email__")
            ):
                continue
            if line.startswith("__all__") and "=" in line:  # Simple __all__ definition
                continue
            # If we find any other code, it's implementation
            return False

        return True

    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = os.path.splitext(file_path)[1].lower()
        language_map = {
            ".py": "Python",
            ".java": "Java",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".dart": "Dart",
            ".vue": "Vue/JavaScript",
            ".jsx": "JavaScript/React",
            ".tsx": "TypeScript/React",
        }
        return language_map.get(ext, "unknown")

    def _is_config_file(self, file_path: str) -> bool:
        """Check if file is a configuration file"""
        import os

        config_extensions = {".ini", ".toml", ".yaml", ".yml", ".json", ".cfg", ".conf"}
        config_names = {
            "setup.py",
            "pyproject.toml",
            "requirements.txt",
            "Dockerfile",
            "Makefile",
        }

        ext = os.path.splitext(file_path)[1].lower()
        name = os.path.basename(file_path)

        return ext in config_extensions or name in config_names

    def _has_implementation_logic(self, content: str) -> bool:
        """Check if content contains actual implementation logic"""
        if not content.strip():
            return False

        lines = [line.strip() for line in content.split("\n") if line.strip()]

        for line in lines:
            # Skip comments and docstrings
            if line.startswith("#") or line.startswith('"""') or line.startswith("'''"):
                continue
            # Skip simple imports and metadata
            if line.startswith(
                ("import ", "from ", "__version__", "__author__", "__email__")
            ):
                continue
            # Skip simple variable assignments (like __all__)
            if any(
                line.startswith(var)
                for var in ["__all__", "__version__", "__author__", "__email__"]
            ):
                continue
            # If we find function/class definitions or other logic, it's implementation
            if any(
                keyword in line
                for keyword in [
                    "def ",
                    "class ",
                    "if ",
                    "for ",
                    "while ",
                    "try:",
                    "except",
                ]
            ):
                return True

        return False

    def _fast_path_categorize(self, file_path: str) -> Optional[str]:
        """
        Fast path categorization using deterministic patterns.
        Returns category if matched, None if ambiguous (needs LLM).

        SIMPLIFIED: Only handle the most obvious cases to avoid complexity.
        """
        if not file_path:
            return None

        basename = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        # 1. Test files - very clear patterns only
        test_patterns = [
            r"test_.*\.py$",
            r".*_test\.py$",
            r".*\.test\.(js|ts)$",
            r".*\.spec\.(js|ts)$",
            r".*_test\.go$",
        ]
        for pattern in test_patterns:
            if re.match(pattern, basename, re.IGNORECASE):
                return "test"

        # Test directories
        if (
            "/test/" in file_path
            or "/tests/" in file_path
            or "/__tests__/" in file_path
            or file_path.startswith("__tests__/")
            or file_path.startswith("tests/")
            or file_path.startswith("test/")
        ):
            return "test"

        # 2. Documentation - clear extensions only
        if ext in [".md", ".rst", ".txt", ".adoc"]:
            return "docs"

        # Documentation directories
        if "/docs/" in file_path or "/doc/" in file_path:
            return "docs"

        # 3. Well-known config files ONLY
        known_configs = [
            "package.json",
            "tsconfig.json",
            "pyproject.toml",
            "Cargo.toml",
            ".gitignore",
            "Dockerfile",
            "jest.config.js",
        ]
        if basename in known_configs:
            return "config"

        # Config file extensions
        if ext in [".yml", ".yaml", ".json", ".toml", ".ini", ".conf"]:
            return "config"

        # Everything else goes to LLM for proper analysis
        return None

    async def categorize_file(
        self, file_path: str, content: str = ""
    ) -> Dict[str, Any]:
        """
        LLM-based file categorization for strict TDD enforcement.

        EVERY file goes through LLM analysis to ensure consistent and
        intelligent categorization. No fast paths, no fallbacks, no shortcuts
        that can be exploited to bypass TDD.

        Returns dict with:
            category: 'structural', 'config', 'test', 'implementation'
            requires_tdd: bool
            reason: str
        """
        # Use 32KB content preview for better context
        content_preview = content[:32768] if content else ""
        basename = os.path.basename(file_path) if file_path else "unknown"

        # Entry point files ALWAYS require TDD
        entry_points = {
            "main.py",
            "app.py",
            "server.py",
            "cli.py",
            "run.py",
            "start.py",
            "index.py",
        }

        prompt = f"""Analyze this code file to determine if it requires Test-Driven Development (TDD).

FILE: {file_path}
BASENAME: {basename}
CONTENT (first 32KB):
---
{content_preview}
---

Categories:
- "test": Test files (contains test functions/classes)
- "implementation": Code with ANY executable logic, including:
  * Function/class definitions with logic
  * ANY executable statements (print, function calls, variable operations)
  * Main execution blocks (if __name__ == "__main__")
  * ANY code that performs operations when imported or run
  * Entry point files (main.py, app.py, server.py, etc.)
- "structural": ONLY files with imports, constants, type definitions, and NO executable code
- "config": Configuration files (JSON, YAML, TOML, etc.)
- "docs": Documentation files
- "data": Data files (CSV, SQL, etc.)

CRITICAL RULES:
1. A file is "implementation" if it contains ANY of these:
   - Function/method definitions with logic: def func(): return x + y
   - Print statements: print("anything") 
   - Function/method calls: main(), obj.method(), func(args)
   - Mathematical operations: x = a + b
   - Control flow: if/for/while with any logic
   - Any code that EXECUTES when the file is imported or run
   - Entry point patterns: if __name__ == "__main__": (even with just pass)
   - File operations: open(), read(), write()
   - Network operations: requests, urllib, http calls
   - Database operations: queries, connections
   - ANY statement that performs an action

2. A file is ONLY "structural" if it contains ONLY:
   - Import statements: import x, from x import y
   - Constant definitions: CONST = "value", VERSION = "1.0.0"
   - Type definitions/annotations: TypeAlias, TypeVar
   - Empty __init__.py files with ONLY imports
   - Class definitions with ONLY pass or constants
   - NO executable code whatsoever

3. Entry point files ({', '.join(f'"{ep}"' for ep in entry_points)}) are ALWAYS "implementation" regardless of content.

Examples:
- print("hello") → implementation (executable statement)
- main() → implementation (function call)
- x = calculate() → implementation (function call)
- result = 1 + 2 → implementation (operation)
- if __name__ == "__main__": pass → implementation (entry point)
- def main(): pass → implementation (function definition)
- def add(a, b): return a + b → implementation (function with logic)
- class X: pass → implementation (class definition)
- CONSTANT = 42 → structural (ONLY if file has ONLY constants)
- import os → structural (ONLY if file has ONLY imports)
- from typing import Dict → structural (ONLY if file has ONLY imports/types)

BE EXTREMELY STRICT: When in doubt, categorize as "implementation". It's better to require tests than to miss executable code.

Respond with ONLY this JSON:
{{
  "category": "<category>",
  "reason": "<why this category>",
  "requires_tdd": <true for test/implementation, false for others>
}}"""

        try:
            # Create categorization request
            request = {"prompt": prompt}
            request_part = ProcessorPart(json.dumps(request))

            # Process through file categorization processor
            result = {}
            async for response_part in self.file_categorization_processor.call(
                request_part
            ):
                json_data = extract_json_from_part(response_part)
                if json_data:
                    result.update(json_data)

            if result and "error" not in result:
                return {
                    "category": result.get(
                        "category", "implementation"
                    ),  # Default to implementation
                    "requires_tdd": result.get(
                        "requires_tdd", True
                    ),  # Default to requiring TDD
                    "reason": result.get("reason", ""),
                }
            else:
                # If LLM fails, default to requiring TDD (safe default)
                return {
                    "category": "implementation",
                    "requires_tdd": True,
                    "reason": "LLM categorization failed - defaulting to require TDD for safety",
                }

        except Exception as e:
            # ANY error defaults to requiring TDD - no bypasses
            return {
                "category": "implementation",
                "requires_tdd": True,
                "reason": f"Categorization error - defaulting to require TDD for safety: {str(e)}",
            }

    async def validate(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        context: str,
        tdd_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Main TDD validation entry point.

        Args:
            tool_name: The Claude tool being executed
            tool_input: The tool's input parameters
            context: Conversation context
            tdd_context: TDD-specific context (test results, todos, modifications)

        Returns:
            TDDValidationResponse dict with TDD compliance status
        """

        # Skip TDD validation if no API key
        if not self.api_key:
            return {
                "approved": False,
                "reason": "TDD validation blocked: GEMINI_API_KEY not configured",
                "tdd_phase": "unknown",
            }

        # Check file categorization for file-based operations
        if tool_name in ["Write", "Edit", "MultiEdit", "Update"]:
            file_path = tool_input.get("file_path", "")

            # Get content for categorization
            if tool_name in ["Write", "Update"]:
                # Write and Update provide content directly
                content = tool_input.get("content", "")
            else:
                # Edit and MultiEdit need to read the file
                import os

                content = ""
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except Exception:
                        # If we can't read the file, use empty content
                        # This will be caught by categorization logic
                        content = ""

            # Get file category using LLM
            categorization = await self.categorize_file(file_path, content)

            # Skip TDD validation for non-implementation files, BUT test files need validation for multiple test rule
            category = categorization.get("category", "unknown")
            if not categorization.get("requires_tdd", True) and category != "test":
                return {
                    "approved": True,
                    "reason": f"TDD validation not required for {category} files: {categorization.get('reason', '')}",
                    "tdd_phase": "not_applicable",
                    "file_category": category,
                }

        # Route to operation-specific validation
        try:
            if tool_name == "Edit":
                return await self.validate_edit_operation(tool_input, tdd_context)
            elif tool_name == "Write":
                return await self.validate_write_operation(tool_input, tdd_context)
            elif tool_name == "MultiEdit":
                return await self.validate_multi_edit_operation(tool_input, tdd_context)
            elif tool_name == "Update":
                # Update has special handling to diff against existing content
                return await self.validate_update_operation(tool_input, tdd_context)
            else:
                # Other operations (Bash, etc.) don't need TDD validation
                return {
                    "approved": True,
                    "reason": f"{tool_name} operation doesn't require TDD validation",
                    "tdd_phase": "unknown",
                }

        except Exception as e:
            # Fail-safe: block operation if TDD validation fails
            return {
                "approved": False,
                "reason": f"TDD validation service error: {str(e)}",
                "tdd_phase": "unknown",
            }

    async def validate_edit_operation(
        self, tool_input: Dict[str, Any], tdd_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate Edit operations for TDD compliance"""

        file_path = tool_input.get("file_path", "")
        old_content = tool_input.get("old_string", "")
        new_content = tool_input.get("new_string", "")

        # Build TDD analysis prompt
        prompt = self.build_edit_validation_prompt(
            old_content, new_content, file_path, tdd_context
        )

        return await self.execute_tdd_validation(prompt, [file_path])

    async def validate_write_operation(
        self, tool_input: Dict[str, Any], tdd_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate Write operations for TDD compliance"""

        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")

        # Pre-validation: Check test count for test files (ONE test rule)
        if self.detect_test_files(file_path, content):
            test_functions = self.extract_test_functions(content)
            test_count = len(test_functions)

            if test_count > 1:
                return {
                    "approved": False,
                    "violation_type": "multiple_tests",
                    "test_count": test_count,
                    "tdd_phase": "red",
                    "reason": f"TDD: Multiple tests ({test_count}) detected in {file_path}. The ONE test rule requires writing only one test at a time to follow Red-Green-Refactor cycle properly.",
                    "suggestions": [
                        "Split into separate Write operations, one test at a time",
                        "Write first test, run it (RED phase), implement code (GREEN phase), then write next test",
                        "Follow TDD discipline: one test → implementation → refactor → repeat",
                    ],
                    "detailed_analysis": f"Found {test_count} test functions: {', '.join(test_functions)}. TDD methodology requires writing one failing test at a time to maintain focused development and proper test coverage.",
                }
            elif test_count == 1:
                # Single test file - allow without LLM validation to avoid intermittent failures
                return {
                    "approved": True,
                    "violation_type": None,
                    "test_count": test_count,
                    "tdd_phase": "red",
                    "reason": "TDD: Writing single test file - following ONE test rule",
                    "suggestions": [],
                    "detailed_analysis": f"Test file with single test function: {test_functions[0] if test_functions else 'test'}. Following TDD methodology.",
                }
        else:
            # Pre-validation: Check if implementation file has corresponding tests
            # Only check for non-trivial implementation files
            if self._has_implementation_logic(content):
                test_results = tdd_context.get("test_results")

                # Check if there are recent test results or test files in context
                has_failing_tests = bool(
                    test_results
                    and (
                        test_results.get("failures")
                        or test_results.get("errors", 0) > 0
                        or test_results.get("status") == "failed"
                    )
                )

                # Simple heuristic: implementation files should only be written after tests
                # Check if context is empty or has no meaningful test data
                # Note: test_results might be None even if the key exists
                if not tdd_context or tdd_context.get("test_results") is None:
                    # No test context or no test results - block implementation
                    return {
                        "approved": False,
                        "violation_type": "premature_implementation",
                        "tdd_phase": "red",
                        "reason": f"TDD: Writing implementation file {file_path} without failing tests. TDD requires writing a failing test first (Red phase) before implementation.",
                        "suggestions": [
                            "Write a failing test first that describes the desired behavior",
                            "Run the test to confirm it fails (Red phase)",
                            "Only then implement the minimal code to make the test pass (Green phase)",
                            "Follow TDD cycle: Red → Green → Refactor",
                        ],
                        "detailed_analysis": "Implementation file detected without evidence of failing tests. TDD discipline requires test-first development to ensure all code is tested and necessary.",
                    }
                elif not has_failing_tests:
                    # Has test results but no failures - also block
                    return {
                        "approved": False,
                        "violation_type": "premature_implementation",
                        "tdd_phase": "red",
                        "reason": f"TDD: Writing implementation file {file_path} without failing tests. All tests are passing - write a failing test first.",
                        "suggestions": [
                            "Write a failing test for the new functionality",
                            "Ensure the test fails before implementing",
                            "Only implement enough code to make the test pass",
                        ],
                        "detailed_analysis": "Test results show all tests passing. TDD requires a failing test before implementation.",
                    }

        # Build TDD analysis prompt
        prompt = self.build_write_validation_prompt(file_path, content, tdd_context)

        return await self.execute_tdd_validation(prompt, [file_path])

    async def validate_multi_edit_operation(
        self, tool_input: Dict[str, Any], tdd_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate MultiEdit operations for TDD compliance"""

        edits = tool_input.get("edits", [])
        file_path = tool_input.get("file_path", "")

        # Build TDD analysis prompt for multiple edits
        prompt = self.build_multi_edit_validation_prompt(edits, file_path, tdd_context)

        return await self.execute_tdd_validation(prompt, [file_path])

    def build_edit_validation_prompt(
        self,
        old_content: str,
        new_content: str,
        file_path: str,
        tdd_context: Dict[str, Any],
    ) -> str:
        """Build validation prompt for Edit operations"""

        tdd_principles = TDDCorePrompt.get_tdd_principles()
        edit_analysis = EditAnalysisPrompt.get_analysis_prompt(
            old_content, new_content, file_path
        )
        context_info = TDDContextFormatter.format_tdd_context(tdd_context)

        return f"""You are a TDD compliance validator. Analyze this Edit operation for Test-Driven Development violations.

CRITICAL: You MUST analyze ONLY the file specified below. Do NOT reference any other files.

FILE BEING VALIDATED: {file_path}

{tdd_principles}

{edit_analysis}

{context_info}

## CRITICAL INSTRUCTION
You are analyzing ONLY the file: {file_path}
Do NOT mention or reference any other files (no Java files, no other languages).
Base your analysis SOLELY on the content provided above.

## VALIDATION REQUIREMENTS

Your task is to determine if this Edit operation violates TDD principles. Focus on:

1. **New Test Count**: How many completely new tests are being added?
2. **Implementation Scope**: Is the implementation minimal and test-driven?
3. **TDD Phase Compliance**: Does this follow Red-Green-Refactor properly?
4. **Over-implementation**: Are features being added beyond test requirements?

## DECISION FRAMEWORK

**APPROVE** if:
- Zero or one new test being added
- Implementation is minimal and addresses specific test failures
- Changes follow Red-Green-Refactor discipline
- No premature optimization or over-engineering

**BLOCK** if:
- Multiple new tests being added in single operation
- Over-implementation beyond current test requirements
- Implementation without corresponding test failures
- Features added that aren't tested

## RESPONSE FORMAT

Provide structured TDD validation response with:
- **approved**: boolean decision
- **violation_type**: specific TDD violation if any
- **test_count**: number of new tests detected
- **tdd_phase**: current phase (red/green/refactor)
- **reason**: clear explanation of decision
- **suggestions**: actionable TDD improvements
- **detailed_analysis**: comprehensive TDD assessment

Analyze thoroughly and enforce TDD discipline to maintain code quality and test coverage."""

    def build_write_validation_prompt(
        self, file_path: str, content: str, tdd_context: Dict[str, Any]
    ) -> str:
        """Build validation prompt for Write operations"""

        tdd_principles = TDDCorePrompt.get_tdd_principles()
        write_analysis = WriteAnalysisPrompt.get_analysis_prompt(file_path, content)
        context_info = TDDContextFormatter.format_tdd_context(tdd_context)

        return f"""You are a TDD compliance validator. Analyze this Write operation for Test-Driven Development violations.

CRITICAL: You MUST analyze ONLY the file specified below. Do NOT reference any other files.

FILE BEING VALIDATED: {file_path}

{tdd_principles}

{write_analysis}

{context_info}

## CRITICAL INSTRUCTION
You are analyzing ONLY the file: {file_path}
Do NOT mention or reference any other files (no Java files, no other languages).
Base your analysis SOLELY on the content provided above.

## VALIDATION REQUIREMENTS

Your task is to determine if this Write operation violates TDD principles. Focus on:

1. **File Type**: Is this a test file or implementation file?
2. **Test Count**: If test file, count how many NEW test functions are being added (CRITICAL: only ONE allowed)
3. **Test Coverage**: For implementation files, are there corresponding tests?
4. **Implementation Justification**: Is implementation driven by test failures?
5. **Scope Assessment**: Is implementation minimal and focused?

## DECISION FRAMEWORK

**APPROVE** if:
- Writing test files with ONLY ONE new test at a time
- Writing minimal implementation to address specific test failures
- Creating infrastructure/setup code that supports testing
- Implementation scope matches test requirements

**BLOCK** if:
- Writing multiple tests in a single operation (even in test files)
- Creating implementation files without corresponding tests
- Over-implementing beyond current test requirements
- Writing speculative code not driven by test failures
- Implementing multiple features without adequate test coverage

## RESPONSE FORMAT

Provide structured TDD validation response focusing on file creation compliance with TDD workflow."""

    def build_multi_edit_validation_prompt(
        self, edits: List[Dict[str, Any]], file_path: str, tdd_context: Dict[str, Any]
    ) -> str:
        """Build validation prompt for MultiEdit operations"""

        tdd_principles = TDDCorePrompt.get_tdd_principles()
        multi_edit_analysis = MultiEditAnalysisPrompt.get_analysis_prompt(edits)
        context_info = TDDContextFormatter.format_tdd_context(tdd_context)

        return f"""You are a TDD compliance validator. Analyze this MultiEdit operation for Test-Driven Development violations.

CRITICAL: You MUST analyze ONLY the file specified below. Do NOT reference any other files.

FILE BEING VALIDATED: {file_path}

{tdd_principles}

{multi_edit_analysis}

{context_info}

## CRITICAL INSTRUCTION
You are analyzing ONLY the file: {file_path}
Do NOT mention or reference any other files (no Java files, no other languages).
Base your analysis SOLELY on the content provided above.

## VALIDATION REQUIREMENTS

Your task is to determine if this MultiEdit operation violates TDD principles. Focus on:

1. **Cumulative New Tests**: Total new tests across ALL edits
2. **Sequential Implementation**: Is each edit minimal and justified?
3. **Scope Coherence**: Do all edits work toward single test goal?
4. **Progressive Compliance**: Does each edit maintain TDD discipline?

## CRITICAL RULE

**CUMULATIVE NEW TEST COUNT** across all edits must not exceed 1. This is the most important check for MultiEdit operations.

## DECISION FRAMEWORK

**APPROVE** if:
- Total new tests across all edits ≤ 1
- Each edit contributes to minimal implementation
- Sequential changes maintain test-driven approach
- No over-implementation or feature sprawl

**BLOCK** if:
- Total new tests across all edits > 1
- Edits implement features beyond test requirements
- Sequential changes show scope creep or over-engineering
- MultiEdit is being used to circumvent single-test rule

## RESPONSE FORMAT

Provide structured TDD validation response with special attention to cumulative effects of multiple edits."""

    async def validate_language_consistency(
        self, response: Dict[str, Any], file_path: str, affected_files: List[str]
    ) -> Dict[str, Any]:
        """Check if response contains language-inappropriate suggestions"""
        language = self.detect_language(file_path)
        if language == "unknown":
            return response

        # Quick check for obvious language mismatches
        combined_text = (
            f"{response.get('reason', '')} {response.get('detailed_analysis', '')}"
        )

        # Count language indicators
        if language == "Python":
            # Count Java indicators in Python response
            java_indicators = (
                combined_text.count(".java")
                + combined_text.count("public class")
                + combined_text.count("@Test")
                + combined_text.count("assertEquals")
                + combined_text.count("ServiceImpl")
                + combined_text.count("src/test/java")
            )
            if java_indicators >= 2:  # Multiple indicators suggest Java
                # Return sanitized response
                return {
                    "approved": response.get("approved", False),
                    "violation_type": response.get("violation_type"),
                    "test_count": response.get("test_count"),
                    "affected_files": response.get("affected_files", affected_files),
                    "tdd_phase": response.get("tdd_phase", "unknown"),
                    "reason": response.get("reason", "")
                    .replace("ServiceImpl.java", "implementation file")
                    .replace("Test.java", "test file"),
                    "suggestions": [
                        s for s in response.get("suggestions", []) if ".java" not in s
                    ],
                    "detailed_analysis": "Language-appropriate TDD validation required. Please follow Python testing patterns.",
                }

        return response

    async def execute_tdd_validation(
        self, prompt: str, affected_files: List[str]
    ) -> Dict[str, Any]:
        """Execute TDD validation using Gemini with structured response"""

        try:
            # Create validation request
            request = {"prompt": prompt}
            request_part = ProcessorPart(json.dumps(request))

            # Process through TDD validation processor
            result = {}
            async for response_part in self.processor.call(request_part):
                json_data = extract_json_from_part(response_part)
                if json_data:
                    result.update(json_data)

            # Check if we got a valid result
            if not result:
                # No valid JSON response from LLM
                if os.environ.get("DEBUG"):
                    print("DEBUG: No result from LLM", file=sys.stderr)
                return {
                    "approved": False,
                    "reason": "TDD validation blocked: No valid response from LLM",
                    "tdd_phase": "unknown",
                    "affected_files": affected_files,
                }

            if "error" not in result:
                # Apply language consistency validation
                if affected_files and affected_files[0]:
                    result = await self.validate_language_consistency(
                        result, affected_files[0], affected_files
                    )

                return {
                    "approved": result.get("approved", False),
                    "violation_type": result.get("violation_type"),
                    "test_count": result.get("test_count"),
                    "affected_files": result.get("affected_files", affected_files),
                    "tdd_phase": result.get("tdd_phase", "unknown"),
                    "reason": result.get("reason", ""),
                    "suggestions": result.get("suggestions", []),
                    "detailed_analysis": result.get("detailed_analysis"),
                }
            else:
                # Handle error case
                return {
                    "approved": False,
                    "reason": f"TDD validation blocked: {result.get('error', 'TDD validation service error')}",
                    "tdd_phase": "unknown",
                    "affected_files": affected_files,
                }

        except Exception as e:
            # Fail-safe: block operation if TDD validation fails
            return {
                "approved": False,
                "reason": f"TDD validation service error: {str(e)}",
                "tdd_phase": "unknown",
                "affected_files": affected_files,
            }

    def detect_test_files(self, file_path: str, content: str = "") -> bool:
        """Detect if a file is a test file based on path and content"""

        # Path-based detection
        test_path_patterns = [
            r"test.*\.py$",
            r".*_test\.py$",
            r".*\.test\.py$",
            r"test.*\.js$",
            r".*\.test\.js$",
            r".*\.spec\.js$",
            r"test.*\.go$",
            r".*_test\.go$",
            r"Test.*\.java$",
            r".*Test\.java$",
            r"/tests?/",
            r"\\tests?\\",
        ]

        for pattern in test_path_patterns:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True

        # Content-based detection
        if content:
            test_content_patterns = [
                r"def test_",
                r"class Test",
                r"import unittest",
                r"test\(",
                r"describe\(",
                r"it\(",
                r"expect\(",
                r"func Test",
                r"@Test",
                r"@pytest",
            ]

            for pattern in test_content_patterns:
                if re.search(pattern, content):
                    return True

        return False

    def count_new_tests(self, old_content: str, new_content: str) -> int:
        """Count new test functions added (character-by-character comparison)"""

        # Extract test functions from both contents
        old_tests = self.extract_test_functions(old_content)
        new_tests = self.extract_test_functions(new_content)

        # Count tests that exist in new but not in old
        new_test_count = 0
        for test in new_tests:
            if test not in old_tests:
                new_test_count += 1

        return new_test_count

    def extract_test_functions(self, content: str) -> List[str]:
        """Extract test function names from code content"""

        test_patterns = [
            r"def (test_\w+)",  # Python test functions
            r"def (should_\w+)",  # Python BDD-style tests
            r'test\s*\(\s*[\'"]([^\'"]+)[\'"]',  # JavaScript test()
            r'it\s*\(\s*[\'"]([^\'"]+)[\'"]',  # JavaScript it()
            r"func (Test\w+)",  # Go test functions
            r"@Test\s+\w+\s+(\w+)",  # Java test methods
        ]

        test_functions = []
        for pattern in test_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            test_functions.extend(matches)

        return test_functions

    async def validate_update_operation(
        self, tool_input: Dict[str, Any], tdd_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate Update operations for TDD compliance.

        Update operations replace entire file content, so we need to:
        1. Read the existing file content
        2. Compare old vs new to count only genuinely new tests
        3. Apply the same TDD rules but only for new additions
        """

        file_path = tool_input.get("file_path", "")
        new_content = tool_input.get("content", "")

        # Try to read existing file content
        import os

        old_content = ""
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    old_content = f.read()
            except Exception:
                # If we can't read the file, treat it as a new file (Write operation)
                return await self.validate_write_operation(tool_input, tdd_context)
        else:
            # File doesn't exist, treat as Write operation
            return await self.validate_write_operation(tool_input, tdd_context)

        # For test files, check new test count
        if self.detect_test_files(file_path, new_content):
            old_tests = self.extract_test_functions(old_content)
            new_tests = self.extract_test_functions(new_content)

            # Count only genuinely new tests
            genuinely_new_tests = [t for t in new_tests if t not in old_tests]
            new_test_count = len(genuinely_new_tests)

            if new_test_count > 1:
                return {
                    "approved": False,
                    "violation_type": "multiple_tests",
                    "test_count": new_test_count,
                    "tdd_phase": "red",
                    "reason": f"TDD: Multiple new tests ({new_test_count}) detected in Update operation. The ONE test rule requires adding only one new test at a time.",
                    "suggestions": [
                        f"You're adding {new_test_count} new tests: {', '.join(genuinely_new_tests)}",
                        "Add only the first new test, commit, then add the next test in a separate Update",
                        "Follow TDD discipline: one test → implementation → refactor → repeat",
                    ],
                    "detailed_analysis": f"Existing tests: {len(old_tests)}, Total tests after update: {len(new_tests)}, New tests being added: {new_test_count}. TDD requires incremental test development.",
                }
            elif new_test_count == 0:
                # Special case: modifying test file without adding new tests
                # This is always allowed (refactoring existing tests)
                return {
                    "approved": True,
                    "reason": "TDD: Test file modification without adding new tests is allowed. Refactoring existing tests is a valid TDD practice.",
                    "tdd_phase": "refactor",
                    "test_count": 0,
                    "affected_files": [file_path],
                    "detailed_analysis": f"Test file update detected with no new tests added. Existing tests: {len(old_tests)}, Total tests after update: {len(new_tests)}. Test refactoring and improvements are encouraged.",
                }
            # If it's a test file adding exactly one new test, continue to LLM validation

        # Implementation file logic - only for non-test files
        elif not self.detect_test_files(file_path, new_content):
            # Pre-validation: Check if implementation file update has corresponding tests
            # Only check for non-trivial implementation files
            if self._has_implementation_logic(new_content):
                # Check if there are recent test results or test files in context
                test_results = tdd_context.get("test_results")
                has_failing_tests = bool(
                    test_results
                    and (
                        test_results.get("failures")
                        or test_results.get("errors", 0) > 0
                        or test_results.get("status") == "failed"
                    )
                )

                # Simple heuristic: implementation updates should only happen after tests
                # Check if context is empty or has no meaningful test data
                # Note: test_results might be None even if the key exists
                if not tdd_context or tdd_context.get("test_results") is None:
                    # No test context or no test results - block implementation
                    return {
                        "approved": False,
                        "violation_type": "premature_implementation",
                        "tdd_phase": "red",
                        "reason": "TDD: Updating implementation without failing tests. TDD requires writing a failing test first (Red phase) before implementation.",
                        "suggestions": [
                            "Write a failing test first that describes the desired behavior",
                            "Run the test to confirm it fails (Red phase)",
                            "Only then update the implementation to make the test pass (Green phase)",
                            "Follow TDD cycle: Red → Green → Refactor",
                        ],
                        "detailed_analysis": "Implementation update detected without evidence of failing tests. TDD discipline requires test-first development to ensure all changes are tested and necessary.",
                    }
                elif not has_failing_tests:
                    # Has test results but no failures - also block
                    return {
                        "approved": False,
                        "violation_type": "premature_implementation",
                        "tdd_phase": "red",
                        "reason": "TDD: Updating implementation without failing tests. All tests are passing - write a failing test first.",
                        "suggestions": [
                            "Write a failing test for the new functionality",
                            "Ensure the test fails before implementing",
                            "Only then update the implementation",
                        ],
                        "detailed_analysis": "Test results show all tests passing. TDD requires a failing test before implementation updates.",
                    }

        # Build TDD analysis prompt for Update operations
        prompt = self.build_update_validation_prompt(
            file_path, old_content, new_content, tdd_context
        )

        return await self.execute_tdd_validation(prompt, [file_path])

    def build_update_validation_prompt(
        self,
        file_path: str,
        old_content: str,
        new_content: str,
        tdd_context: Dict[str, Any],
    ) -> str:
        """Build validation prompt specifically for Update operations"""

        tdd_principles = TDDCorePrompt.get_tdd_principles()
        context_info = TDDContextFormatter.format_tdd_context(tdd_context)

        return f"""You are a TDD compliance validator. Analyze this Update operation for Test-Driven Development violations.

CRITICAL: You MUST analyze ONLY the file specified below. Do NOT reference any other files.

FILE BEING VALIDATED: {file_path}

{tdd_principles}

## UPDATE OPERATION ANALYSIS

File Path: {file_path}

## CRITICAL INSTRUCTION
You are analyzing ONLY the file: {file_path}
Do NOT mention or reference any other files (no Java files, no other languages).
Base your analysis SOLELY on the content provided below.

## STEP 1: FILE TYPE IDENTIFICATION

CRITICAL: First, analyze the ACTUAL file being updated to determine its type.

File path indicators for TEST FILES:
- Ends with: _test.py, .test.py, _spec.py, .spec.py
- Contains: /test/, /tests/, /spec/, /specs/
- Common patterns: test_*.py, *_test.py, test*.py

Content indicators for TEST FILES:
- Contains: def test_*, class Test*, @pytest, import pytest
- Contains: describe(, it(, expect(, assert
- Contains: unittest, TestCase, @Test

File being updated: {file_path}

IMPORTANT: Look at the ACTUAL file path and content above, not hypothetical examples!
If the file contains test functions like "def test_feature_one", it IS a test file!

PREVIOUS CONTENT (first 3000 chars):
{old_content[:3000]}

NEW CONTENT (first 3000 chars):  
{new_content[:3000]}

{context_info}

## CRITICAL: UPDATE OPERATION RULES

Update operations REPLACE the entire file content. You must:
1. First determine if this is a TEST FILE or PRODUCTION CODE
2. Compare old vs new content to identify what's actually changing
3. Count only GENUINELY NEW tests (not existing tests)
4. Apply TDD rules only to the NET changes, not the entire file
5. Recognize test modification/evolution as valid TDD practice

## TEST FILE VS PRODUCTION CODE

**For TEST FILES (files containing test functions):**
- Refactoring existing tests without adding new ones is ALWAYS ALLOWED
- Adding ONE new test is allowed
- Adding multiple new tests (net increase > 1) is BLOCKED
- Test files do NOT require failing tests in context - they ARE the tests

**For PRODUCTION CODE (implementation files):**
- Must have failing tests in context before implementation
- Implementation changes must be justified by test failures
- Over-implementation beyond test requirements is BLOCKED

## TEST MODIFICATION VS ADDITION

**Test Modification (ALLOWED during Red phase):**
- Changing test implementation but keeping same function name
- Renaming test function (e.g., test_login → test_login_redirects)
- Replacing one test with another (removing old, adding new = net zero)
- Simplifying complex test into focused one

**Test Addition (ONE at a time):**
- Net increase in test count must be ≤ 1
- Count = (new total tests) - (old total tests)
- If count > 1, this is adding multiple tests → BLOCK

## VALIDATION REQUIREMENTS

Focus on:
1. **NET Test Change**: (new test count) - (old test count) ≤ 1
2. **Test Evolution**: Is this refining existing test or adding new behavior?
3. **Implementation Justification**: If adding implementation, is it test-driven?
4. **Change Purpose**: Red phase refinement vs new feature addition

## DECISION FRAMEWORK

**APPROVE** if:
- TEST FILE: Modifying/refactoring existing tests without adding new ones
- TEST FILE: Adding only ONE new test (net increase = 1)
- TEST FILE: Replacing one test with another (net increase = 0)
- PRODUCTION CODE: Adding minimal implementation for existing failing tests
- PRODUCTION CODE: Refactoring while keeping tests green

**BLOCK** if:
- TEST FILE: Adding multiple new tests (net increase > 1)
- PRODUCTION CODE: Adding implementation without test justification
- PRODUCTION CODE: Over-implementing beyond test requirements
- INCORRECTLY treating test file modifications as "new feature files"

CRITICAL: If the file contains test functions (def test_*, it(), describe(), etc.), it is a TEST FILE, not a feature/production file. Test files being modified do NOT require "corresponding test files" - they ARE the test files!

## STEP 2: APPLY CORRECT RULES

If you determined this is a TEST FILE:
- APPROVE if modifying existing tests without adding new ones
- APPROVE if adding only ONE new test
- BLOCK only if adding multiple new tests
- DO NOT ask for "corresponding test files" - this IS the test file!

If you determined this is PRODUCTION CODE:
- Check for failing tests in context
- Ensure implementation is test-driven

Remember: The file may already contain tests. Only new additions count toward the one-test limit."""
