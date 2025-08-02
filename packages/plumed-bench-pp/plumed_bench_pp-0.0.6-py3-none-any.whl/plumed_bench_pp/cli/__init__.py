# SPDX-FileCopyrightText: 2024-present Daniele Rapetti <iximiel@gmail.com>
#
# SPDX-License-Identifier: MIT
import click

# TODO: suggest this
# https://click.palletsprojects.com/en/8.1.x/shell-completion/
import plumed_bench_pp.utils as pbpputils
from plumed_bench_pp.__about__ import __version__
from plumed_bench_pp.constants import (
    APPLY,
    BM_CALCULATION_PART1,
    BM_CALCULATION_PART2,
    BM_FIRSTSTEP,
    BM_INIT,
    BM_WARMUP,
    CALCULATE,
    PREPARE,
    SHARE,
    TOTALTIME,
    UPDATE,
    WAIT,
)
from plumed_bench_pp.parser import parse_full_benchmark_output
from plumed_bench_pp.tabulate import convert_to_table

row_choiches = {
    "BM_INIT": BM_INIT,
    "BM_FIRSTSTEP": BM_FIRSTSTEP,
    "BM_WARMUP": BM_WARMUP,
    "BM_CALCULATION_PART1": BM_CALCULATION_PART1,
    "BM_CALCULATION_PART2": BM_CALCULATION_PART2,
    "TOTALTIME": TOTALTIME,
    "PREPARE": PREPARE,
    "SHARE": SHARE,
    "WAIT": WAIT,
    "CALCULATE": CALCULATE,
    "APPLY": APPLY,
    "UPDATE": UPDATE,
}


def get_filelist(files: "tuple[str]") -> list:
    filelist = []

    for f in files:
        with open(f) as ff:
            filelist.append(parse_full_benchmark_output(ff.readlines()))

    return filelist


def get_data(filelist, rows):
    data = {}
    for k in pbpputils.get_kernels(filelist):
        data[k] = convert_to_table(filelist, rows, kernel=k, inputlist=".dat")
    return data


@click.command()
@click.argument("files", type=click.Path(readable=True), nargs=-1)
def kernels(files):
    """List the kernels in the given files"""
    filelist = get_filelist(files)

    for p in pbpputils.get_kernels(filelist):
        click.echo(p)


@click.command()
@click.argument("files", type=click.Path(readable=True), nargs=-1)
@click.option("--output", "-o", type=click.STRING, help="The output file to write the plot to")
@click.option(
    "--row",
    "-r",
    type=click.Choice(list(row_choiches.keys())),
    multiple=False,
    default="TOTALTIME",
    help="The row to plot",
)
def plot(files, output, row):
    """Plot the data in the given files

    This assumes that the simulation data is given in kernels"""
    from os.path import commonpath

    import matplotlib.pyplot as plt

    from plumed_bench_pp.plot import plot_histo
    # import matplotlib
    # # matplotlib.use('Agg')
    # print(f"Interactive mode: {matplotlib.is_interactive()}")
    # print(f"matplotlib backend: {matplotlib.rcParams['backend']}")

    rowtoplot = row_choiches[row]

    filelist = get_filelist(files)
    data = get_data(filelist, [rowtoplot])
    fig, ax = plt.subplots()
    kernels = list(pbpputils.get_kernels(filelist))
    cpf = commonpath(kernels)
    titles = [k[len(cpf) :] for k in kernels]

    plot_histo(ax, [data[k] for k in kernels], rowtoplot, titles=titles)
    ax.legend()
    if output is None:
        plt.show()
    else:
        fig.savefig(output)


@click.command()
@click.argument("files", type=click.Path(readable=True), nargs=-1)
@click.option(
    "--rows",
    "-r",
    type=click.Choice(list(row_choiches.keys())),
    multiple=True,
    default=["TOTALTIME"],
    help="The row(s) to plot",
)
def show(files, rows):
    """Show on the screen the accumulated results of benchmark from the given files

    This assumes that the simulation data is given in kernels"""

    rowstoplot = [row_choiches[row] for row in rows]
    filelist = get_filelist(files)
    data = get_data(filelist, rowstoplot)
    kernels = list(pbpputils.get_kernels(filelist))

    for k in kernels:
        click.echo("Kernel: ")
        click.echo(click.style(k, bold=True))
        for r in rowstoplot:
            click.echo(click.style(r, fg="red", bold=True))
            click.echo(data[k][r])


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="plmdbpp")
def plmdbpp():
    pass


plmdbpp.add_command(kernels)
plmdbpp.add_command(plot)
plmdbpp.add_command(show)
