from pathlib import Path
from typing import List, Tuple

import astropy.units as u
import matplotlib
import matplotlib.lines as mlines
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from astropy.io import fits
from astropy.visualization import quantity_support
from matplotlib.axes import Axes

from . import io
from .colors import get_colorlist
from .utils import (
    _axplot,
    get_plot_layout,
    get_prefix,
    read_yaml_to_namespace,
    transform_coordinates,
)

quantity_support()
plt.style.use(["science", "vibrant"])
matplotlib.rcParams.update(
    {
        "font.family": "serif",
        "image.resample": False,
        "pgf.texsystem": "pdflatex",
        "pgf.rcfonts": False,
        "savefig.bbox": "tight",
        "text.usetex": True,
        "text.latex.preamble": r"\usepackage{siunitx}",
    }
)

# TODO: Rename columns to a more appropriate name at some point
COLUMNS = read_yaml_to_namespace(Path(__file__).parent / "config" / "columns.yaml")
COLORS = plt.rcParams["axes.prop_cycle"].by_key()["color"]


def get_label(column: str, unit: str) -> str:
    """Sets the label."""
    # HACK: Very specific case, better solution possible?
    unit = unit.replace(r"\mu m", r"\si{\micro\metre}")
    return f"$ {column.label} $ ({unit})"


def get_baseline_and_angle(
    hdul, ext: str, index: int | None = None
) -> Tuple[u.Quantity, u.Quantity]:
    """Computes baseline and angle from (u, v)-coordinates of an extension."""
    if "vis" in ext:
        x = io._get_column(hdul, ext, "ucoord", index)
        y = io._get_column(hdul, ext, "vcoord", index)
    elif "t3" in ext:
        x, y = [], []
        for i in range(1, 3):
            x.append(io._get_column(hdul, ext, f"u{i}coord", index))
            y.append(io._get_column(hdul, ext, f"v{i}coord", index))

        x.append(x[0] + x[1])
        y.append(y[0] + y[1])
        x, y = u.Quantity(x), u.Quantity(y)
    else:
        # TODO: Raise some error here
        ...

    baseline, angle = np.hypot(x, y), np.arctan2(x, y)
    if "t3" in ext:
        index_longest = np.argmax(baseline, axis=0)
        baseline = [b[i] for i, b in zip(index_longest, baseline.T)]
        angle = [a[i] for i, a in zip(index_longest, angle.T)]

    return u.Quantity(baseline), u.Quantity(angle)


def get_spatial_frequency(
    wl: u.Quantity, baseline: u.Quantity, unit: str = "Mlam"
) -> u.Quantity:
    """Computes spatial frequency from baseline (considering unit)."""
    sp_freq = baseline.reshape(-1, 1) / wl
    match unit:
        case "cycles/mas":
            factor = u.mas.to(u.rad)
        case "cycles/arcsec":
            factor = u.arcsec.to(u.rad)
        case "Mlam":
            factor = 1e-6
        case _:
            factor = 1

    return factor * sp_freq


class Oifits(Axes):
    """Class derived from matplotlib.axes.Axes that allows easy plotting of oifits data"""

    name = "Oifits"
    xtype, ytype = None, None
    colorbar = None

    def axis_presets(self, *columns, **kwargs) -> None:
        """Sets the default values for the axis."""
        if kwargs.get("legend", False):
            self.legend(**kwargs["legend"])

        self.set_xlabel(kwargs.get("xlabel", get_label(columns[0], self.get_xlabel())))
        self.set_ylabel(kwargs.get("ylabel", get_label(columns[1], self.get_ylabel())))
        self.set_xlim(kwargs.get("xlim", columns[0].lim))
        self.set_ylim(kwargs.get("ylim", columns[1].lim))

    # TODO: Implement the tracks again.
    # TODO: Implement here indicies like GRAVITY needs them
    def uv(
        self,
        hduls: List[fits.HDUList],
        model_hduls: List[fits.HDUList] | None = None,
        color_by: str = "date",
        overlay: str = "station",
        isolines: bool = True,
        tracks: bool = False,
        **kwargs,
    ) -> Axes:
        """Plots the uv coverage.

        Parameters
        ----------
        hduls : list of astropy.io.fits.HDUList
        model_hduls : list of astropy.io.fits.HDUList, optional
            A list of HDULists with model data to plot. The model hduls have to
            be in the same order as the hduls.
        color_by : str, optional
            The coloring of the uv points. Can be "file"/"date", "instrument", or "station".
            Default is "date" (i.e. the "file").
        overlay : str, optional
            If the uv points should be overlayed with something.
            Possible options are "number" (for a file based numbering), "station" for the station names,
            or "visamp", "vis2data" for plots of the visibilities or squared visibilities.
            In case of "visamp" it will display the "visphi" on the mirrored side.
            Default is "station".
        legend : bool, optional
            If the legend should be displayed.

        """
        column_x, column_y = COLUMNS.u, COLUMNS.v
        match color_by:
            case "instrument":
                instruments = [
                    io._get_header_entry(hdul, "instrument") for hdul in hduls
                ]
                legend_labels = []
                for entry in instruments:
                    if entry not in legend_labels:
                        legend_labels.append(entry)
            case "date" | "file" | _:
                legend_labels = [io._get_header_entry(hdul, "date") for hdul in hduls]

        colors = dict(zip(legend_labels, COLORS))
        inset_amps, inset_phis = [], []
        file_letters = io.get_labels(hduls)
        for file_index, hdul in enumerate(hduls):
            ucoord = io._get_column(hdul, "oi_vis2", "ucoord")
            vcoord = io._get_column(hdul, "oi_vis2", "vcoord")

            if color_by == "station":
                color = COLORS[: len(ucoord)] * 2
            else:
                color = colors[io._get_header_entry(hdul, color_by)]

            line = self.scatter(
                u.Quantity([ucoord, -ucoord]),
                u.Quantity([vcoord, -vcoord]),
                s=kwargs.get("markersize", 5),
                marker="x",
                color=color,
            )

            labels = []
            if overlay in ["number", "station"]:
                if overlay == "number":
                    labels = [
                        f"{file_letters[file_index]}.{i + 1}"
                        for i in np.arange(ucoord.size)
                    ]
                elif overlay == "station":
                    labels = io._get_stations(hdul, "vis2")

                for label_index, label in enumerate(labels):
                    self.annotate(
                        label,
                        xy=(ucoord[label_index], vcoord[label_index]),
                        xytext=(0.5, 2.0),
                        textcoords="offset points",
                        fontsize=6,
                        color="black",
                    )
            elif any(x in overlay for x in ["visamp", "vis2data"]):
                # TODO: Rewrite this with better globals (e.g. that have "oi_vis" info)
                x = io._get_column(hdul, "oi_wavelength", "eff_wave")
                xlims = (np.min(x), np.max(x))
                yphi, yphierr, ymodelphi = None, None, None
                if "visamp" in overlay:
                    y = io._get_column(hdul, "oi_vis", "visamp", masked=True)
                    yerr = io._get_column(hdul, "oi_vis", "visamperr", masked=True)
                    if "only" not in overlay:
                        yphi = io._get_column(hdul, "oi_vis", "visphi", masked=True)
                        yphierr = io._get_column(
                            hdul, "oi_vis", "visphierr", masked=True
                        )
                    if model_hduls is not None:
                        ymodel = io._get_column(
                            model_hduls[file_index], "oi_vis", "visamp", masked=True
                        )
                        ymodelphi = io._get_column(
                            model_hduls[file_index], "oi_vis", "visphi", masked=True
                        )
                else:
                    # TODO: Rewrite this with better globals (e.g. that have "oi_vis" info)
                    y = io._get_column(hdul, "oi_vis2", "vis2data", masked=True)
                    yerr = io._get_column(hdul, "oi_vis2", "vis2err", masked=True)
                    if model_hduls is not None:
                        ymodel = io._get_column(
                            model_hduls[file_index], "oi_vis2", "vis2data", masked=True
                        )

                # TODO: At some point replace this with the `visualise` method
                for amp_index, amp in enumerate(y):
                    inset_kwargs = {
                        "color": line[0].get_color(),
                        "inset_width": kwargs.pop("inset_width", 20),
                        "inset_height": kwargs.pop("inset_height", 20),
                        "show_axis": kwargs.pop("show_axis", False),
                        "linewidth": kwargs.pop("linewidth", 0.5),
                        "errorbar": kwargs.pop("errorbar", True),
                    }
                    inset_amp = _axplot(
                        self,
                        x,
                        amp,
                        yerr[amp_index],
                        inset_point=(ucoord[amp_index], vcoord[amp_index]),
                        **inset_kwargs,
                    )
                    inset_amp.axhline(0, color="grey", linestyle="--", linewidth=0.35)
                    if model_hduls is not None:
                        inset_amp.plot(
                            x,
                            ymodel[amp_index],
                            color="black",
                            alpha=0.8,
                            linewidth=0.23,
                            zorder=5,
                        )

                    inset_amp.set_xlim(xlims)
                    inset_amps.append(inset_amp)
                    if yphi is not None:
                        inset_phi = _axplot(
                            self,
                            x,
                            yphi[amp_index],
                            yphierr[amp_index],
                            inset_point=(-ucoord[amp_index], -vcoord[amp_index]),
                            **inset_kwargs,
                        )
                        if ymodelphi is not None:
                            inset_phi.plot(
                                x,
                                ymodelphi[amp_index],
                                color="black",
                                alpha=0.8,
                                linewidth=0.23,
                                zorder=5,
                            )
                        inset_phi.axhline(
                            0, color="grey", linestyle="--", linewidth=0.35
                        )
                        self = _axplot(
                            self, x, y[amp_index], yerr[amp_index], **inset_kwargs
                        )
                        inset_phi.set_xlim(xlims)
                        inset_phis.append(inset_phi)

        if inset_amps:
            amp_bounds = np.array([amp_ax.get_ylim() for amp_ax in inset_amps])
            amp_lims = np.min(amp_bounds[:, 0]), np.max(amp_bounds[:, 1])
            [amp_ax.set_ylim(amp_lims) for amp_ax in inset_amps]

        if inset_phis:
            phi_bounds = np.array([phi_ax.get_ylim() for phi_ax in inset_phis])
            # TODO: Make it so that the user can input their own lims
            # phi_lims = np.min(phi_bounds[:, 0]), np.max(phi_bounds[:, 1])
            [phi_ax.set_ylim([-20, 20]) for phi_ax in inset_phis]

        handles = []
        for legend_label, color in zip(
            legend_labels, colors.values() if isinstance(colors, dict) else colors
        ):
            handles.append(
                mlines.Line2D(
                    [],
                    [],
                    color=color,
                    marker="X",
                    linestyle="None",
                    label=legend_label,
                    markersize=4,
                    markeredgewidth=1,
                )
            )

        self.plot(0, 0, "+", color="grey", markersize=4, markeredgewidth=1)

        if isolines:
            for radius in np.arange(0, np.abs(column_x.lim).max() + 50, 50):
                self.add_patch(
                    patches.Circle(
                        (0, 0),
                        radius,
                        fill=False,
                        edgecolor="green",
                        linewidth=0.5,
                        linestyle="--",
                    )
                )

        plt.gca().invert_xaxis()
        self.set_aspect("equal")

        legend = kwargs.get("legend", True)
        kwargs_legend = {"handles": handles, "fontsize": "small", "loc": "upper right"}
        self.axis_presets(
            column_x,
            column_y,
            **{**kwargs, "legend": kwargs_legend if legend else legend},
        )
        return self

    def visualise(
        self,
        hduls: fits.HDUList | List[fits.HDUList],
        xname: str,
        yname: str,
        cname: str | None = None,
        index: int | None = None,
        **kwargs,
    ):
        """Plots all the specified observables in a collage.

        Parameters
        ----------
        """
        self.xtype, self.ytype, self.cname = xname, yname, cname
        column_x, column_y = getattr(COLUMNS, xname), getattr(COLUMNS, yname)
        for hdul in hduls:
            if io._get_hdu(hdul, ext := column_y.ext, index) is None:
                continue

            wl = io._get_column(hdul, "oi_wavelength", "eff_wave", index, unit=True)
            ydata = io._get_column(hdul, ext, yname, index, masked=True)
            yerr = io._get_column(hdul, ext, column_y.err, index, masked=True)
            match xname:
                case "length":
                    xdata, _ = get_baseline_and_angle(hdul, ext, index)
                case "spa_freq":
                    xdata = get_spatial_frequency(
                        wl, get_baseline_and_angle(hdul, ext, index)[0]
                    )
                case "pa":
                    _, xdata = get_baseline_and_angle(hdul, ext, index)
                case "eff_wave" | _:
                    xdata = wl.to(f"{get_prefix(wl.min())}{wl.decompose().unit}")

            # TODO: Implement colorbar with `cname`
            if cname is not None:
                ...

            if cname is not None:
                ...

            # TODO: Implement big plot for all of the files (for spatial frequencies)
            for val, err in zip(ydata, yerr):
                _axplot(self, xdata, val, err, errorbar=True)

        # TODO: Implement error if the types are different (corr vs. abs for multiple files)
        match yname:
            case "visamp":
                amptype = io._get_header_entry(hduls[0], "amptyp", column_y.ext)
                column_y = column_y.corr if "corr" in amptype else column_y.abs
            case "visphi":
                phitype = io._get_header_entry(hduls[0], "phityp", column_y.ext)
                column_y = column_y.diff if "diff" in phitype else column_y.abs
        self.axis_presets(column_x, column_y, **kwargs)
        return self


# TODO: Make it so that overcrowding in this plot is averted… But how?
# TODO: Reimplement sorting for shortest to longest baseline
def _vs_spf(
    hduls: List[fits.HDUList],
    observable: str,
    model_hduls: List[fits.HDUList] | None = None,
    ylims: List[float] | None = None,
    max_plots: int = 20,
    number: bool = False,
    legend: bool = True,
    transparent: bool = False,
    savefig: Path | None = None,
    **kwargs,
) -> None:
    """Plots the observables of the model.

    Parameters
    ----------
    hduls : list of astropy.io.fits.HDUList
        A list of HDULists to plot.
    observable : str, optional
        The observable to plot. "visamp", "visphi", "t3phi" and "vis2data" are available.
    model_hduls : list of astropy.io.fits.HDUList, optional
        A list of HDULists with model data to plot. The model hduls have to
        be in the same order as the hduls.
    ylims : list of float, optional
        The y-axis limits for the plots.
    max_plots : int, optional
        The maximal number of plots to show.
    number : bool, optional
        If the plots should be numbered.
    transparent : bool, optional
        If the plots should be transparent.
    savefig : Path, optional
        The save file for the plots.
    """
    wls, stations, labels, file_letters = [], [], [], io.get_labels(hduls)
    spfs, psis, vals, errs, model_vals = [], [], [], [], []

    extension, column, amptype = EXTENSIONS[observable], COLUMNS[observable], ""
    for index, hdul in enumerate(hduls):
        if observable in ["visamp", "visphi"]:
            ampentry = io._get_header_entry(hduls[0], "amptyp", extension)
            if "corr" in ampentry or "diff" in ampentry:
                amptype = "corr"
            else:
                amptype = "abs"

        val = io._get_column(hdul, extension, observable, masked=True)
        err = io._get_column(hdul, extension, column["err"], masked=True)
        if model_hduls is not None:
            model_vals.extend(io._get_column(model_hduls[index], extension, observable))

        label = [f"{file_letters[index]}.{i + 1}" for i in range(val.shape[0])]
        sta_index = io._get_column(hdul, extension, "sta_index")
        sta_index_to_name = dict(
            zip(
                io._get_column(hdul, "oi_array", "sta_index").tolist(),
                io._get_column(hdul, "oi_array", "sta_name"),
            )
        )
        station = list(
            map(lambda x: "-".join(x), np.vectorize(sta_index_to_name.get)(sta_index))
        )
        wls.extend(
            [io._get_column(hdul, "oi_wavelength", "eff_wave") for _ in range(len(val))]
        )
        if observable in ["visamp", "visphi", "vis2data"]:
            x = io._get_column(hdul, extension, "ucoord")
            y = io._get_column(hdul, extension, "vcoord")
        else:
            x1, x2 = map(
                lambda x: io._get_column(hdul, "oi_t3", x), ["u1coord", "u2coord"]
            )
            y1, y2 = map(
                lambda x: io._get_column(hdul, "oi_t3", x), ["v1coord", "v2coord"]
            )
            x123, y123 = np.array([x1, x2, x1 + x2]), np.array([y1, y2, y1 + y2])

            spf = np.hypot(x123, y123)
            longest_ind = (np.arange(spf.T.shape[0]), np.argmax(spf.T, axis=1))
            x, y = x123.T[longest_ind], y123.T[longest_ind]

        ut, vt = transform_coordinates(x, y)
        spf, psi = np.hypot(ut, vt), np.rad2deg(np.arctan2(ut, vt))

        vals.extend(val)
        errs.extend(err)
        spfs.extend(spf)
        psis.extend(psi)
        labels.extend(label)
        stations.extend(station)

    label_colors = np.unique([label.split(".")[0] for label in labels])
    label_colors = dict(zip(label_colors, get_colorlist("tab20", len(label_colors))))

    rows, cols = get_plot_layout(max_plots)
    fig, axarr = plt.subplots(
        rows,
        cols,
        figsize=(cols * 4, rows * 4),
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )

    for index, (ax, b, psi) in enumerate(zip(axarr.flat, spfs, psis)):
        line = ax.plot(
            wls[index],
            vals[index],
            color=label_colors[labels[index].split(".")[0]],
            label=rf"{stations[index]}, B={b:.2f} m, $\psi$={psi:.2f}$^\circ$",
        )
        ax.fill_between(
            wls[index],
            vals[index] + errs[index],
            vals[index] - errs[index],
            color=line[0].get_color(),
            alpha=0.5,
        )
        if model_vals:
            ax.plot(wls[index], model_vals[index], color="black", label="Model")

        # TODO: Switch this here to annotate?
        if number:
            ax.text(
                0.05,
                0.95,
                labels[index],
                transform=ax.transAxes,
                fontsize=14,
                fontweight="bold",
                va="top",
                ha="left",
            )
        if legend:
            ax.legend()

    bounds = np.array([ax.get_ylim() for ax in axarr.flat])
    ymin, ymax = np.min(bounds[:, 0]), np.max(bounds[:, 1])
    if ylims is None:
        ylims = column["ylims"] if not amptype else column["ylims"][amptype]
        if ylims[0] is not None:
            ylims[0] = ymin - ymin * 0.25
        if ylims[1] is not None:
            ylims[1] = ymax - ymax * 0.25

    [ax.remove() if not ax.has_data() else ax.set_ylim(ylims) for ax in axarr.flat]

    fig.supxlabel(r"$ \lambda (\si{\metre}) $", fontsize=16)
    fig.supylabel(
        column["label"] if not amptype else column["label"][amptype], fontsize=16
    )
    if savefig is not None:
        plt.savefig(
            savefig,
            format=savefig.suffix[1:],
            dpi=300,
            transparent=transparent,
            bbox_inches="tight",
        )
    else:
        plt.show()
    plt.close()
