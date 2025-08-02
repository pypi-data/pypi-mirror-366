# SPDX-FileCopyrightText: 2024-present Daniele Rapetti <daniele.rapetti@sissa.it>
#
# SPDX-License-Identifier: MIT

# for py3.8
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import re


@dataclass
class BenchmarkRow:
    """
    A class representing a single row in the benchmark table.

    Args:
        cycles (int): The number of benchmark cycles.
        total (float): The total time in seconds.
        average (float): The average time in seconds.
        minimum (float): The minimum time in seconds.
        maximum (float): The maximum time in seconds.
    """

    cycles: int
    total: float
    average: float
    minimum: float
    maximum: float

    def as_list(self) -> list:
        """
        A method to return the BenchmarkRow attributes as a list.
        """
        return [self.cycles, self.total, self.average, self.minimum, self.maximum]

    @staticmethod
    def from_re_match(result: re.Match) -> BenchmarkRow:
        """
        A method to create a BenchmarkRow instance from a regex match result.

        Args:
            result (re.Match): The regex match result containing the required groups.

        Returns:
            BenchmarkRow: A BenchmarkRow instance initialized with the extracted data.
        """
        return BenchmarkRow(
            cycles=int(result.group("Cycles")),
            total=float(result.group("Total")),
            average=float(result.group("Average")),
            minimum=float(result.group("Minimum")),
            maximum=float(result.group("Maximum")),
        )

    @staticmethod
    def from_dict(data: dict) -> BenchmarkRow:
        """
        Creates a new instance of the BenchmarkRow class from a dictionary containing the necessary data.

        Args:
            data (dict): A dictionary with the following keys: "Cycles", "Total", "Average", "Minimum", and "Maximum".

        Returns:
            BenchmarkRow: A new instance of the BenchmarkRow class initialized with the data from the dictionary.
        """

        return BenchmarkRow(
            cycles=data["Cycles"],
            total=data["Total"],
            average=data["Average"],
            minimum=data["Minimum"],
            maximum=data["Maximum"],
        )


@dataclass
class KernelBenchmark:
    """
    A class representing a benchmark for a kernel-input pair.

    Attributes:
        kernel (str): The name of the kernel.
        input (str): The name of the input file.
        compare (dict): A dictionary containing the fraction and error of the benchmark.
        rows (dict): A dictionary containing the benchmark rows.
    """

    kernel: str = ""
    input: str = ""
    compare: dict = field(default_factory=dict)
    rows: dict = field(default_factory=dict)

    def has_data(self) -> bool:
        return len(self.rows) > 0 or len(self.compare) > 0 or self.input != "" or self.kernel != ""


@dataclass
class BenchmarkSettings:
    """
    A class representing the settings for benchmarking.
    """

    #: The list of kernels as specified in the command line
    kernels: list = field(default_factory=list)
    #: The list of input files as specified in the command line
    inputs: list = field(default_factory=list)
    #: The number of benchmark steps as specified in the command line
    steps: int = -1
    #: The number of atoms in the system as specified in the command line
    atoms: int = -1
    #: The maximum time in seconds as specified in the command line
    maxtime: float = -1.0
    #: The time in seconds to sleep between benchmark steps as specified in the command line
    sleep: float = 0.0
    #: The type of atom distribution as specified in the command line
    atom_distribution: str = "line"
    #: The shuffled option, as specified in the command line
    shuffled: bool = False
    #: The domain decomposition option, as specified in the command line
    domain_decomposition: bool = False


@dataclass
class BenchmarkRun:
    """
    A class representing a benchmark run.

    It contains the settings as a :class:`.BenchmarkSettings` and the results of each kernel-input file combination as a :class:`.KernelBenchmark` dictionary.
    """

    settings: BenchmarkSettings = field(default_factory=BenchmarkSettings)
    runs: dict[str, KernelBenchmark] = field(default_factory=dict)

    def extract_rows(self, rows: list, keys: list[str] | None = None) -> dict[str, dict[str, list]]:
        """
        Extracts the specified rows from the given data dictionary.
        Works with the results of plumed_bench_pp.parser.parse_benchmark_output

        Args:
            rows (list): The list of rows to extract.
            keys (list or None): The keys to access, otherwise iterate on everithing

        Returns:
            dict[str, dict[str,list]]: A dictionary of the simulations.
        """
        df = {}
        iterateon = keys if keys else self.runs
        for key in iterateon:
            tmp = {}
            for row in rows:
                tmp[row] = self.runs[key].rows[row].as_list()
            df[key] = tmp

        return df
