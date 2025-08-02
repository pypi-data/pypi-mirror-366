# SPDX-FileCopyrightText: 2024-present Daniele Rapetti <daniele.rapetti@sissa.it>
#
# SPDX-License-Identifier: MIT

# for py3.8
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pandas import DataFrame

from plumed_bench_pp.constants import TIMINGCOLS
from plumed_bench_pp.utils import _common_iterable

if TYPE_CHECKING:
    from typing import Any

    from plumed_bench_pp.types import BenchmarkRun


def _checkfile(fname: str, pattern: str | list[str] | re.Pattern) -> bool:
    """
    A function to check if the file name matches the provided pattern.

    The pattern can be a string, a list of strings or a regular expression.

    Args:
        fname (str): The file name to check.
        pattern (str|list[str]|re.Pattern): The pattern to match against the file name.

    Returns:
        bool: True if the file name matches the pattern, False otherwise.
    """

    if isinstance(pattern, list):
        return fname in pattern
    if isinstance(pattern, re.Pattern):
        return pattern.search(fname) is not None
    return pattern in fname


def convert_to_table(
    filesdict: dict[Any, BenchmarkRun] | list[BenchmarkRun],
    rows_to_extract: list[str],
    kernel: str,
    inputlist: str | list[str] | re.Pattern,
) -> dict[str, DataFrame]:
    """
    Generates a table using the specified rows.

    Extracts the specified rows from the given files list or dict,
    filtering the specified kernel and input files.

    Args:
        filesdict (dict | list): A dictionary containing file data parsed by
            :func:`parse_benchmark_output.`
        rows_to_extract (list[str]): A list of strings representing the rows
            to extract from the files the most common ones are in :mod:`plumed_bench_pp.constants`.
        kernel (str): A string specifying the kernel to filter files by.
        inputlist (str | list[str] | re.Pattern): A string, list of strings,
            or regular expression pattern to filter the plumed input files used
            by the desired kernel.

    Returns:
        dict[str, DataFrame]: A dictionary containing the table data indexed by report's rows
    """

    data: dict[str, DataFrame] = {}
    tmp: dict = {}
    for row in rows_to_extract:
        tmp[row] = []
    for file in _common_iterable(filesdict):
        key = None
        for k in file.runs:
            if (file.runs[k].kernel == kernel) and _checkfile(file.runs[k].input, inputlist):
                key = k
                break

        if key is None:
            # print warning?
            continue
        natoms = file.settings.atoms

        tt = file.extract_rows(rows_to_extract, [key])
        for row in rows_to_extract:
            tmp[row].append([natoms, *tt[key][row]])

    for row in rows_to_extract:
        data[row] = DataFrame(tmp[row], columns=["natoms", *TIMINGCOLS]).set_index("natoms").sort_index()
    return data
