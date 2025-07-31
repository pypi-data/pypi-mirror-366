import numpy as np
import matplotlib.pyplot as plt


def draw_cells(cflag, ax=None):
    """Plots lit/dark cells"""
    Y, X = np.mgrid[0:12, 0:33]
    C = np.pad(
        cflag.astype(int), [0, 352-cflag.size],
        constant_values=7
    ).reshape(11, 32)

    if ax is None:
        fig, ax = plt.subplots(
            1, 1, figsize=(10, 4), tight_layout=True, dpi=200
        )
    ax.pcolor(
        X-0.5, Y-0.5, C, cmap=plt.cm.tab10,
        edgecolors='w', lw=0.5, vmin=0, vmax=9
    )
    ax.set_aspect(1)
    ax.set_title('Lit cells', fontsize=8)
    ax.tick_params(axis='both', labelsize=8)
    ax.yaxis.set_ticks(range(0, 11))
    ax.yaxis.set_ticklabels(range(0, 321, 32))
    ax.xaxis.set_ticks(range(3, 33, 4))

    return ax
