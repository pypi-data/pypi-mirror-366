# SPDX-License-Identifier: MIT
from pathlib import Path

from parserclass import FunctionArgParser, parserclass
from pytest import raises


def _simple(arg1: bool, arg2: bool = True):
    pass


def _complex(arg1: Path | str, arg2: str):
    pass


@parserclass
class parser:
    simple = _simple
    complex = _complex


subparser = FunctionArgParser(_simple)


def test_parser():
    result = parser.parse("simple")
    expected = ([], {})
    assert result == expected


def test_subparser():
    result = parser.parse("simple")
    expected = ([], {})
    assert result == expected


def test_argument_union():
    result = parser.parse("complex", "HERE", "NOW")
    expected = ([Path("HERE"), "NOW"], {})
    assert result == expected


def test_MissingParserArgumentsError():
    from parserclass.errors import MissingParserArgumentError

    with raises(MissingParserArgumentError):
        parser._parse()


def test_MissingFunctionArgumentsError():
    from parserclass.errors import MissingFunctionArgumentsError

    with raises(MissingFunctionArgumentsError):
        subparser._parse()
