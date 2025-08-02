# SPDX-License-Identifier: MIT
from dataclasses import dataclass
from typing import Callable


@dataclass(kw_only=True)
class ArgumentError(Exception):
    """An error from creating or using an argument (optional or positional)."""

    path: list[str]
    usage: Callable[[str], str]


class MissingParserArgumentError(ArgumentError):
    pass


@dataclass
class MissingFunctionArgumentsError(ArgumentError):
    """An error from a missing required argument."""

    arg: list[str]  # type: ignore

    def __str__(self) -> str:
        return f"Missing required arguments: {' ,'.join(arg for arg in self.arg)}"


@dataclass
class UnrecognizedArgumentError(ArgumentError):
    """An error from passing an unkown argument."""

    arg: str

    def __str__(self) -> str:
        return f"Unrecognized argument: {self.arg}"


@dataclass
class ArgumentTypeError(ArgumentError):
    """An error from trying to convert a command line string to a type."""

    arg: str
