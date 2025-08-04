import pytest
from wixok.folder import Folder
from pathlib import Path

def test_exists_for_existing_directory(tmp_path: Path):
    folder_path = tmp_path / "check"
    folder_path.mkdir()
    assert Folder.exists(folder_path) is True

def test_exists_for_nonexistent_path(tmp_path: Path):
    folder_path = tmp_path / "missing"
    assert Folder.exists(folder_path) is False

def test_create_folder(tmp_path: Path):
    new_folder = tmp_path / "new"
    assert Folder.create(tmp_path, "new") is True
    assert new_folder.exists() and new_folder.is_dir()

def test_create_folder_path_is_file(tmp_path: Path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")
    assert Folder.create(file_path) is False

def test_create_nested_directories(tmp_path: Path):
    nested = tmp_path / "a" / "b" / "c"
    assert Folder.create(nested) is True
    assert nested.exists()

def test_delete_empty_folder(tmp_path: Path):
    folder_path = tmp_path / "to_delete"
    folder_path.mkdir()
    assert Folder.delete(folder_path) is True
    assert not folder_path.exists()

def test_delete_nonexistent_folder(tmp_path: Path):
    folder_path = tmp_path / "ghost"
    assert Folder.delete(folder_path) is False

def test_delete_non_directory(tmp_path: Path):
    file_path = tmp_path / "not_a_dir.txt"
    file_path.write_text("data")
    assert Folder.delete(file_path) is False

def test_delete_non_empty_folder(tmp_path: Path):
    folder_path = tmp_path / "filled"
    folder_path.mkdir()
    (folder_path / "file.txt").write_text("stuff")
    assert Folder.delete(folder_path) is True
    assert not folder_path.exists()

def test_cwd_returns_string():
    cwd = Folder.cwd()
    assert isinstance(cwd, str)
    assert Path(cwd).exists()