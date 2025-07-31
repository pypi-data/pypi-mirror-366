#!/usr/bin/env python3
"""
Demo tests for the new hybrid factory pattern in run_validation_factory.

These tests demonstrate both convenience mode and raw mode usage.
"""

import json
from typing import Any

import pytest


class TestHybridFactoryDemo:
    """Demo tests for hybrid factory pattern."""

    @pytest.mark.quick
    def test_convenience_mode_usage(self, run_validation_factory: Any) -> None:
        """Demo: Using convenience mode (existing behavior)."""
        tool_data = {
            "tool": "Write",
            "input": {"file_path": "demo.txt", "content": "Hello, world!"},
            "conversation_context": "",
        }

        # This is the existing convenience mode
        returncode, stdout, stderr = run_validation_factory(tool_data)
        # With API key present, simple writes should be allowed
        assert returncode == 0, f"Expected success with API key, stderr: {stderr}"

    @pytest.mark.quick
    def test_raw_mode_usage(self, run_validation_factory: Any) -> None:
        """Demo: Using raw mode for direct control."""
        # Prepare the same data but use raw mode for direct subprocess control
        formatted_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "demo.txt", "content": "Hello, world!"},
            "transcript_path": "",
        }

        # This is the new raw mode
        returncode, stdout, stderr = run_validation_factory(
            args=[
                "uv",
                "run",
                "python",
                "-m",
                "cc_validator.test_entry",
                json.dumps(formatted_data),
            ],
            env={},  # Custom environment
        )
        # With API key present, simple writes should be allowed
        assert (
            returncode == 0
        ), f"Expected success with API key in raw mode, stderr: {stderr}"

    @pytest.mark.quick
    def test_error_handling_mixed_modes(self, run_validation_factory: Any) -> None:
        """Demo: Error handling when mixing convenience and raw modes."""
        with pytest.raises(
            ValueError, match="Cannot specify both 'tool_data'.*and 'args'"
        ):
            run_validation_factory(
                {"tool": "Write", "input": {}},  # convenience mode
                args=["echo", "test"],  # raw mode - should raise error
            )

    @pytest.mark.quick
    def test_error_handling_no_arguments(self, run_validation_factory: Any) -> None:
        """Demo: Error handling when no arguments provided."""
        with pytest.raises(
            ValueError, match="Must specify either 'tool_data'.*or 'args'"
        ):
            run_validation_factory()  # No arguments - should raise error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
