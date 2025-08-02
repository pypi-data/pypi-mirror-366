# SPDX-FileCopyrightText: 2024-present Daniele Rapetti <daniele.rapetti@sissa.it>
#
# SPDX-License-Identifier: MIT

# for py3.8
from __future__ import annotations

import re
from itertools import dropwhile
from typing import TYPE_CHECKING

from plumed_bench_pp.types import BenchmarkRow, BenchmarkRun, BenchmarkSettings, KernelBenchmark
from plumed_bench_pp.utils import kernel_name

if TYPE_CHECKING:
    from collections.abc import Iterable

# using raw string (r) to avoid warnings with the escaped characters
__FLOATMATCH = r"[+-]?(?:\d+(?:[.]\d*)?(?:e[+-]?\d+)?|[.]\d+(?:e[+-]?\d+)?)"
__Kernel = re.compile(r"Kernel:\s*(\S*)")
__Input = re.compile(r"Input:\s*(\S*)")
__Comparative = re.compile(rf"Comparative:\s*({__FLOATMATCH}) \+\- ({__FLOATMATCH})")
# __NumerOfAtoms = re.compile(r" Number of atoms: (\d+)")
__Data = re.compile(
    rf"(?:PLUMED: |BENCH:  )(?P<name>.+)\s+(?P<Cycles>[0-9]+)+\s+"
    rf"(?P<Total>{__FLOATMATCH})+\s+"
    rf"(?P<Average>{__FLOATMATCH})+\s+"
    rf"(?P<Minimum>{__FLOATMATCH})+\s+"
    rf"(?P<Maximum>{__FLOATMATCH})+"
)
# these are the regexes for the first few lines of the benchmark output
# BENCH:  Welcome to PLUMED benchmark
__BMKernelList = re.compile(r"BENCH:  Using --kernel=(.+)")
__BMPlumedList = re.compile(r"BENCH:  Using --plumed=(.+)")
__BMSteps = re.compile(r"BENCH:  Using --nsteps=(\d+)")
__BMNatoms = re.compile(r"BENCH:  Using --natoms=(\d+)")
__BMNatomsOverriden = re.compile(r"BENCH:  Distribution overrode --natoms, Using --natoms=(\d+)")
__BMMaxtime = re.compile(r"BENCH:  Using --maxtime=({__FLOATMATCH}|[-+]?\d+)")
__BMSleep = re.compile(r"BENCH:  Using --sleep=(\d+)")
__BMAtomDistributions = re.compile(r"BENCH:  Using --atom-distribution=(.+)")
__BMIsSuffled = re.compile(r"BENCH:  Using --shuffled")
__BMUseDomainDecomposition = re.compile(r"BENCH:  Using --domain-decomposition")


def parse_benchmark_output(lines: list[str] | Iterable[str]) -> dict:
    """
    Parses the benchmark report lines into a dictionary.
    If you have a complete run with the header use :func:`parse_full_benchmark_output`

    Args:
        lines (list[str]): The list of lines containing benchmark output data.

    Returns:
        dict: A dictionary containing the parsed benchmark data.
    """
    data: dict = {}
    kernel: KernelBenchmark = KernelBenchmark()
    for line in lines:
        if result := __Kernel.search(line):
            if kernel.has_data():
                data[kernel_name(data, f"{kernel.kernel}+{kernel.input}")] = kernel

                kernel = KernelBenchmark()
            kernel.kernel = result.group(1)
        elif result := __Input.search(line):
            kernel.input = result.group(1)
        elif result := __Comparative.search(line):
            kernel.compare = {
                "fraction": float(result.group(1)),
                "error": float(result.group(2)),
            }
        elif result := __Data.search(line):
            name = result.group("name").strip()
            if name == "":
                name = "Plumed"
            kernel.rows[name] = BenchmarkRow.from_re_match(result)
    # add the last kernel
    if kernel.has_data():
        data[kernel_name(data, f"{kernel.kernel}+{kernel.input}")] = kernel
    return data


def parse_plumed_time_report(lines: list[str]) -> KernelBenchmark:
    """
    Parses the given list of lines containing the time report that plumed prints at the end of the runs.

    Args:
        lines (list[str]): A list of lines containing the Plumed time report.

    Returns:
        KernelBenchmark: The parsed time report.

    """

    data: KernelBenchmark = KernelBenchmark()
    for line in lines:
        if result := __Data.search(line):
            name = result.group("name").strip()
            if name == "":
                name = "Plumed"
            data.rows[name] = BenchmarkRow.from_re_match(result)
    return data


def parse_full_benchmark_output(lines: list[str]) -> BenchmarkRun:
    """
    A function to parse the full benchmark output.

    Args:
        lines (list[str]): The complete output of the benchmark run. Already split into lines.

    Returns:
        BenchmarkRun: The parsed benchmark run.
    """

    header = BenchmarkSettings()
    if "BENCH:  Welcome to PLUMED benchmark" in lines[0]:
        # there is an header :)
        for line in lines:
            if "BENCH:  Initializing the setup of the kernel(s)" in line:
                break
            atoms_overriden = False
            if result := __BMKernelList.search(line):
                header.kernels = result.group(1).split(":")
            elif result := __BMPlumedList.search(line):
                header.inputs = result.group(1).split(":")
            elif result := __BMSteps.search(line):
                header.steps = int(result.group(1))
            elif result := __BMNatoms.search(line):
                if not atoms_overriden:
                    header.atoms = int(result.group(1))
            elif result := __BMNatomsOverriden.search(line):
                atoms_overriden = True
                header.atoms = int(result.group(1))
            elif result := __BMMaxtime.search(line):
                header.maxtime = float(result.group(1))
            elif result := __BMSleep.search(line):
                header.sleep = float(result.group(1))
            elif result := __BMAtomDistributions.search(line):
                header.atom_distribution = result.group(1)
            elif result := __BMIsSuffled.search(line):
                header.shuffled = True
            elif result := __BMUseDomainDecomposition.search(line):
                header.domain_decomposition = True
    return BenchmarkRun(
        settings=header,
        runs=parse_benchmark_output(dropwhile(lambda line: not line.startswith("BENCH:  Starting MD loop"), lines)),
    )
