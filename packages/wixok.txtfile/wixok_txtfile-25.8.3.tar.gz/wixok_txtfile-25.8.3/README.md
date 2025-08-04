# TXTFile

Simple Python package for text file operations.

## Install

```bash
pip install wixok.txtfile
```

## Usage

```python
from wixok.txtfile import TXTFile

# Read entire file content as a string
content = TXTFile.load("data.txt")
print(content)  # 'line 1\nline 2\nline 3\nline 4\n'

# Read file lines into a list
lines = TXTFile.load_lines("data.txt")
print(lines)  # ['line 1', 'line 2', 'line 3', 'line 4']

# Add a line to the file
success = TXTFile.add_line("data.txt", "line 5")
print(success)  # True

# Clear file contents
cleared = TXTFile.clear("data.txt")
print(cleared)  # True
```

## Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `load(path)` | Read entire file content as a single string | `str` |
| `load_lines(path)` | Read file lines into a list of strings | `list[str]` |
| `add_line(path, text)` | Append a line to the file (with newline) | `bool` |
| `clear(path)` | Empty the file | `bool` |

## Debug Mode

```python
TXTFile.debug = True  # Enable error messages
```