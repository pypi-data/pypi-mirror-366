# folder

Simple Python package for folder operations.

## Install

```bash
pip install wixok.folder
```

## Usage

```python
from wixok.folder import Folder

# Check if a folder exists
exists = Folder.exists("/tmp/myfolder")
print(exists)  # True

# Create a folder
success = Folder.create("/tmp", "myfolder")
print(success)  # True

# Delete the folder
deleted = Folder.delete("/tmp/myfolder")
print(deleted)  # True

# Get the current working directory
cwd = Folder.cwd()
print(cwd)  # e.g., '/home/user/project'
```

## Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `Folder.exists(path)` | Check if a folder exists and is a directory | `bool` |
| `Folder.create(path, name="")` | Create a folder at the given path (and optional subfolder name) | `bool` |
| `Folder.delete(path)` | Delete a folder at the given path | `bool` |
| `Folder.cwd()` | Get the current working directory path | `str` |

## Debug Mode

```python
folder.debug = True  # Enable error messages
```