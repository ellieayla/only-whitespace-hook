
from argparse import ArgumentParser
import sys
from only_whitespace_hook.util import repo_has_non_whitespace_changes_staged, git_diff_non_whitespace_changed_filenames, git_diff_all_changed_filenames, DEFAULT_HEADER_LINE
import subprocess
import os


def main(args: None | list[str]) -> int:
    p = ArgumentParser()
    p.add_argument("--header", type=str, required=False, default=DEFAULT_HEADER_LINE, help="commit message text indicating a whitespace-only change. (default '%(default)s')")
    p.add_argument("commit_message_filename", metavar="COMMIT_MSG", help="Path to the commit message file.")
    a = p.parse_args(args)

    with open(a.commit_message_filename, 'r') as commit_message_file:
        if a.header not in commit_message_file.read():
            # not a claim of whitespace-only, fast-exit
            return 0

    non_whitespace_changed_files = git_diff_non_whitespace_changed_filenames()

    # claim this is a whitespace-only commit
    if not non_whitespace_changed_files:
        # and it's true
        return 0

    print(f"Commit message says '{a.header}', but non-whitespace changes are staged.", file=sys.stderr)
    print(f"Split into multiple commits or amend the commit message.", file=sys.stderr)
    print(f"  Hint:  git diff --staged --ignore-all-space --ignore-blank-lines -- {" ".join(non_whitespace_changed_files)}", file=sys.stderr)
    
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
