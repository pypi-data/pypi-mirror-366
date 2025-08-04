import pytest
from wixok.txtfile import TXTFile
from pathlib import Path


def test_load_empty(tmp_path: Path):
    file = tmp_path / "empty.txt"
    assert TXTFile.load(file) == ""


def test_load_existing_file(tmp_path: Path):
    file = tmp_path / "test.txt"
    file.write_text("Hello\nWorld\n")
    assert TXTFile.load(file) == "Hello\nWorld\n"


def test_load_lines_empty(tmp_path: Path):
    file = tmp_path / "empty.txt"
    assert TXTFile.load_lines(file) == []


def test_load_lines_existing_file(tmp_path: Path):
    file = tmp_path / "test.txt"
    file.write_text("Line one\nLine two\nLine three\n")
    assert TXTFile.load_lines(file) == ["Line one", "Line two", "Line three"]


def test_add_line_and_load(tmp_path: Path):
    file = tmp_path / "data.txt"
    assert TXTFile.add_line(file, "Line one") is True
    assert TXTFile.add_line(file, "Line two") is True
    assert TXTFile.load(file) == "Line one\nLine two\n"
    assert TXTFile.load_lines(file) == ["Line one", "Line two"]


def test_add_line_to_existing_file(tmp_path: Path):
    file = tmp_path / "existing.txt"
    file.write_text("First line\n")
    assert TXTFile.add_line(file, "Second line") is True
    assert TXTFile.load_lines(file) == ["First line", "Second line"]


def test_clear_existing_file(tmp_path: Path):
    file = tmp_path / "to_clear.txt"
    file.write_text("foo\nbar\n")
    assert TXTFile.clear(file) is True
    assert TXTFile.load(file) == ""
    assert TXTFile.load_lines(file) == []


def test_clear_nonexistent_file(tmp_path: Path):
    file = tmp_path / "new.txt"
    assert TXTFile.clear(file) is True
    assert file.exists()
    assert TXTFile.load(file) == ""
    assert TXTFile.load_lines(file) == []


def test_load_with_unicode(tmp_path: Path):
    file = tmp_path / "unicode.txt"
    content = "Hello 世界\nEmoji: 🌍\n"
    file.write_text(content, encoding='utf-8')
    assert TXTFile.load(file) == content
    assert TXTFile.load_lines(file) == ["Hello 世界", "Emoji: 🌍"]


def test_add_line_with_unicode(tmp_path: Path):
    file = tmp_path / "unicode_add.txt"
    unicode_text = "Unicode: 你好 🚀"
    assert TXTFile.add_line(file, unicode_text) is True
    assert TXTFile.load_lines(file) == [unicode_text]


def test_file_permissions_error(tmp_path: Path):
    file = tmp_path / "readonly.txt"
    file.write_text("content")
    file.chmod(0o000)
    try:
        assert TXTFile.load(file) == ""
        assert TXTFile.load_lines(file) == []
        assert TXTFile.add_line(file, "new line") is False
        assert TXTFile.clear(file) is False
    finally:
        file.chmod(0o644)


def test_debug_mode(tmp_path: Path, capsys):
    file = tmp_path / "nonexistent.txt"
    original = TXTFile.debug
    TXTFile.debug = True
    try:
        TXTFile.load(file)
        captured = capsys.readouterr()
        assert "not found" in captured.out
        TXTFile.add_line(tmp_path / "debug_test.txt", "test")
        captured = capsys.readouterr()
        assert "added successfully" in captured.out
    finally:
        TXTFile.debug = original


def test_path_types(tmp_path: Path):
    file_path = tmp_path / "path_test.txt"
    assert TXTFile.add_line(file_path, "Path object") is True
    assert TXTFile.add_line(str(file_path), "String path") is True
    lines = TXTFile.load_lines(file_path)
    assert lines == ["Path object", "String path"]
    content = TXTFile.load(str(file_path))
    assert content == "Path object\nString path\n"
