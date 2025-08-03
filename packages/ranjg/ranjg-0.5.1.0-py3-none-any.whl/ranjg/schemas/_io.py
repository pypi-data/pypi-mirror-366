import json

from ..error import SchemaFileIOError


def load(filepath: str) -> dict:
    """load a schema file

    Raises:
        SchemaFileIOError:
            When loading file is failed
    """
    try:
        with open(filepath) as fp:
            loaded_schema = json.load(fp)
    except json.decoder.JSONDecodeError as e:
        raise SchemaFileIOError(f'This file cannot be parsed as schema: {filepath}') from e

    return loaded_schema
