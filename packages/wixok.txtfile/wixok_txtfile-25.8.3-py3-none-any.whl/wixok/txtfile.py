from pathlib import Path
import os

class TXTFile:
    """Utility class for basic text file operations."""

    debug = False

    @staticmethod
    def load(path: str | Path) -> str:
        """
        Read the entire content of a text file and return it as a string.

        :param path: Path to the file to read.
        :return: File content as string or an empty string if an error occurs.
        """
        file_path = Path(path)
        try:
            # Deny if write access is not permitted (treat read as blocked when no write permission)
            if file_path.exists() and not os.access(file_path, os.W_OK):
                raise PermissionError
            return file_path.read_text(encoding='utf-8')
        except FileNotFoundError:
            if TXTFile.debug:
                print(f"Error: File '{file_path}' not found.")
        except PermissionError:
            if TXTFile.debug:
                print(f"Error: Permission denied while reading file '{file_path}'.")
        except UnicodeDecodeError:
            if TXTFile.debug:
                print(f"Error: File '{file_path}' contains invalid or non-text characters.")
        except Exception as e:
            if TXTFile.debug:
                print(f"Unexpected error while loading file '{file_path}': {e}")
        return ""

    @staticmethod
    def load_lines(path: str | Path) -> list[str]:
        """
        Read all lines from a text file and return them as a list of stripped strings.

        :param path: Path to the file to read.
        :return: List of lines without trailing newlines or an empty list if an error occurs.
        """
        file_path = Path(path)
        try:
            # Deny if write access is not permitted
            if file_path.exists() and not os.access(file_path, os.W_OK):
                raise PermissionError
            with file_path.open('r', encoding='utf-8') as file:
                return [line.strip() for line in file]
        except FileNotFoundError:
            if TXTFile.debug:
                print(f"Error: File '{file_path}' not found.")
        except PermissionError:
            if TXTFile.debug:
                print(f"Error: Permission denied while reading file '{file_path}'.")
        except UnicodeDecodeError:
            if TXTFile.debug:
                print(f"Error: File '{file_path}' contains invalid or non-text characters.")
        except Exception as e:
            if TXTFile.debug:
                print(f"Unexpected error while reading file '{file_path}': {e}")
        return []

    @staticmethod
    def add_line(path: str | Path, text: str) -> bool:
        """
        Append a line of text to the end of the file, adding a newline character.

        :param path: Path to the file to write to.
        :param text: Text to append to the file.
        :return: True if text was added successfully; False otherwise.
        """
        file_path = Path(path)
        try:
            if file_path.exists() and not os.access(file_path, os.W_OK):
                raise PermissionError
            with file_path.open('a', encoding='utf-8') as file:
                file.write(text + '\n')
            if TXTFile.debug:
                print(f"Text added successfully to '{file_path}'.")
            return True
        except FileNotFoundError:
            if TXTFile.debug:
                print(f"Error: File '{file_path}' not found.")
        except PermissionError:
            if TXTFile.debug:
                print(f"Error: Permission denied while writing to file '{file_path}'.")
        except IsADirectoryError:
            if TXTFile.debug:
                print(f"Error: '{file_path}' is a directory, not a file.")
        except Exception as e:
            if TXTFile.debug:
                print(f"Unexpected error while adding text to file '{file_path}': {e}")
        return False

    @staticmethod
    def clear(path: str | Path) -> bool:
        """
        Truncate the file to zero length, effectively clearing its contents.

        :param path: Path to the file to clear.
        :return: True if the file was cleared successfully; False otherwise.
        """
        file_path = Path(path)
        try:
            if file_path.exists() and not os.access(file_path, os.W_OK):
                raise PermissionError
            with file_path.open('w', encoding='utf-8'):
                pass
            if TXTFile.debug:
                print(f"File '{file_path}' cleared successfully.")
            return True
        except FileNotFoundError:
            with file_path.open('w', encoding='utf-8'):
                pass
            if TXTFile.debug:
                print(f"File '{file_path}' created and cleared successfully.")
            return True
        except PermissionError:
            if TXTFile.debug:
                print(f"Error: Permission denied while clearing file '{file_path}'.")
        except IsADirectoryError:
            if TXTFile.debug:
                print(f"Error: '{file_path}' is a directory, not a file.")
        except Exception as e:
            if TXTFile.debug:
                print(f"Unexpected error while clearing file '{file_path}': {e}")
        return False