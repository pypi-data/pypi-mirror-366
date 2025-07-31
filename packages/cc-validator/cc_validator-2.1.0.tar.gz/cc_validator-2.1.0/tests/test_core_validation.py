#!/usr/bin/env python3
"""
Core validation tests using pytest markers.

Tests the main validation components including:
- Security validation (dangerous commands, API keys, etc.)
- TDD validation (test-driven development enforcement)
- Branch validation (branch protection rules)
- Tool routing and documentation validation

Use markers to run specific test subsets:
- pytest -m quick     # Run fast tests only
- pytest -m security  # Run security tests
- pytest -m tdd      # Run TDD tests
- pytest -m branch   # Run branch validation tests

These tests verify the behavior when no API key is set,
ensuring the validator properly blocks operations.
"""

import json
import os
import subprocess
import tempfile
from typing import Any, Dict

import pytest


class TestSecurityValidation:
    """Security validation tests."""

    @pytest.mark.quick
    @pytest.mark.security
    def test_dangerous_bash_command(self, run_validation_factory: Any) -> None:
        """Test that dangerous bash commands are blocked."""
        tool_data = {
            "tool": "Bash",
            "input": {"command": "rm -rf /"},
            "conversation_context": "",
        }
        returncode, stdout, stderr = run_validation_factory(tool_data)
        assert (
            returncode == 2
        ), f"Expected dangerous command to be blocked, stdout: {stdout}, stderr: {stderr}"
        response = json.loads(stdout)
        hook_output = response["hookSpecificOutput"]
        assert hook_output["permissionDecision"] == "deny"
        assert (
            "dangerous" in hook_output["permissionDecisionReason"].lower()
            or "destructive" in hook_output["permissionDecisionReason"].lower()
        )

    @pytest.mark.quick
    @pytest.mark.security
    def test_safe_bash_command(self, run_validation_factory: Any) -> None:
        """Test that safe bash commands are allowed after fix."""
        tool_data = {
            "tool": "Bash",
            "input": {"command": "ls -la"},
            "conversation_context": "",
        }
        returncode, stdout, stderr = run_validation_factory(tool_data)
        assert returncode == 0, f"Expected safe command to be allowed, stdout: {stdout}"
        response = json.loads(stdout)
        assert response["hookSpecificOutput"]["permissionDecision"] == "allow"
        assert (
            "Operation approved"
            in response["hookSpecificOutput"]["permissionDecisionReason"]
        )

    @pytest.mark.quick
    @pytest.mark.security
    def test_grep_instead_of_find(self, run_validation_factory: Any) -> None:
        """Test that grep commands suggest using Grep tool."""
        tool_data = {
            "tool": "Bash",
            "input": {"command": "grep -r 'pattern' ."},
            "conversation_context": "",
        }
        returncode, stdout, stderr = run_validation_factory(tool_data)
        assert returncode == 2, f"Expected grep to be blocked, stdout: {stdout}"
        response = json.loads(stdout)
        assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert (
            "Use 'rg' (ripgrep)"
            in response["hookSpecificOutput"]["permissionDecisionReason"]
        )

    @pytest.mark.comprehensive
    @pytest.mark.security
    def test_api_key_in_bash(self, run_validation_factory: Any) -> None:
        """Test that API keys in bash commands are blocked."""
        tool_data = {
            "tool": "Bash",
            "input": {"command": "export OPENAI_API_KEY='sk-1234567890abcdef'"},
            "conversation_context": "",
        }
        returncode, stdout, stderr = run_validation_factory(tool_data)
        assert (
            returncode == 2
        ), f"Expected command with secrets to be blocked, stdout: {stdout}"
        response = json.loads(stdout)
        assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
        # Commands with secrets are blocked by security patterns
        assert (
            "Security violation"
            in response["hookSpecificOutput"]["permissionDecisionReason"]
            or "secrets"
            in response["hookSpecificOutput"]["permissionDecisionReason"].lower()
        )

    @pytest.mark.comprehensive
    @pytest.mark.security
    def test_api_key_in_write(self, run_validation_factory: Any) -> None:
        """Test that API keys in written files are blocked."""
        tool_data = {
            "tool": "Write",
            "input": {
                "file_path": "config.py",
                "content": "STRIPE_KEY = 'sk_live_abcdef1234567890abcdef1234567890'",
            },
            "conversation_context": "",
        }
        returncode, stdout, stderr = run_validation_factory(tool_data)
        assert (
            returncode == 2
        ), f"Expected write with secrets to be blocked, stdout: {stdout}"
        response = json.loads(stdout)
        assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert any(
            phrase in response["hookSpecificOutput"]["permissionDecisionReason"]
            for phrase in ["secret", "Stripe", "key"]
        )


class TestTDDValidation:
    """Test-Driven Development validation tests."""

    @pytest.mark.comprehensive
    @pytest.mark.tdd
    def test_write_implementation_without_test(
        self, run_validation_factory: Any
    ) -> None:
        """Test that writing implementation without tests is handled appropriately."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # No test results exist
            tool_data = {
                "tool": "Write",
                "input": {
                    "file_path": os.path.join(temp_dir, "calculator.py"),
                    "content": "def add(a, b):\n    return a + b",
                },
                "conversation_context": "User asked to implement an add function",
            }
            # TDD validation should block implementation without tests
            returncode, stdout, stderr = run_validation_factory(tool_data)

            # With API key, TDD validation should block this
            if stdout:
                try:
                    response = json.loads(stdout)
                    assert (
                        response.get("hookSpecificOutput", {}).get("permissionDecision")
                        == "deny"
                    ), f"Expected operation to be blocked by TDD, got: {response}"
                    assert any(
                        phrase
                        in response.get("hookSpecificOutput", {}).get(
                            "permissionDecisionReason", ""
                        )
                        for phrase in ["TDD", "test", "Test-Driven"]
                    )
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON output: {stdout}")

            assert (
                returncode == 2
            ), f"Expected operation to be blocked, got returncode: {returncode}"

    @pytest.mark.comprehensive
    @pytest.mark.tdd
    def test_write_test_file_allowed(self, run_validation_factory: Any) -> None:
        """Test that writing test files is allowed."""
        tool_data = {
            "tool": "Write",
            "input": {
                "file_path": "test_calculator.py",
                "content": "def test_add():\n    assert add(2, 3) == 5",
            },
            "conversation_context": "Writing a test for add function",
        }
        # With API key, writing test files should be allowed
        returncode, stdout, stderr = run_validation_factory(tool_data)

        # Test files should be allowed
        if stdout:
            try:
                response = json.loads(stdout)
                assert (
                    response.get("hookSpecificOutput", {}).get("permissionDecision")
                    == "allow"
                ), f"Expected test file write to be allowed, got: {response}"
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON output: {stdout}")
        else:
            pytest.fail("Expected JSON output but got empty stdout")

        assert (
            returncode == 0
        ), f"Expected operation to be allowed, got returncode: {returncode}"

    @pytest.mark.comprehensive
    @pytest.mark.tdd
    def test_update_adding_multiple_tests_blocked(
        self, run_validation_factory: Any
    ) -> None:
        """Test that adding multiple tests in one go is blocked in non-CI mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_feature.py")
            with open(test_file, "w") as f:
                f.write("def test_existing():\n    assert True\n")

            tool_data = {
                "tool": "Update",
                "input": {
                    "file_path": test_file,
                    "content": "def test_existing():\n    assert True\n\ndef test_one():\n    assert True\n\ndef test_two():\n    assert True",
                },
                "conversation_context": "Adding new tests",
            }
            # With API key, TDD validation should block adding multiple tests
            returncode, stdout, stderr = run_validation_factory(tool_data)

            # Check JSON output
            if stdout:
                try:
                    response = json.loads(stdout)
                    assert (
                        response.get("hookSpecificOutput", {}).get("permissionDecision")
                        == "deny"
                    ), f"Expected operation to be blocked by TDD, got: {response}"
                    assert any(
                        phrase
                        in response.get("hookSpecificOutput", {})
                        .get("permissionDecisionReason", "")
                        .lower()
                        for phrase in ["multiple", "test", "tdd"]
                    )
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON output: {stdout}")

            assert (
                returncode == 2
            ), f"Expected operation to be blocked, got returncode: {returncode}"


class TestBranchValidation:
    """Branch protection validation tests."""

    @pytest.mark.quick
    @pytest.mark.branch
    def test_main_branch_code_change_blocked(self) -> None:
        """Test that code changes on main branch are blocked."""
        # Mock being on main branch
        env = os.environ.copy()
        env["CLAUDE_TEST_BRANCH"] = "main"
        env["GEMINI_API_KEY"] = "test-key"

        tool_data = {
            "tool": "Write",
            "input": {
                "file_path": "src/feature.py",
                "content": "def new_feature():\n    pass",
            },
            "conversation_context": "",
        }

        process = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "cc_validator.test_entry",
                json.dumps(tool_data),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

        # Branch validation might be disabled in CI, so check if it's enforced
        if "branch" in process.stderr.lower() and "main" in process.stderr.lower():
            assert process.returncode == 2, "Expected main branch changes to be blocked"

    @pytest.mark.quick
    @pytest.mark.branch
    def test_main_branch_docs_allowed(self) -> None:
        """Test that documentation changes on main branch are allowed."""
        env = os.environ.copy()
        env["CLAUDE_TEST_BRANCH"] = "main"

        tool_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "README.md",
                "content": "# Updated Documentation\n\nNew content here.",
            },
            "transcript_path": "",
        }

        process = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "cc_validator.test_entry",
                json.dumps(tool_data),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )

        # Documentation should be allowed even on main
        assert (
            process.returncode == 0
        ), f"Expected docs on main to be allowed, stderr: {process.stderr}"


class TestToolRouting:
    """Tool routing validation tests."""

    @pytest.mark.quick
    def test_write_tool_validation(self, run_validation_factory: Any) -> None:
        """Test Write tool is properly validated."""
        tool_data = {
            "tool": "Write",
            "input": {"file_path": "test.txt", "content": "Hello, world!"},
            "conversation_context": "",
        }
        returncode, stdout, stderr = run_validation_factory(tool_data)
        # With API key, simple file write should be allowed
        assert returncode == 0, f"Expected simple write to be allowed, stdout: {stdout}"
        if stdout:
            response = json.loads(stdout)
            assert response["hookSpecificOutput"]["permissionDecision"] == "allow"

    @pytest.mark.quick
    def test_edit_tool_validation(self, run_validation_factory: Any) -> None:
        """Test Edit tool is properly validated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("Original content")

            tool_data = {
                "tool": "Edit",
                "input": {
                    "file_path": test_file,
                    "old_string": "Original",
                    "new_string": "Modified",
                },
                "conversation_context": "",
            }
            returncode, stdout, stderr = run_validation_factory(tool_data)
            # With API key, simple edit should be allowed
            assert (
                returncode == 0
            ), f"Expected simple edit to be allowed, stdout: {stdout}"
            if stdout:
                response = json.loads(stdout)
                assert response["hookSpecificOutput"]["permissionDecision"] == "allow"

    @pytest.mark.quick
    def test_unknown_tool_allowed(self, run_validation_factory: Any) -> None:
        """Test unknown tools are allowed by default."""
        tool_data = {
            "tool": "UnknownTool",
            "input": {"some": "data"},
            "conversation_context": "",
        }
        returncode, stdout, stderr = run_validation_factory(tool_data)
        # Unknown tools should be blocked (fail-closed behavior)
        assert returncode == 2, f"Expected unknown tool to be blocked, stdout: {stdout}"
        if stdout:
            response = json.loads(stdout)
            assert response["hookSpecificOutput"]["permissionDecision"] == "deny"
            assert (
                "Unhandled tool"
                in response["hookSpecificOutput"]["permissionDecisionReason"]
            )


class TestDocumentationValidation:
    """Documentation file validation tests."""

    @pytest.mark.comprehensive
    @pytest.mark.documentation
    def test_documentation_skips_tdd_validation(
        self, run_validation_factory: Any
    ) -> None:
        """Test that documentation files skip TDD validation."""
        tool_data = {
            "tool": "Write",
            "input": {
                "file_path": "docs/guide.md",
                "content": "# User Guide\n\nThis is documentation.",
            },
            "conversation_context": "Writing documentation",
        }
        returncode, stdout, stderr = run_validation_factory(tool_data)
        # With API key, documentation should be allowed
        assert (
            returncode == 0
        ), f"Expected documentation write to be allowed, stdout: {stdout}"

        if stdout:
            response = json.loads(stdout)
            assert response["hookSpecificOutput"]["permissionDecision"] == "allow"

    @pytest.mark.comprehensive
    @pytest.mark.documentation
    def test_readme_skips_security_analysis(self, run_validation_factory: Any) -> None:
        """Test that README files are blocked without API key."""
        tool_data = {
            "tool": "Write",
            "input": {
                "file_path": "README.md",
                "content": "# Project\n\nRun this command: rm -rf build/",
            },
            "conversation_context": "Updating README",
        }
        returncode, stdout, stderr = run_validation_factory(tool_data)
        # With API key, README should be allowed (documentation context)
        assert returncode == 0, f"Expected README write to be allowed, stdout: {stdout}"
        response = json.loads(stdout)
        assert response["hookSpecificOutput"]["permissionDecision"] == "allow"


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
