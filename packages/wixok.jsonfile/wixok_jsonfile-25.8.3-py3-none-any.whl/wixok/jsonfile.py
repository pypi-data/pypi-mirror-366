import json
from pathlib import Path
import os

class JSONFile:
    """Utility class for basic JSON file operations."""

    debug = False

    @staticmethod
    def load(path: str | Path) -> list:
        """
        Load and return the JSON content of a file as a list.
        - If the file contains a dict, wrap it in a list.
        - If the file contains a list, return it directly.
        Returns an empty list if the file is missing, unreadable, or invalid.

        :param path: Path to the JSON file.
        :return: List of dicts or items, or empty list on failure.
        """
        file_path = Path(path)
        try:
            if file_path.exists() and not os.access(file_path, os.W_OK):
                raise PermissionError
            with file_path.open('r', encoding='utf-8') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
                else:
                    if JSONFile.debug:
                        print(f"Error: JSON content in '{file_path}' is not a list or dict.")
        except FileNotFoundError:
            if JSONFile.debug:
                print(f"Error: File '{file_path}' not found.")
        except PermissionError:
            if JSONFile.debug:
                print(f"Error: Permission denied while reading file '{file_path}'.")
        except UnicodeDecodeError:
            if JSONFile.debug:
                print(f"Error: File '{file_path}' contains invalid or non-text characters.")
        except json.JSONDecodeError:
            if JSONFile.debug:
                print(f"Error: Invalid JSON format in file '{file_path}'.")
        except IsADirectoryError:
            if JSONFile.debug:
                print(f"Error: '{file_path}' is a directory, not a file.")
        except Exception as e:
            if JSONFile.debug:
                print(f"Unexpected error while loading file '{file_path}': {e}")
        return []

    @staticmethod
    def append(path: str | Path, new_data) -> bool:
        """
        Append data (list item or dictionary key-values) to an existing JSON file.

        :param path: Path to the JSON file.
        :param new_data: Data to append. Must be a list item or a dict.
        :return: True if successful, False otherwise.
        """
        file_path = Path(path)

        try:
            if file_path.exists() and not os.access(file_path, os.W_OK):
                raise PermissionError

            with file_path.open('r', encoding='utf-8') as file:
                existing_data = json.load(file)

            if isinstance(existing_data, list):
                if isinstance(new_data, list):
                    existing_data.extend(new_data)
                else:
                    existing_data.append(new_data)
            elif isinstance(existing_data, dict):
                if not isinstance(new_data, dict):
                    if JSONFile.debug:
                        print(f"Error: Cannot append non-dict data to a dict in '{file_path}'.")
                    return False
                existing_data.update(new_data)
            else:
                if JSONFile.debug:
                    print(f"Error: Unsupported JSON structure in file '{file_path}'.")
                return False

            with file_path.open('w', encoding='utf-8') as file:
                json.dump(existing_data, file, indent=4)
            return True

        except FileNotFoundError:
            if JSONFile.debug:
                print(f"Error: File '{file_path}' not found.")
        except PermissionError:
            if JSONFile.debug:
                print(f"Error: Permission denied while writing to file '{file_path}'.")
        except json.JSONDecodeError:
            if JSONFile.debug:
                print(f"Error: Invalid JSON format in file '{file_path}'.")
        except UnicodeDecodeError:
            if JSONFile.debug:
                print(f"Error: File '{file_path}' contains invalid characters.")
        except Exception as e:
            if JSONFile.debug:
                print(f"Unexpected error while appending to file '{file_path}': {e}")
        return False

    @staticmethod
    def save(path: str | Path, data) -> bool:
        """
        Save the given data (list or dict) to a JSON file, overwriting its contents.

        :param path: Path to the JSON file.
        :param data: Data to save (must be JSON serializable).
        :return: True if saved successfully, False otherwise.
        """
        file_path = Path(path)

        try:
            if file_path.exists() and not os.access(file_path, os.W_OK):
                raise PermissionError

            with file_path.open('w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)
            return True

        except PermissionError:
            if JSONFile.debug:
                print(f"Error: Permission denied while saving to file '{file_path}'.")
        except IsADirectoryError:
            if JSONFile.debug:
                print(f"Error: '{file_path}' is a directory, not a file.")
        except TypeError as e:
            if JSONFile.debug:
                print(f"Error: Data is not JSON serializable: {e}")
        except Exception as e:
            if JSONFile.debug:
                print(f"Unexpected error while saving file '{file_path}': {e}")
        return False
