from typing import Tuple, Union


def normalize_exclusive_minimum(schema: dict) -> Tuple[Union[int, float, None], Union[int, float, None]]:
    """Normalize exclusive minimum.

    If ``schema.exclusiveMinimum`` is boolean value, convert to Draft-7-style exclusiveMinimum.
    Otherwise, returns values in schema.

    Args:
        schema: JSON schema

    Returns:
        Inclusive minimum and exclusive minimum in Draft-7-style.
    """
    inclusive_minimum = schema.get("minimum", None)
    exclusive_minimum = schema.get("exclusiveMinimum", None)

    if exclusive_minimum is True:
        exclusive_minimum = inclusive_minimum
        inclusive_minimum = None
    elif exclusive_minimum is False:
        exclusive_minimum = None

    return inclusive_minimum, exclusive_minimum


def normalize_exclusive_maximum(schema: dict) -> Tuple[Union[int, float, None], Union[int, float, None]]:
    """Normalize exclusive maximum.

    If ``schema.exclusiveMaximum`` is boolean value, convert to Draft-7-style exclusiveMaximum.
    Otherwise, returns values in schema.

    Args:
        schema: JSON schema

    Returns:
        Inclusive maximum and exclusive maximum in Draft-7-style.
    """
    inclusive_maximum = schema.get("maximum", None)
    exclusive_maximum = schema.get("exclusiveMaximum", None)
    if exclusive_maximum is True:
        exclusive_maximum = inclusive_maximum
        inclusive_maximum = None
    elif exclusive_maximum is False:
        exclusive_maximum = None

    return inclusive_maximum, exclusive_maximum
