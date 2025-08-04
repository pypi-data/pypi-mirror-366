# shooortcuts

Simple and helpful cli shortcuts.

## 1. Installation

```bash
pip install shooortcuts
```

Or install from source:

```bash
git clone https://github.com/monosolo101/shooortcuts.git
cd shooortcuts
pip install -e .
```

## 2. Commands

### `ass` (Auto Save State)

Creates a temporary commit with an auto-generated version string.  
This is extremely helpful when you **make small incremental code changes**.

```bash
$ ass
# Created temporary commit with version message: __init__    # If this is the first commit
# Created temporary commit with version message: a1b2c3d     # If a previous commit exists
```

Version string rules:

- If no commits exist: "**\_\_init\_\_**" will be used as the version
- If the last commit is a temp commit made by `ass`: the last version string will be reused
- If the last commit is not a temp commit: the short hash of the last non-temp commit will be used

### `css` (Commit Saved State)

Converts temporary commits into a permanent commit.  
Use this to **convert previous temporary commits into a final formal commit with a proper message**.

```bash
$ css "feat: implement new feature"
```

Behavior:

1. If the oldest temporary commit is an "**\_\_init\_\_**" commit:

   - Replaces it with the new commit
   - Example: `__init__` → `feat: implement new feature`

2. If there is a non-temporary commit before the temporary commits:

   - Resets to that commit
   - Creates a new commit with all changes
   - Example: `normal → temp1 → temp2` becomes `normal → new`

3. If all commits are temporary:
   - Creates a new commit replacing all temporary commits
   - Example: `temp1 → temp2` becomes `new`

### `dss` (Drop State to Stash)

Discards changes made since the last commit, saving them to the stash.  
Useful when recent changes turn out to be a mess.

```bash
$ dss
Saved changes to stash
```

Behavior:

- If there are no changes: prints "No changes to drop"
- Otherwise: saves all changes to the stash with message `"gitCMD: auto stash"`
- Changes can be recovered later using `git stash pop` or `git stash apply`

### `fss` (Fuck off Saved State)

Moves temporary commits to a new branch and resets the main branch.  
Use this when everything feels like a mistake and you want to restore the codebase to the last formal commit.

```bash
$ fss
#Saved current changes as temporary commit
#Created new branch: temp/abc123_250325
#Reset main to last non-temp commit
```

Behavior:

1. If there are uncommitted changes:
   - Creates a temporary commit with current changes
2. If no commits exist: prints "No commits to fuck off" and stop
3. If all commits are temporary: prints a warning and exits and stop
4. If there are no temporary commits: prints "No temporary commits to fuck off" and stop
5. Otherwise:
   - Creates a new branch `temp/$version_YYMMDD_HHMMSS`
   - Moves all temporary commits to the new branch
   - Resets the main branch to the last non-temporary commit

## 3. Use Case

Typical workflow:

```bash
# Step 0: The repo is in a clean state since the last commit
git log
commit aaa (HEAD -> main)

# Step 1: Make some changes
$ ass
# Saved temporary state
# Created temporary commit with version message: aaa

# Step 2: Make more changes
$ ass
# Saved another state
# Created temporary commit with version message: aaa

# Step 4: AI messed something up
$ dss
# Discard all changes and return to Step 2

# Step 5: Make more changes and get ready for a proper commit
$ css "feat: complete implementation"
# Squash all xxxxx temp commits into a formal commit
# Created commit: feat: complete implementation

# Optional Step 5: Decide the whole thing was a mistake
$ fss
# Discard all changes and return to Step 0
# Reset main to last non-temp commit
```

This allows you to:

1. Save work-in-progress changes frequently
2. Convert them into a clean commit when ready, or discard them entirely if needed
3. Maintain a clean Git history
