#!/usr/bin/env python3
"""
Integration tests for Claude Code hook execution.

These tests simulate the actual Claude Code environment and verify that
the validator works correctly when invoked as a pre-commit hook.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from typing import Dict, Any, Tuple, Optional, List
import signal
import pytest


class MockClaudeCodeEnvironment:
    """Mock environment that simulates Claude Code's hook invocation"""

    def __init__(self, timeout_ms: int = 15000):
        self.timeout_ms = timeout_ms
        self.timeout_seconds = timeout_ms / 1000.0

    def create_hook_input(
        self,
        tool_name: str,
        tool_input: Dict[str, Any],
        session_id: str = "test-session-123",
        transcript_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a hook input matching Claude Code's format"""
        if transcript_path is None:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".jsonl", delete=False
            ) as f:
                f.write('{"role": "user", "content": "Test command"}\\n')
                transcript_path = f.name

        return {
            "session_id": session_id,
            "transcript_path": transcript_path,
            "hook_event_name": "PreToolUse",
            "tool_name": tool_name,
            "tool_input": tool_input,
        }

    def invoke_hook(
        self, hook_input: Dict[str, Any], env_vars: Optional[Dict[str, str]] = None
    ) -> Tuple[int, str, str, float]:
        """
        Invoke the validator hook with timeout handling.

        Returns: (exit_code, stdout, stderr, duration_ms)
        """
        start_time = time.time()

        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        try:
            process = subprocess.Popen(
                ["uv", "run", "python", "-m", "cc_validator"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                preexec_fn=os.setsid if sys.platform != "win32" else None,
            )

            try:
                stdout, stderr = process.communicate(
                    input=json.dumps(hook_input), timeout=self.timeout_seconds
                )
                exit_code = process.returncode
            except subprocess.TimeoutExpired:
                # Kill the entire process group
                if sys.platform != "win32":
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()

                # Give it a moment to terminate gracefully
                try:
                    process.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    process.kill()

                stdout, stderr = process.communicate()
                exit_code = -1
                stderr = f"TIMEOUT: Hook execution exceeded {self.timeout_ms}ms limit\\n{stderr}"

        except Exception as e:
            exit_code = -2
            stdout = ""
            stderr = f"ERROR: {str(e)}"

        duration_ms = (time.time() - start_time) * 1000
        return exit_code, stdout, stderr, duration_ms


class IntegrationTestSuite:
    """Integration test suite for Claude Code hooks"""

    def __init__(self) -> None:
        self.env = MockClaudeCodeEnvironment()
        self.results: list[dict[str, Any]] = []

    def run_test(
        self,
        test_name: str,
        tool_name: str,
        tool_input: Dict[str, Any],
        expected_exit_code: int,
        expected_in_output: Optional[List[str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        max_duration_ms: Optional[float] = None,
    ) -> bool:
        """Run a single integration test"""
        print(f"\\n{'=' * 60}")
        print(f"TEST: {test_name}")
        print(f"Tool: {tool_name}")

        hook_input = self.env.create_hook_input(tool_name, tool_input)
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input, env_vars
        )

        print(f"Exit Code: {exit_code} (expected: {expected_exit_code})")
        print(f"Duration: {duration_ms:.2f}ms")

        passed = True

        # Check exit code
        if exit_code != expected_exit_code:
            print("✗ FAILED - Wrong exit code")
            print(f"  Expected: {expected_exit_code}, Got: {exit_code}")
            if stderr:
                print(f"  Stderr: {stderr[:200]}...")
            passed = False

        # Check expected output
        if expected_in_output and passed:
            output = stdout + stderr
            for expected in expected_in_output:
                if expected not in output:
                    print(f"✗ FAILED - Missing expected output: '{expected}'")
                    print(f"  Stdout: {stdout[:200]}...")
                    print(f"  Stderr: {stderr[:200]}...")
                    passed = False

        # Check duration
        if max_duration_ms and duration_ms > max_duration_ms:
            print(f"⚠️  WARNING - Exceeded max duration: {max_duration_ms}ms")

        if passed:
            print("✓ PASSED")

        self.results.append(
            {"test": test_name, "passed": passed, "duration_ms": duration_ms}
        )

        # Clean up transcript file
        if "transcript_path" in hook_input:
            try:
                os.unlink(hook_input["transcript_path"])
            except OSError:
                pass

        return passed

    def run_timeout_test(self) -> bool:
        """Test timeout handling specifically"""
        print(f"\\n{'=' * 60}")
        print("TEST: Timeout Handling")

        # Create a hook input that will cause a long-running operation
        hook_input = self.env.create_hook_input(
            "Write",
            {
                "file_path": "test.py",
                "content": "x" * 1000000,  # Very large content to slow down processing
            },
        )

        # Use a very short timeout to force timeout
        env = MockClaudeCodeEnvironment(timeout_ms=100)  # 100ms timeout
        exit_code, stdout, stderr, duration_ms = env.invoke_hook(hook_input)

        print(f"Exit Code: {exit_code}")
        print(f"Duration: {duration_ms:.2f}ms")

        passed = True
        if exit_code != -1:  # -1 indicates timeout
            print("✗ FAILED - Should have timed out")
            passed = False
        elif "TIMEOUT" not in stderr:
            print("✗ FAILED - No timeout message in stderr")
            passed = False
        elif duration_ms > 200:  # Should timeout around 100ms
            print("✗ FAILED - Timeout took too long")
            passed = False
        else:
            print("✓ PASSED - Correctly handled timeout")

        self.results.append(
            {"test": "Timeout Handling", "passed": passed, "duration_ms": duration_ms}
        )

        return passed

    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        print("\\nClaude Code Hook Integration Tests")
        print("=" * 60)

        # Test 1: Basic Write operation (with API key)
        self.run_test(
            "Write - With API Key",
            "Write",
            {"file_path": "test.py", "content": "def hello(): pass"},
            0,  # Should pass
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )

        # Test 2: Write operation without API key
        self.run_test(
            "Write - No API Key",
            "Write",
            {"file_path": "test.py", "content": "def hello(): pass"},
            2,  # Should fail without API key
            ["GEMINI_API_KEY not configured"],
            env_vars={},
        )

        # Test 3: Dangerous Bash command
        self.run_test(
            "Bash - Dangerous Command",
            "Bash",
            {"command": "rm -rf /"},
            2,  # Should block
            ["potentially destructive"],
            env_vars={},
        )

        # Test 4: Edit operation
        self.run_test(
            "Edit - Normal Operation",
            "Edit",
            {
                "file_path": "main.py",
                "old_string": "old code",
                "new_string": "new code",
            },
            2,  # Should fail without API key
            ["GEMINI_API_KEY not configured"],
            env_vars={},
        )

        # Test 5: MultiEdit operation
        self.run_test(
            "MultiEdit - Multiple Changes",
            "MultiEdit",
            {
                "file_path": "app.py",
                "edits": [
                    {"old_string": "v1", "new_string": "v2"},
                    {"old_string": "old", "new_string": "new"},
                ],
            },
            2,  # Should fail without API key
            ["GEMINI_API_KEY not configured"],
            env_vars={},
        )

        # Test 6: TodoWrite operation
        self.run_test(
            "TodoWrite - Always Allowed",
            "TodoWrite",
            {"todos": [{"id": "1", "task": "Test task", "status": "pending"}]},
            0,  # Always allowed - output is silent for TodoWrite
            env_vars={},
        )

        # Test 7: Write with secrets
        self.run_test(
            "Write - With Production Secrets",
            "Write",
            {
                "file_path": "config.py",
                "content": 'API_KEY = "sk_live_1234567890abcdefghijklmnop"',
            },
            2,  # Should block
            ["Security violation"],
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )

        # Test 8: Timeout handling
        self.run_timeout_test()

        # Print summary
        print(f"\\n{'=' * 60}")
        print("SUMMARY")
        print(f"{'=' * 60}")

        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        avg_duration = sum(r["duration_ms"] for r in self.results) / total

        print(f"Passed: {passed}/{total}")
        print(f"Average Duration: {avg_duration:.2f}ms")

        if passed < total:
            print("\\nFailed Tests:")
            for r in self.results:
                if not r["passed"]:
                    print(f"  - {r['test']}")

        return passed == total


class TestClaudeCodeIntegration:
    """Integration tests for Claude Code hook execution"""

    env: MockClaudeCodeEnvironment

    def setup_method(self) -> None:
        """Setup test environment"""
        self.env = MockClaudeCodeEnvironment()

    def test_write_with_api_key(self) -> None:
        """Test Write operation with API key - writing documentation should be allowed"""
        hook_input = self.env.create_hook_input(
            "Write",
            {
                "file_path": "README.md",
                "content": "# My Project\n\nThis is a simple project.",
            },
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )
        # Writing documentation should be allowed
        assert exit_code == 0
        assert duration_ms < 15000

    def test_write_test_file_with_api_key(self) -> None:
        """Test writing a test file with API key - should be allowed"""
        hook_input = self.env.create_hook_input(
            "Write",
            {
                "file_path": "test_hello.py",
                "content": "def test_hello():\n    assert True",
            },
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )
        # Writing a single test should be allowed
        assert exit_code == 0
        assert duration_ms < 15000

    def test_write_config_file(self) -> None:
        """Test Write operation with config file - should be allowed"""
        hook_input = self.env.create_hook_input(
            "Write",
            {"file_path": ".gitignore", "content": "*.pyc\n__pycache__/\n.venv/"},
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )
        assert exit_code == 0  # Writing config files should be allowed

    def test_dangerous_bash_command(self) -> None:
        """Test that dangerous Bash commands are blocked"""
        hook_input = self.env.create_hook_input("Bash", {"command": "rm -rf /"})
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input, env_vars={}
        )
        assert exit_code == 2  # Should be blocked
        # Parse JSON output to check for block message
        try:
            response = json.loads(stdout)
            hook_output = response["hookSpecificOutput"]
            assert hook_output["permissionDecision"] == "deny"
            assert (
                "dangerous" in hook_output["permissionDecisionReason"].lower()
                or "destructive" in hook_output["permissionDecisionReason"].lower()
            )
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

    def test_safe_bash_commands_allowed(self) -> None:
        """Test that safe Bash commands are allowed after the default deny bug fix"""
        safe_commands = [
            "ls -la",
            "pwd",
            "echo 'Hello World'",
            "npm test",
            "git status",
            "node -v",
            "cat README.md",
            "cd src",
            "mkdir test_dir",
        ]

        for command in safe_commands:
            hook_input = self.env.create_hook_input("Bash", {"command": command})
            exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
                hook_input,
                env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
            )
            # Should be allowed with exit code 0
            if exit_code != 0:
                print(f"\nCommand '{command}' failed with exit code {exit_code}")
                print(f"Stdout: {stdout}")
                print(f"Stderr: {stderr}")
            assert (
                exit_code == 0
            ), f"Command '{command}' was blocked but should be allowed"

            # Parse JSON output to verify approval
            try:
                response = json.loads(stdout)
                hook_output = response["hookSpecificOutput"]
                assert (
                    hook_output["permissionDecision"] == "allow"
                ), f"Command '{command}' denied"
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON output for command '{command}': {stdout}")

    def test_tool_enforcement_patterns(self) -> None:
        """Test that tool enforcement patterns work correctly"""
        blocked_commands = [
            ("python --version", "uv run python"),
            ("python3 script.py", "uv run python"),
            ("grep 'pattern' file.txt", "rg"),
            ("find . -name '*.py'", "rg --files"),
        ]

        for command, suggested_tool in blocked_commands:
            hook_input = self.env.create_hook_input("Bash", {"command": command})
            exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
                hook_input,
                env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
            )
            # Should be blocked with exit code 2
            assert (
                exit_code == 2
            ), f"Command '{command}' should be blocked by tool enforcement"

            # Parse JSON output to verify block reason mentions the suggested tool
            try:
                response = json.loads(stdout)
                hook_output = response["hookSpecificOutput"]
                assert hook_output["permissionDecision"] == "deny"
                assert suggested_tool in hook_output["permissionDecisionReason"]
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON output for command '{command}': {stdout}")

    def test_edit_operation(self) -> None:
        """Test Edit operation with API key on config file"""
        hook_input = self.env.create_hook_input(
            "Edit",
            {
                "file_path": ".gitignore",
                "old_string": "*.pyc",
                "new_string": "*.pyc\n*.pyo",
            },
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )
        assert exit_code == 0  # Should pass with API key for config file edit

    def test_multiedit_operation(self) -> None:
        """Test MultiEdit operation with API key on config file"""
        hook_input = self.env.create_hook_input(
            "MultiEdit",
            {
                "file_path": "package.json",
                "edits": [
                    {
                        "old_string": '"version": "1.0.0"',
                        "new_string": '"version": "1.0.1"',
                    },
                    {
                        "old_string": '"main": "index.js"',
                        "new_string": '"main": "src/index.js"',
                    },
                ],
            },
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )
        assert exit_code == 0  # Should pass with API key for config file edits

    def test_todowrite_operation(self) -> None:
        """Test TodoWrite operation with API key"""
        hook_input = self.env.create_hook_input(
            "TodoWrite",
            {"todos": [{"id": "1", "task": "Test task", "status": "pending"}]},
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )
        assert exit_code == 0  # Should pass with API key

    def test_write_with_production_secrets(self) -> None:
        """Test that production secrets are blocked"""
        hook_input = self.env.create_hook_input(
            "Write",
            {
                "file_path": "config.py",
                "content": 'API_KEY = "sk_live_1234567890abcdefghijklmnop"',
            },
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )
        assert exit_code == 2  # Should be blocked
        # Parse JSON output to check for security block message
        try:
            response = json.loads(stdout)
            hook_output = response["hookSpecificOutput"]
            assert hook_output["permissionDecision"] == "deny"
            assert (
                "security" in hook_output["permissionDecisionReason"].lower()
                or "secret" in hook_output["permissionDecisionReason"].lower()
            )
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

    def test_timeout_handling(self) -> None:
        """Test that timeouts are handled correctly"""
        # Create a hook input that will cause a long-running operation
        hook_input = self.env.create_hook_input(
            "Write",
            {
                "file_path": "test.py",
                "content": "x" * 1000000,  # Very large content
            },
        )

        # Use a very short timeout
        env = MockClaudeCodeEnvironment(timeout_ms=100)
        exit_code, stdout, stderr, duration_ms = env.invoke_hook(
            hook_input, env_vars={}
        )

        assert exit_code == -1  # Timeout exit code
        assert "TIMEOUT" in stderr
        assert duration_ms < 200  # Should timeout around 100ms

    def test_json_output_allowed_operation(self) -> None:
        """Test JSON output format for allowed operations"""
        hook_input = self.env.create_hook_input(
            "Write", {"file_path": "demo.txt", "content": "Hello, world!"}
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )

        # Parse JSON output
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

        # Verify JSON structure
        assert "hookSpecificOutput" in response
        hook_output = response["hookSpecificOutput"]
        assert "hookEventName" in hook_output
        assert hook_output["hookEventName"] == "PreToolUse"
        assert "permissionDecision" in hook_output
        assert "permissionDecisionReason" in hook_output
        assert hook_output["permissionDecision"] == "allow"
        assert hook_output["permissionDecisionReason"] == "Operation approved"

        # Verify clean output
        assert stderr == ""
        assert exit_code == 0

    def test_json_output_blocked_operation(self) -> None:
        """Test JSON output format for blocked operations"""
        hook_input = self.env.create_hook_input("Bash", {"command": "rm -rf /"})
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )

        # Exit code should be 2, but output should be in stdout, not stderr
        assert exit_code == 2

        # Parse JSON output from stdout
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

        # Verify JSON structure
        assert "hookSpecificOutput" in response
        hook_output = response["hookSpecificOutput"]
        assert "hookEventName" in hook_output
        assert hook_output["hookEventName"] == "PreToolUse"
        assert "permissionDecision" in hook_output
        assert "permissionDecisionReason" in hook_output
        assert hook_output["permissionDecision"] == "deny"
        assert "❌" in hook_output["permissionDecisionReason"]
        # Note: suggestions (→) may or may not be present depending on the specific block reason

        # Verify stderr is empty (all output should be in stdout as JSON)
        assert stderr == ""

    def test_json_output_dangerous_command(self) -> None:
        """Test JSON output for dangerous command with proper formatting"""
        hook_input = self.env.create_hook_input(
            "Bash", {"command": "sudo rm -rf --no-preserve-root /"}
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )

        # Should block with exit code 2
        assert exit_code == 2

        # Parse JSON output
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

        # Verify JSON structure
        hook_output = response["hookSpecificOutput"]
        assert hook_output["permissionDecision"] == "deny"
        assert "❌" in hook_output["permissionDecisionReason"]
        assert (
            "dangerous" in hook_output["permissionDecisionReason"].lower()
            or "destructive" in hook_output["permissionDecisionReason"].lower()
        )

        # Verify clean output
        assert stderr == ""

    # CI mode test removed - CI mode no longer exists

    def test_json_output_invalid_json_input(self) -> None:
        """Test JSON output when input is invalid JSON"""
        # Directly test with invalid JSON input
        env = os.environ.copy()
        env.update({"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")})

        process = subprocess.Popen(
            ["uv", "run", "python", "-m", "cc_validator"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        # Send invalid JSON
        stdout, stderr = process.communicate(input="{ invalid json }")
        exit_code = process.returncode

        # Should allow with exit code 0 (fail-safe)
        assert exit_code == 0

        # Parse JSON output
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

        # Verify JSON structure
        hook_output = response["hookSpecificOutput"]
        assert hook_output["permissionDecision"] == "allow"
        assert "Invalid JSON input" in hook_output["permissionDecisionReason"]
        assert (
            "allowing operation to proceed" in hook_output["permissionDecisionReason"]
        )

        # Verify clean output
        assert stderr == ""

    def test_json_output_complex_block_reason(self) -> None:
        """Test JSON output with complex multi-line block reasons"""
        hook_input = self.env.create_hook_input(
            "Write",
            {
                "file_path": "config.py",
                "content": 'API_KEY = "sk_live_1234567890abcdefghijklmnop"\nSECRET = "prod_secret_key"',
            },
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )

        # Should block
        assert exit_code == 2

        # Parse JSON output
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

        # Verify JSON structure
        hook_output = response["hookSpecificOutput"]
        assert hook_output["permissionDecision"] == "deny"
        reason = hook_output["permissionDecisionReason"]

        # Should have structured format with emoji, suggestions, and details
        assert "❌" in reason
        assert "→" in reason  # Suggestions
        assert "\n" in reason  # Multi-line

        # Verify clean output
        assert stderr == ""

    def test_json_output_no_extraneous_output(self) -> None:
        """Test that only valid JSON is output to stdout"""
        hook_input = self.env.create_hook_input(
            "Edit",
            {
                "file_path": "main.py",
                "old_string": "old code",
                "new_string": "new code",
            },
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )

        # Should only have one JSON object in stdout
        lines = stdout.strip().split("\n")
        assert len(lines) == 1

        # Should be valid JSON
        try:
            response = json.loads(lines[0])
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

        # Verify it's the expected format
        assert "hookSpecificOutput" in response
        hook_output = response["hookSpecificOutput"]
        assert "hookEventName" in hook_output
        assert hook_output["hookEventName"] == "PreToolUse"
        assert "permissionDecision" in hook_output
        assert "permissionDecisionReason" in hook_output

        # No stderr output
        assert stderr == ""

    def test_json_output_todowrite_silent_approval(self) -> None:
        """Test that TodoWrite operations have clean JSON output"""
        hook_input = self.env.create_hook_input(
            "TodoWrite",
            {"todos": [{"id": "1", "task": "Test task", "status": "pending"}]},
        )
        exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
            hook_input,
            env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
        )

        # Should allow
        assert exit_code == 0

        # Parse JSON output
        try:
            response = json.loads(stdout)
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {stdout}")

        # TodoWrite should have minimal approval message
        hook_output = response["hookSpecificOutput"]
        assert hook_output["permissionDecision"] == "allow"
        assert hook_output["permissionDecisionReason"] == "Operation approved"

        # Verify clean output
        assert stderr == ""

    def test_json_output_exception_handling(self) -> None:
        """Test JSON output when an exception occurs during validation"""
        # Create a hook input with missing required fields to trigger validation errors
        # Missing tool_name should cause an issue
        hook_input = {
            "session_id": "test-session-123",
            "transcript_path": "/tmp/test.jsonl",
            "hook_event_name": "PreToolUse",
            # Missing tool_name field
            "tool_input": {"file_path": "test.py", "content": "def hello(): pass"},
        }

        # Create the transcript file so that's not the issue
        with open("/tmp/test.jsonl", "w") as f:
            f.write('{"role": "user", "content": "Test"}\n')

        try:
            exit_code, stdout, stderr, duration_ms = self.env.invoke_hook(
                hook_input,
                env_vars={"GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY", "")},
            )

            # Should block with exit code 2 (fail-closed for missing tool_name)
            assert exit_code == 2

            # Parse JSON output
            try:
                response = json.loads(stdout)
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON output: {stdout}")

            # When tool_name is missing, it defaults to empty string and blocks
            hook_output = response["hookSpecificOutput"]
            assert hook_output["permissionDecision"] == "deny"
            assert "Unhandled tool ''" in hook_output["permissionDecisionReason"]

            # Verify clean output (no stderr)
            assert stderr == ""

        finally:
            # Clean up
            try:
                os.unlink("/tmp/test.jsonl")
            except OSError:
                pass

    def teardown_method(self, method: Any) -> None:
        """Clean up after each test"""
        # Clean up any temporary transcript files
        import glob

        for f in glob.glob("/tmp/*.jsonl"):
            try:
                os.unlink(f)
            except OSError:
                pass


def main() -> None:
    """Run integration tests standalone"""
    suite = IntegrationTestSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    # Support both pytest and standalone execution
    if len(sys.argv) > 1 and sys.argv[1] == "--standalone":
        main()
    else:
        pytest.main([__file__, "-v"])
