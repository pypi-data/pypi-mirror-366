from typing import List
from pathlib import Path
from typing import Optional
from typing import Union

ALLOWED_EXTENSIONS = [".txt", ".pdf"]


def validate_file_extension(filepath: Union[str, Path], allowed_extensions: List[str]):
    """
    Validates the file extension against a list of allowed extensions.

    :param filepath: The path to the file to be validated.
    :param allowed_extensions: A list of allowed file extensions.
    :raises ValueError: If the file extension is not in the allowed list.
    """
    filepath = Path(filepath) if isinstance(filepath, str) else filepath
    if not filepath.suffix:
        raise ValueError("File has no extension.")

    if not any(filepath.suffix == ext for ext in allowed_extensions):
        raise ValueError(
            f"Invalid file type. Allowed types are: {', '.join(allowed_extensions)}"
        )


def validate_filepath(filepath: Union[str, Path]):
    """
    Validates the file path to ensure it exists.

    :param filepath: The path to the file to be validated.
    :raises FileNotFoundError: If the file does not exist.
    """
    filepath = Path(filepath) if isinstance(filepath, str) else filepath
    validate_file_extension(filepath, ALLOWED_EXTENSIONS)
    if not filepath.exists():
        raise FileNotFoundError(f"The file {filepath} does not exist.")
