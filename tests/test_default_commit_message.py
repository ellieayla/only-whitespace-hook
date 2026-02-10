from only_whitespace_hook.default_commit_message import main, commit_message_blank
from only_whitespace_hook import util
from pathlib import Path
import pytest


def test_no_staged_changes_passes_silently(populated_git_repo: Path) -> None:
    #default_commit_message.main()
    assert main([".git/COMMIT_MSG"]) == 0


def test_dirty_working_directory_ignored(populated_git_repo: Path) -> None:
    populated_git_repo.joinpath("third").write_text("third")
    assert set() == util.git_diff_all_changed_filenames()
    assert main([".git/COMMIT_MSG"]) == 0


def test_whitespace_change_provokes_new_commit_message(populated_git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with open(populated_git_repo.joinpath("first"), 'a') as f:
        f.write("\n\n\n    \n\n\n")
    util.cmd_output(*('git', 'add', '--', 'first'), retcode=0)

    msg = populated_git_repo / ".git" / "COMMIT_MSG"
    msg.write_text('')
    assert {'first'} == util.git_diff_all_changed_filenames()

    # not on merge commit
    with monkeypatch.context() as m:
        m.setenv("PRE_COMMIT_COMMIT_MSG_SOURCE", "merge")
        assert main(["--header=MARKER", ".git/COMMIT_MSG"]) == 0
        assert msg.read_text() == ''

    # first with empty message
    assert main(["--header=MARKER", ".git/COMMIT_MSG"]) == 0
    assert 'MARKER of 1 file\n\n -  first\n' == msg.read_text()

    # first with existing message
    msg.write_text('existing')
    assert main(["--header=MARKER", ".git/COMMIT_MSG"]) == 0
    assert 'existing\nMARKER of 1 file\n -  first\n' == msg.read_text()

    # reentrant without adding another marker
    assert main(["--header=MARKER", ".git/COMMIT_MSG"]) == 0
    assert 'existing\nMARKER of 1 file\n -  first\n' == msg.read_text()


def test_new_empty_file_not_considered_whitespace(populated_git_repo: Path) -> None:
    populated_git_repo.joinpath("third").touch()

    util.cmd_output(*('git', 'add', '--', 'third'), retcode=0)

    msg = populated_git_repo / ".git" / "COMMIT_MSG"
    msg.write_text('')

    assert {'third'} == util.git_diff_all_changed_filenames()
    assert {'third'} == util.git_diff_non_whitespace_changed_filenames()

    assert main(["--header=MARKER", ".git/COMMIT_MSG"]) == 0

    assert '' == msg.read_text()


def test_mixed_change(populated_git_repo: Path) -> None:
    with open(populated_git_repo.joinpath("first"), 'a') as f:
        f.write("\n\n\n    \n\n\n")
    with open(populated_git_repo.joinpath("second"), 'a') as f:
        f.write("2222")

    util.cmd_output(*('git', 'add', '--', 'first', 'second'), retcode=0)

    msg = populated_git_repo / ".git" / "COMMIT_MSG"
    assert not msg.exists()

    assert {'first', 'second'} == util.git_diff_all_changed_filenames()

    assert main(["--header=MARKER", ".git/COMMIT_MSG"]) == 0
    assert not msg.exists()

@pytest.mark.parametrize("message,expected", [
    ("", True),
    ("\n", True),
    ("\n# comment\n#comment\n", True),
    ("header\n\n#comment\n", False),
    ("\n#comment\ntrailing\n", False),
])
def test_existing_commit_message_blank(message: str, expected: bool) -> None:
    assert commit_message_blank(message) == expected
