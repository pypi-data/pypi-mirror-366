"""Parsers for argparse.ArgumentParser.add_argument
"""


def positive_integer(string: str) -> int:
    value = int(string)

    if value <= 0:
        raise ValueError('invalid literal for positive_int(): ' + repr(string))

    return int(string)
