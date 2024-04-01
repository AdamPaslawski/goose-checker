import os

from goose_checker.chains import terraform_checker
from goose_checker.diff import GitDiff
from goose_checker.models import AzureGooseChecker
from tests.conftest import temporary_change_dir


def test_terraform_checker():
    # Create a mock GitDiff object

    with open("tests/mock_diff/git_diff_tf_s3.txt") as f:
        terraform_diff = f.read()

    diff = GitDiff(file_name="dev/s3.tf", diff=terraform_diff)
    with temporary_change_dir("tests/mock_repo_tf"):
        # Create a mock GooseChecker object
        goose_checker = AzureGooseChecker(
            deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME"), with_respect_to="main"
        )
        # Call the function under test
        result = terraform_checker(diff, goose_checker)

    # Assert the expected behavior
    assert result.silly_mistakes == ""
    assert result.other_issues != ""
