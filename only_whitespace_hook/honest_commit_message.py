
from argparse import ArgumentParser
import sys
from only_whitespace_hook.util import cmd_output
import subprocess
import os


def repo_has_non_whitespace_changes_staged() -> bool:
    cmd = ('git', 'diff', '--staged', '--quiet', '--ignore-all-space', '--ignore-blank-lines')
    exit_code = subprocess.call(cmd)
    assert exit_code in (0, 1)
    return exit_code != 0  # exits 1 if diff would have shown output


def git_diff_file_names() -> set[str]:
    cmd = ('git', 'diff', '--staged', '--name-only', '-z')  # -z is the \0 seperator
    return set(cmd_output(*cmd).split("\0"))


HEADER_LINE = "Whitespace-only change"


def main() -> int:
    # ref https://git-scm.com/docs/githooks#_prepare_commit_msg
    # the git prepare-commit-msg hook takes 1-3 parameters.
    # pre-commit puts the first argument in sys.argv - the path to a filename containing the in-progress commit message
    assert len(sys.argv) == 2
    commit_message_filename = sys.argv[1]

    # pre-commit puts the second argument in PRE_COMMIT_COMMIT_MSG_SOURCE:
    #  - unset:    - normal 'git commit'
    #  - message:  - git commit -m / -F
    #  - template: - git commit -t / commit.template set
    #  - merge:    - .git/MERGE_MSG exists
    #  - commit:   - git commit --amend
    # only alter 'message' and unset cases.

    git_dir = cmd_output('git', 'rev-parse', '--git-dir').rstrip()
    
    message_source = os.environ.get('PRE_COMMIT_COMMIT_MSG_SOURCE', 'message')
    if message_source != 'message':
        # don't pre-populate a commit message for merge/amend commits
        return 0

    if repo_has_non_whitespace_changes_staged():
        # fast exit - normal git commit with changes
        return 0
    
    changed_files = git_diff_file_names()

    if not changed_files:  # empty commit?
        return 0

    with open(commit_message_filename, 'a+') as commit_message_file:
        end_position = commit_message_file.tell()
        commit_message_file.seek(0)  # go back to start of file for reading
        if HEADER_LINE in commit_message_file.read():
            # already have the line we would have added, just exit without altering the file
            return 0
        
        commit_message_file.seek(end_position)
        if end_position:
            # appending to existing content in message, add seperator
            commit_message_file.write("\n\n")

        commit_message_file.write(f"{HEADER_LINE} of {len(changed_files)} file{'s' if len(changed_files) != 1 else ''}:\n")
        for filename in changed_files:
            commit_message_file.write(f"  {filename}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
