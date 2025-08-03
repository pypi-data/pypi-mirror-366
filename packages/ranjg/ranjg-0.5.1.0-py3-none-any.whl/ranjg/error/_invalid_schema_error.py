"""A module that provides InvalidSchemaError

A module that provides the schema error class ``InvalidSchemaError`` to __init__.
"""
import os
from typing import List, Iterable, Union, Iterator

from jsonschema import ValidationError


_INDENT_UNIT_LENGTH = 4


def __path_part_to_str(path_part: Union[str, int]) -> str:
    """Convert one JSON path parcel to a string.

    Args:
        path_part: A string or integer representing a JSON path compartment.

    Returns:
        A parcel of string representing a JSON path.
    """
    return f"[{path_part}]" \
        if isinstance(path_part, int) \
        else f"[\"{path_part}\"]"


def _path_to_str(path: Iterable[Union[str, int]]) -> str:
    """Convert a JSON path to string.

    Args:
        path: An Iterable representing a JSON path

    Returns:
        A string representing the JSON path
    """
    return "".join(map(__path_part_to_str, path))


class InvalidSchemaError(Exception):
    """Schema error class.

    This error raises if the schema is invalid.

    When the schema is valid but no value satisfy it (exp: ``schema.minimum > schema.maximum``), ``SchemaConflictError``
    is raised.
    """

    def __init__(self,
                 validation_error_list: List[ValidationError]):
        """Initialize InvalidSchemaError

        Args:
            validation_error_list:
                A list of validation errors that caused this error.
        """
        # (List[ValidationErrorWrapper]) A list of validation errors that caused this error.
        self.__cause_list = map(lambda e: ValidationErrorWrapper(e), validation_error_list)

        message_line_list = self._make_message_line_list()

        super().__init__(os.linesep + os.linesep.join(message_line_list))

    def _make_message_line_list(self) -> List[str]:
        """Create an error message

        Returns:
            A list consisting of lines of messages.
        """
        return sum(map(lambda c: c.make_message(), self.__cause_list), [])


class ValidationErrorWrapper:
    """Wrapper of the ``ValidationError`` Class
    """

    @property
    def base_error(self) -> ValidationError:
        """The ValidationError
        """
        return self.__base_error

    @property
    def context(self) -> Iterator:
        """The context of error.
        """
        return map(lambda e: ValidationErrorWrapper(e), self.base_error.context)

    def __init__(self, base_error: ValidationError):
        self.__base_error = base_error

    def make_message(self, indent: int = _INDENT_UNIT_LENGTH) -> List[str]:
        """Generates validation error messages.

        Args:
            indent: The number of spaces at the beginning of each line.

        Returns:
            A list consisting of lines of messages.
        """
        path_str = _path_to_str(self.base_error.absolute_path)
        context_line_list = self._make_message_of_context(indent)

        return [
                   f"{indent * ' '}On instance{path_str}:",
                   f"{(indent + _INDENT_UNIT_LENGTH) * ' '}{self.base_error.message}",
               ] + context_line_list

    def _make_message_of_context(self, indent: int):
        """Create error messages of error context.

        Create a message from all validation errors that caused this.

        Args:
            indent: The number of spaces at the beginning of each line.

        Returns:
            A list consisting of lines of messages.
        """

        def context_to_message_line(e: ValidationErrorWrapper):
            return e.make_message(indent + 2 * _INDENT_UNIT_LENGTH)

        return sum(map(context_to_message_line, self.context), [])
