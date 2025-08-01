# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

import re
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from functools import partial, wraps
from importlib import metadata
from textwrap import dedent
from types import SimpleNamespace
from typing import IO, TYPE_CHECKING, Any, AnyStr, NoReturn, TypeVar, cast

import click
from click.exceptions import Exit

from tomcli import __version__ as _ver
from tomcli._peekable import peekable
from tomcli.formatters import DEFAULT_FORMATTER
from tomcli.toml import Reader, Writer

_T = TypeVar("_T")
if TYPE_CHECKING:
    from typing_extensions import ParamSpec

    _P = ParamSpec("_P")


DEFAULT_CONTEXT_SETTINGS = context_settings = dict(
    help_option_names=["-h", "--help"],
    show_default=True,
)

# https://toml.io/en/v1.0.0#keys
TOML_KEY_MATCHER = re.compile(r"[A-Za-z0-9_-]+")

CLICK_82 = tuple(map(int, metadata.version("click").split(".")[:2])) >= (8, 2)


@contextmanager
def _std_cm(path: str, dash_stream: IO[AnyStr], mode: str) -> Iterator[IO[AnyStr]]:
    if str(path) == "-":
        yield dash_stream
    else:
        with open(path, mode) as fp:
            yield cast(IO[AnyStr], fp)


def fatal(*args: object, returncode: int = 1) -> NoReturn:
    print(*args, file=sys.stderr)
    raise Exit(returncode)


def _verify_part(part: str) -> str:
    """
    Verify that an unquoted key is valid, per the TOML standard

    See https://toml.io/en/v1.0.0#keys.
    """
    if not TOML_KEY_MATCHER.fullmatch(part):
        raise ValueError(
            f"Invalid selector part: `{part}`. Try wrapping the key in quotes."
        )
    return part


def split_by_dot(selector: str) -> Iterator[str]:
    r"""
    Split dot-separated TOML keys.
    Handles quoted keys and ensures that unquoted keys only include characters
    allwoed by TOML 1.0.

    >>> list(split_by_dot("."))
    []
    >>> list(split_by_dot(""))
    []
    >>> list(split_by_dot("a.b"))
    ['a', 'b']
    >>> list(split_by_dot("'a.b'"))
    ['a.b']
    >>> list(split_by_dot('"a.b".c'))
    ['a.b', 'c']
    >>> list(split_by_dot('c."a.b.100".z'))
    ['c', 'a.b.100', 'z']
    >>> list(split_by_dot("'quoted \"value\"'.abc"))
    ['quoted "value"', 'abc']
    >>> list(split_by_dot("'ab'x"))
    Traceback (most recent call last):
        ...
    ValueError: Invalid selector part: `'ab'x`. Expected `.` or end but got `x`.
    >>> list(split_by_dot("a.b.."))
    Traceback (most recent call last):
        ...
    ValueError: Invalid selector part: `b..`. Expected character or end but got `.`.
    >>> list(split_by_dot("a.b.'a"))
    Traceback (most recent call last):
        ...
    ValueError: Invalid selector part: `'a`. Expected `'` but got end.
    >>> next(split_by_dot("ajja ."))
    Traceback (most recent call last):
        ...
    ValueError: Invalid selector part: `ajja `. Try wrapping the key in quotes.
    """

    # Special case root
    if selector == ".":
        return

    quotes = ("'", '"')
    quote: str | None = None
    it = peekable(selector)
    parts = ""

    def _err(part: str, expected: str, but: str | None = None) -> NoReturn:
        but = but if but is not None else f"`{it.peek()}`"
        msg = f"Invalid selector part: `{part}`. Expected {expected} but got {but}."
        raise ValueError(msg)

    for character in it:
        if character == quote:
            # Don't allow something like `"ab"c.d`.
            if it.peek(...) not in (".", ...):
                quote = cast(str, quote)
                _err(quote + parts + quote + it.peek(), "`.` or end")
            quote = None
            # Short circuit. We know the next is a "."
            yield parts
            parts = ""
            next(it, ...)
        elif quote is None and character == ".":
            if it.peek(...) == ".":
                _err(parts + "..", "character or end")
            yield _verify_part(parts)
            parts = ""
        elif character in quotes and not quote:
            quote = character
        else:
            parts += character
    if quote:
        _err(quote + parts, expected=f"`{quote}`", but="end")
    if parts:
        yield _verify_part(parts)


# TODO: Add CLI tests to make sure error handling works properly for
# RWEnumChoice options when an invalid option is passed and also that different
# casings work properly.
if TYPE_CHECKING or CLICK_82:
    RWEnumChoice = click.Choice
else:

    class RWEnumChoice(click.Choice):  # pyright: ignore[reportMissingTypeArgument]
        # Based on https://github.com/pallets/click/pull/2210 and
        # https://github.com/pallets/click/issues/605
        # Copyright 2014 Pallets and Click contributors
        def __init__(
            self,
            enum_type: type[Enum],
            case_sensitive: bool = True,
            force_lowercase: bool = True,
        ):
            # Disable type argument errors for compat with older click
            super().__init__(  # pyright: ignore[reportUnknownMemberType]
                choices=[
                    element.name.lower() if force_lowercase else element.name
                    for element in enum_type
                ],
                case_sensitive=case_sensitive,
            )
            self.enum_type = enum_type
            self.force_lowercase: bool = force_lowercase

        def convert(
            self,
            value: Any,
            param: click.Parameter | None,  # noqa: ARG002
            ctx: click.Context | None,  # noqa: ARG002
        ) -> Any:
            value = super().convert(value=value, param=param, ctx=ctx)
            if value is None:
                return None
            return self.enum_type[value.upper() if self.force_lowercase else value]


@dataclass
class SharedArg:
    param: Any
    help: str | None = None  # noqa: A003

    def __call__(self, func: Callable[_P, _T]) -> Callable[_P, _T]:
        return self.param(func)


class TomcliError(Exception):
    """
    Base class for tomcli Exceptions that are caught automatically
    """


def _get_metavar(arg: click.Argument) -> str:
    metavar: str | None = None
    if arg.metavar is not None:
        metavar = arg.metavar
    else:
        metavar = cast(str, arg.name).upper()
    return metavar.removesuffix("...")


def add_args_and_help(
    *params: SharedArg | Any,
) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    def inner(func: Callable[_P, _T]) -> Callable[_P, _T]:
        helps: list[str] = []
        for param in reversed(params):
            param(func)
            arg = cast(click.Argument, func.__click_params__[-1])  # type: ignore[attr-defined]
            metavar = _get_metavar(arg)
            phelp = f"* {metavar}"
            if isinstance(param, SharedArg) and param.help:
                phelp += f": {param.help}"
            helps.append(phelp)
        helps.reverse()
        func.__doc__ = dedent(func.__doc__) + "\n\n" if func.__doc__ else ""
        func.__doc__ += "\n\n".join(helps)

        @wraps(func)
        def newfunc(*args: _P.args, **kwargs: _P.kwargs) -> _T:
            try:
                return func(*args, **kwargs)
            except TomcliError as exc:
                fatal(str(exc))

        return newfunc

    return inner


class PATTERN_TYPES(str, Enum):
    REGEX_FULLMATCH = "regex_fullmatch"
    REGEX = "regex"  # Same behavior as REGEX_FULLMATCH
    REGEX_PARTIAL = "regex_partial"
    REGEX_SEARCH = "regex_search"
    FNMATCH = "fnmatch"


SELECTOR_HELP = (
    "A dot separated map to a key in the TOML mapping."
    " Example: 'section1.subsection.value'"
)

_required_partial = partial(
    click.option,
    "--required / --not-required",
    default=False,
    help="Fail if no match for PATTERN is found",
)

SHARED_PARAMS = SimpleNamespace(
    writer=click.option("--writer", default=None, type=RWEnumChoice(Writer, False)),
    reader=click.option("--reader", default=None, type=RWEnumChoice(Reader, False)),
    path=SharedArg(
        click.argument("path"),
        help="Path to a TOML file to read. Use '-' to read from stdin."
        " Set to `...` when calling `--help` for a subcommand",
    ),
    selector=SharedArg(
        click.argument("selector"),
        help=SELECTOR_HELP,
    ),
    selectors=SharedArg(
        click.argument("selectors", metavar="SELECTOR...", nargs=-1, required=True),
        help=SELECTOR_HELP,
    ),
    formatter=click.option("-F", "--formatter", default=DEFAULT_FORMATTER),
    required=_required_partial(),
    required_partial=_required_partial,
    version=click.version_option(_ver, message="%(version)s"),
    pattern=SharedArg(
        click.argument("pattern"),
        help="Pattern against which to match strings",
    ),
    pattern_type=click.option(
        "-t",
        "--type",
        "pattern_type",
        default=PATTERN_TYPES.REGEX_FULLMATCH,
        type=RWEnumChoice(PATTERN_TYPES, False),
    ),
    repl=SharedArg(click.argument("repl"), help="Replacement string"),
)


__all__ = (
    "DEFAULT_CONTEXT_SETTINGS",
    "_std_cm",
    "fatal",
    "RWEnumChoice",
    "SharedArg",
    "add_args_and_help",
    "SELECTOR_HELP",
    "SHARED_PARAMS",
)
