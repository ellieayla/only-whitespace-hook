# https://github.com/pre-commit/pre-commit-hooks/blob/main/pre_commit_hooks/util.py

import subprocess

class CalledProcessError(RuntimeError):
    pass

def cmd_output(*cmd: str, retcode: int | None = 0, **kwargs: Any) -> str:
    kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault('stderr', subprocess.PIPE)
    proc = subprocess.Popen(cmd, **kwargs)
    stdout, stderr = proc.communicate()
    stdout = stdout.decode()
    if retcode is not None and proc.returncode != retcode:
        raise CalledProcessError(cmd, retcode, proc.returncode, stdout, stderr)
    return stdout
