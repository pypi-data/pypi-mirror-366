# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from random import choices
from string import ascii_letters, digits, punctuation
from typing import Dict, List, Iterator, ByteString


def random_string(vocabulary: str = None, length: int = 20, exclude: str = None) -> str:
    """ Create random string """

    if not vocabulary:
        vocabulary = ascii_letters + digits + punctuation

    choices_ = []
    while len(choices_) < length:
        char = choices(vocabulary)[0]
        if not exclude or (exclude and char not in exclude):
            choices_.append(char)

    return "".join(choices_)


def get_batches(list_: List, n: int) -> Iterator:
    """
    Divide a list into chunks...

    :param list_: List to divide.
    :param n: Number of elements by chunk.
    :return:
    """

    for i in range(0, len(list_), n):
        yield list_[i:i + n]


def remove_attributes(record: Dict, attrs: List[str]) -> None:
    """ Remove attributes from a Dict """

    for key in attrs:
        if key in record:
            del record[key]


def rename_attributes(record: Dict, mapper: Dict[str, str]) -> None:
    """ Rename the object attributes using the column_mapper """

    _items = list(record.items())
    for key, value in _items:
        if key in mapper:
            record[mapper[key]] = record[key]
            del record[key]


def add_attributes(record: Dict, expected_attrs: List[str]):
    """
    The function add to the dictionary the list of
    attributes (if not exists) expected
    using None...

    :param record: Dictionary to update.
    :param expected_attrs: Attributes to add.
    :return:
    """

    for key in expected_attrs:
        if key not in record:
            record[key] = None


def convert_data_type(data: Dict, columns_type_mapper: Dict) -> None:
    """
    Update (cast) the value depending on the specified type...

    :param data: Dictionary to update.
    :param columns_type_mapper: Dictionary that specify the data types.
    """

    if not columns_type_mapper:
        return

    for key, type_ in columns_type_mapper.items():
        if key in data and data[key] is not None:
            value = data[key].strip() if type_ == "float" else data[key]
            data.update({
                key: eval(f"{type_}({value})")
            })


def to_snake_case(string: str) -> str:
    """ It converts a string from camel-case to snake-case """

    return "".join(
        ["_" + i.lower() if i.isupper() else i for i in string]
    ).lstrip("_")


def flatten_json(data: Dict, flatten_sublist: bool = False):
    """
    Utility function for flattening dictionary objects...

    :param data: Object to flatten.
    :param flatten_sublist: Set as True if you want to flatten sublist objects.

    :return: Flatten data (dictionary).
    """

    res = {}

    def flatten(x, name: str = ""):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + "_")

        elif flatten_sublist and isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1

        else:
            res[name[:-1]] = x

    flatten(data)
    return res


def to_one_line(multiline_string: str) -> str:
    """ It converts a multiline string to a single line one """

    return re.sub(
        pattern=r"\s+", repl=" ",
        string=multiline_string.replace("\n", "")
    ).strip()


def bytes_to_str(data: List | Dict | ByteString, encoding: str = "utf-8"):
    """
    Convert bytes to str in keys and values...

    Example:
        {b"key": b"value"})         -> {"key": "value"}
        {b"key": [1, 2, b"3"]}      -> {"key": [1, 2, "3"]}
        [1, 2, b"3", {b"a": b"a"}]  -> [1, 2, "3", {"a": "a"}]
        b"test")                    -> "test"
    """

    def convert(obj_, encoding_, result=None):
        if not result:
            result = {}

        if isinstance(obj_, dict):
            dic_ = {}
            for key in obj_:
                previous_key = key
                if isinstance(key, bytes):
                    key = key.decode()

                dic_[key] = convert(obj_[previous_key], encoding_, dic_)

            return dic_

        elif isinstance(obj_, list):
            return [convert(x, encoding_, result or {}) for x in obj_]

        else:
            return obj_.decode() if isinstance(obj_, bytes) else obj_

    return convert(data, encoding)
