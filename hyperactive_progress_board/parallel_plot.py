from time import time
import matplotlib
from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import make_interp_spline


plt.locator_params(axis="y", nbins=3)
plt.locator_params(axis="x", nbins=3)


def parallel_plot(
    df, cols, rank_attr, cmap="Spectral", spread=True, curved=True, curvedextend=0.1
):
    # from https://github.com/jraine/parallel-coordinates-plot-dataframe/blob/master/parallel_plot.py

    """Produce a parallel coordinates plot from pandas dataframe with line colour with respect to a column.
    Required Arguments:
        df: dataframe
        cols: columns to use for axes
        rank_attr: attribute to use for ranking
    Options:
        cmap: Colour palette to use for ranking of lines
        spread: Spread to use to separate lines at categorical values
        curved: Spline interpolation along lines
        curvedextend: Fraction extension in y axis, adjust to contain curvature
    Returns:
        x coordinates for axes, y coordinates of all lines"""

    c_time = time()

    colmap = matplotlib.cm.get_cmap(cmap)
    cols = cols + [rank_attr]

    fig, axes = plt.subplots(
        1, len(cols) - 1, sharey=False, figsize=(3 * len(cols) + 3, 5)
    )
    valmat = np.ndarray(shape=(len(cols), len(df)))
    x = np.arange(0, len(cols), 1)
    ax_info = {}

    c_time1 = time()

    for i, col in enumerate(cols):
        vals = df[col]
        if (vals.dtype == float) & (len(np.unique(vals)) > 20):
            minval = np.min(vals)
            maxval = np.max(vals)
            rangeval = maxval - minval
            vals = np.true_divide(vals - minval, maxval - minval)
            nticks = 5
            tick_labels = [
                round(minval + i * (rangeval / nticks), 4) for i in range(nticks + 1)
            ]
            ticks = [0 + i * (1.0 / nticks) for i in range(nticks + 1)]
            valmat[i] = vals
            ax_info[col] = [tick_labels, ticks]
        else:
            vals = vals.astype("category")
            cats = vals.cat.categories
            c_vals = vals.cat.codes
            minval = 0
            maxval = len(cats) - 1
            if maxval == 0:
                c_vals = 0.5
            else:
                c_vals = np.true_divide(c_vals - minval, maxval - minval)
            tick_labels = cats
            ticks = np.unique(c_vals)
            ax_info[col] = [tick_labels, ticks]
            if spread is not None:
                offset = np.arange(-1, 1, 2.0 / (len(c_vals))) * 2e-2
                np.random.shuffle(offset)
                print("\n c_vals", c_vals.shape)
                print(" offset", offset.shape, "\n")

                c_vals = c_vals + offset
            valmat[i] = c_vals

    c_time2 = time()

    extendfrac = curvedextend if curved else 0.05
    for i, ax in enumerate(axes):
        for idx in range(valmat.shape[-1]):
            if curved:
                x_new = np.linspace(0, len(x), len(x) * 20)
                a_BSpline = make_interp_spline(
                    x, valmat[:, idx], k=3, bc_type="clamped"
                )
                y_new = a_BSpline(x_new)
                ax.plot(x_new, y_new, color=colmap(valmat[-1, idx]), alpha=0.3)
            else:
                ax.plot(x, valmat[:, idx], color=colmap(valmat[-1, idx]), alpha=0.3)
        ax.set_ylim(0 - extendfrac, 1 + extendfrac)
        ax.set_xlim(i, i + 1)

    c_time3 = time()

    for dim, (ax, col) in enumerate(zip(axes, cols)):
        ax.xaxis.set_major_locator(ticker.FixedLocator([dim]))
        ax.yaxis.set_major_locator(ticker.FixedLocator(ax_info[col][1]))
        ax.set_yticklabels(ax_info[col][0])
        ax.set_xticklabels([cols[dim]])

    c_time4 = time()

    plt.subplots_adjust(wspace=0)
    norm = matplotlib.colors.Normalize(0, 1)  # *axes[-1].get_ylim())
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cbar = plt.colorbar(
        sm,
        pad=0,
        ticks=ax_info[rank_attr][1],
        extend="both",
        extendrect=True,
        extendfrac=extendfrac,
    )
    if curved:
        cbar.ax.set_ylim(0 - curvedextend, 1 + curvedextend)
    cbar.ax.set_yticklabels(ax_info[rank_attr][0])
    cbar.ax.set_xlabel(rank_attr)
    # plt.show()

    c_time5 = time()

    time1 = c_time1 - c_time
    time2 = c_time2 - c_time1
    time3 = c_time3 - c_time2
    time4 = c_time4 - c_time3
    time5 = c_time5 - c_time4

    print("\n")
    print(" time1:", round(time1, 2))
    print(" time2:", round(time2, 2))
    print(" time3:", round(time3, 2))
    print(" time4:", round(time4, 2))
    print(" time5:", round(time5, 2))
    print(" total time, ", round(c_time5 - c_time, 2))
    print("\n")

    return fig


"""
import numpy as np
from hyperactive import Hyperactive


def ackley_function(para):
    x, y = para["x"], para["y"]

    loss = (
        -20 * np.exp(-0.2 * np.sqrt(0.5 * (x * x + y * y)))
        - np.exp(0.5 * (np.cos(2 * np.pi * x) + np.cos(2 * np.pi * y)))
        + np.exp(1)
        + 20
    )

    return -loss


search_space = {
    "x": list(np.arange(-10, 10, 0.01)),
    "y": list(np.arange(-10, 10, 0.01)),
    "str": ["str1", "str2", "str3"],
}


hyper = Hyperactive()
hyper.add_search(ackley_function, search_space, n_iter=1000)
hyper.run()


search_data = hyper.results(ackley_function)

cols = list(search_data.columns)
cols.remove("score")
rank_attr = "score"

parallel_plot(search_data, cols, rank_attr)
"""
