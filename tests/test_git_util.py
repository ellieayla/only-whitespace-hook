import pytest
from only_whitespace_hook import util
from pathlib import Path


def test_see_git_root(populated_git_repo) -> None:
    cmd = ('git', 'rev-parse', '--absolute-git-dir')
    left = (populated_git_repo / '.git').absolute()
    right = Path(util.cmd_output(*cmd, retcode=0).splitlines()[0])
    assert left == right


def test_git_exception(populated_git_repo: Path):
    cmd = ('git', 'commit', '-m', '')
    with pytest.raises(util.CalledProcessError):
        util.cmd_output(*cmd, retcode=0)


@pytest.mark.parametrize("git_output,expected", [
    ('', set()),
    ('\0\0\0', set()),
    ('single\0', set(['single'])),
    ('lines with whitespace\0  are preserved\0without trimming  \0', set(["lines with whitespace", "  are preserved", "without trimming  "]))
])
def test_split_null_terminators(git_output: str, expected: set[str]) -> None:    
    assert util.split_null_terminators(git_output) == expected
