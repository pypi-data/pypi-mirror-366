import re
import sys

from .common import get_repo, print_git_log


def css_command():
    if len(sys.argv) < 2:
        print("Error: Commit message required")
        print("Usage: css <commit message>")
        sys.exit(1)

    message = sys.argv[1]
    repo = get_repo()

    # Check if there are any changes
    if not repo.is_dirty(untracked_files=True):
        print("No changes to commit")
        return

    # Handle empty repository or no commits
    try:
        current = repo.head.commit
    except (ValueError, TypeError):
        # No commits yet, just create a new one
        repo.git.add(".")
        repo.index.commit(message)
        print(f"Created initial commit:\n{message}")
        print_git_log()
        return

    oldest_temp = None

    while current:
        if re.match(r"gitCMD: auto temp commit for .*", current.message):
            oldest_temp = current
            current = current.parents[0] if current.parents else None
        else:
            break

    # If oldest temporary commit is an init commit or all commits are temporary
    if oldest_temp:
        if oldest_temp.parents:
            repo.git.reset(oldest_temp.parents[0])  # Reset to parent if exists
        else:
            repo.git.update_ref("-d", "HEAD")  # Delete HEAD reference properly
        repo.git.add(".")
        repo.index.commit(message)
        print(f"Created commit:\n{message}")
        print_git_log()
    else:
        # Reset to that commit but keep changes
        repo.git.reset(current.hexsha)

        # Add and commit with new message
        repo.git.add(".")
        repo.index.commit(message)
        print(f"Created commit:\n{message}")
        print_git_log()
