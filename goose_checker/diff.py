import subprocess

from pydantic import BaseModel

# Intelligently analyze git diff


class GitDiff(BaseModel):
    file_name: str
    diff: str


def get_all_files_with_diff(with_respect_to: str) -> list:
    """Get all files with a diff compared to the given branch or commit."""
    result = subprocess.run(
        ["git", "diff", "--name-only", with_respect_to], capture_output=True, check=True
    )
    result_list = list(result.stdout.decode().split("\n"))

    # Remove any empty string
    result_list = [x for x in result_list if x]

    return result_list


def _get_diff_for_file(file_name: str, with_respect_to: str) -> str:
    """Get the diff for a specific file compared to the given branch or commit."""
    result = subprocess.run(
        ["git", "diff", with_respect_to, file_name], capture_output=True, check=True
    )
    return result.stdout.decode()


def get_git_diffs(with_respect_to: str) -> list[GitDiff]:
    """Get all files with a diff compared to the given branch or commit."""
    files_with_diff = get_all_files_with_diff(with_respect_to)
    diffs = []
    for file in files_with_diff:
        try:
            diff = _get_diff_for_file(file, with_respect_to)
        except subprocess.CalledProcessError:
            print(f"Failed to get diff for {file}")
            continue
        diffs.append(GitDiff(file_name=file, diff=diff))
    return diffs
