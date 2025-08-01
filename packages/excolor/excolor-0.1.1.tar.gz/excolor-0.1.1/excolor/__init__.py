# -*- coding: utf-8 -*-
"""
Extended colors for python.

This package provides tools for working with colors, gradients, and image processing
in Python. It includes functionality for creating and manipulating color maps,
generating gradients, processing images, and more.
"""

from .patch import *
from .palette import *
from .gradient import *
from .imagetools import *
from .wallpaper import *
from .colortools import *
from .colortypes import *
from .cmaptools import *
from .utils import interpolate_colors
from .cmaptools import _add_extended_colormaps

try:
    from pkg_resources import get_distribution
    __version__ = get_distribution("excolor").version
except Exception:
    __version__ = "0.1.0"

_add_extended_colormaps()
del _add_extended_colormaps