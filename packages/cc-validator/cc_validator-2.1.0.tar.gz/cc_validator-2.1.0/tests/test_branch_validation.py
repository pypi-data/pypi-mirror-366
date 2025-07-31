#!/usr/bin/env python3

import asyncio
import unittest
from typing import Any
from unittest.mock import patch, MagicMock
import subprocess
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cc_validator.security_validator import SecurityValidator


class TestBranchValidation(unittest.TestCase):
    """Test branch validation functionality in SecurityValidator"""

    def setUp(self) -> None:
        self.validator = SecurityValidator()

    @patch.dict(os.environ, {"CLAUDE_TEST_BRANCH": ""}, clear=False)
    @patch("subprocess.run")
    def test_get_current_branch_success(self, mock_run: Any) -> None:
        """Test successful branch detection"""
        mock_run.return_value = MagicMock(stdout="feature/test-branch\n", returncode=0)

        branch = self.validator._get_current_branch()

        self.assertEqual(branch, "feature/test-branch")
        mock_run.assert_called_once_with(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=os.getcwd(),
        )

    @patch.dict(os.environ, {"CLAUDE_TEST_BRANCH": ""}, clear=False)
    @patch("subprocess.run")
    def test_get_current_branch_not_git_repo(self, mock_run: Any) -> None:
        """Test branch detection when not in a git repo"""
        mock_run.side_effect = subprocess.CalledProcessError(128, "git")

        branch = self.validator._get_current_branch()

        self.assertIsNone(branch)

    @patch.dict(os.environ, {"CLAUDE_TEST_BRANCH": ""}, clear=False)
    @patch("subprocess.run")
    def test_get_current_branch_detached_head(self, mock_run: Any) -> None:
        """Test branch detection in detached HEAD state"""
        mock_run.return_value = MagicMock(stdout="HEAD\n", returncode=0)

        branch = self.validator._get_current_branch()

        self.assertIsNone(branch)

    @patch.object(SecurityValidator, "_get_current_branch")
    def test_is_protected_branch_main(self, mock_get_branch: Any) -> None:
        """Test protected branch detection for main branch"""
        mock_get_branch.return_value = "main"

        is_protected = self.validator._is_protected_branch()

        self.assertTrue(is_protected)

    @patch.object(SecurityValidator, "_get_current_branch")
    def test_is_protected_branch_feature(self, mock_get_branch: Any) -> None:
        """Test protected branch detection for feature branch"""
        mock_get_branch.return_value = "feature/my-feature"

        is_protected = self.validator._is_protected_branch()

        self.assertFalse(is_protected)

    def test_is_allowed_file_on_main_readme(self) -> None:
        """Test allowed files on main - README.md"""
        self.assertTrue(self.validator._is_allowed_file_on_main("README.md"))
        self.assertTrue(self.validator._is_allowed_file_on_main("project/README.md"))

    def test_is_allowed_file_on_main_docs(self) -> None:
        """Test allowed files on main - docs directory"""
        self.assertTrue(self.validator._is_allowed_file_on_main("docs/guide.md"))
        self.assertTrue(
            self.validator._is_allowed_file_on_main("docs/api/reference.md")
        )

    def test_is_allowed_file_on_main_code(self) -> None:
        """Test disallowed files on main - code files"""
        self.assertFalse(self.validator._is_allowed_file_on_main("src/main.py"))
        self.assertFalse(
            self.validator._is_allowed_file_on_main("tests/test_example.py")
        )

    def test_extract_issue_number_valid(self) -> None:
        """Test extracting issue number from valid branch name"""
        issue_num = self.validator._extract_issue_number("123-fix-bug")
        self.assertEqual(issue_num, "123")

        issue_num = self.validator._extract_issue_number("42-add-feature-xyz")
        self.assertEqual(issue_num, "42")

    def test_extract_issue_number_invalid(self) -> None:
        """Test extracting issue number from invalid branch name"""
        issue_num = self.validator._extract_issue_number("feature/my-feature")
        self.assertIsNone(issue_num)

        issue_num = self.validator._extract_issue_number("main")
        self.assertIsNone(issue_num)

    @patch("subprocess.run")
    def test_validate_issue_exists_success(self, mock_run: Any) -> None:
        """Test validating issue exists successfully"""
        mock_run.return_value = MagicMock(returncode=0)

        exists = self.validator._validate_issue_exists("42")

        self.assertTrue(exists)
        mock_run.assert_called_once_with(
            ["gh", "issue", "view", "42"],
            capture_output=True,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )

    @patch("subprocess.run")
    def test_validate_issue_exists_not_found(self, mock_run: Any) -> None:
        """Test validating issue that doesn't exist"""
        mock_run.return_value = MagicMock(returncode=1)

        exists = self.validator._validate_issue_exists("999")

        self.assertFalse(exists)

    @patch("subprocess.run")
    def test_validate_issue_exists_gh_not_installed(self, mock_run: Any) -> None:
        """Test validating issue when gh CLI not installed"""
        mock_run.side_effect = FileNotFoundError()

        exists = self.validator._validate_issue_exists("42")

        self.assertTrue(exists)  # Assumes issue exists when can't check

    @patch.object(SecurityValidator, "_extract_issue_number")
    @patch.object(SecurityValidator, "_validate_issue_exists")
    def test_get_issue_workflow_suggestions_with_invalid_issue(
        self, mock_validate: Any, mock_extract: Any
    ) -> None:
        """Test suggestions when issue doesn't exist"""
        mock_extract.return_value = "999"
        mock_validate.return_value = False

        suggestions = self.validator._get_issue_workflow_suggestions("999-feature")

        self.assertIn("Issue #999 not found", suggestions[0])
        self.assertIn("gh issue list", suggestions[1])

    @patch.object(SecurityValidator, "_is_protected_branch")
    @patch.object(SecurityValidator, "_get_current_branch")
    def test_check_branch_validation_on_main_with_code(
        self, mock_get_branch: Any, mock_is_protected: Any
    ) -> None:
        """Test branch validation blocks code changes on main"""
        mock_get_branch.return_value = "main"
        mock_is_protected.return_value = True

        result = self.validator._check_branch_validation("src/main.py")

        self.assertIsNotNone(result)
        assert result is not None  # Type narrowing for mypy
        self.assertFalse(result["approved"])
        self.assertIn("protected branch", result["reason"])
        self.assertIsInstance(result["suggestions"], list)

    @patch.object(SecurityValidator, "_is_protected_branch")
    def test_check_branch_validation_on_main_with_docs(
        self, mock_is_protected: Any
    ) -> None:
        """Test branch validation allows docs on main"""
        mock_is_protected.return_value = True

        result = self.validator._check_branch_validation("README.md")

        self.assertIsNone(result)

    @patch.object(SecurityValidator, "_is_protected_branch")
    def test_check_branch_validation_on_feature_branch(
        self, mock_is_protected: Any
    ) -> None:
        """Test branch validation allows everything on feature branches"""
        mock_is_protected.return_value = False

        result = self.validator._check_branch_validation("src/main.py")

        self.assertIsNone(result)

    @patch.object(SecurityValidator, "_check_branch_validation")
    def test_validate_file_operation_with_branch_block(
        self, mock_check_branch: Any
    ) -> None:
        """Test file operation validation blocked by branch check"""
        mock_check_branch.return_value = {
            "approved": False,
            "reason": "Protected branch",
            "suggestions": ["Use feature branch"],
        }

        result = asyncio.run(
            self.validator.validate_file_operation(
                {
                    "file_path": "src/main.py",
                    "content": "print('hello')",
                }
            )
        )

        self.assertFalse(result["approved"])
        self.assertEqual(result["reason"], "Protected branch")

    @patch("cc_validator.security_validator.ENFORCE_ISSUE_WORKFLOW", False)
    def test_branch_validation_disabled(self) -> None:
        """Test branch validation when disabled in config"""
        result = self.validator._check_branch_validation("src/main.py")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
