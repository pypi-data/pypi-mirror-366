def is_integer(value) -> bool:
    if not isinstance(value, (int, float)):
        return False

    return int(value) == value
