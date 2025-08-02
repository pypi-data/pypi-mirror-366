# SPDX-FileCopyrightText: 2024-present Daniele Rapetti <daniele.rapetti@sissa.it>
#
# SPDX-License-Identifier: MIT

from plumed_bench_pp.utils import get_inputfiles, get_kernels, get_kernels_and_inputfiles, kernel_name


def test_kernel_name():
    mydict = {}
    mydict[kernel_name(mydict, "bar")] = "bar->1"
    mydict[kernel_name(mydict, "bar")] = "bar->0"
    mydict[kernel_name(mydict, "foo")] = "foo->1"
    mydict[kernel_name(mydict, "foo")] = "foo->2"
    mydict[kernel_name(mydict, "foo")] = "foo->3"

    assert "foo" in mydict
    assert mydict["foo"] == "foo->1"
    assert "foo(1)" in mydict
    assert mydict["foo(1)"] == "foo->2"
    assert "foo(2)" in mydict
    assert mydict["foo(2)"] == "foo->3"

    assert "bar" in mydict
    assert mydict["bar"] == "bar->1"
    assert "bar(1)" in mydict
    assert mydict["bar(1)"] == "bar->0"


def test_get_kernels(incremental_output):
    parsed_input, _, _ = incremental_output
    for k in parsed_input:
        ret = get_kernels(parsed_input[k])
        for run in parsed_input[k].runs.values():
            assert run.kernel in ret


def test_get_inputfiles(incremental_output):
    parsed_input, _, _ = incremental_output
    for k in parsed_input:
        ret = get_inputfiles(parsed_input[k])
        for run in parsed_input[k].runs.values():
            assert run.input in ret


def test_get_kernels_dict(incremental_output):
    parsed_input, _, _ = incremental_output
    ret = get_kernels(parsed_input)
    for myinput in parsed_input.values():
        for run in myinput.runs.values():
            assert run.kernel in ret


def test_get_inputfiles_dict(incremental_output):
    parsed_input, _, _ = incremental_output
    ret = get_inputfiles(parsed_input)
    for myinput in parsed_input.values():
        for run in myinput.runs.values():
            assert run.input in ret


def test_get_kernels_list(incremental_output):
    parsed_input, _, _ = incremental_output
    ret = get_kernels([parsed_input[k] for k in parsed_input])
    for myinput in parsed_input.values():
        for run in myinput.runs.values():
            assert run.kernel in ret


def test_get_inputfiles_list(incremental_output):
    parsed_input, _, _ = incremental_output
    ret = get_inputfiles([parsed_input[k] for k in parsed_input])
    for myinput in parsed_input.values():
        for run in myinput.runs.values():
            assert run.input in ret


def test_get_kernels_and_inputfiles(incremental_output):
    parsed_input, _, _ = incremental_output
    for myinput in parsed_input.values():
        ret = get_kernels_and_inputfiles(parsed_input)
        for run in myinput.runs.values():
            assert (run.kernel, run.input) in ret


def test_get_kernels_and_inputfiles_dict(incremental_output):
    parsed_input, _, _ = incremental_output
    ret = get_kernels_and_inputfiles(parsed_input)
    for myinput in parsed_input.values():
        for run in myinput.runs.values():
            assert (run.kernel, run.input) in ret


def test_get_kernels_and_inputfiles_list(incremental_output):
    parsed_input, _, _ = incremental_output
    ret = get_kernels_and_inputfiles([parsed_input[k] for k in parsed_input])
    for myinput in parsed_input.values():
        for run in myinput.runs.values():
            assert (run.kernel, run.input) in ret
