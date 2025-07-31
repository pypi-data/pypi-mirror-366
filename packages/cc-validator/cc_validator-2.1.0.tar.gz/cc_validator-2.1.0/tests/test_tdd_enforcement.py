#!/usr/bin/env python3
"""
Comprehensive TDD enforcement tests for all file operations.

This test suite verifies that the TDD validation system properly enforces
the Red-Green-Refactor cycle by blocking implementation code written without
corresponding failing tests.

Run with: uv run python tests/test_tdd_enforcement.py
"""

import json
import subprocess
import sys
import os
import tempfile
import threading
import concurrent.futures
import time
from typing import Dict, Any, Tuple, Callable


def run_validation(
    tool_data: Dict[str, Any], timeout: int = 60
) -> Tuple[int, str, str]:
    """Run validation and return exit code, stdout, and stderr"""
    try:
        process = subprocess.run(
            ["uv", "run", "python", "-m", "cc_validator"],
            input=json.dumps(tool_data),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return process.returncode, process.stdout, process.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "TIMEOUT: Validation took too long"


def create_test_transcript() -> str:
    """Create a minimal test transcript file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        f.write('{"role": "user", "content": "Create implementation"}\n')
        return f.name


class TDDEnforcementTests:
    """Test suite for TDD enforcement across all file operations"""

    def __init__(self) -> None:
        self.transcript_path = create_test_transcript()
        self.passed = 0
        self.total = 0
        self.lock = threading.Lock()  # Thread safety for counters

    def cleanup(self) -> None:
        """Clean up test files"""
        try:
            os.unlink(self.transcript_path)
        except OSError:
            pass

    def assert_blocked(
        self,
        test_name: str,
        tool_data: Dict[str, Any],
        expected_reason_fragment: str = "",
    ) -> bool:
        """Assert that the tool operation is blocked (exit code 2)"""
        with self.lock:
            self.total += 1
        code, stdout, stderr = run_validation(tool_data)

        print(f"\n{'=' * 60}")
        print(f"TEST: {test_name}")
        print(f"Tool: {tool_data['tool_name']}")
        print(f"File: {tool_data['tool_input'].get('file_path', 'N/A')}")
        print(f"Exit Code: {code}")

        if code == 2:
            print("✓ PASSED - Correctly blocked")
            if (
                expected_reason_fragment
                and expected_reason_fragment.lower() not in stderr.lower()
            ):
                print(
                    f"⚠️  WARNING: Expected '{expected_reason_fragment}' in error message"
                )
                print(f"   Actual stderr: {stderr[:200]}...")
            with self.lock:
                self.passed += 1
            return True
        else:
            print("✗ FAILED - Should have been blocked")
            print(f"   Stdout: {stdout[:100]}...")
            print(f"   Stderr: {stderr[:100]}...")
            return False

    def assert_allowed(self, test_name: str, tool_data: Dict[str, Any]) -> bool:
        """Assert that the tool operation is allowed (exit code 0)"""
        with self.lock:
            self.total += 1
        code, stdout, stderr = run_validation(tool_data)

        print(f"\n{'=' * 60}")
        print(f"TEST: {test_name}")
        print(f"Tool: {tool_data['tool_name']}")
        print(f"File: {tool_data['tool_input'].get('file_path', 'N/A')}")
        print(f"Exit Code: {code}")

        if code == 0:
            print("✓ PASSED - Correctly allowed")
            with self.lock:
                self.passed += 1
            return True
        else:
            print("✗ FAILED - Should have been allowed")
            print(f"   Stderr: {stderr[:200]}...")
            return False

    def test_write_implementation_without_test(self) -> bool:
        """Write tool should block implementation without test"""
        return self.assert_blocked(
            "Write implementation without test",
            {
                "tool_name": "Write",
                "tool_input": {
                    "file_path": "calculator.py",
                    "content": "def add(a, b):\n    return a + b\n",
                },
                "transcript_path": self.transcript_path,
            },
            "TDD",
        )

    def test_write_test_file(self) -> bool:
        """Write tool should allow test files"""
        return self.assert_allowed(
            "Write test file",
            {
                "tool_name": "Write",
                "tool_input": {
                    "file_path": "test_calculator.py",
                    "content": "def test_add():\n    assert add(1, 2) == 3\n",
                },
                "transcript_path": self.transcript_path,
            },
        )

    def test_update_implementation_without_test(self) -> bool:
        """Update tool should block implementation without test"""
        return self.assert_blocked(
            "Update implementation without test",
            {
                "tool_name": "Update",
                "tool_input": {
                    "file_path": "calculator.py",
                    "content": "def multiply(a, b):\n    return a * b\n",
                },
                "transcript_path": self.transcript_path,
            },
            "TDD",
        )

    def test_update_test_file(self) -> bool:
        """Update tool should allow test files"""
        return self.assert_allowed(
            "Update test file",
            {
                "tool_name": "Update",
                "tool_input": {
                    "file_path": "test_calculator.py",
                    "content": "def test_multiply():\n    assert multiply(2, 3) == 6\n",
                },
                "transcript_path": self.transcript_path,
            },
        )

    def test_update_add_one_test_to_existing(self) -> bool:
        """Update adding one new test to existing file should be allowed (Issue #35)"""
        # Create a temporary test file with one existing test
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_test.py", delete=False
        ) as f:
            f.write("def test_existing():\n    assert True\n")
            test_file = f.name

        try:
            return self.assert_allowed(
                "Update adding one test to existing",
                {
                    "tool_name": "Update",
                    "tool_input": {
                        "file_path": test_file,
                        "content": "def test_existing():\n    assert True\n\ndef test_new():\n    assert True\n",
                    },
                    "transcript_path": self.transcript_path,
                },
            )
        finally:
            os.unlink(test_file)

    def test_update_add_multiple_tests_to_existing(self) -> bool:
        """Update adding multiple new tests to existing file should be blocked (Issue #35)"""
        # Create a temporary test file with one existing test
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_test.py", delete=False
        ) as f:
            f.write("def test_existing():\n    assert True\n")
            test_file = f.name

        try:
            return self.assert_blocked(
                "Update adding multiple tests to existing",
                {
                    "tool_name": "Update",
                    "tool_input": {
                        "file_path": test_file,
                        "content": "def test_existing():\n    assert True\n\ndef test_new_one():\n    assert True\n\ndef test_new_two():\n    assert True\n",
                    },
                    "transcript_path": self.transcript_path,
                },
                "multiple",
            )
        finally:
            os.unlink(test_file)

    def test_edit_adds_multiple_tests(self) -> bool:
        """Edit tool should block adding multiple tests"""
        return self.assert_blocked(
            "Edit adding multiple tests",
            {
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "test_calculator.py",
                    "old_string": "def test_add():\n    assert True",
                    "new_string": "def test_add():\n    assert True\n\ndef test_subtract():\n    assert True\n\ndef test_multiply():\n    assert True",
                },
                "transcript_path": self.transcript_path,
            },
            "multiple",
        )

    def test_edit_single_test(self) -> bool:
        """Edit tool should allow adding single test"""
        return self.assert_allowed(
            "Edit adding single test",
            {
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "test_calculator.py",
                    "old_string": "# Empty test file",
                    "new_string": "def test_add():\n    assert True",
                },
                "transcript_path": self.transcript_path,
            },
        )

    def test_multiedit_multiple_tests(self) -> bool:
        """MultiEdit should block if total new tests > 1"""
        return self.assert_blocked(
            "MultiEdit with multiple tests",
            {
                "tool_name": "MultiEdit",
                "tool_input": {
                    "file_path": "test_calculator.py",
                    "edits": [
                        {
                            "old_string": "# tests here",
                            "new_string": "def test_add():\n    assert True",
                        },
                        {
                            "old_string": "# more tests",
                            "new_string": "def test_subtract():\n    assert True",
                        },
                    ],
                },
                "transcript_path": self.transcript_path,
            },
            "multiple",
        )

    def test_multiedit_single_test(self) -> bool:
        """MultiEdit should allow single test across edits"""
        return self.assert_allowed(
            "MultiEdit with single test",
            {
                "tool_name": "MultiEdit",
                "tool_input": {
                    "file_path": "test_calculator.py",
                    "edits": [
                        {"old_string": "# setup", "new_string": "import calculator"},
                        {
                            "old_string": "# test",
                            "new_string": "def test_add():\n    assert True",
                        },
                    ],
                },
                "transcript_path": self.transcript_path,
            },
        )

    def test_write_with_comments(self) -> bool:
        """Write should block code with comments"""
        return self.assert_blocked(
            "Write with comments",
            {
                "tool_name": "Write",
                "tool_input": {
                    "file_path": "example.py",
                    "content": "# This is a comment\ndef hello():\n    return 'world'  # inline comment\n",
                },
                "transcript_path": self.transcript_path,
            },
            "comment",
        )

    def test_write_no_comments(self) -> bool:
        """Write should allow code without comments"""
        return self.assert_allowed(
            "Write without comments",
            {
                "tool_name": "Write",
                "tool_input": {
                    "file_path": "test_example.py",
                    "content": "def test_hello():\n    assert hello() == 'world'\n",
                },
                "transcript_path": self.transcript_path,
            },
        )

    def test_structural_files(self) -> bool:
        """Structural files should be allowed without TDD"""
        test_cases = [
            ("__init__.py", ""),
            ("__init__.py", "from .module import function"),
            ("setup.py", "from setuptools import setup\n\nsetup(name='test')"),
            ("config.toml", "[tool.test]\nkey = 'value'"),
        ]

        results = []
        for filename, content in test_cases:
            result = self.assert_allowed(
                f"Structural file: {filename}",
                {
                    "tool_name": "Write",
                    "tool_input": {"file_path": filename, "content": content},
                    "transcript_path": self.transcript_path,
                },
            )
            results.append(result)

        return all(results)

    def test_update_modify_existing_test(self) -> bool:
        """Update modifying existing test implementation should be allowed"""
        # Create a temporary test file with one test
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_test.py", delete=False
        ) as f:
            f.write(
                "def test_oauth_redirect():\n    response = client.get('/auth/login')\n    assert response.status_code == 302\n"
            )
            test_file = f.name

        try:
            return self.assert_allowed(
                "Update modifying existing test",
                {
                    "tool_name": "Update",
                    "tool_input": {
                        "file_path": test_file,
                        "content": "def test_oauth_redirect():\n    response = client.get('/auth/login')\n    assert response.status_code != 404\n",
                    },
                    "transcript_path": self.transcript_path,
                },
            )
        finally:
            os.unlink(test_file)

    def test_update_rename_test_function(self) -> bool:
        """Update renaming test function should be allowed (net zero change)"""
        # Create a temporary test file with one test
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_test.py", delete=False
        ) as f:
            f.write("def test_login():\n    assert True\n")
            test_file = f.name

        try:
            return self.assert_allowed(
                "Update renaming test function",
                {
                    "tool_name": "Update",
                    "tool_input": {
                        "file_path": test_file,
                        "content": "def test_login_redirects_to_google():\n    assert True\n",
                    },
                    "transcript_path": self.transcript_path,
                },
            )
        finally:
            os.unlink(test_file)

    def test_update_replace_test_with_different_one(self) -> bool:
        """Update replacing one test with another should be allowed (net zero)"""
        # Create a temporary test file with one complex test
        with tempfile.NamedTemporaryFile(
            mode="w", suffix="_test.py", delete=False
        ) as f:
            f.write(
                """def test_google_oauth_login_redirects_to_google():
    with patch('auth.get_google_sso') as mock_sso:
        mock_sso.get_login_url.return_value = "https://google.com"
        response = client.get("/auth/login")
        assert response.status_code == 307
"""
            )
            test_file = f.name

        try:
            return self.assert_allowed(
                "Update replacing test with simpler one",
                {
                    "tool_name": "Update",
                    "tool_input": {
                        "file_path": test_file,
                        "content": "def test_google_oauth_login_endpoint_exists():\n    response = client.get('/auth/login')\n    assert response.status_code != 404\n",
                    },
                    "transcript_path": self.transcript_path,
                },
            )
        finally:
            os.unlink(test_file)

    def run_all_tests(self) -> int:
        """Run all TDD enforcement tests in parallel"""
        print("TDD ENFORCEMENT TEST SUITE")
        print("=" * 80)
        print("Verifying Red-Green-Refactor cycle enforcement")
        print("Tests require GEMINI_API_KEY for LLM-based validation")
        print("PARALLEL EXECUTION: Running 16 tests concurrently")
        print("=" * 80)

        start_time = time.time()

        # Core TDD enforcement tests
        tests = [
            self.test_write_implementation_without_test,
            self.test_write_test_file,
            self.test_update_implementation_without_test,
            self.test_update_test_file,
            self.test_update_add_one_test_to_existing,
            self.test_update_add_multiple_tests_to_existing,
            self.test_update_modify_existing_test,
            self.test_update_rename_test_function,
            self.test_update_replace_test_with_different_one,
            self.test_edit_adds_multiple_tests,
            self.test_edit_single_test,
            self.test_multiedit_multiple_tests,
            self.test_multiedit_single_test,
            self.test_write_with_comments,
            self.test_write_no_comments,
            self.test_structural_files,
        ]

        print("Starting parallel test execution...")

        # Run tests in parallel
        def run_single_test(test_func: Callable[[], bool]) -> bool:
            try:
                return test_func()
            except Exception as e:
                print(f"\n✗ TEST ERROR: {test_func.__name__}")
                print(f"   Exception: {e}")
                with self.lock:
                    self.total += 1
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=13) as executor:
            list(executor.map(run_single_test, tests))

        elapsed_time = time.time() - start_time

        print(f"\n{'=' * 80}")
        print(f"FINAL RESULTS: {self.passed}/{self.total} tests passed")
        print(f"Total execution time: {elapsed_time:.1f} seconds")

        if self.passed == self.total:
            print("🎉 ALL TESTS PASSED - TDD enforcement is working correctly!")
            return 0
        else:
            print("❌ SOME TESTS FAILED - TDD enforcement has issues!")
            failure_rate = (self.total - self.passed) / self.total * 100
            print(f"   Failure rate: {failure_rate:.1f}%")
            return 1


def main() -> int:
    """Main test runner"""
    # Check requirements
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY required for TDD validation tests")
        print("Set the environment variable and try again.")
        return 1

    # Run tests
    test_suite = TDDEnforcementTests()
    try:
        result = test_suite.run_all_tests()
        return result
    finally:
        test_suite.cleanup()


if __name__ == "__main__":
    sys.exit(main())
