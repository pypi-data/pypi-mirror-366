"""Tests for utility functions in the cacts.utils module."""

import tempfile

import pytest

from cacts.utils import (
    expect, run_cmd, run_cmd_no_fail,
    str_to_bool, is_git_repo
)
# from cacts.utils import evaluate_py_expressions  # Import issue with pylint


class MockObject:
    """Mock object class for testing"""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.name = "MockObject"
        self.value = "${project.name}_value"


def test_expect():
    """Test the expect function"""
    # Should not raise when condition is True
    expect(True, "This should not raise")

    # Should raise RuntimeError when condition is False
    with pytest.raises(RuntimeError, match="ERROR: This should raise"):
        expect(False, "This should raise")

    # Test custom exception type
    with pytest.raises(ValueError, match="ERROR: Custom exception"):
        expect(False, "Custom exception", exc_type=ValueError)


def test_run_cmd():
    """Test the run_cmd function"""
    stat, output, errput = run_cmd("echo Hello, World!")
    assert stat == 0
    assert output == "Hello, World!"
    assert errput == ""

    # Test command that fails
    stat, output, errput = run_cmd("exit 1")
    assert stat == 1


def test_run_cmd_no_fail():
    """Test the run_cmd_no_fail function"""
    output = run_cmd_no_fail("echo Hello, World!")
    assert output == "Hello, World!"

    # Test command that fails should raise exception
    with pytest.raises(RuntimeError):
        run_cmd_no_fail("exit 1")


def test_str_to_bool():
    """Test the str_to_bool function"""
    assert str_to_bool("True", "test_var") is True
    assert str_to_bool("False", "test_var") is False

    with pytest.raises(ValueError,
                       match="Invalid value 'Invalid' for 'test_var'"):
        str_to_bool("Invalid", "test_var")


def test_is_git_repo():
    """Test the is_git_repo function"""
    # Should return True since we're in a git repo
    assert is_git_repo() is True

    # Test with a path that's not a git repo
    with tempfile.TemporaryDirectory() as temp_dir:
        assert is_git_repo(temp_dir) is False
