from pathlib import Path

class TXTToolkit:
    """Utility class for basic text file operations: load, count, add, and clear."""

    debug = False

    @staticmethod
    def load(file_path: str | Path) -> list[str]:
        """
        Read all lines from a text file and return them as a list of stripped strings.

        :param file_path: Path to the file to read.
        :return: List of lines without trailing newlines or an empty list if an error occurs.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file]
        except FileNotFoundError:
            if TXTToolkit.debug:
                print(f"Error: File '{file_path}' not found.")
        except PermissionError:
            if TXTToolkit.debug:
                print(f"Error: Permission denied while reading file '{file_path}'.")
        except UnicodeDecodeError:
            if TXTToolkit.debug:
                print(f"Error: File '{file_path}' contains invalid or non-text characters.")
        except Exception as e:
            if TXTToolkit.debug:
                print(f"Unexpected error while reading file '{file_path}': {e}")
        return []

    @staticmethod
    def count(file_path: str | Path) -> int:
        """
        Count the number of non-empty lines in the file.

        :param file_path: Path to the file to inspect.
        :return: Number of lines in the file, or 0 if an error occurs.
        """
        try:
            return len(TXTToolkit.load(file_path))
        except Exception:
            return 0

    @staticmethod
    def add(file_path: str | Path, text: str) -> bool:
        """
        Append a line of text to the end of the file, adding a newline character.

        :param file_path: Path to the file to write to.
        :param text: Text to append to the file.
        :return: True if text was added successfully; False otherwise.
        """
        try:
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write(text + '\n')
            if TXTToolkit.debug:
                print(f"Text added successfully to '{file_path}'.")
            return True
        except FileNotFoundError:
            if TXTToolkit.debug:
                print(f"Error: File '{file_path}' not found.")
        except PermissionError:
            if TXTToolkit.debug:
                print(f"Error: Permission denied while writing to file '{file_path}'.")
        except IsADirectoryError:
            if TXTToolkit.debug:
                print(f"Error: '{file_path}' is a directory, not a file.")
        except Exception as e:
            if TXTToolkit.debug:
                print(f"Unexpected error while adding text to file '{file_path}': {e}")
        return False

    @staticmethod
    def clear(file_path: str | Path) -> bool:
        """
        Truncate the file to zero length, effectively clearing its contents.

        :param file_path: Path to the file to clear.
        :return: True if the file was cleared successfully; False otherwise.
        """
        try:
            with open(file_path, 'w', encoding='utf-8'):
                pass
            if TXTToolkit.debug:
                print(f"File '{file_path}' cleared successfully.")
            return True
        except FileNotFoundError:
            if TXTToolkit.debug:
                print(f"Error: File '{file_path}' not found.")
        except PermissionError:
            if TXTToolkit.debug:
                print(f"Error: Permission denied while clearing file '{file_path}'.")
        except IsADirectoryError:
            if TXTToolkit.debug:
                print(f"Error: '{file_path}' is a directory, not a file.")
        except Exception as e:
            if TXTToolkit.debug:
                print(f"Unexpected error while clearing file '{file_path}': {e}")
        return False