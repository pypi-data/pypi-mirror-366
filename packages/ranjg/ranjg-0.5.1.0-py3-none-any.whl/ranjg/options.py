import json
from functools import lru_cache
from typing import NamedTuple, Union

from .error import OptionsFileIOError


NO_COPY = 'NO_COPY'
SHALLOW_COPY = 'SHALLOW_COPY'
DEEP_COPY = 'DEEP_COPY'


class Options(NamedTuple):
    """Options of ``ranjg.gen``.

    See Also:
        :doc:`ranjg-options`:
            To know what options are used in each generation.
    """

    #: The maximum number of generation when multiple attempts are required to obtain a result that satisfies the
    #: schema.
    #: If it is None, regeneration is repeated until a result that matches the schema is obtained.
    #: If it is too small, there is a high probability that the generation will fail and raise an GenerateError.
    regeneration_attempt_limit: int = 50

    #: In bool generation, returns True with probability x, False with probability 1-x.
    default_prob_of_true_given_bool: Union[int, float] = 0.5

    #: In string generation, it is used as the difference between minLength and maxLength, if necessary.
    #: If only one of minLength and maxLength is specified, it is used to determine the other.
    default_length_range_of_genstr: int = 0

    #: In string generation, it is used as the value of minLength when both minLength and maxLength are not specified.
    default_min_length_of_string: int = 1

    #: In string generation, it is used as the value of maxLength when both minLength and maxLength are not specified.
    default_max_length_of_string: int = 10

    #: In dict generation, every optional property in the schema is contained in the result dict with a x probability
    #: independently
    default_prob_of_optional_properties: Union[int, float] = 0.5

    #: In dict generation, it is used to generate properties for which no schema is specified.
    #: For example, a property is required but its schema is not specified.
    default_schema_of_properties: dict = {"type": "null"}

    #: In dict generation, when a property whose name matches each key is generated, the corresponding value is used as
    #: the schema.
    priority_schema_of_properties: dict = {}

    #: In list generation, it is used to generate elements for which no schema is specified.
    #: For example, when `item` is specified as tuple format, and minLength is greater than its length.
    default_schema_of_items: dict = {"type": "null"}

    #: In generation from enum, it specifies how to generate an output value from elements in schema.enum.
    #: For example, if schema.enum contains objects of type list or dict as its content,
    #: and the result value is returned as it is,
    #: any change operation on the result value will change the way schema works.
    #:
    #: If it is options.NO_COPY, generated value has same id for one of element in schema.enum.
    #: If it is options.SHALLOW_COPY, generated value is shallow copy of one of element in schema.enum.
    #: If it is options.DEEP_COPY, generated value is deep copy of one of element in schema.enum.
    #: See the description of copy pickle for information on shallow copy and deep copy.
    enum_copy_style: str = DEEP_COPY

    @classmethod
    @lru_cache(maxsize=1)
    def default(cls):
        """Default options

        It is used when an user don't specify options.

        Returns:
            Options: Default options
        """
        return Options()


def __object_hook_on_load(d: dict) -> Union[Options, dict]:
    # Options を json.load メソッドでロードする際の object_hook として使用する

    # object_hook はルートオブジェクト以外にも使用されるため、たとえば d が
    # default_schema_of_properties に対応する dict である場合もある。
    # そのため、Options にできない場合はルートオブジェクトではないと判断して d をそのまま返す。
    try:
        return Options(**d)
    except TypeError:
        return d


def load(filepath: str) -> Options:
    """load an option file

    Raises:
        OptionsFileIOError:
            When loading file is failed
    """
    try:
        with open(filepath, mode='r') as f:
            # object_hook により、json.load の戻り値は Options にパース可能なら Options に、
            # そうでないなら dict になる。
            options: Union[Options, dict] = json.load(f, object_hook=__object_hook_on_load)
    except json.decoder.JSONDecodeError as e:
        raise OptionsFileIOError(f'This file cannot be parsed as options: {filepath}') from e

    if isinstance(options, Options):
        return options
    else:
        raise OptionsFileIOError(f'This file cannot be parsed as options: {filepath}')
