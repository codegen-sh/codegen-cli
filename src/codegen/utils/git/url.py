from urllib.parse import urlparse

from pygit2.repository import Repository


def get_repo_full_name(repo: Repository) -> str:
    full_name = get_repo_full_name_from_url(get_git_url(repo))
    if not full_name:
        raise ValueError("Could not determine repository full name from URL")
    full_name = full_name.split(":")[1]
    return full_name


def get_git_url(repo: Repository) -> str:
    return repo.remotes[0].url


def get_repo_full_name_from_url(git_url: str) -> str:
    git_url = git_url.replace(".git", "")
    url_parts = urlparse(git_url).path.strip("/").split("/")
    if len(url_parts) < 2:
        return None
    repo_full_name = f"{url_parts[0]}/{url_parts[1]}"
    return repo_full_name
