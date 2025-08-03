# -*- coding: utf-8 -*-

import csv

from io import StringIO
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List


def records_from_csv(path: str, file_args: Dict = None, reader_args: Dict = None) -> Iterator[Dict]:
    """
    Returns records from a CSV file...

    :return: An iterable of dictionaries.
    :rtype: Iterator[Dict]
    """

    file_args = file_args or {}
    reader_args = reader_args or {}

    with open(path, **file_args) as f_:
        reader = csv.DictReader(f_, **reader_args)
        for rec in reader:
            yield rec


def records_from_buffer(data: str, newline: str = None, **kwargs) -> Iterator[Dict]:
    """
    Returns records from file-like object...

    :return: An iterable of dictionaries.
    :rtype: Iterator[Dict]
    """

    dialect = kwargs.pop("dialect", "excel")
    quoting = kwargs.pop("quoting", csv.QUOTE_NONNUMERIC)

    reader = csv.DictReader(
        StringIO(data, newline=newline),
        dialect=dialect, quoting=quoting,
        **kwargs)

    for rec in reader:
        yield rec


def records_to_buffer(
        records: List[Dict], columns: List[str] = None,
        with_headers: bool = True,
        **kwargs) -> StringIO:

    """
    Save records from file-like object...

    :param records: A collection of dictionary records to write.
    :type records: Iterable[Dict]
    :param columns: A list of column names specifying the order of fields.
    :type columns: List[str]
    :param with_headers: Whether to include column headers in the CSV (default is True).
    :type with_headers: bool, optional

    :return: The buffer.
    :rtype: StringIO
    """

    buffer = StringIO()
    dialect = kwargs.pop("dialect", "excel")
    quoting = kwargs.pop("quoting", csv.QUOTE_NONNUMERIC)
    columns = columns or records[0].keys()

    csv_writer = csv.DictWriter(
        buffer, fieldnames=columns,
        dialect=dialect, quoting=quoting,
        **kwargs)

    if with_headers:
        csv_writer.writeheader()

    csv_writer.writerows(records)
    return buffer


def records_to_csv(
        file_path: str, records: Iterable[Dict], columns: List[str], with_headers: bool = True,
        quoting: int = csv.QUOTE_ALL, dialect=csv.excel, file_args: Dict = None,
        writer_args: Dict = None) -> str:

    """
    It writes records (dictionaries) to a CSV file...

    :param file_path: The path where the CSV file will be saved.
    :type file_path: str
    :param records: A collection of dictionary records to write.
    :type records: Iterable[Dict]

    :param columns: A list of column names specifying the order of fields.
    :type columns: List[str]
    :param with_headers: Whether to include column headers in the CSV (default is True).
    :type with_headers: bool, optional

    :param quoting: Quoting style for the CSV (default is csv.QUOTE_ALL).
    :type quoting: int, optional
    :param dialect: The CSV dialect to use (default is csv.excel).
    :type dialect: csv.Dialect, optional

    :param file_args: Additional arguments for `open()` when writing the file (default is None).
    :type file_args: Dict, optional
    :param writer_args: Additional arguments for `csv.DictWriter` (default is None).
    :type writer_args: Dict, optional

    :return: The file path of the saved CSV.
    :rtype: str

    :raises ValueError: If `columns` is empty or records contain keys not in `columns`.
    :raises IOError: If there is an error writing to the file.
    """

    file_args = file_args or {}
    writer_args = writer_args or {}

    with open(file_path, mode="w", **file_args) as file:
        writer = csv.DictWriter(
            file, fieldnames=columns, dialect=dialect,
            quoting=quoting, **writer_args)

        if with_headers:
            writer.writeheader()

        writer.writerows(records)

    return file_path
