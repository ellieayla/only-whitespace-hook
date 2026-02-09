import pytest
from pathlib import Path
from only_whitespace_hook import util
from contextlib import contextmanager, chdir
from unittest import mock
import argparse


@pytest.fixture
def empty_git_repository(tmp_path: Path):
    with chdir(tmp_path):
        util.cmd_output(*('git', 'init'))
        yield tmp_path


@pytest.fixture
def populated_git_repo(empty_git_repository: Path) -> Path:
    (empty_git_repository / "first").write_text("first")
    (empty_git_repository / "second").write_text("second")
    util.cmd_output(*('git', 'add', '--', 'first', 'second'))
    util.cmd_output(*('git', 'commit', '-m', 'initial commit'))
    return empty_git_repository
