from .common import get_repo, print_git_log


def dss_command():
    repo = get_repo()

    # Check if there are any changes
    if not repo.is_dirty(untracked_files=True):
        print("No changes to drop")
        return

    # Save changes to stash
    repo.git.add(".")
    repo.git.stash("save", "gitCMD: auto stash")
    print("Saved changes to stash")
    print_git_log()
