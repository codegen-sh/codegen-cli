import os
from pathlib import Path

from dulwich.repo import Repo

from codegen.utils.git.folder import get_git_folder


def get_git_repo(path: os.PathLike | None = None) -> Repo | None:
    if path is None:
        path = Path.cwd()
    git_folder = get_git_folder(path)
    if git_folder is None:
        return None
    return Repo(str(git_folder))
