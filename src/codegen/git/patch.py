from pygit2 import Diff
from pygit2.repository import Repository


def apply_patch(git_repo: Repository, patch: str):
    patch = Diff.parse_diff(patch)
    git_repo.apply(patch)
