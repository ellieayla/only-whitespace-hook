
from argparse import ArgumentParser
import sys
from only_whitespace_hook.util import repo_has_non_whitespace_changes_staged, git_diff_all_changed_filenames, DEFAULT_HEADER_LINE
import sys
import os


def main(args: None | list[str] = None) -> int:
    # pre-commit puts the second argument in PRE_COMMIT_COMMIT_MSG_SOURCE:
    #  - unset:    - normal 'git commit'
    #  - message:  - git commit -m / -F
    #  - template: - git commit -t / commit.template set
    #  - merge:    - .git/MERGE_MSG exists
    #  - commit:   - git commit --amend
    # only alter 'message' and unset cases.
    message_source = os.environ.get('PRE_COMMIT_COMMIT_MSG_SOURCE', 'message')
    if message_source != 'message':
        # don't pre-populate a commit message for merge/amend commits, fast-exit
        return 0

    p = ArgumentParser()
    p.add_argument("--header", type=str, required=False, default=DEFAULT_HEADER_LINE, help="commit message text indicating a whitespace-only change. (default '%(default)s')")
    p.add_argument("commit_message_filename", metavar="COMMIT_MSG", help="Path to the commit message file.")
    a = p.parse_args(args)

    if repo_has_non_whitespace_changes_staged():
        # fast exit - normal git commit with changes
        return 0

    changed_files = git_diff_all_changed_filenames()

    if not changed_files:  # empty commit?
        return 0

    with open(a.commit_message_filename, 'a+') as commit_message_file:
        # save position, seek to beginning, read contents, and check whether the header line is already added
        end_position = commit_message_file.tell()
        commit_message_file.seek(0)
        existing_commit_message = commit_message_file.read()
        if a.header in existing_commit_message:
            # already have the line we would have added, just exit without altering the file
            return 0
        
        commit_message_file.seek(end_position, os.SEEK_SET)
        if existing_commit_message:
            commit_message_file.write("\n")  # add a seperator

        commit_message_file.write(f"{a.header} of {len(changed_files)} file{'s' if len(changed_files) != 1 else ''}\n")
        for filename in changed_files:
            commit_message_file.write(f" -  {filename}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
