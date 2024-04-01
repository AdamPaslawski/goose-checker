from unittest.mock import patch

from goose_checker.diff import get_git_diffs


def test_get_git_diffs():
    with patch("goose_checker.diff.get_all_files_with_diff") as mock_all_files:
        with patch("goose_checker.diff._get_diff_for_file") as mock_get_diff_for_file:
            mock_all_files.return_value = (
                open("tests/mock_diff/name_only_diff.txt").read().split("\n")
            )
            mock_get_diff_for_file.return_value = open(
                "tests/mock_diff/example_diff.txt"
            ).read()
            with_respect_to = "main"
            diffs = get_git_diffs(with_respect_to)

            assert len(diffs) == 1
