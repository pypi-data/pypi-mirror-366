"""The package of factories.

A factory is constructed with a schema and generate values according to the schema.

Generating values according to the schema can also be accomplished using ``ranjg.gen``,
but each time ``ranjg.gen`` is run, a Factory is internally generated.
Therefore, if you want to generate values repeatedly with the same schema,
it is recommended to generate the Factory only once and use its method ``gen`` repeatedly.

Examples:
    The following code is most simple usage.

    >>> import ranjg
    >>> schema_dict = { 'type': 'string' }
    >>> factory = ranjg.Factory(schema_dict)    # -> A factory according to the schema
    >>> generated_1 = factory.gen()  # -> A value according to the schema
    >>> generated_2 = factory.gen()  # -> A value according to the schema (Almost certainly different than before.)
    >>> generated_3 = factory.gen()  # It can be generated as many times as you want.

    ``factory.gen`` can receive a keyword argument ``options``.
    See also :doc:`ranjg-options` to know about options.
"""
import abc
import collections.abc as collections
import copy
import math
import random
import re
import string
import sys
from typing import TypeVar, Generic, Optional, Union, Iterable, Tuple, Sequence, Dict, Any, List, Type

try:
    from typing import GenericMeta  # python 3.6
except ImportError:
    # in 3.7, GenericMeta doesn't exist but we don't need it
    class GenericMeta(type):
        pass

import jsonschema
import rstr

import ranjg
from . import schemas
from ._number_range import NumberRange
from .error import SchemaConflictError, GenerateError, GenerateConflictError
from .schemas.normalize import normalize_exclusive_maximum, normalize_exclusive_minimum
from .options import Options
from ._context import GenerationContext, SchemaContext
from .util.listutil import fix_length

_T = TypeVar('_T')


class MetaFactory(GenericMeta, abc.ABCMeta):
    def __call__(cls: Type['Factory'], *args, **kwargs):
        obj: Factory = cls.__new__(cls, *args, **kwargs)

        # サブクラスの __init__ で使用しない引数を削除
        if "gen_type" in kwargs:
            del kwargs["gen_type"]

        obj.__init__(*args, **kwargs)
        return obj


class Factory(abc.ABC, Generic[_T], metaclass=MetaFactory):
    """Returns a Factory instance according to the schema.

    Args:
        schema (dict, optional):
            JSON schema object. See also :doc:`ranjg-json-schema`.
        schema_is_validated (bool, optional):
            Whether the schema is already validated or not.
            (In normal usage, this argument is not specified.)
        context (SchemaContext, optional):
            The context of factory construction.
            (In normal usage, this argument is not specified.)
        gen_type (str, optional):
            If specified, ignore ``schema.type`` and create a factory that generates values of the specified type.
            (In normal usage, this argument is not specified.)
    Returns:
        A factory to generate values according the schema.

    Raises:
        SchemaConflictError:
            When the schema specified as arguments has conflict.
            In other words, when no value can satisfy the schema.
    """
    _schema: dict
    #: True であれば、_schema 全体が (子要素のスキーマも含め) validated。
    _schema_is_validated: bool = False

    def __new__(cls, schema: Optional[dict], *,
                schema_is_validated: bool = False,
                context: Optional[SchemaContext] = None,
                gen_type: Union[str, None] = None):
        if schema is None:
            schema = {}

        # 実際に生成されるインスタンスの型を決定
        if cls is Factory:
            cls = cls._decide_concrete(gen_type, schema.get('type'), schema.get('enum'))

        return object.__new__(cls)

    def __init__(self, schema: Optional[dict], *,
                 schema_is_validated: bool = False,
                 context: Optional[SchemaContext] = None,
                 gen_type: Union[str, None] = None):
        self._schema = schema if schema is not None else {}
        self._schema_is_validated = schema_is_validated

        self.validate_schema()

    @classmethod
    def _decide_concrete(cls,
                         gen_type: Union[str, Iterable[str], None],
                         schema_type: Union[str, Iterable[str], None],
                         schema_enum: Union[Iterable, None]) -> Type['Factory']:
        if gen_type is None:
            if schema_enum is not None:
                return EnumFactory

            gen_type = schema_type

        if isinstance(gen_type, str):
            if gen_type in _FACTORY_MAP:
                return _FACTORY_MAP[gen_type]
            else:
                raise ValueError(f"Unsupported type: {gen_type}")
        elif isinstance(gen_type, Iterable):
            return MultiFactory
        elif gen_type is None:
            # TODO: NoneFactory 固定でよいか要検討
            return NoneFactory
        else:
            raise ValueError(f"Unsupported type: {gen_type}")

    @abc.abstractmethod
    def gen(self,
            *,
            options: Optional[Options] = None,
            context: Optional[GenerationContext] = None) -> _T:
        """Generate value according to the schema specified for the factory construction.

        Args:
            options (Options, optional):
                The options for generation.
            context (GenerationContext, optional):
                The context of generation.
                (In normal usage, this argument is not specified. This argument is for using this function recursively.)

        Returns:
            Generated something.

        Raises:
            GenerateError:
                If an unforeseen error arises.
        """

    @property
    def schema_is_validated(self) -> bool:
        return self._schema_is_validated

    def validate_schema(self) -> None:
        """validate schema

        It determines if the schema is free of irregularities.

        Raises:
            InvalidSchemaError:
                When the schema is invalid
        """
        if not self._schema_is_validated:
            schemas.validate(self._schema)
            self._schema_is_validated = True

    def gen_as_child(self, *,
                     # 入力漏れを防ぐため、引数にデフォルト値は設定しない。
                     options: Options,
                     parent_context: GenerationContext,
                     child_key: Union[str, int]) -> _T:
        """Generate value as another dict or list.

        It is wrapper of ``Factory#gen`` for ranjg development since it is called in ``ListFactory#gen`` etc..
        Normally, **there is no need for users of ranjg to use this method**.

        This method is provided for the purpose of not creating bugs in child element generation.
        As part of this, to prevent omission of argument specification, no default argument is provided.

        In order to fulfill the purpose of this method's existence, this method should be used when creating child
        elements in ranjg.

        Args:
            options (Options):
                The options for generation.
                Usually, the options used to generate the parent element is specified as is.
            parent_context (GenerationContext):
                The context of construction.
                Usually, the context used to generate the parent element is specified as is.
            child_key (str|int):
                The path to the generated element from the parent element.
                If the parent element is a dict, it is a string; if it is a list, it is an integer.

        Returns:
            Generated something.
        """
        return self.gen(options=options,
                        context=parent_context.resolve(child_key, self._schema))


class NoneFactory(Factory[None]):

    def __init__(self, schema: Optional[dict], *,
                 schema_is_validated: bool = False, context: Optional[SchemaContext] = None):
        super(NoneFactory, self).__init__(schema, schema_is_validated=schema_is_validated, context=context)

    def gen(self,
            *,
            options: Optional[Options] = None,
            context: Optional[GenerationContext] = None) -> None:
        return None


class BoolFactory(Factory[bool]):

    def __init__(self, schema: Optional[dict], *,
                 schema_is_validated: bool = False, context: Optional[SchemaContext] = None):
        super(BoolFactory, self).__init__(schema, schema_is_validated=schema_is_validated, context=context)

    def gen(self,
            *,
            options: Optional[Options] = None,
            context: Optional[GenerationContext] = None) -> bool:
        if options is None:
            options = Options.default()

        return random.random() < options.default_prob_of_true_given_bool


class IntFactory(Factory[int]):
    _schema_minimum: Optional[int]
    _schema_maximum: Optional[int]

    def __init__(self, schema: Optional[dict], *,
                 schema_is_validated: bool = False, context: Optional[SchemaContext] = None):
        super(IntFactory, self).__init__(schema, schema_is_validated=schema_is_validated, context=context)

        if context is None:
            context = SchemaContext.root(self._schema)

        # Convert float or exclusive value in schema to integer inclusive value.
        self._schema_minimum = _get_inclusive_integer_minimum(self._schema)
        self._schema_maximum = _get_inclusive_integer_maximum(self._schema)

        if self._schema_minimum is not None and self._schema_maximum is not None and \
                self._schema_minimum > self._schema_maximum:
            raise SchemaConflictError("There are no integers in the range specified by the schema.", context)

    def gen(self,
            *,
            options: Optional[Options] = None,
            context: Optional[GenerationContext] = None) -> int:

        minimum, maximum = _apply_default_int(self._schema_minimum, self._schema_maximum)
        return random.randint(minimum, maximum)


def _get_inclusive_integer_minimum(schema: dict) -> Optional[int]:
    """Returns minimum as integer and not exclusive.

    To make it easier to use for randomly generation, convert float or exclusive minimum in schema to integer inclusive
    value.

    Args:
        schema: JSON schema for randomly generation.

    Returns:
        Inclusive minimum.
    """
    # exclusiveMinimum が真理値である場合、Draft7スタイルに変更
    inclusive_minimum, exclusive_minimum = normalize_exclusive_minimum(schema)

    minimum = None
    if inclusive_minimum is not None and exclusive_minimum is not None:
        minimum = max(__to_int_minimum(inclusive_minimum, False), __to_int_minimum(exclusive_minimum, True))
    elif exclusive_minimum is not None:
        minimum = __to_int_minimum(exclusive_minimum, True)
    elif inclusive_minimum is not None:
        minimum = __to_int_minimum(inclusive_minimum, False)

    return minimum


def _get_inclusive_integer_maximum(schema: dict) -> Optional[int]:
    """Returns maximum as integer and not exclusive.

    To make it easier to use for randomly generation, convert float or exclusive maximum in schema to integer inclusive
    value.

    Args:
        schema: JSON schema for randomly generation.

    Returns:
        Inclusive maximum.
    """
    # exclusiveMaximum が真理値である場合、Draft7スタイルに変更
    inclusive_maximum, exclusive_maximum = normalize_exclusive_maximum(schema)

    maximum = None
    if inclusive_maximum is not None and exclusive_maximum is not None:
        maximum = min(__to_int_maximum(inclusive_maximum, False), __to_int_maximum(exclusive_maximum, True))
    elif exclusive_maximum is not None:
        maximum = __to_int_maximum(exclusive_maximum, True)
    elif inclusive_maximum is not None:
        maximum = __to_int_maximum(inclusive_maximum, False)

    return maximum


def _apply_default_int(minimum: Optional[int], maximum: Optional[int]) -> Tuple[int, int]:
    """Apply default minimum and maximum.

    Args:
        minimum: None or minimum value of integer to generate
        maximum: None or maximum value of integer to generate

    Returns:
        A pair of minimum and maximum. They are not None.
    """
    if minimum is None and maximum is None:
        minimum = 0
        maximum = 100
    elif minimum is None:
        minimum = maximum - 5
    elif maximum is None:
        maximum = minimum + 5

    return minimum, maximum


def __to_int_minimum(minimum: Union[float, int], exclusive: bool) -> int:
    """Converts the minimum value by float type to int type.

    As long as the return value is used as the minimum of integer value, it works the same way as if the argument is
    used.

    Args:
        minimum: The minimum value
        exclusive: Whether to exclude the endpoints

    Returns:
        The minimum value by integer type
    """
    if exclusive:
        return math.floor(minimum) + 1
    else:
        return math.ceil(minimum)


def __to_int_maximum(maximum: Union[float, int], exclusive: bool) -> int:
    """Converts the maximum value by float type to int type.

    As long as the return value is used as the maximum of integer value, it works the same way as if the argument is
    used.

    Args:
        maximum: The maximum value
        exclusive: Whether to exclude the endpoints

    Returns:
        The maximum value by integer type
    """
    if exclusive:
        return math.ceil(maximum) - 1
    else:
        return math.floor(maximum)


__default_number_schema = {
    "minimum": -sys.float_info.max / 2,
    "exclusiveMinimum": float('-inf'),
    "maximum": sys.float_info.max / 2,
    "exclusiveMaximum": float('inf'),
}


def __validate(value: float, schema: dict) -> bool:
    """Check if the value matches the schema.

    This function is only used to filter out illegal values in the float generation process, so it doesn't check every
    item in the schema. If you want to validate a value, it is recommended to use ``jsonschema`` module.

    Args:
        value: Value to be checked.
        schema: Normalized JsonSchema.

    Returns:
        True if it conforms to the scheme, otherwise False.
    """

    if value is None:
        return False

    return schema["exclusiveMinimum"] < value < schema["exclusiveMaximum"] and \
           schema["minimum"] <= value <= schema["maximum"]


def _apply_default(number_range: NumberRange) -> NumberRange:
    """Apply default range.

    Args:
        number_range: A range.

    Returns:
        A range with minimum and maximum. They are not None.
    """
    if number_range.minimum is None:
        if number_range.maximum is None:
            return NumberRange(minimum=0.0,
                               maximum=1.0,
                               exclusive_minimum=False,
                               exclusive_maximum=True)
        else:
            return number_range.replace(minimum=_little_less(number_range.maximum), exclusive_minimum=False)
    else:
        if number_range.maximum is None:
            return number_range.replace(maximum=_little_greater(number_range.minimum), exclusive_maximum=True)
        else:
            return number_range


def _check_consistency(number_range: NumberRange, context: SchemaContext):
    """Check the instance in consistency

    Attributes:
        number_range:
            Subject of the examination.

    Raises:
        SchemaConflictError:
            If number_range has consistency.
    """
    # 矛盾が発生するのは、最大と最小の両方が定義されている場合のみ
    if number_range.minimum is None or number_range.maximum is None:
        return

    if number_range.minimum > number_range.maximum:
        if number_range.exclusive_minimum is False and number_range.exclusive_maximum is False:
            raise SchemaConflictError("Minimum value must be lower than or equal to the maximum value.", context)
        if number_range.exclusive_minimum is True and number_range.exclusive_maximum is False:
            raise SchemaConflictError("ExclusiveMinimum value must be lower than the maximum value.", context)
        if number_range.exclusive_minimum is False and number_range.exclusive_maximum is True:
            raise SchemaConflictError("Minimum value must be lower than the exclusiveMaximum value.", context)
        if number_range.exclusive_minimum is True and number_range.exclusive_maximum is True:
            raise SchemaConflictError("ExclusiveMinimum value must be lower than the exclusiveMaximum value.", context)
    elif number_range.minimum == number_range.maximum:
        if number_range.exclusive_minimum is True and number_range.exclusive_maximum is False:
            raise SchemaConflictError("ExclusiveMinimum value must be lower than the maximum value.", context)
        if number_range.exclusive_minimum is False and number_range.exclusive_maximum is True:
            raise SchemaConflictError("Minimum value must be lower than the exclusiveMaximum value.", context)
        if number_range.exclusive_minimum is True and number_range.exclusive_maximum is True:
            raise SchemaConflictError("ExclusiveMinimum value must be lower than the exclusiveMaximum value.", context)


def _little_greater(number: float) -> float:
    """Return a number greater than the argument.

    Args:
        number: A number.

    Returns:
        A number greater than the argument.
    """
    if number > 0:
        return number * sys.float_info.radix
    elif number < 0:
        return number / sys.float_info.radix
    else:
        return 1.0


def _little_less(number: float) -> float:
    """Return a number less than the argument.

    Args:
        number: A number.

    Returns:
        A number less than the argument.
    """
    if number > 0:
        return number / sys.float_info.radix
    elif number < 0:
        return number * sys.float_info.radix
    else:
        return -1.0


class NumFactory(Factory[float]):
    _number_range: NumberRange

    def __init__(self, schema: Optional[dict], *,
                 schema_is_validated: bool = False, context: Optional[SchemaContext] = None):
        super(NumFactory, self).__init__(schema, schema_is_validated=schema_is_validated, context=context)

        if context is None:
            context = SchemaContext.root(self._schema)

        # 生成する数値の範囲
        number_range = NumberRange.from_schema(self._schema)
        _check_consistency(number_range, context)
        self._number_range = _apply_default(number_range)

    def gen(self,
            *,
            options: Optional[Options] = None,
            context: Optional[GenerationContext] = None) -> float:
        if options is None:
            options = Options.default()
        if context is None:
            context = GenerationContext.root(self._schema)

        # 境界値を許容しない Schema であっても、境界値を含む乱数生成を行うため、
        # Schema に合致する値を引くまで生成を繰り返す。
        for i in range(options.regeneration_attempt_limit):
            generated = random.uniform(self._number_range.minimum, self._number_range.maximum)

            if generated == float("inf") or generated == float("-inf") or generated == float("NaN"):
                raise GenerateError("Error by too large or too small maximum or minimum", context)

            if generated in self._number_range:
                break
        else:
            raise GenerateError("No valid value generated on loop.", context)

        return generated


def _normalize_schema(schema: dict, options: Options, context: GenerationContext) -> dict:
    """Schema normalization.

    To make it easier to use for randomly generation, set items to ``schema`` object.

    Args:
        schema: JSON schema for randomly generation.

    Returns:
        New schema based on ``schema`` and the default values.
    """
    n_schema = schema.copy()
    n_schema.setdefault("pattern", None)

    # minLength と maxLength がともに指定されていない場合、デフォルト設定を使う
    if "minLength" not in n_schema and "maxLength" not in n_schema:
        n_schema["minLength"] = max(0, options.default_min_length_of_string)
        n_schema["maxLength"] = options.default_max_length_of_string

        if n_schema["minLength"] > n_schema["maxLength"]:
            raise GenerateConflictError("\"options.default_min_length_of_string\" must be lower than or equal to the "
                                        "\"options.default_max_length_of_string\" value.", context)
    # minLength が設定されていて maxLength が指定されていない場合
    elif "maxLength" not in n_schema:
        length_range = max(0, options.default_length_range_of_genstr)
        n_schema["maxLength"] = n_schema["minLength"] + length_range
    # maxLength が設定されていて minLength が指定されていない場合
    elif "minLength" not in n_schema:
        length_range = max(0, options.default_length_range_of_genstr)
        n_schema["minLength"] = max(0, n_schema["maxLength"] - length_range)

    return n_schema


class StrFactory(Factory[str]):
    _schema: dict

    def __init__(self, schema: Optional[dict], *,
                 schema_is_validated: bool = False, context: Optional[SchemaContext] = None):
        super(StrFactory, self).__init__(schema, schema_is_validated=schema_is_validated, context=context)

        if context is None:
            context = SchemaContext.root(self._schema)

        if self._schema.get("minLength", float("-inf")) > self._schema.get("maxLength", float("inf")):
            raise SchemaConflictError("\"minLength\" must be lower than or equal to the \"maxLength\" value.", context)

    def gen(self,
            *,
            options: Optional[Options] = None,
            context: Optional[GenerationContext] = None) -> str:
        if options is None:
            options = Options.default()
        if context is None:
            context = GenerationContext.root(self._schema)

        schema = _normalize_schema(self._schema, options, context)

        pattern = re.compile(schema["pattern"]) if schema["pattern"] is not None else None
        min_length = schema["minLength"]
        max_length = schema["maxLength"]

        # pattern の指定がある場合、それを使用する
        if pattern is not None:
            generated = rstr.xeger(pattern)
        # maxLength が 0 の場合、空文字でよい
        elif max_length is not None and max_length <= 0:
            generated = ""
        # いずれにも当てはまらない場合、英字列を生成する。
        else:
            generated = rstr.rstr(string.ascii_letters, start_range=min_length, end_range=max_length)

        return generated


def _schema_is_tuple_validation(schema: dict) -> bool:
    """Determines if the schema is for a tuple validation or not.

    Args:
        schema: JSON schema object for list values.

    Returns:
        True if the schema is for a tuple validation, otherwise False.
    """

    items = schema.get("items")
    return isinstance(items, collections.Sequence)


def _get_range_of_length(schema: dict, context: SchemaContext) -> Tuple[Optional[int], Optional[int]]:
    """Determine the range of the size of the list to be generated with the schema.

    If each of them are not specified in the schema, returns None. This function checks for inconsistencies in the
    schema. If it doesn't raise Error, there are no inconsistencies in the schema.

    Args:
        schema: JSON schema object for list values.

    Returns:
        The minimum and maximum size of the list to be generated. Not specified parameter will be None.

    Raises:
        SchemaConflictError: If there are inconsistencies in the schema.
    """

    min_items: int = schema.get("minItems")
    max_items: int = schema.get("maxItems")

    if min_items is not None and max_items is not None and min_items > max_items:
        raise SchemaConflictError("There are no integers in the range of length specified by the schema.", context)

    # schema がタプル指定である場合
    if _schema_is_tuple_validation(schema):
        items = list(schema.get("items"))
        additional_items = schema.get("additionalItems")

        if additional_items is False:
            if min_items is not None and len(items) < min_items:
                raise SchemaConflictError(
                    "In tuple validation, when \"additionalItems\" is false, \"minItems\" must be less than or equal "
                    "to size of \"items\".", context)
            elif max_items is not None:
                return min_items, min(max_items, len(items))
            else:
                return min_items, len(items)

        else:
            return min_items, max_items

    # schema がリスト指定である場合
    else:
        return min_items, max_items


def _apply_default_length(min_items: Optional[int], max_items: Optional[int]) -> Tuple[int, int]:
    """Apply default minItems and maxItems.

    Args:
        min_items: None or minimum length of the list to generate
        max_items: None or maximum length of the list to generate

    Returns:
        The minimum and maximum size of the list to be generated.
    """
    if min_items is None:
        if max_items is None:
            min_items = 1
        else:
            min_items = min(1, max_items)

    if max_items is None:
        if min_items is None:
            max_items = 5
        else:
            max_items = max(5, min_items)

    return min_items, max_items


class ListFactory(Factory[list]):
    _tuple_items_factory: Sequence[Factory]
    _other_items_factory: Optional[Factory]

    def __init__(self, schema: Optional[dict], *,
                 schema_is_validated: bool = False, context: Optional[SchemaContext] = None):
        super(ListFactory, self).__init__(schema, schema_is_validated=schema_is_validated, context=context)

        if context is None:
            context = SchemaContext.root(self._schema)

        # 生成する list の大きさの範囲
        min_items, max_items = _get_range_of_length(self._schema, context)
        self._min_items, self._max_items = _apply_default_length(min_items, max_items)

        if _schema_is_tuple_validation(self._schema):
            self._tuple_items_factory = [Factory(item_schema,
                                                 schema_is_validated=self.schema_is_validated,
                                                 context=context.resolve(i, item_schema))
                                         for i, item_schema in enumerate(self._schema["items"])]
            additional_items_schema: Union[bool, dict, None] = self._schema.get("additionalItems")
            if additional_items_schema is not None and not isinstance(additional_items_schema, bool):
                self._other_items_factory = \
                    Factory(additional_items_schema,
                            schema_is_validated=self.schema_is_validated,
                            # TODO: additionalItems 用のパスを検討
                            context=context.resolve('additionalItems', additional_items_schema))
            else:
                self._other_items_factory = None
        else:
            self._tuple_items_factory = tuple()
            items_schema = self._schema.get("items")
            if items_schema is not None:
                self._other_items_factory = Factory(items_schema,
                                                    schema_is_validated=self.schema_is_validated,
                                                    # TODO: items 用のパスを検討
                                                    context=context.resolve('items', items_schema))
            else:
                self._other_items_factory = None

    def _get_other_items_factory(self, options: Options) -> Factory:
        if self._other_items_factory is not None:
            return self._other_items_factory
        else:
            schema = options.default_schema_of_items
            return Factory(schema,
                           context=SchemaContext.for_options(schema, path=('default_schema_of_items',)))

    def _get_items_factory_list(self, item_count: int, options: Options) -> Iterable[Factory]:
        return fix_length(self._tuple_items_factory, item_count,
                          padding_item=self._get_other_items_factory(options))

    def gen(self,
            *,
            options: Optional[Options] = None,
            context: Optional[GenerationContext] = None) -> list:
        if options is None:
            options = Options.default()
        if context is None:
            context = GenerationContext.root(self._schema)

        # 生成する list の大きさ
        item_count = random.randint(self._min_items, self._max_items)

        # 生成するリスト
        result = [None] * item_count

        # 各要素のファクトリ
        item_factory_list = self._get_items_factory_list(item_count, options)

        # 要素を1つずつ生成
        for key, item_factory in enumerate(item_factory_list):
            result[key] = item_factory.gen_as_child(options=options,
                                                    parent_context=context,
                                                    child_key=key)

        return result


class DictFactory(Factory[dict]):
    _property_factories: Dict[str, Factory]
    _required_keys: Iterable[str]
    _properties: Dict[str, dict]

    def __init__(self, schema: Optional[dict], *,
                 schema_is_validated: bool = False, context: Optional[SchemaContext] = None):
        super(DictFactory, self).__init__(schema, schema_is_validated=schema_is_validated, context=context)

        if context is None:
            context = SchemaContext.root(self._schema)

        self._property_factories = {prop: Factory(prop_schema,
                                                  schema_is_validated=self.schema_is_validated,
                                                  context=context.resolve(prop, prop_schema))
                                    for prop, prop_schema in self._schema.get("properties", {}).items()}

        self._required_keys = self._schema.get("required", tuple())
        self._properties = self._schema.get("properties", dict())

    def _get_properties_factory(self, property_name: str) -> Factory:
        return self._property_factories[property_name]

    def _factory_of(self, key: str,
                    *,
                    options: Options) -> Factory:
        if key in options.priority_schema_of_properties:
            schema = options.priority_schema_of_properties[key]
            return Factory(schema,
                           context=SchemaContext.for_options(
                               schema, path=('priority_schema_of_properties', key)))
        elif key in self._property_factories:
            return self._property_factories[key]
        else:
            schema = options.default_schema_of_properties
            return Factory(schema,
                           context=SchemaContext.for_options(
                               schema, path=('default_schema_of_properties',)))

    def gen(self,
            *,
            options: Optional[Options] = None,
            context: Optional[GenerationContext] = None) -> dict:
        if options is None:
            options = Options.default()
        if context is None:
            context = GenerationContext.root(self._schema)

        generated: Dict[str, Any] = dict()

        # すでに生成or棄却が済んだキー
        # それぞれのキーは生成された場合は True, 棄却された場合は False を値に持つ。
        generated_keys: Dict[str, bool] = dict()

        # 必須項目を生成する
        for required_key in self._required_keys:
            # すでに生成済みの項目は生成しない。ただし、棄却済みであるものは生成する。
            if generated_keys.get(required_key) is True:
                continue

            next_factory = self._factory_of(required_key, options=options)
            generated[required_key] = next_factory.gen_as_child(options=options,
                                                                parent_context=context,
                                                                child_key=required_key)
            generated_keys[required_key] = True

        # 必須でない項目を生成する
        for prop_key in self._properties.keys():
            # すでに生成or棄却済みの項目は生成しない。
            if generated_keys.get(prop_key) is not None:
                continue

            # 一定確率 (options に指定) で生成しない。
            if random.random() >= options.default_prob_of_optional_properties:
                generated_keys[prop_key] = False
                continue

            next_factory = self._factory_of(prop_key, options=options)
            generated[prop_key] = next_factory.gen_as_child(options=options,
                                                            parent_context=context,
                                                            child_key=prop_key)
            generated_keys[prop_key] = True

        return generated


class MultiFactory(Factory[None]):
    _factories: List[Factory]

    def __init__(self, schema: Optional[dict], *,
                 schema_is_validated: bool = False, context: Optional[SchemaContext] = None):
        super(MultiFactory, self).__init__(schema, schema_is_validated=schema_is_validated, context=context)

        # schema['type'] がリストでない場合 (strであるばあいを含む) やリストが空である場合例外を生じる
        schema_type = schema.get('type')
        if isinstance(schema_type, str) or not isinstance(schema_type, Iterable) or len(schema_type) <= 0:
            raise ValueError('For MultiFactory, schema.type must be iterable of at least 1 strings')

        # 各 type の factory を生成
        self._factories = [Factory(schema,
                                   schema_is_validated=self.schema_is_validated,
                                   context=context, gen_type=typ)
                           for typ in schema_type]

    def gen(self,
            *,
            options: Optional[Options] = None,
            context: Optional[GenerationContext] = None) -> None:
        factory = random.choice(self._factories)
        return factory.gen(options=options, context=context)


class EnumFactory(Factory[None]):
    _enum_values: Sequence

    def __init__(self, schema: Optional[dict], *,
                 schema_is_validated: bool = False, context: Optional[SchemaContext] = None):
        super(EnumFactory, self).__init__(schema, schema_is_validated=schema_is_validated, context=context)

        if context is None:
            context = SchemaContext.root(self._schema)

        enum_values = self._schema.get('enum')

        if not isinstance(enum_values, Sequence):
            raise ValueError(f"schema for {self.__class__.__name__} must have an array 'enum'")

        if len(enum_values) <= 0:
            raise SchemaConflictError('schema.enum must contain at least 1 value', context)

        self._enum_values = tuple(filter(lambda v: _value_satisfies_schema(v, self._schema), enum_values))

        if len(self._enum_values) <= 0:
            raise SchemaConflictError('At least 1 value of schema.enum must satisfy the schema', context)

    def gen(self,
            *,
            options: Optional[Options] = None,
            context: Optional[GenerationContext] = None) -> None:
        if options is None:
            options = Options.default()

        value = random.choice(self._enum_values)

        if options.enum_copy_style == ranjg.options.DEEP_COPY:
            return copy.deepcopy(value)
        elif options.enum_copy_style == ranjg.options.NO_COPY:
            return value
        elif options.enum_copy_style == ranjg.options.SHALLOW_COPY:
            return copy.copy(value)
        else:
            raise GenerateError('options.enum_copy_style is invalid value: ' + options.enum_copy_style, context=context)


def _value_satisfies_schema(value, schema: dict) -> bool:
    try:
        # TODO: 使用する validator を検討
        jsonschema.validate(value, schema)
    except jsonschema.ValidationError:
        return False

    return True


_FACTORY_MAP: Dict[str, Type[Factory]] = {
    'null': NoneFactory,
    'boolean': BoolFactory,
    'integer': IntFactory,
    'number': NumFactory,
    'string': StrFactory,
    'array': ListFactory,
    'object': DictFactory,
}
