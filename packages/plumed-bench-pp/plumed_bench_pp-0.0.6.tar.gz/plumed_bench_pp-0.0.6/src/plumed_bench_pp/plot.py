# SPDX-FileCopyrightText: 2024-present Daniele Rapetti <daniele.rapetti@sissa.it>
#
# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from typing import Any

    from matplotlib.container import BarContainer
    from pandas import DataFrame

from matplotlib.pyplot import Axes


def plot_histo(
    ax: Axes,
    data: "list[dict]|dict[str,DataFrame]",
    row: str,
    barwidth: float = 0.8,
    *,
    normalize_to_cycles: "bool|str" = False,
    colors: "list|None" = None,
    relative_to: "dict[str, DataFrame]| Any" = None,
    relative_to_row: "str|None" = None,
    titles: "list[str]|None" = None,
    equidistant_bars: bool = True,
) -> "list[BarContainer]":
    """
    Plot a histogram based on the provided data for a specified row.

    It can be set up to normalize the data to cycles (normalize_to_cycles) and/or relative to another row.
    `normalize_to_cycles` can be either a boolean flag or the name of the row to use as base for the cycles:
    This is useful when using the TOTALTIME row, that is reported as a single cycle.

    It can be set up to use a custom x-axis or colors for the bars.

    It can be set up to plot relative to another dataset, dividing the value of each column by that number.

    Args:
        ax (Axes): The matplotlib axes to plot the histogram.
        data (list[dict]|dict[str,DataFrame]): The data to be plotted.
        row (str): The row in the data to be plotted.
        barwidth (float, optional): The width of the bars in the histogram. Defaults to 0.8.
        normalize_to_cycles (bool|str, optional): Flag to normalize data to cycles, if set to a row name the cycles of that row will be used. Defaults to False.
        colors (list|None, optional): The colors for the bars in the histogram. Defaults to None.
        relative_to (dict[str, DataFrame]| Any, optional): Data for relative comparison, you can pass a dict contianing the collection of data or the address or index of the desired base in the passed data. Defaults to None.
        equidistant_bars (bool, optional):If set to false the center of the groups bars will be in the number of atoms, by default the bars are evenly spaced. Defaults to True.

    Returns:
        list: The list of plotted bars.
    """
    if not isinstance(data, list):
        data = [data]

    row_cycles = row
    if isinstance(normalize_to_cycles, str):
        # row_cycles is introduced because usually the TOTALTIME is a "single cycle"
        # and the info on the effective number of steps is in the timer relative to apply or calculate
        row_cycles = normalize_to_cycles
        normalize_to_cycles = True
    # divideby: "DataFrame|int" = 1
    if relative_to is not None:
        # relative to mode
        if not isinstance(relative_to, dict):
            # in this case relative_to assubed to be the index of the data
            relative_to = data[relative_to]
        if relative_to_row is None:
            relative_to_row = row
        divideby = relative_to[relative_to_row]
        if normalize_to_cycles:
            divideby = divideby.div(relative_to[row_cycles].Cycles, axis="index")
    else:
        divideby = 1

    ncols = len(data)

    xnames = pd.concat([d[row] for d in data]).index.unique()
    xdict = {int(name): i for i, name in enumerate(xnames)}
    num_bars = len(xnames)
    x = np.arange(num_bars) if equidistant_bars else xnames
    width = np.min(np.diff(np.sort(x))) * (barwidth / ncols)
    ax.set_xticks(x + width * 0.5 * (ncols - 1), xnames)
    bars = []
    for multiplier, d in enumerate(data):
        offset = width * multiplier
        toplot = d[row].copy()
        if normalize_to_cycles:
            toplot = toplot.div(d[row_cycles].Cycles, axis="index")
        toplot = toplot.div(divideby, axis="index", fill_value=None).dropna().Total.values

        xpos = x
        if len(x) != len(d[row]):
            if equidistant_bars:
                xpos = []
                for xname in d[row].index.values:
                    xpos.append(xdict[int(xname)])
                xpos = np.array(xpos)
            else:
                xpos = d[row].index.values
        bars.append(
            ax.bar(
                xpos + offset,
                toplot,
                width,
                color=colors[multiplier] if colors else None,
                label=titles[multiplier] if titles else None,
            )
        )
    return bars


def plot_histo_relative(
    ax: Axes,
    data: "list[dict]|dict[str,DataFrame]",
    row: str,
    relative_to: "dict[str, DataFrame]| Any",
    relative_to_row: "str|None" = None,
    barwidth: float = 0.8,
    **kwargs,
) -> "list[BarContainer]":
    """
    Plots a histogram of the given data relative to the `relative_to` data.

    Args:
        ax (matplotlib.axes.Axes): The axes on which to plot the histogram.
        data (list[dict] | dict[str, pandas.DataFrame]): The data to plot. It can be a list of dictionaries where each
            dictionary contains a DataFrame indexed by the name of a kernel. Alternatively, it can be a single dictionary
            where the keys are the names of the kernels and the values are the corresponding DataFrames.
        row (str): The row to plot.
        relative_to (dict[str, pandas.DataFrame] | Any): The data to which the values of the current data are relative to.
            It can be a dictionary where the keys are the names of the kernels and the values are the corresponding DataFrames.
            Alternatively, it can be a string representing the name of a kernel in the `data` dictionary.
        relative_to_row (str | None): The row in the `relative_to` data to use for the reference values. If None, the row
            specified by `row` is used.
        barwidth (float): The width of the bars in the histogram.
        **kwargs: Additional keyword arguments passed to `plot_histo`.

    Returns:
        list[matplotlib.container.BarContainer]: The bars plotted in the histogram.

    See Also:
        plot_histo: A function that plots a histogram of the given data.
    """
    return plot_histo(
        ax,
        data,
        row,
        barwidth=barwidth,
        relative_to=relative_to,
        relative_to_row=relative_to_row,
        **kwargs,
    )
