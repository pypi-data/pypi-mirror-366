# SPDX-License-Identifier: MIT
from pathlib import Path

from parserclass import parserclass
from pytest import raises


def _clone(
    repository: Path,
    directory: Path,
    mirror: bool = False,
    local: bool = False,
    reference: None | Path = None,
):
    """Clone a repository into a new directory"""
    return


def _status(short: bool = False, branch: str = ""):
    """Show the working tree status"""


@parserclass
class git:
    status = _status
    clone = _clone


USAGE = """Usage: git [ clone | status ]

clone       Clone a repository into a new directory
status      Show the working tree status
"""


def test_parser_noargs(capsys):
    result = git.parse()
    expected = [], {}

    result_message = capsys.readouterr().out
    message = USAGE

    assert result == expected
    assert result_message == message


def test_UnrecognizedArgumentError():
    from parserclass.errors import UnrecognizedArgumentError

    with raises(UnrecognizedArgumentError):
        git._parse("git", "status", "--local")
