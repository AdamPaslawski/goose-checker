import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from dotenv import load_dotenv

from goose_checker.chains import (base_checker, approve_or_deny,
                                  terraform_checker)
from goose_checker.diff import get_git_diffs
from goose_checker.goose_ascii import detected_ascii, goose_ascii
from goose_checker.models import (AzureGooseChecker, GooseCheckerResponse,
                                  OpenAIGooseChecker)


def run_checker(diff, goose_checker):
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


def cli_main():
    parser = argparse.ArgumentParser(description="Checks if you goofed")
    parser.add_argument(
        "--branch",
        nargs="?",
        default=os.environ.get("GOOSE_CHECKER_BRANCH_NAME", "main"),
        help="The branch or commit to compare against",
    )
    parser.add_argument(
        "--model",
        nargs="?",
        default=os.environ.get("GOOSE_CHECKER_MODEL_NAME", "gpt-3.5-turbo"),
        help="LLM model to use, for Azure instances this is the deployment ID.",
    )

    supported_providers = ["azure", "openai"]
    parser.add_argument(
        "--provider",
        nargs="?",
        default=os.environ.get("GOOSE_CHECKER_PROVIDER","openai"),
        choices=supported_providers,
        help=f"The cloud provider to use, choices are: {supported_providers}",
    )

    args = parser.parse_args()

    print(f"Checking for geese by comparing to {args.branch}")
    print(f"Using model: {args.model} provided by {args.provider}")

    if args.provider == "azure":
        goose_checker = AzureGooseChecker(
            with_respect_to=args.branch, deployment_name=args.model
        )
    elif args.provider == "openai":
        goose_checker = OpenAIGooseChecker(
            with_respect_to=args.branch, model=args.model
        )
    else:
        raise ValueError(f"Provider specified not supported: {args.provider}")

    # Lets Cook

    diffs = get_git_diffs(with_respect_to=args.branch)

    all_responses = []
    # Initialize ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit tasks to the executor
        future_to_diff = {
            executor.submit(run_checker, diff, goose_checker): diff for diff in diffs
        }
        # Retrieve and store results as they complete
        for future in as_completed(future_to_diff):
            diff = future_to_diff[future]
            try:
                resp = future.result()
                all_responses.append(resp)
            except Exception as exc:
                print(f"Failed to analyze {diff.file_name} due to {exc}")
    if not all_responses:
        return False

    approved, explanation = approve_or_deny(all_responses, goose_checker)

    if not approved:
        print(goose_ascii)
        print(detected_ascii)
        print(explanation)
    
    else:
        print("Approved! No Geese detected.")

    return approved


if __name__ == "__main__":
    load_dotenv()
    cli_main()
