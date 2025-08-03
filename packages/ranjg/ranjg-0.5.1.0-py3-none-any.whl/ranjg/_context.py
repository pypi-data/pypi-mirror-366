from typing import Tuple, Union, Iterable


class GenerationContext:
    """Context of randomly construction.
    """
    _key_path: Tuple[Union[int, str]]
    _current_schema: dict

    @classmethod
    def root(cls, current_schema: dict):
        return GenerationContext(path=tuple(), current_schema=current_schema)

    def __init__(self, path: Iterable[Union[int, str]], current_schema: dict):
        self._key_path = tuple(path)
        self._current_schema = current_schema

    @property
    def key_path(self) -> Tuple[Union[int, str]]:
        return self._key_path

    def resolve(self, key: Union[int, str], current_schema: dict):
        return GenerationContext(path=(*self._key_path, key), current_schema=current_schema)


class SchemaContext:
    """Context of factory construction.
    """
    _key_path: Tuple[Union[int, str]]
    _current_schema: dict
    _is_for_options: bool = False

    @classmethod
    def root(cls, current_schema: dict):
        return SchemaContext(path=tuple(), current_schema=current_schema)

    @classmethod
    def for_options(cls, current_schema: dict, path: Iterable[Union[int, str]]):
        # Options 内のスキーマを使用する場合の context
        return SchemaContext(path=path, current_schema=current_schema, for_options=True)

    def __init__(self, path: Iterable[Union[int, str]], current_schema: dict, for_options: bool = False):
        self._key_path = tuple(path) if path is not None else None
        self._current_schema = current_schema
        self._is_for_options = for_options

    @property
    def key_path(self) -> Tuple[Union[int, str]]:
        return self._key_path

    def resolve(self, key: Union[int, str], current_schema: dict):
        return SchemaContext(path=(*self._key_path, key), current_schema=current_schema)
