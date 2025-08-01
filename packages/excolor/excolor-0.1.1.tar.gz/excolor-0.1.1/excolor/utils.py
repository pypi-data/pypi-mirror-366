#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains utility functions for colortools and cmaptools.
"""

import os
import re
import numpy as np
import pandas as pd
from typing import Any, Union, Optional, List, Tuple
import matplotlib.colors as mc
from matplotlib.colors import LinearSegmentedColormap, Colormap
from matplotlib import colormaps
from matplotlib.colors import ListedColormap

import warnings
import numpy as np
warnings.filterwarnings("ignore")



_RICH_COLOR_NAMES = None

def _load_rich_color_names():
    """
    Loads the rich color data from the CSV file, caching it in memory.

    This function reads a CSV file containing color names and their corresponding
    RGB values. The data is loaded only once and then cached in a global
    variable `_RICH_COLOR_NAMES` for subsequent calls to avoid repeated file I/O.

    Returns
    -------
    dict
        A dictionary containing two keys:
        - 'names': A numpy array of color names.
        - 'rgbs': A numpy array of RGB values.
    """
    global _RICH_COLOR_NAMES
    if _RICH_COLOR_NAMES is None:
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'colornames.csv')
        df = pd.read_csv(data_path)
        _RICH_COLOR_NAMES = {
            'names': df['name'].to_numpy(),
            'rgbs': df[['R', 'G', 'B']].to_numpy()
        }
    return _RICH_COLOR_NAMES


def get_color_name(color: Any) -> str:
    """
    Finds the closest color name from the rich color dataset for a given color.

    This function converts the input color to RGB, then uses a vectorized
    numpy operation to efficiently find the color with the minimum Euclidean
    distance in the RGB space from a pre-compiled list of over 9,000 colors.

    Parameters
    ----------
    color : Any
        The input color in any format supported by `to_rgb255`.

    Returns
    -------
    str
        The closest matching color name.
    """
    color_data = _load_rich_color_names()
    names = color_data['names']
    rgbs = color_data['rgbs']

    # Convert input color to RGB [0, 255] format
    input_rgb = 255 * np.array(mc.to_rgb(color))

    # Calculate Euclidean distance in a vectorized way
    distances = np.sqrt(np.sum((rgbs - input_rgb) ** 2, axis=1))

    # Find the index of the minimum distance
    closest_idx = np.argmin(distances)

    return names[closest_idx]


def _aspect_ratio(length: int, lmin: int = 0) -> Tuple[int, int]:
    """
    Calculates the optimal grid dimensions for displaying a sequence of items.

    This function determines the best number of rows and columns to arrange
    a given number of items in a grid layout, with the goal of creating a
    visually pleasing aspect ratio close to 5:1 (width:height).

    Parameters
    ----------
    length : int
        Total number of items to arrange in the grid
    lmin : int, default=0
        Minimum number of items required to split into multiple rows.
        If length <= lmin, all items will be placed in a single row.

    Returns
    -------
    tuple of int
        A tuple (n, m) where:
        - n: Number of columns in the grid
        - m: Number of rows in the grid

    Notes
    -----
    The function:
    1. Calculates an initial estimate for the number of columns
    2. Tests various grid configurations around this estimate
    3. Selects the configuration that:
       - Minimizes empty spaces
       - Has an aspect ratio closest to 5:1
       - Has more columns than rows

    Examples
    --------
    >>> _aspect_ratio(12)  # For 12 items
    (6, 2)  # 6 columns, 2 rows
    >>> _aspect_ratio(8, lmin=10)  # Few items, below minimum
    (8, 1)  # Single row
    """
    if length > 0:
        d = np.array([-2, -1, 0, 1, 2])
        n0 = np.sqrt(length / 2)
        ns = []
        ms = []
        ds = []
        for s in [4, 5, 6]:
            n1 = (2 * n0 // s + d).astype(int) * s
            m1 = np.ceil(length / n1).astype(int)
            for k in range(len(n1)):
                if n1[k] > 0 and m1[k] > 0 and n1[k] > m1[k]:
                    delta = n1[k] * m1[k] - length
                    if delta >= 0:
                        ns.append(n1[k])
                        ms.append(m1[k])
                        ds.append(delta)
        mask = np.array(ds) == min(ds)
        ns = np.array(ns)[mask]
        ms = np.array(ms)[mask]
        idx = np.argmin(np.abs(ns / ms - 5))
        n, m = ns[idx], ms[idx]
        if isinstance(n, np.ndarray):
            n, m = n[0], m[0]
        if length <= lmin or n > length:
            n = length
        if n < lmin:
            n = lmin
            m = np.ceil(length / n).astype(int)
    else:
        n, m = 0, 0
    return n, m


def _is_cmap(c: Any) -> bool:
    """
    Tests if the argument is a valid colormap name or matplotlib.colors.Colormap object.

    This function checks whether the input can be used as a colormap in matplotlib.
    It accepts both colormap names (strings) and Colormap objects.

    Parameters
    ----------
    c : str or matplotlib.colors.Colormap
        Input to check for colormap validity

    Returns
    -------
    bool
        True if c is a valid colormap name or Colormap object,
        False otherwise

    Examples
    --------
    >>> _is_cmap('viridis')  # True
    >>> _is_cmap(plt.cm.viridis)  # True
    >>> _is_cmap('not_a_colormap')  # False
    >>> _is_cmap(42)  # False
    """
    if isinstance(c, Colormap):
        return True
    if not isinstance(c, str):
        return False
    try:
        is_cmap = False
        if isinstance(c, str) and c not in mc.CSS4_COLORS:
            cmp = colormaps[c]
            is_cmap = True
    except:
        is_cmap = False
    return is_cmap


def _is_qualitative(cmap: Union[str, Colormap]) -> bool:
    """
    Tests if a colormap is qualitative (categorical).

    This function determines whether a colormap is qualitative, meaning it is
    designed for categorical data with distinct colors rather than continuous
    gradients. Qualitative colormaps typically have a limited number of colors
    (usually 20 or fewer) and are not meant to be interpolated.

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap
        Colormap to check for qualitative properties

    Returns
    -------
    bool
        True if the colormap is qualitative,
        False otherwise

    Examples
    --------
    >>> _is_qualitative('Set1')  # True
    >>> _is_qualitative('viridis')  # False
    >>> _is_qualitative(plt.cm.Set1)  # True
    """
    if isinstance(cmap, str):
        cmap = colormaps[cmap]
    try:
        mask = isinstance(cmap, ListedColormap) & (len(cmap.colors) <= 24)
    except:
        mask = False
    return bool(mask)


def _is_cyclic(cmap: Union[str, Colormap]) -> bool:
    """
    Tests if a colormap is cyclic.

    A cyclic colormap is one where the colors at both ends are similar,
    making it suitable for visualizing periodic data. This function checks
    if the Hue, Saturation, and Value components are approximately the same
    at both ends of the colormap.

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap
        Colormap to check for cyclic properties

    Returns
    -------
    bool
        True if the colormap is cyclic,
        False otherwise

    Examples
    --------
    >>> _is_cyclic('twilight')  # True
    >>> _is_cyclic('viridis')  # False
    >>> _is_cyclic(plt.cm.twilight)  # True
    """
    if isinstance(cmap, str):
        cmap = colormaps[cmap]
    n = 32
    colors = get_colors(cmap, n, exclude_extreme=False)
    hsv = np.array([mc.rgb_to_hsv(mc.to_rgb(color)) for color in colors])
    d = np.abs(hsv[-1] - hsv[0])
    d[0] = min(d[0], abs(d[0] - 1), abs(d[0] + 1))
    mask = np.all(d < 0.1) and not _is_qualitative(cmap)
    return bool(mask)


def _is_divergent(cmap: Union[str, Colormap]) -> bool:
    """
    Tests if a colormap is divergent.

    A divergent colormap is one that has a distinct middle color (often white or gray)
    and diverges to two different colors at the extremes. This function checks for
    divergent properties by analyzing the hue, saturation, and value components
    of the colormap.

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap
        Colormap to check for divergent properties

    Returns
    -------
    bool
        True if the colormap is divergent,
        False otherwise

    Examples
    --------
    >>> _is_divergent('RdBu')  # True
    >>> _is_divergent('viridis')  # False
    >>> _is_divergent(plt.cm.RdBu)  # True
    """
    if isinstance(cmap, str):
        cmap = colormaps[cmap]
    def _fix_hue_phase(h):
        h_ext = np.stack([h - 1, h, h + 1]).T
        h_fix = [h[0]]
        for i in range(len(h) - 1):
            d = np.abs(h_ext[i+1] - h_fix[i])
            j = np.argmin(d)
            h_fix.append(h_ext[i+1][j])
        h_fix = np.array(h_fix)
        return h_fix

    n = 32
    colors = get_colors(cmap, n, exclude_extreme=False)
    h, s, v = np.array([mc.rgb_to_hsv(mc.to_rgb(color)) for color in colors]).T
    d = np.abs(np.diff(_fix_hue_phase(h)))
    i = np.argmax(d)
    hmask = (d[i] > 0.05) & (abs(i - n / 2) < 4)
    
    p = np.polyfit(np.arange(len(v)), v, 2)
    i = -p[1] / (2 * p[0]) if p[0] != 0 else 0
    vmask = (abs(p[0]) > 0.001) & (abs(i - n / 2) < 4)

    p = np.polyfit(np.arange(len(s)), s, 2)
    i = -p[1] / (2 * p[0]) if p[0] != 0 else 0
    smask = (abs(p[0]) > 0.001) & (abs(i - n / 2) < 3)
    
    mask = np.sum([hmask, smask, vmask]) >= 2
    mask = mask and not _is_cyclic(cmap) and not _is_qualitative(cmap)
    return bool(mask)


def get_colors(
    cmap: Union[str, Colormap],
    n: Optional[int] = None,
    exclude_extreme: bool = True
) -> List[str]:
    """
    Extracts colors from a colormap with optional sampling and filtering.

    This function extracts colors from a colormap, with options to:
    - Specify the number of colors to extract
    - Exclude extreme (very dark/light) colors
    - Handle both qualitative and continuous colormaps appropriately

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap
        Colormap name or instance
    n : int, optional
        Sumpling number of colors to extract. If None:
        - For qualitative colormaps: uses all colors
        - For continuous colormaps: uses 10 colors (9 for divergent)
    exclude_extreme : bool, default=True
        Filtering out the darkest and lightest colors from the output.
        This is useful for continuous colormaps to avoid pure black/white.

    Returns
    -------
    list of str
        List of colors in hex format, sampled from the colormap

    Examples
    --------
    >>> get_colors('viridis', n=5)  # Get 5 colors from viridis
    >>> get_colors('Set1')  # Get all colors from qualitative colormap
    >>> get_colors('RdBu', exclude_extreme=False)  # Include extremes
    """
    if isinstance(cmap, str):
        cmap = colormaps[cmap]
    if isinstance(cmap, ListedColormap):
        colors = [mc.to_hex(c) for c in cmap.colors] # type: ignore
        if n is None and len(colors) > 24:
            n = 24
        if n is not None and len(colors) > 0 and n != len(colors):
            colors = interpolate_colors(colors, n=10*len(colors))
            cmap = LinearSegmentedColormap.from_list("cmap", colors)
            colors = get_colors(cmap, n, exclude_extreme=False)
    else:
        n = 10 - int(_is_divergent(cmap)) if n is None else n
        dn = 1 if exclude_extreme else 0
        idx = np.arange(dn, n + dn) / (n + 2 * dn - 1)
        colors = cmap(idx)
    colors = [mc.to_hex(c) for c in colors]
    return colors


def interpolate_colors(c: List, n: int = 5) -> List[str]:
    """
    Creates a smooth gradient of colors by interpolating between input colors.

    This function takes a list of colors and generates a new list with n colors
    by creating a smooth gradient between the input colors using linear interpolation.

    Parameters
    ----------
    c : list
        List of input colors in any matplotlib-compatible format (hex, name, etc.)
    n : int, default=5
        Number of colors to generate in the output list

    Returns
    -------
    list of str
        List of n colors in hex format, forming a smooth gradient between the
        input colors

    Examples
    --------
    >>> interpolate_colors(['#FF0000', '#00FF00'], n=3)
    ['#FF0000', '#808000', '#00FF00']
    >>> interpolate_colors(['red', 'blue'], n=4)
    ['#FF0000', '#800080', '#0000FF']
    """
    if not isinstance(c, list) or len(c) <= 1:
        raise ValueError("Input must be a list of two or more colors")
    c = [mc.to_hex(c_) for c_ in c]
    gradient = np.linspace(0,1,n)
    cmap = LinearSegmentedColormap.from_list("cmap", c)
    colors = cmap(gradient)
    colors = [mc.to_hex(color).upper() for color in colors]
    return colors


import types
__all__ = [name for name, thing in globals().items()
          if not (name.startswith("_") or isinstance(thing, types.ModuleType))]
del types
