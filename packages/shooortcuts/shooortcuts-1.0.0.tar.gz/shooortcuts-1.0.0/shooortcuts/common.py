import re

from git import Repo
from git.exc import InvalidGitRepositoryError

TEMP_COMMIT_PREFIX = "gitCMD: auto temp commit for"


def get_repo():
    try:
        repo = Repo(".", search_parent_directories=True)
        return repo
    except InvalidGitRepositoryError:
        print("Error: Not a git repository")
        exit(1)


def get_version_from_last_commit():
    repo = get_repo()

    try:
        if not repo.heads:  # No branches yet
            return "__init__"

        last_commit = repo.head.commit

        # Check if last commit was from gss
        match = re.match(f"{TEMP_COMMIT_PREFIX} (.*)", last_commit.message)

        if match:
            return match.group(1)

        return last_commit.hexsha[:7]
    except (ValueError, TypeError):
        # This happens when there are no commits yet
        return "__init__"


def print_git_log():
    repo = get_repo()
    try:
        commits = list(repo.iter_commits(max_count=5))
        print("\nLatest commits:")
        for commit in commits:
            short_hash = commit.hexsha[:7]
            print(f"{short_hash} {commit.message}")
    except (ValueError, TypeError):
        # No commits yet
        pass
