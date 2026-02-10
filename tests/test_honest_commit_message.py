from pytest import CaptureFixture
from only_whitespace_hook.honest_commit_message import main
from only_whitespace_hook import util
from pathlib import Path


def test_empty_commit_message_noop(populated_git_repo: Path) -> None:
    msg = populated_git_repo / ".git" / "COMMIT_MSG"

    msg.write_text("")
    assert main([".git/COMMIT_MSG"]) == 0


def test_normal_commit_message_noop(populated_git_repo: Path) -> None:
    msg = populated_git_repo / ".git" / "COMMIT_MSG"

    msg.write_text("changed some things")
    assert main([".git/COMMIT_MSG"]) == 0


def test_marked_commit_message_with_text_change(populated_git_repo: Path, capsys: CaptureFixture[str]) -> None:
    with open(populated_git_repo.joinpath("second"), 'a') as f:
        f.write("2222")
    util.cmd_output(*('git', 'add', '--', 'second'), retcode=0)

    msg = populated_git_repo / ".git" / "COMMIT_MSG"

    msg.write_text("MARKER")

    assert main(["--header=MARKER", ".git/COMMIT_MSG"]) == 1

    captured = capsys.readouterr()
    assert 'non-whitespace changes are staged' in captured.err


def test_marked_commit_message_with_whitespace_change(populated_git_repo: Path, capsys: CaptureFixture[str]) -> None:
    with open(populated_git_repo.joinpath("second"), 'a') as f:
        f.write("\n\n\n\n")
    util.cmd_output(*('git', 'add', '--', 'second'), retcode=0)

    msg = populated_git_repo / ".git" / "COMMIT_MSG"

    msg.write_text("MARKER")

    assert main(["--header=MARKER", ".git/COMMIT_MSG"]) == 0

    captured = capsys.readouterr()
    assert '' == captured.err
