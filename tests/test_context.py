import os
from unittest.mock import mock_open, patch

from goose_checker.context import get_terraform_context
from goose_checker.diff import GitDiff
from tests.conftest import temporary_change_dir


def test_get_terraform_context():
    # Mock the open function to return file contents
    # Create a GitDiff object
    diff = GitDiff(file_name="prod/s3.tf", diff="doesn't matter for this test")

    with temporary_change_dir("tests/mock_repo_tf"):

        result = get_terraform_context(diff)

    assert len(result) == 1  # don't return the file for which we have a diff in
