from pygit2 import Diff
from pygit2.repository import Repository
from typing import List


def apply_patch(git_repo: Repository, patch: str):
    """
    Apply a git patch to the repository.
    
    Args:
        git_repo: The repository to apply the patch to
        patch: A string containing the git patch/diff
    """
    # Parse the entire patch into a Diff object
    diff_patch = Diff.parse_diff(git_diff=patch)
    
    # Apply each file's changes individually
    for patch_file in diff_patch:
        try:
            # Create a new diff containing just this file's changes
            file_diff = Diff.parse_diff(git_diff=str(patch_file))
            # Apply the individual file changes
            git_repo.apply(file_diff)
        except Exception as e:
            print(f"Error applying patch to {patch_file.delta.new_file.path}: {str(e)}")