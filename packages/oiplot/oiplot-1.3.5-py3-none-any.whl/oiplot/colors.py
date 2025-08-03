from typing import List

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps as mcm
from matplotlib.colors import ListedColormap

cmap = plt.get_cmap("inferno")
new_colors = np.vstack(([1, 1, 1, 1], cmap(np.linspace(0, 1, 256))))
winferno = ListedColormap(new_colors, name="winferno")
mpl.colormaps.register(cmap=winferno)


def convert_style_to_colormap(style: str) -> ListedColormap:
    """Converts a style into a colormap."""
    plt.style.use(style)
    colormap = ListedColormap(plt.rcParams["axes.prop_cycle"].by_key()["color"])
    plt.style.use("default")
    return colormap


def get_colormap(colormap: str) -> ListedColormap:
    """Gets the colormap as the matplotlib colormaps or styles."""
    try:
        return mcm.get_cmap(colormap)
    except ValueError:
        return convert_style_to_colormap(colormap)


def get_colorlist(colormap: str, ncolors: int | None) -> List[str]:
    """Gets the colormap as a list from the matplotlib colormaps."""
    return [get_colormap(colormap)(i) for i in range(ncolors)]
