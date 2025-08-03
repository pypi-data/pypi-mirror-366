from typing import Union
from pathlib import Path
import yaml


def get_root_directory() -> Path:
    """
    Returns the root directory of the project.

    :return: Path object pointing to the root directory.
    """
    return Path(__file__).parent.parent


def read_yaml(filepath: Union[str, Path]) -> dict:
    """
    Reads a YAML file and returns its content as a dictionary.

    :param filepath: The path to the YAML file to be read.
    :return: A dictionary containing the content of the YAML file.
    """
    with open(filepath, "r") as file:
        return yaml.safe_load(file)


def read_template(template_name: str) -> str:
    """
    Reads a template file and returns its content.

    :param template_name: The name of the template file to be read.
    :return: The content of the template file.
    """
    root_dir = get_root_directory()
    templates_dir = root_dir / "configs" / "templates"
    template_path = templates_dir / f"{template_name}.txt"

    if not template_path.exists():
        raise FileNotFoundError(
            f"Template '{template_name}' not found in {templates_dir}."
        )

    file = read_file(template_path)
    return file


def read_file(filepath: Union[str, Path]) -> str:
    """
    Reads a file and returns its content.

    :param filepath: The path to the file to be read.
    :return: The content of the file.
    """

    with open(filepath, "r") as file:
        return file.read()
