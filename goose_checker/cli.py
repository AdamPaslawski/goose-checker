import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from pydantic import BaseModel

from goose_checker.chains import (approve_or_deny, base_checker,
                                  terraform_checker)
from goose_checker.diff import get_git_diffs
from goose_checker.goose_ascii import detected_ascii, goose_ascii
from goose_checker.models import (AzureGooseChecker, GooseChecker,
                                  GooseCheckerResponse, OpenAIGooseChecker)


class AppConfig(BaseModel):
    branch: str = os.environ.get("GOOSE_CHECKER_BRANCH_NAME", "main")
    model: str = os.environ.get("GOOSE_CHECKER_MODEL_NAME", "gpt-3.5-turbo")
    provider: str = os.environ.get("GOOSE_CHECKER_PROVIDER", "openai")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def run_checker(diff, goose_checker: GooseChecker):
    if diff.file_name.endswith(".tf"):
        return terraform_checker(diff=diff, goose_checker=goose_checker)
    else:
        return base_checker(diff=diff, goose_checker=goose_checker)


def display_issues(responses: list[GooseCheckerResponse]):
    for response in responses:
        if response.silly_mistakes:  # Checks if silly_mistakes is not empty
            print("\n")
            print(f"File Name: {response.file_name}")
            print(f"Silly Mistakes: {response.silly_mistakes}")
            print(f"Other Issues: {response.other_issues}")
            print("\n")


def parse_args() -> AppConfig:
    parser = argparse.ArgumentParser(description="Checks if you goofed")
    parser.add_argument(
        "--branch", nargs="?", help="The branch or commit to compare against"
    )
    parser.add_argument(
        "--model",
        nargs="?",
        help="LLM model to use, for Azure instances this is the deployment ID.",
    )
    supported_providers = ["azure", "openai"]
    parser.add_argument(
        "--provider",
        nargs="?",
        choices=supported_providers,
        help=f"The cloud provider to use, choices are: {supported_providers}",
    )

    args = parser.parse_args()
    return AppConfig(branch=args.branch, model=args.model, provider=args.provider)


def main(config: AppConfig):
    print(f"Checking for geese by comparing to {config.branch}")
    print(f"Using model: {config.model} provided by {config.provider}")

    if config.provider == "azure":
        goose_checker = AzureGooseChecker(
            with_respect_to=config.branch, deployment_name=config.model
        )
    elif config.provider == "openai":
        goose_checker = OpenAIGooseChecker(
            with_respect_to=config.branch, model=config.model
        )
    else:
        raise ValueError(f"Provider specified not supported: {config.provider}")

    diffs = get_git_diffs(with_respect_to=config.branch)

    if len(diffs) == 0:
        print(
            f"Compared your current checked out branch to {config.branch} and found nothing to check"
        )
        return False

    all_responses = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_diff = {
            executor.submit(run_checker, diff, goose_checker): diff for diff in diffs
        }
        for future in as_completed(future_to_diff):
            diff = future_to_diff[future]
            try:
                resp = future.result()
                all_responses.append(resp)
            except Exception as exc:
                print(f"Failed to analyze {diff.file_name} due to {exc}")

    approved, explanation = approve_or_deny(all_responses, goose_checker)

    if not approved:
        print("Geese detected:")
        print(explanation)
        return approved
    else:
        print("Approved! No Geese detected.")

    return approved


def cli_main():
    config = parse_args()
    main(config)


if __name__ == "__main__":
    load_dotenv()
    cli_main()
