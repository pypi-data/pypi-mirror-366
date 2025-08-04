from pathlib import Path
import shutil
import os

class Folder:
    """Utility class for basic folder operations."""

    debug = False

    @staticmethod
    def exists(path: str | Path) -> bool:
        """
        Check if the folder exists at the given path.
        """
        try:
            folder_path = Path(path)
            return folder_path.is_dir()
        except Exception as e:
            if Folder.debug:
                print(f"Error checking existence of '{path}': {type(e).__name__}: {e}")
            return False

    @staticmethod
    def create(path: str | Path, name: str = "") -> bool:
        """
        Create a folder at the given path, optionally with a subfolder name.
        """
        try:
            folder_path = Path(path) / name if name else Path(path)

            if folder_path.exists() and not folder_path.is_dir():
                if Folder.debug:
                    print(f"Cannot create folder '{folder_path}': Path exists and is not a directory.")
                return False

            folder_path.mkdir(parents=True, exist_ok=True)

            if Folder.debug:
                print(f"Folder '{folder_path}' created successfully.")
            return True
        except PermissionError:
            if Folder.debug:
                print(f"Permission denied: Cannot create folder '{folder_path}'.")
        except FileNotFoundError:
            if Folder.debug:
                print(f"Base path does not exist: '{path}'")
        except OSError as e:
            if Folder.debug:
                print(f"OSError while creating folder '{folder_path}': {type(e).__name__}: {e}")
        except Exception as e:
            if Folder.debug:
                print(f"Unexpected error creating folder '{folder_path}': {type(e).__name__}: {e}")
        return False

    @staticmethod
    def delete(path: str | Path) -> bool:
        """
        Recursively delete the folder at the given path, even if it's not empty.
        """
        folder_path = Path(path)
        try:
            if not folder_path.exists():
                if Folder.debug:
                    print(f"Cannot delete: Folder '{folder_path}' does not exist.")
                return False

            if not folder_path.is_dir():
                if Folder.debug:
                    print(f"Cannot delete: Path '{folder_path}' is not a directory.")
                return False

            shutil.rmtree(folder_path)

            if Folder.debug:
                print(f"Folder '{folder_path}' deleted successfully.")
            return True
        except PermissionError:
            if Folder.debug:
                print(f"Permission denied: Cannot delete folder '{folder_path}'.")
        except OSError as e:
            if Folder.debug:
                print(f"OSError: Could not delete folder '{folder_path}': {type(e).__name__}: {e}")
        except Exception as e:
            if Folder.debug:
                print(f"Unexpected error deleting folder '{folder_path}': {type(e).__name__}: {e}")
        return False

    @staticmethod
    def cwd() -> str:
        """
        Return the current working directory as a string.
        """
        try:
            cwd = os.getcwd()
            if Folder.debug:
                print(f"Current working directory: {cwd}")
            return cwd
        except Exception as e:
            if Folder.debug:
                print(f"Error retrieving current working directory: {type(e).__name__}: {e}")
            return ""
