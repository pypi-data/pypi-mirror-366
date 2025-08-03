import copy
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Dict, List

import astropy.units as u
import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.utils.masked import Masked

# TODO: Find a better way to do this grep or such
KEY_TO_ATTRIBUTE = {
    "date": "date-obs",
    "instrument": "instrume",
    "tpl_start": "hierarch eso tpl start"
}


def read(
    files_or_hduls: Path | fits.HDUList | Iterable[Path | List[fits.HDUList]],
) -> List[fits.HDUList]:
    """Reads a list of fits files into hduls and copies them (skips already opened hduls)."""
    if not isinstance(files_or_hduls, Iterable):
        files_or_hduls = [files_or_hduls]

    hduls = []
    for fits_file in files_or_hduls:
        if isinstance(fits_file, fits.HDUList):
            hdul = fits_file
        elif isinstance(fits_file, Path):
            with fits.open(fits_file) as hdul:
                hdul = copy.deepcopy(hdul)
        else:
            raise ValueError(
                "Input must be a Path or HDUList or an iterable containing those."
            )

        hduls.append(hdul)
    return hduls


def sort(hduls: List[fits.HDUList], by: str | List[str]) -> List[fits.HDUList]:
    by = [by] if not isinstance(by, (tuple, list, np.ndarray)) else by
    data = {
        "index": range(len(hduls)),
        **{key: [_get_header_entry(hdul, key) for hdul in hduls] for key in by},
    }
    return [hduls[i] for i in pd.DataFrame(data).sort_values(by=by)["index"].tolist()]


def filter(hduls: List[fits.HDUList], conditions: Dict[str, Any]) -> List[fits.HDUList]:
    df = pd.DataFrame(
        {
            "index": range(len(hduls)),
            **{
                key: [
                    _get_header_entry(hdul, key)
                    for key in conditions.keys()
                    for hdul in hduls
                ]
            },
        }
    )

    for key, value in conditions.items():
        df = df[df[key] == value]

    return [hduls[i] for i in df["index"].tolist()]


# TODO: Write these into the get
def _get_stations(hdul: fits.HDUList, extension: str) -> List[str]:
    """Gets the station names from the hdul for an extension."""
    sta_index = _get_column(hdul, extension, "sta_index", unit=False)
    sta_index_to_name = dict(
        zip(
            _get_column(hdul, "oi_array", "sta_index", unit=False).tolist(),
            _get_column(hdul, "oi_array", "sta_name", unit=False),
        )
    )
    return list(
        map(lambda x: "-".join(x), np.vectorize(sta_index_to_name.get)(sta_index))
    )


# TODO: Write these into the get
def _get_header_entry(
    hdul: List[fits.HDUList], key: str, extension: str | int = 0
) -> List[str]:
    """Gets an entry from the hdul's specified header. Default is the primary header."""
    content = hdul[extension].header.get(KEY_TO_ATTRIBUTE.get(key, key).upper(), "")
    if key == "date":
        content = content.split("T")[0]
    return content


# TODO: Write these into the get
def _get_hdu(
    hdul: fits.HDUList,
    name: str,
    index: int | None = None,
) -> fits.BinTableHDU | None:
    """Gets an extension from the hdul."""
    try:
        return hdul[name, index]
    except (KeyError, IndexError):
        return None


# TODO: Write these into the get
def _get_column(
    hdul: fits.HDUList,
    extension: str,
    column: str,
    index: int | None = None,
    masked: bool = False,
    unit: bool = True,
) -> Any:
    """Gets a column from the hdul."""
    hdu = _get_hdu(hdul, extension, index)
    try:
        values = hdu.data[column]
        if masked:
            values = Masked(values, mask=hdu.data["flag"])
        if unit:
            # TODO: This could be problematic with the index?
            key = [k for k, v in hdu.header.items() if column.upper() == v][0]
            index_key = int("".join([c for c in key if c.isdigit()]))
            unit = hdu.header[f"TUNIT{index_key}"]
            if unit.lower() in ["adu"]:
                unit = unit.lower()
            values *= u.Unit(unit)

        return values
    except (AttributeError, KeyError):
        return None


# TODO: Finish this
def get(hdul: fits.HDUList, key: str) -> Any:
    """Returns the value of the keyword in the header.

    Parameters
    ----------
    key : str
        Can be any (case-insensitve ) OIFITS2 keyword (e.g. "OI_VIS", "VISAMP") or
        a combination in the following way "OI_VIS.header.<header_key>",
        "OI_VIS.VISAMP", etc.
    """
    ...


# TODO: Finish this
def set(hdul: fits.HDUList, key: str, value: Any) -> None:
    """Sets arrays or units for the keyword in the header.

    Parameters
    ----------
    key : str
        Can be any (case-insensitve ) OIFITS2 keyword (e.g. "OI_VIS", "VISAMP") or
        a combination in the following way "OI_VIS.header.<header_key>",
        "OI_VIS.VISAMP", etc.
    value : any
        The value to be set.
    """
    ...


def get_labels(hduls: List[fits.HDUList]) -> List[str]:
    return [f"{chr(ord('A') + i)}" for i, _ in enumerate(hduls)]
