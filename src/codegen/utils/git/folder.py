import os
from pathlib import Path


def get_git_folder(path: os.PathLike) -> Path | None:
    path = Path(path)
    while path != path.root:
        if (path / ".git").exists():
            return path
        path = path.parent
    return None
