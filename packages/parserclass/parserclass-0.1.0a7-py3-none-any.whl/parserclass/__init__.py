# SPDX-License-Identifier: MIT
from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass, field
from inspect import (
    Parameter,
    getdoc,
    getmembers,
    isfunction,
    signature,
)
from types import FunctionType, ModuleType, UnionType
from typing import (
    Any,
    Callable,
    get_args,
    get_origin,
    get_type_hints,
)

from parserclass._vendor.retrieveableset import RetrievableSet
from parserclass.errors import (
    ArgumentError,
    MissingFunctionArgumentsError,
    MissingParserArgumentError,
    UnrecognizedArgumentError,
)

from .types import Unset

__all__ = [
    "parameters_from_function",
    "functions_from_module",
    "FunctionParameter",
    "FunctionArgParser",
    "BaseArgParser",
    "parserclass",
]

type Args = list[Any]
type Kwargs = dict[str, Any]
type RunTriplet[T] = tuple[Callable[..., T], Args, Kwargs]


@dataclass(kw_only=True)
class FunctionParameter:
    name: str
    index: int
    default: Unset | Any = field(default_factory=Unset)
    type: Unset | type = field(default_factory=Unset)

    @property
    def required(self) -> bool:
        return self.default is Unset

    def __hash__(self) -> int:
        return hash(self.name)


def parameters_from_function(func: Callable[..., Any]) -> list[FunctionParameter]:
    annotations = get_type_hints(func)

    index = 0
    parameters: list[FunctionParameter] = []
    for name, param in signature(func).parameters.items():
        typ = annotations.get(name, Unset)
        default = param.default if param.default is not Parameter.empty else Unset

        parameters.append(
            FunctionParameter(name=name, index=index, default=default, type=typ)
        )
        index += 1
    return parameters


def _functions_from_module(
    module: ModuleType, *, public_only: bool = True
) -> Generator[tuple[str, FunctionType], None, None]:
    if public_only:
        for name, obj in getmembers(module):
            if isfunction(obj):
                if obj.__module__ == module.__name__:
                    yield name, obj


def functions_from_module(
    module: ModuleType, public_only: bool = True
) -> Generator[tuple[str, FunctionType], None, None]:
    if not public_only:
        yield from _functions_from_module(module)
    else:
        for name, obj in _functions_from_module(module):
            if not name.startswith("_"):
                yield name, obj


class FunctionArgParser[T]:
    name: str
    doc: None | str
    parameters: RetrievableSet[FunctionParameter]
    function: Callable[..., T]

    def __init__(self, func: Callable[..., T], /, name: str | None = None):
        self.name = name if name is not None else func.__name__
        self.doc = getdoc(func)
        self.function = func
        self.parameters = RetrievableSet(parameters_from_function(func))

    def __hash__(self) -> int:
        return hash(self.name)

    def usage(self, path: str = "") -> str:
        if path == "":
            path = self.name

        message = f"Usage: {path} "
        message += (
            "  ".join([f"[ {parser.name} ]" for parser in self.parameters]) + "\n\n"
        )
        return message.strip()

    def _parse(self, *std_args: str) -> RunTriplet[T]:
        args: Args = []
        kwargs: Kwargs = {}

        parameters = RetrievableSet(reversed(self.parameters))
        _args = list(reversed(std_args))
        while len(_args) > 0:
            if _args[-1].startswith("--"):
                break

            if not parameters[-1].required:
                break

            arg = _args.pop()
            param = parameters.pop()

            if isinstance(param.type, Unset):
                # warn("", category=RuntimeWarning)
                # TODO: Warn when there's no annotation
                ## Code will still append to args as string
                args.append(arg)
            elif get_origin(param.type) is UnionType:
                possible_types = get_args(param.type)
                for typ in possible_types:
                    try:
                        newArg = typ(arg)
                    except Exception as e:
                        print(e)
                    else:
                        break
                else:
                    raise Exception(possible_types)
                args.append(newArg)
            else:
                # TODO: Handle Enums
                # TODO: Handle multi argument types
                newArg = param.type(arg)
                args.append(newArg)

        while len(_args) > 0:
            key = _args.pop()

            if key.startswith("--"):
                key = key.removeprefix("--")

            if key not in parameters:
                raise UnrecognizedArgumentError(
                    path=[self.name], arg=key, usage=self.usage
                )

            param = parameters.get(key)
            if param.type is bool:
                if len(_args) > 0 and not _args[-1].startswith("--"):
                    value = _args.pop()
                else:
                    # TODO: Should we reverse the default value or set it to True in cli_flags?
                    value = True
                kwargs[key] = value
            else:
                value = _args.pop()

        missingArguments = [param.name for param in parameters if param.required]
        if missingArguments:
            raise MissingFunctionArgumentsError(
                path=[self.name], arg=missingArguments, usage=self.usage
            )

        return self.function, args, kwargs

    def parse(self, *std_args: str) -> tuple[Args, Kwargs]:
        try:
            _result, args, kwargs = self._parse(*std_args)
            return args, kwargs
        except ArgumentError as err:
            print(err)
            return [], {}

    def parse_and_run(self, *std_args: str) -> T | None:
        try:
            result, args, kwargs = self._parse(*std_args)
            return result(*args, **kwargs)
        except ArgumentError as err:
            print(err)
            return None


@dataclass(kw_only=True)
class BaseArgParser:
    @staticmethod
    def _fieldset_factory() -> RetrievableSet[BaseArgParser | FunctionArgParser[Any]]:
        return RetrievableSet()

    name: str
    doc: str = field(default_factory=str)
    subparsers: RetrievableSet[BaseArgParser | FunctionArgParser[Any]] = field(
        default_factory=_fieldset_factory
    )

    def __hash__(self) -> int:
        return hash(self.name)

    def usage(self, path: str = "") -> str:
        if path == "":
            path = self.name

        message = f"Usage: {path} "
        message += (
            "[ "
            + " | ".join([f"{parser.name}" for parser in self.subparsers])
            + " ]"
            + "\n\n"
        )

        padding = (
            len(max((getattr(parser, "name") for parser in self.subparsers), key=len))
            % 4
            + 1
        ) * 4
        for parser in self.subparsers:
            if parser.doc is not None and parser.doc != "":
                message += f"{parser.name:<{padding}}" + parser.doc + "\n"
            else:
                message += parser.name + "\n"
        return message.strip()

    def _parse(self, *std_args: str) -> RunTriplet[Any]:
        try:
            if len(std_args) == 0:
                raise MissingParserArgumentError(path=[], usage=self.usage)

            _args = list(std_args)
            arg = _args.pop(0)
            if arg in self.subparsers:
                subparser = self.subparsers.get(arg)

                match subparser:
                    case BaseArgParser():
                        return subparser._parse(*_args)
                    case FunctionArgParser():
                        return subparser._parse(*_args)
                    case _:
                        raise TypeError(type(subparser))
            else:
                raise UnrecognizedArgumentError(path=[], usage=self.usage, arg=arg)
        except ArgumentError as err:
            err.path.append(self.name)
            raise err

    def parse(self, *std_args: str) -> tuple[Args, Kwargs]:
        try:
            _result, args, kwargs = self._parse(*std_args)
            return args, kwargs
        except ArgumentError as err:
            if isinstance(err, MissingParserArgumentError):
                pass
            else:
                print(err)
            print(err.usage(" ".join(reversed(err.path))))
            return [], {}

    def parse_and_run(self, *std_args: str) -> Any:
        try:
            result, args, kwargs = self._parse(*std_args)
            return result(*args, **kwargs)
        except ArgumentError as err:
            if isinstance(err, MissingParserArgumentError):
                pass
            else:
                print(err)
            print(err.usage(" ".join(reversed(err.path))))
            return None


# TODO: Support keyword arguments
def parserclass(cls: type, /, name: str = "") -> BaseArgParser:
    cls_name = cls.__name__ if name == "" else name
    functions: dict[str, FunctionType] = {}
    subparsers: dict[str, BaseArgParser] = {}

    publicMembers = ((n, v) for n, v in getmembers(cls) if not n.startswith("_"))
    for name, value in publicMembers:
        if isinstance(value, FunctionType):
            functions[name] = value
        elif isinstance(value, BaseArgParser):
            subparsers[name] = value
        delattr(cls, name)

    parser = BaseArgParser(name=cls_name)
    for name, function in functions.items():
        parser.subparsers.add(FunctionArgParser(function, name=name))

    for name, submodule in subparsers.items():
        submodule.name = name
        parser.subparsers.add(submodule)
    return parser
