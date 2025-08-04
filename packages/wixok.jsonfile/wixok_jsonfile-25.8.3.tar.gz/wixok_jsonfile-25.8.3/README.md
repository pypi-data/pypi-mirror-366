# JSONFile

Simple Python package for JSON file operations.

## Install

```bash
pip install wixok.jsonfile
```

## Usage

```python
from wixok.jsonfile import JSONFile

# Load JSON data
items = JSONFile.load("data.json")
print(items)  # [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}, ...]

# Append to existing file (list or dict)
success = JSONFile.append("data.json", {"id": 3, "name": "Charlie"})
print(success)  # True

# Save (overwrite) JSON data
saved = JSONFile.save("output.json", [{"a": 1}, {"b": 2}])
print(saved)  # True
```

## Methods

| Method               | Description                                                      | Returns        |
|----------------------|------------------------------------------------------------------|----------------|
| `load(path)`         | Load JSON content. Wraps dicts as `[dict]`, returns empty list on error. | `list`         |
| `append(path, data)` | Append a dict or list item to an existing JSON list/dict file.   | `bool`         |
| `save(path, data)`   | Overwrite file with JSON-serializable `data`.                    | `bool`         |

## Debug Mode

```python
JSONFile.debug = True  # Enable error messages
```