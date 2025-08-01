# Copyright (C) 2023 Maxwell G <maxwell@gtmx.me>
#
# SPDX-License-Identifier: MIT
from __future__ import annotations

from pathlib import Path
from shutil import copy2

import pytest
from click.testing import CliRunner

from tomcli.cli.set import app
from tomcli.toml import load, loads

HERE = Path(__file__).resolve().parent
TEST_DATA = HERE / "test_data"
ROOT = HERE.parent


def test_set_del(reader: str, writer: str) -> None:
    path = str(TEST_DATA / "pyproject.toml")
    with open(path, "rb") as fp:
        data = load(fp)
    del data["build-system"]

    args = [
        "-o",
        "-",
        "--reader",
        reader,
        "--writer",
        writer,
        path,
        "del",
        "build-system",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0
    assert loads(ran.stdout) == data


def test_set_del_inplace(reader: str, writer: str, tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    copy2(TEST_DATA / "pyproject.toml", path)
    with open(path, "rb") as fp:
        data = load(fp)
    del data["project"]["name"]

    args = ["--reader", reader, "--writer", writer, str(path), "del", "project.name"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0
    with open(path, "rb") as fp:
        assert data == load(fp)


@pytest.mark.parametrize(
    "typ, expected",
    [
        pytest.param("str", {"data": "3.14"}),
        pytest.param("float", {"data": 3.14}),
        pytest.param("int", {"data": 3}),
        pytest.param("list", {"data": ["3.14"]}),
    ],
)
def test_set(rwargs, typ: str, expected):
    path = TEST_DATA / "test1.toml"
    with open(path, "rb") as fp:
        data = load(fp)
    data.update(expected)

    args = [*rwargs, "-o", "-", str(path), typ, "data", "3.14"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    print(ran.stdout)
    assert ran.exit_code == 0
    assert loads(ran.stdout) == data


def test_set_multilevel(reader: str, writer: str, tmp_path: Path):
    path = tmp_path / "pyproject.toml"
    copy2(TEST_DATA / "pyproject.toml", path)
    with open(path, "rb") as fp:
        data = load(fp)
    # Replace project.license string with dict
    data["project"]["license"] = {"text": "MIT"}

    for cmd in (("del", "project.license"), ("str", "project.license.text", "MIT")):
        args = ["--reader", reader, "--writer", writer, str(path), *cmd]
        ran = CliRunner().invoke(app, args, catch_exceptions=False)
        assert ran.exit_code == 0
    with open(path, "rb") as fp:
        assert data == load(fp)


def test_set_str_root(rwargs, tmp_path: Path):
    path = tmp_path / "pyproject.toml"
    copy2(TEST_DATA / "pyproject.toml", path)
    args = [*rwargs, str(path), "str", ".", "abc"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 1
    fun_msg = (
        "Your heart is in the right place,"
        " but we can't replace the whole file with a string\n"
    )
    assert ran.output == fun_msg


def test_set_append(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [*rwargs, str(path), "append", "lst.data", "456", "789"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["lst"]["data"].append("456")
    orig["lst"]["data"].append("789")
    assert loads(path.read_text()) == orig


def test_set_append_error(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    copy2(orig_path, path)

    args = [*rwargs, str(path), "append", "abc.data", "4"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 1
    assert ran.output == (
        "You can only append values to an existing list."
        " Use the 'list' subcommand to create a new list\n"
    )


def test_set_lists_replace_regex(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [*rwargs, str(path), "lists", "replace", "lst.data", r"\d", "xxxx"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["lst"]["data"] = ["xxxx", "xxxx", "abc", "456"]
    assert loads(path.read_text()) == orig


def test_set_lists_replace_regex_partial(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [
        *rwargs,
        str(path),
        "lists",
        "replace",
        "--type",
        "regex_partial",
        "lst.data",
        r"ab",
        "12",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["lst"]["data"][2] = "12c"  # "abc" -> "12c"
    assert loads(path.read_text()) == orig


def test_set_lists_replace_regex_search(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [
        *rwargs,
        str(path),
        "lists",
        "replace",
        "--type",
        "regex_search",
        "lst.data",
        r"bc",
        "23",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["lst"]["data"][2] = "a23"  # "abc" -> "a23"
    assert loads(path.read_text()) == orig


def test_set_lists_delitem_regex_search(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [
        *rwargs,
        str(path),
        "lists",
        "delitem",
        "--type",
        "regex_search",
        "lst.data",
        "bc",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["lst"]["data"].pop(2)  # "abc" -> removed
    assert loads(path.read_text()) == orig


def test_set_lists_replace_regex2(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [
        *rwargs,
        str(path),
        "lists",
        "replace",
        "--type=fnmatch",
        "mixed.data",
        "*",
        "xxxx",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["mixed"]["data"] = ["xxxx", 1, "xxxx", 2, "xxxx"]
    assert loads(path.read_text()) == orig


def test_set_lists_replace_regex_first(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [
        *rwargs,
        str(path),
        "lists",
        "replace",
        "--first",
        "lst.data",
        r"\d",
        "xxxx",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["lst"]["data"] = ["xxxx", "2", "abc", "456"]
    assert loads(path.read_text()) == orig


def test_lists_replace_error(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    copy2(orig_path, path)

    args = [*rwargs, str(path), "lists", "replace", "abc.data", "xxx", "xxx"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 1
    assert ran.output == "You cannot replace values unless the value is a list\n"


def test_set_lists_delitem_regex(rwargs, tmp_path: Path):
    orig_path = TEST_DATA / "test2.toml"
    path = tmp_path / "test2.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [*rwargs, str(path), "lists", "delitem", "lst.data", r"\d"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["lst"]["data"] = ["abc", "456"]
    assert loads(path.read_text()) == orig


@pytest.mark.parametrize(
    "cmd, boolean",
    [
        pytest.param("true", True, id="true"),
        pytest.param("false", False, id="false"),
    ],
)
def test_set_bool(rwargs, tmp_path: Path, cmd: str, boolean: bool):
    orig_path = TEST_DATA / "test1.toml"
    path = tmp_path / "test1.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [*rwargs, str(path), cmd, "bool_key"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    orig["bool_key"] = boolean
    assert loads(path.read_text()) == orig


def test_set_lists_delitem_key(rwargs, tmp_path: Path) -> None:
    orig_path = TEST_DATA / "test_9.toml"
    path = tmp_path / "test_9.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [*rwargs, str(path), "lists", "delitem", "--key=name", "test", "delete_.*"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    del orig["test"][0]
    assert loads(path.read_text()) == orig


def test_set_lists_delitem_key_required(rwargs, tmp_path: Path) -> None:
    orig_path = TEST_DATA / "test_9.toml"
    path = tmp_path / "test_9.toml"
    orig = loads(orig_path.read_text())
    copy2(orig_path, path)

    args = [
        *rwargs,
        str(path),
        "lists",
        "delitem",
        "--required",
        "--key=name",
        "test",
        "delete_.*",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0

    del orig["test"][0]
    assert loads(path.read_text()) == orig


def test_set_lists_lists_delitem_required(rwargs, tmp_path: Path) -> None:
    orig_path = TEST_DATA / "pyproject.toml"
    path = tmp_path / "pyproject.toml"
    orig_contents = orig_path.read_text()
    orig = loads(orig_contents)
    copy2(orig_path, path)

    args = [
        *rwargs,
        str(path),
        "lists",
        "delitem",
        "--required",
        "project.dependencies",
        "nothing",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=True)
    assert ran.exit_code == 1
    assert ran.output == "No match was found for PATTERN\n"
    assert path.read_text() == orig_contents

    args = [*rwargs, str(path), "lists", "delitem", "project.dependencies", "nothing"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0
    assert loads(path.read_text()) == orig


def test_replace(rwargs, tmp_path: Path) -> None:
    orig_path = TEST_DATA / "test1.toml"
    path = tmp_path / "test1.toml"
    orig_contents = orig_path.read_text()
    orig = loads(orig_contents)
    copy2(orig_path, path)

    args = [*rwargs, str(path), "replace", "abc.data", r"\d+", "x234"]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0
    changed = loads(path.read_text())
    orig["abc"]["data"] = "x234"
    assert changed == orig

    args = [
        *rwargs,
        str(path),
        "replace",
        "--not-required",
        "abc.data",
        r"does not match",
        "fjjfjf",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 0
    changed_contents = path.read_text()
    changed = loads(changed_contents)
    assert changed == orig

    args = [
        *rwargs,
        str(path),
        "replace",
        "abc.data",
        r"does not match",
        "fjjfjf",
    ]
    ran = CliRunner().invoke(app, args, catch_exceptions=False)
    assert ran.exit_code == 1
    print(ran)
    assert ran.output == "No match was found for PATTERN\n"
    assert path.read_text() == changed_contents
