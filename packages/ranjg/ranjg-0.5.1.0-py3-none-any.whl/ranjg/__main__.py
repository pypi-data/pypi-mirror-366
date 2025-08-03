import string
import sys
import argparse
from typing import Tuple, Optional, TextIO, Iterable

from .util.listutil import count
from ._arg_parser import positive_integer
from . import gen


__formatter = string.Formatter()


def main():
    """A function to be called when the module is executed on the command line.
    """
    # 引数を取得
    args = parse_args()

    # 出力先を決定
    output_file, output_file_list, output_fp = get_output_target(args)

    gen(schema_file=args.schema_file_path, output_file=output_file, output_fp=output_fp, options_file=args.options,
        multiplicity=args.multiplicity, output_file_list=output_file_list,
        # To ensure that generated value is exposed to garbage collection earlier.
        return_none=True)


def _count_placeholder(format_string: str) -> int:
    return count(lambda t: t[1] is not None, __formatter.parse(format_string))


def parse_args():
    """Get and parse command line arguments.

    Returns:
        An object that holds the values obtained from the command line arguments.
    """
    parser = argparse.ArgumentParser(description="Generate json file randomly according to json schema.")

    parser.add_argument("schema_file_path", help="Path of json schema file. This file is used as base schema.")
    parser.add_argument("--json_output", "-j", help="Path to which json file is written.")
    parser.add_argument("-n", dest="file_num", type=positive_integer,
                        help="The number of output json file. "
                             "Repeats the generation for the specified number of times and outputs the result to each "
                             "file. If it is specified, --json_output is required and used as format of filepath.")
    parser.add_argument("--options", help="Path of options file.")
    parser.add_argument("--list", "-l", dest="multiplicity", type=positive_integer,
                        help="If specified, repeats the generation for the specified number of times "
                             "and outputs the results as a list.")

    args = parser.parse_args()

    if args.file_num is not None:
        # -n の指定時は --json_output が必須
        if args.json_output is None:
            parser.error("the following arguments are required when -n is specified: --json_output")

        # -n に指定がある場合、--json_output は1つのプレースホルダーを持つフォーマットでなくてはならない
        if _count_placeholder(args.json_output) != 1:
            parser.error("when -n is specified, --json_output must have exactly one placeholder such as '{}'")

    return args


def get_output_target(args) -> Tuple[Optional[str], Optional[Iterable[str]], Optional[TextIO]]:
    """Returns the values to be used as ``(output_file, output_file_list, output_fp)``, arguments of ``ranjg.gen``.

    Args:
        args: An object that holds the values obtained from the command line arguments.

    Returns:
        The values to be used as ``(output_file, output_file_list, output_fp)``, arguments of ``ranjg.gen``.
    """
    if args.file_num is not None:
        return None, map(lambda i: args.json_output.format(i), range(args.file_num)), None
    elif args.json_output is not None:
        return args.json_output, None, None
    else:
        return None, None, sys.stdout


if __name__ == "__main__":
    main()
