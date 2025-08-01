"""This module contains Requirements class, which is the core of the current process."""
import os
import re
from enum import Enum
from typing import List, Tuple


class RequirementsFormat(str, Enum):
    pip_list = "pip_list"
    pip_freeze = "pip_freeze"


class Requirements:
    """
    A class that handles parsing and rendering requirements data.

    Attributes:
        None

    Methods:
        _read_file_contents: Read the contents of a file.
        _from_pip_freeze: Parse data in the pip freeze format.
        _from_pip_list: Parse data in the pip list format.
        render: Render the requirements data based on the specified format.
    """

    def _merge_multiple_requirements(self, source_path: str) -> set:
        requirements = set()
        paths = os.listdir(source_path)
        paths = [
            os.path.join(source_path, path) for path in paths if path.endswith(".txt")
        ]

        for file in paths:
            with open(file, "r") as src:
                requirements.update(src.read().splitlines())

        return requirements

    def _read_file_contents(self, source_path: str) -> str:
        """
        Read the contents of a file.

        Args:
            source_path: The path to the file to be read.

        Returns:
            The contents of the file as a string.
        """
        basepath = os.path.abspath(source_path)
        if os.path.isdir(basepath):
            return self._merge_multiple_requirements(basepath)
        with open(basepath, "r") as src:
            return src.read().splitlines()

    def _from_pip_freeze(self, data: str) -> List[Tuple[str, str]]:
        """
        Parse data in the pip freeze format.

        Args:
            data: The pip freeze formatted data to be parsed.

        Returns:
            A list of tuples containing package names and versions.
        """

        lines = [line for line in data if not line.startswith("#")]
        pattern = r"(==|<=|>=|<|>)"
        package_data = [re.split(pattern, line) for line in lines]
        return [
            (package[0], package[2]) if len(package) > 1 else package
            for package in package_data
        ]

    def _from_pip_list(self, data: str) -> List[Tuple[str, str]]:
        """
        Parse data in the pip list format.

        Args:
            data: The pip list formatted data to be parsed.

        Returns:
            A list of tuples containing package names and versions.
        """

        package_data = [tuple(line.split()) for line in data[2:]]
        return [(package[0], package[1]) for package in package_data]  # pylint

    def render(self, source_path: str, format: str) -> List[Tuple[str, str]]:
        """
        Render the requirements data based on the specified format.

        Args:
            source_path: The path to the requirements file.
            format: The format of the requirements file (e.g., "pip_freeze", "pip_list"). # noqa

        Returns:
            A list of tuples containing package names and versions.
        """
        data = self._read_file_contents(source_path)
        if format == "pip_freeze":
            return self._from_pip_freeze(data)
        if format == "pip_list":
            return self._from_pip_list(data)
