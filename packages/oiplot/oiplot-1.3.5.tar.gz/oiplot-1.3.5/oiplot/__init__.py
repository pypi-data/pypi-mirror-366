import matplotlib.projections as proj

from . import colors, io, orbit, shapes, utils
from .oifits import Oifits

proj.register_projection(Oifits)

__version__ = "1.3.5"
__all__ = ["io", "colors", "oifits", "orbit", "shapes", "utils"]
