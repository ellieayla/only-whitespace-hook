
from argparse import ArgumentParser
import sys
from only_whitespace_hook.util import cmd_output

def git_diff_files_with_non_whitespace_changes() -> set[str]:
    cmd = ('git', 'diff', '--staged', '--name-only', '--ignore-all-space')
    return set(cmd_output(*cmd).splitlines())

def main() -> int:
    print(sys.argv)
    return 1    



if __name__ == "__main__":
    raise SystemExit(main())
