import pytest
from txttoolkit import TXTToolkit
from pathlib import Path


def test_load_empty(tmp_path: Path):
    # Loading a non-existent (or empty) file should return an empty list
    file = tmp_path / "empty.txt"
    assert TXTToolkit.load(file) == []


def test_add_and_load(tmp_path: Path):
    # Adding lines creates the file and load returns them in order
    file = tmp_path / "data.txt"
    assert TXTToolkit.add(file, "Line one")
    assert TXTToolkit.add(file, "Line two")

    assert TXTToolkit.load(file) == ["Line one", "Line two"]


def test_count(tmp_path: Path):
    # Count counts non-empty lines
    file = tmp_path / "count.txt"
    # initially empty
    assert TXTToolkit.count(file) == 0

    TXTToolkit.add(file, "a")
    TXTToolkit.add(file, "b")
    # now two lines
    assert TXTToolkit.count(file) == 2


def test_clear(tmp_path: Path):
    # clear should truncate the file
    file = tmp_path / "to_clear.txt"
    # prepare file with content
    file.write_text("foo\nbar\n")
    # clear and verify
    assert TXTToolkit.clear(file) is True
    assert TXTToolkit.load(file) == []
    assert TXTToolkit.count(file) == 0


def test_clear_nonexistent(tmp_path: Path):
    # clearing a non-existent file still creates/truncates it
    file = tmp_path / "new.txt"
    # clear should succeed (creates empty file)
    assert TXTToolkit.clear(file) is True
    # file now exists and is empty
    assert file.exists() and file.read_text() == ""
    assert TXTToolkit.load(file) == []
    assert TXTToolkit.count(file) == 0