# SPDX-FileCopyrightText: 2024-present Daniele Rapetti <daniele.rapetti@sissa.it>
#
# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

from plumed_bench_pp.types import BenchmarkRun


def _append_kernel_rec(keys: "list[str] | Iterable[str]", name: str, level: int) -> str:
    nm = name if level == 0 else f"{name}({level})"
    if nm in keys:
        return _append_kernel_rec(keys, name, level + 1)
    return nm


def kernel_name(data: dict, name: str) -> str:
    return _append_kernel_rec(data.keys(), name, 0)


def _common_iterable(obj):
    """Iterates over the values of a dict or any iterable"""
    if isinstance(obj, dict):
        yield from obj.values()
    else:
        yield from obj


def get_kernels(data: "BenchmarkRun|list[BenchmarkRun]") -> "set[str]":
    """
    Returns a set of unique kernel names extracted from the benchmark data.

    Args:
        data (BenchmarkRun | list[BenchmarkRun]): The data to extract kernel names from.
            It can be a single :class:`.BenchmarkRun` object or a list of :class:`.BenchmarkRun` objects.

    Returns:
        set[str]: A set of unique kernel names extracted from the given data.
    """

    toret = []
    if isinstance(data, BenchmarkRun):
        data = [data]
    for d in _common_iterable(data):
        toret += [d.runs[k].kernel for k in d.runs]

    return set(toret)


def get_inputfiles(data: "BenchmarkRun|list[BenchmarkRun]") -> "set[str]":
    """
    Retrieves the set of input files from the given benchmark data.

    Args:
        data (BenchmarkRun | list[BenchmarkRun]): The data to extract input files from.
            It can be a single :class:`.BenchmarkRun` object or a list of :class:`.BenchmarkRun` objects.

    Returns:
        set[str]: A set of unique input file names extracted from the given data.
    """

    toret = []
    if isinstance(data, BenchmarkRun):
        data = [data]
    for d in _common_iterable(data):
        toret += [d.runs[k].input for k in d.runs]

    return set(toret)


def get_kernels_and_inputfiles(data: "BenchmarkRun|list[BenchmarkRun]") -> "list[tuple[str, str]]":
    """
    Retrieves a list of tuples containing the kernel and input file names from the given benchmark data.

    Args:
        data (BenchmarkRun | list[BenchmarkRun]): The data to extract kernel and input file names from.
            It can be a single :class:`.BenchmarkRun` object or a list of :class:`.BenchmarkRun` objects.

    Returns:
        list[tuple[str, str]]: A list of tuples, where each tuple contains the kernel and input file names
        extracted from the given data.
    """

    toret = []
    if isinstance(data, BenchmarkRun):
        data = [data]
    for d in _common_iterable(data):
        toret += [(d.runs[k].kernel, d.runs[k].input) for k in d.runs]

    return toret
