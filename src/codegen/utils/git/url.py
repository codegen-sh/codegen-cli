from pygit2.repository import Repository


def get_git_url(repo: Repository) -> str:
    return repo.remotes[0].url
