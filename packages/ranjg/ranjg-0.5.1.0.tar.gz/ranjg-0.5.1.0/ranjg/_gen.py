import itertools
import json
from typing import Optional, TextIO, Iterable

import ranjg
from . import schemas
from ._context import GenerationContext
from .options import Options
from .options import load as load_options
from .util.numutil import is_integer


def __count_not_null(*args) -> int:
    return len(tuple(filter(lambda v: v is not None, args)))


def gen(schema: dict = None,
        *,
        schema_file: str = None,
        output_file: str = None,
        output_file_list: Iterable[str] = None,
        output_fp: TextIO = None,
        output_fp_list: Iterable[TextIO] = None,
        options: Optional[Options] = None,
        options_file: str = None,
        multiplicity: Optional[int] = None,
        schema_is_validated: bool = False,
        return_none: bool = False,
        context: Optional[GenerationContext] = None):
    """Generate something randomly according to the JSON schema.

    This function is not fully compliant with the JSON schema, and unsupported parameters in the schema are ignored.
    See also :doc:`ranjg-json-schema` to explore the supported parameters.

    Examples
        The following code is most simple usage.

        >>> import ranjg
        >>> schema_dict = { 'type': 'string' }
        >>> ranjg.gen(schema_dict)    # -> returns some string

        By replacing the contents of ``schema_dict``, you can change the value to be generated.

        If you want to specify a schema without a python dict but with JSON file, you can use argument ``schema_file``.

        >>> import ranjg
        >>> schema_path = './schema_file.json'
        >>> ranjg.gen(schema_file=schema_path)  # -> returns some value

        If you want to get the result as JSON file, you can use argument ``output_file`` or ``output_fp``. (Following
        two examples will run similarly.

        >>> import ranjg
        >>> schema_dict = { 'type': 'string' }
        >>> ranjg.gen(schema_dict, output_file='./output.json')
        >>> # -> returns the result value and writes the result to specified file

        >>> import ranjg
        >>> schema_dict = { 'type': 'string' }
        >>> with open('./output.json', 'w+') as out_fp:
        >>>     ranjg.gen(schema_dict, output_fp=out_fp)
        >>>     # -> returns the result value and writes the result to specified file

    Args:
        schema (dict, optional):
            JSON schema object. See also :doc:`ranjg-json-schema`.
            Only one of this argument or ``schema_file`` needs to be specified.
        schema_file (str, optional):
            The path to JSON schema file. This JSON schema is used instead of the argument ``schema``.
        output_file (str, optional):
            The path to a file where the result will be output as JSON.
            If ``multiplicity`` is specified, a list consisting of the generated values will be output as json.
        output_file_list (Iterable[str], optional):
            The list of paths to a file where the result will be output as JSON.
            It repeats the generation and outputs each result to each file.
        output_fp (TextIO, optional):
            The writing object of a file where the result will be output as JSON.
            If ``multiplicity`` is specified, a list consisting of the generated values will be output as json.
        output_fp_list (Iterable[TextIO], optional):
            The list of writing objects of files where the result will be output as JSON.
            It repeats the generation and outputs each result to each file.
        options (Options, optional):
            The options for generation.
        options_file (str, optional):
            The path to options file. This is parsed as JSON to an Options instance.
        multiplicity (int, optional):
            If specified, it repeats the generation for the specified number of times and returns the results as a list.
        schema_is_validated (bool, optional):
            Whether the schema is already validated or not.
            (In normal usage, this argument is not specified.)
        return_none (bool, default=False):
            If it is True, this function returns None.
            (If it is False, the result contains all outputs.
            In particular, if it is repeated a lot, such as when a large list is specified in output_file_list,
            it may overwhelm memory.)
        context (GenerationContext):
            The context of construction.
            (In normal usage, this argument is not specified. This argument is for using this function recursively.)

    Returns:
        Generated something. It is satisfies the JSON schema.
        However, if ``multiplicity`` is specified, it returns a list, each element of which satisfies the schema.

    Raises:
        SchemaFileIOError:
            When loading schema_file is failed
        OptionsFileIOError:
            When loading options_file is failed
        InvalidSchemaError:
            When the schema specified as arguments is invalid.
        SchemaConflictError:
            When the schema specified as arguments has confliction.
            In other words, when no value can satisfy the schema.
        GenerateError:
            If an unforeseen error arises.
    """
    if schema is None and schema_file is None:
        raise ValueError("schema or schema_file must be specified.")
    if schema is not None and schema_file is not None:
        raise ValueError("Only one of schema and schema_file can be set.")
    if __count_not_null(output_file, output_fp, output_file_list, output_fp_list) >= 2:
        raise ValueError("Only one of (output_file, output_fp, output_file_list, output_fp_list) can be set. "
                         "(You don't have to set either one.)")
    if options is not None and options_file is not None:
        raise ValueError("Only one of options and options_file can be set. (You don't have to set either one.)")
    if multiplicity is not None and not (is_integer(multiplicity) and 0 <= multiplicity):
        raise ValueError(f"Illegal argument 'multiplicity': {multiplicity}")

    # スキーマファイルを読み込み
    if schema_file is not None:
        schema = schemas.load(schema_file)

    # スキーマの不正判定
    if not schema_is_validated:
        schemas.validate(schema)

    # オプションファイルを読み込み
    if options_file is not None:
        options = load_options(options_file)

    # ファイル出力先を正規化
    if output_file is not None:
        output_list = ((output_file, None),)
    elif output_fp is not None:
        output_list = ((None, output_fp),)
    elif output_file_list is not None:
        output_list = itertools.zip_longest(output_file_list, tuple())
    elif output_fp_list is not None:
        output_list = itertools.zip_longest(tuple(), output_fp_list)
    else:
        output_list = ((None, None),)

    factory = ranjg.Factory(schema, schema_is_validated=True)

    # メソッドの戻り値を保持するリストを作成
    if return_none:
        # 戻り値による出力を行わない場合、要素を保持しないダミーリストを使用する。
        # これにより、生成したものがリスト内に残らなくなり、早期にガベージコレクションされるようになる。
        result_list = _DummyList()
    else:
        # 戻り値を返す場合、生成したものをすべて保持する必要があるため、リストに保持する。
        result_list = []

    # 出力先の数だけ生成処理を繰り返す。
    for output_file, output_fp in output_list:

        # ランダムに値を生成
        if multiplicity is None:
            generated = factory.gen(options=options, context=context)
            result_list.append(generated)
        else:
            generated = [factory.gen(options=options, context=context) for _ in range(multiplicity)]
            result_list.extend(generated)

        # 出力先指定がある場合、JSONとして出力する
        if output_file is not None:
            with open(output_file, "w+") as fp:
                json.dump(generated, fp)
        if output_fp is not None:
            json.dump(generated, output_fp)

    if return_none:
        return None
    elif output_file_list is None and output_fp_list is None and multiplicity is None:
        return result_list[0]
    else:
        return result_list


class _DummyList(list):
    """List to ignore change operations.
    """

    def __setitem__(self, key, value):
        # ignore change operations
        pass

    def append(self, __object) -> None:
        # ignore change operations
        pass

    def extend(self, __iterable) -> None:
        # ignore change operations
        pass

    def __getitem__(self, key):
        return None

    def __len__(self) -> int:
        return 0
