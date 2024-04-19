import os

from goose_checker.chains import terraform_checker, base_checker, approve_or_deny
from goose_checker.diff import GitDiff
from goose_checker.models import AzureGooseChecker, GooseCheckerResponse
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
    assert len(result.issues) == 1
    assert result.chain_of_thought != ""


def test_goose_detector_secret():

    with open("tests/mock_diff/git_diff_tf_secrets.txt") as f:
        diff = f.read()

    diff = GitDiff(file_name="prod/secrets.tf", diff=diff)
    result = base_checker(
        diff,
        AzureGooseChecker(
            deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME"), with_respect_to="main"
        ),
    )

    assert len(result.issues) != 0
    assert len(result.chain_of_thought) > 0


def test_approval_chain():
    
    responses = [
        GooseCheckerResponse(
            file_name="dev/s3.tf", chain_of_thought="1. In line 776, there is a missing closing square bracket ']' after the first 'arn' value.\n2. In line 792, there is a typo in the 'arn' value, 'md-api-db-useame' should be 'md-api-db-username'.", issues=["Missing closing square bracket", " Typo in 'arn' value"]
        )
    ]
    result = approve_or_deny(
        responses,
        AzureGooseChecker(
            deployment_name=os.getenv("AZURE_DEPLOYMENT_NAME"), with_respect_to="main"
        ),
    )
    assert result.approved == False
    assert result.instructions_to_engineer != ""
