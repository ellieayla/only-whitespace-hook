# https://github.com/pre-commit/pre-commit-hooks/blob/main/pre_commit_hooks/util.py

import subprocess
from typing import Any, cast

DEFAULT_HEADER_LINE = "Whitespace-only change"


class CalledProcessError(RuntimeError):
    pass

def cmd_output(*cmd: str, retcode: int | None = 0, **kwargs: Any) -> str:
    kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault('stderr', subprocess.PIPE)
    proc = subprocess.Popen(cmd, text=True, **kwargs)
    stdout, stderr = proc.communicate()  # type Tuple[str,str]
    if retcode is not None and proc.returncode != retcode:
        raise CalledProcessError(cmd, retcode, proc.returncode, stdout, stderr)
    return cast(str, stdout)


def split_null_terminators(output: str) -> set[str]:
    """Many git commands support outputing null-terminated filename lists via a -z parameter. Split them."""
    return set([_ for _ in output.split("\0") if _ != ''])


def repo_has_non_whitespace_changes_staged() -> bool:
    cmd = ('git', 'diff', '--staged', '--quiet', '--ignore-all-space', '--ignore-blank-lines')
    try:
        cmd_output(*cmd, retcode=0)
        return False
    except CalledProcessError as e:
        process_exit_code = e.args[2]
        if process_exit_code == 1:
            return True
        else:
            raise  # pragma: nocover


def git_diff_non_whitespace_changed_filenames() -> set[str]:
    cmd = ('git', 'diff', '--staged', '--ignore-all-space', '--ignore-blank-lines', '--numstat', '-z')
    lines = split_null_terminators(cmd_output(*cmd, retcode=0))
    return set([_.split(maxsplit=2)[2] for _ in lines])


def git_diff_all_changed_filenames() -> set[str]:
    cmd = ('git', 'diff', '--staged', '--name-only', '-z')  # -z is the \0 seperator
    return split_null_terminators(cmd_output(*cmd, retcode=0))
