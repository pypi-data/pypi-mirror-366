# SPDX-FileCopyrightText: 2024-present Daniele Rapetti <daniele.rapetti@sissa.it>
#
# SPDX-License-Identifier: MIT

from plumed_bench_pp.parser import (
    parse_benchmark_output,
    parse_full_benchmark_output,
    parse_plumed_time_report,
)


def test_parse_benchmark_output(readme_example_benchmark_output):
    example, expected = readme_example_benchmark_output
    lines = example.split("\n")
    assert parse_benchmark_output(lines) == expected


def test_parse_plumed_time_report(plumed_time_report):
    example, expected = plumed_time_report
    # this is an output of plumed with "DEBUG DETAILED_TIMERS" set
    lines = example.split("\n")
    assert parse_plumed_time_report(lines) == expected


def test_parse_full_benchmark_output_noheader(full_benchmark_output_noheader):
    example, expected = full_benchmark_output_noheader
    lines = example.split("\n")
    assert parse_full_benchmark_output(lines) == expected


def test_parse_full_benchmark_output1k2f(full_benchmark_output_1k2f):
    example, expected = full_benchmark_output_1k2f
    lines = example.split("\n")
    assert parse_full_benchmark_output(lines) == expected


def test_parse_full_benchmark_output2k1f(full_benchmark_output_2k1f):
    example, expected = full_benchmark_output_2k1f
    lines = example.split("\n")
    assert parse_full_benchmark_output(lines) == expected


def test_parse_full_benchmark_output2k1f_overridenatoms(full_benchmark_output_2k1f_override):
    example, expected = full_benchmark_output_2k1f_override
    lines = example.split("\n")
    assert parse_full_benchmark_output(lines) == expected
