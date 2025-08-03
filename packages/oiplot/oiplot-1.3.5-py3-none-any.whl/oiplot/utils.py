from pathlib import Path
from types import SimpleNamespace
from typing import Any, Tuple

import astropy.units as u
import numpy as np
import yaml
from matplotlib.axes import Axes
from numpy.typing import NDArray


PREFIXES = np.load(Path(__file__).parent / "config" / "prefixes.npy").tolist()


def get_prefix(value: u.Quantity) -> str:
    """Gets the correct prefix for the unit."""
    base = value.decompose().value
    for prefix, exp in zip(PREFIXES, range(-27, 33, 3)):
        if base < 10**exp:
            return prefix
    return PREFIXES[-1]


def get_figsize(
    textwidth: float = 7.24551,
    aspect_ratio: float = 6 / 8,
    scale: float = 1.0,
):
    """Gets the figsize for a certain textwidth.credits

    Returns
    -------
    width : float
    height : float

    Notes
    -----
    Default is the A&A two-column layout.
    """
    width = textwidth * scale
    return width, width * aspect_ratio


# TODO: Make this possible for 2D as well
def rotate(x: Any, y: Any, pa: float):
    """Rotates the points for a certain angle."""
    return (
        np.vstack([x, y]).T
        @ np.array([[np.cos(pa), -np.sin(pa)], [np.sin(pa), np.cos(pa)]])
    ).T


def get_extent(dim: int, pixel_size: float = 1.0) -> NDArray[Any]:
    """Gets the extent of a grid/image."""
    return np.array([-1, 1, -1, 1]) * 0.5 * dim * pixel_size


def read_yaml_to_namespace(file_name: Path) -> SimpleNamespace:
    """Reads a yaml file and returns a dictionary.
    Also converts all units from strings to astropy.units.
    """
    with open(file_name, "r") as file:
        content = yaml.safe_load(file)

    for key, val in content.items():
        if not isinstance(val, dict):
            continue

        for k, v in val.items():
            if "unit" in k:
                if isinstance(v, dict):
                    v = {i: u.Unit(j) for i, j in v.items()}
                else:
                    v = u.Unit(v)

            content[key][k] = SimpleNamespace(**v) if isinstance(v, dict) else v
        content[key] = SimpleNamespace(**val) if isinstance(val, dict) else val

    return SimpleNamespace(**content)


def inset_at_point(
    ax: Axes,
    x: int | float,
    y: int | float,
    width: int | float,
    height: int | float,
) -> Axes:
    """Insets a plot into an axis at certain data coordinates.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
    x : int or float
    y : int or float
    width : int or float
    height : int or float
    """
    return ax.inset_axes(
        (x - width / 2, y - height / 2, width, height), transform=ax.transData
    )


# TODO: Add colorbar support here (and setting limits via the collections)
def _axplot(
    ax: Axes,
    x: NDArray,
    y: NDArray,
    yerr: NDArray,
    z: NDArray | None = None,
    errorbar: bool = False,
    **kwargs,
):
    """Plots data onto an ax."""
    show_axis = kwargs.pop("show_axis", True)
    width, height = kwargs.pop("inset_width", 0.2), kwargs.pop("inset_height", 0.2)
    if (inset_point := kwargs.pop("inset_point", None)) is not None:
        ax = inset_at_point(ax, *inset_point, width, height)
        ax.axis("on" if show_axis else "off")

    line = ax.plot(x, y, **kwargs)[0]
    if errorbar:
        ax.fill_between(
            x,
            y + yerr,
            y - yerr,
            alpha=kwargs.get("alpha", 0.5),
            color=line.get_color(),
        )


def get_plot_layout(nplots: int) -> Tuple[int, int]:
    """Gets the best plot arrangement for a given number of plots."""
    sqrt_nplots = np.sqrt(nplots)
    rows, cols = int(np.floor(sqrt_nplots)), int(np.ceil(sqrt_nplots))

    while rows * cols < nplots:
        if cols < rows:
            cols += 1
        else:
            rows += 1

    while (rows - 1) * cols >= nplots:
        rows -= 1

    return rows, cols


def transform_coordinates(
    x: float | np.ndarray,
    y: float | np.ndarray,
    cinc: float | None = 1,
    pa: float = 0,
    axis: str = "y",
) -> Tuple[float | np.ndarray, float | np.ndarray]:
    """Stretches and rotates the coordinate space depending on the
    cosine of inclination and the positional angle.

    Parameters
    ----------
    x: float or numpy.ndarray or astropy.units.Quantity
        The x-coordinate.
    y: float or numpy.ndarray or astropy.units.Quantity
        The y-coordinate.
    cinc: float, optional
        The cosine of the inclination.
    pa: float, optional
        The positional angle of the object (in degree).
    axis: str, optional
        The axis to stretch the coordinates on.

    Returns
    -------
    xt: float or numpy.ndarray
        Transformed x coordinate.
    yt: float or numpy.ndarray
        Transformed y coordinate.
    """
    xt, yt = rotate(x, y, pa)
    if cinc is not None:
        if axis == "x":
            xt /= cinc
        elif axis == "y":
            xt *= cinc

    return xt, yt
