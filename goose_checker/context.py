import glob
from pathlib import Path

from pydantic import BaseModel

from goose_checker.diff import GitDiff


class BaseContext(BaseModel):
    file_name: str
    contents: str


class TerraformContext(BaseContext):
    pass


def get_terraform_context(diff: GitDiff) -> list[TerraformContext]:

    ret = []

    file_path = Path(diff.file_name)
    # Use glob to find matching files excluding the current file's directory
    pattern = f"**/{file_path.name}"
    for entry in glob.glob(pattern, recursive=True):
        path = Path(entry)
        if path != file_path and path.name == file_path.name:
            with open(path, "r") as f:
                contents = f.read()
                ret.append(TerraformContext(file_name=path.name, contents=contents))
    return ret
