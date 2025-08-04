# TXTToolkit

Simple Python utility for text file operations.

## Install

```bash
pip install txttoolkit
```

## Usage

```python
from txt_toolkit import TXTToolkit

# Read file
lines = TXTToolkit.load("data.txt")
print(lines)  # ['line 1', 'line 2', 'line 3', 'line 4']

# Count lines
count = TXTToolkit.count("data.txt")
print(count)  # 4

# Add a line
add = TXTToolkit.add("data.txt", "line 4")
print(add)  # True

# Clear file
clear = TXTToolkit.clear("data.txt")
print(clear)  # True
```

## Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `load(path)` | Read file lines into list | `list[str]` |
| `count(path)` | Count non-empty lines | `int` |
| `add(path, text)` | Append line to file | `bool` |
| `clear(path)` | Empty the file | `bool` |

## Debug Mode

```python
TXTToolkit.debug = True  # Enable error messages
```

## License

MIT