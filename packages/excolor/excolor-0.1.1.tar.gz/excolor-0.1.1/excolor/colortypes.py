#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains functions to convert colors between different color formats.
"""

import os
import re
import colorsys
import numpy as np
import matplotlib.colors as mc
from typing import Any, List, Tuple, Optional, Union
from functools import wraps


def convert_lists(func):
    """
    Decorator to add list support to a color conversion function.

    This decorator wraps a color conversion function, allowing it to accept a list
    of colors in addition to a single color. If the input `c` is a list and not a
    recognized single color format, the decorator will apply the wrapped function
    to each item in the list and return a list of the results.

    Parameters
    ----------
    func : callable
        The color conversion function to wrap.

    Returns
    -------
    callable
        The wrapped function with added support for list inputs.
    """
    @wraps(func)
    def wrapper(c, *args, **kwargs):
        if _get_color_type(c) is None and isinstance(c, list):
            return [func(color, *args, **kwargs) for color in c]
        return func(c, *args, **kwargs)
    return wrapper


COLOR_TYPES = [
    'name', 'hex', 'hexa', 'rgb|hls|hsl|hsv|oklch', 'rgba', 'rgb255', 'rgba255', 
    'rgb255 formatted', 'rgba255 formatted', 'hsl formatted', 'hls formatted', 'hsv formatted', 'oklch formatted',
]


def _is_arraylike(x: Any) -> bool:
    """
    Checks if an object is array-like (can be treated as a sequence of elements).

    This function tests whether an object can be treated as an array or sequence,
    supporting operations like indexing and iteration. It checks for common
    array-like types in Python and NumPy.

    Parameters
    ----------
    x : Any
        Object to check for array-like properties

    Returns
    -------
    bool
        True if x is array-like (numpy.ndarray, list, tuple, or set),
        False otherwise

    Examples
    --------
    >>> _is_arraylike([1, 2, 3])  # True
    >>> _is_arraylike(np.array([1, 2, 3]))  # True
    >>> _is_arraylike((1, 2, 3))  # True
    >>> _is_arraylike({1, 2, 3})  # True
    >>> _is_arraylike(42)  # False
    """
    mask = isinstance(x, np.ndarray) or isinstance(x, list)
    mask = mask or isinstance(x, tuple) or isinstance(x, set)
    return bool(mask)


def _is_color(x: Any) -> bool:
    """
    Checks if the input is a valid color representation.

    Returns True if x is:
    - an RGB or RGBA array (using _is_rgb)
    - a valid hex color string (using _is_hex)
    - a named color string in matplotlib (CSS4_COLORS, BASE_COLORS, TABLEAU_COLORS, XKCD_COLORS)
    Otherwise returns False.

    Parameters
    ----------
    x : Any
        Input to check

    Returns
    -------
    bool
        True if x is a valid color, False otherwise

    Examples
    --------
    >>> _is_color((1.0, 0.0, 0.0))  # True (RGB)
    >>> _is_color('#FF00AA')  # True (hex)
    >>> _is_color('red')  # True (named)
    >>> _is_color('notacolor')  # False
    """
    if _get_color_type(x) is not None:
        return True
    return False


def _is_named_color(x: Any) -> bool:
    """
    Checks if the input is a valid matplotlib named color.

    Parameters
    ----------
    x : Any
        Object to check.

    Returns
    -------
    bool
        True if x is a named color, False otherwise.
    """
    if not isinstance(x, str):
        return False
    # Exclude hex strings, which are handled by _is_hex
    if x.startswith('#'):
        return False
    # Use matplotlib's own color-like check
    return mc.is_color_like(x)


def _is_hex(x: Any) -> bool:
    """
    Checks if the input is a valid hex color string.

    A valid hex color string starts with '#' and is either 7 or 9 characters long (e.g. '#RRGGBB' or '#RRGGBBAA'),
    and all characters after '#' are valid hexadecimal digits.

    Parameters
    ----------
    x : object
        Input to check

    Returns
    -------
    bool
        True if x is a valid hex color string, False otherwise

    Examples
    --------
    >>> _is_hex('#FF00AA')  # True
    >>> _is_hex('#FF00AABB')  # True
    >>> _is_hex('#GG00AA')  # False
    >>> _is_hex('red')  # False
    """
    if not isinstance(x, str):
        return False
    match = re.search(r'^#(?:[0-9a-fA-F]{3,4}){1,2}$', x)
    return bool(match)


def _is_rgb(x: Any) -> bool:
    """
    Checks if an object is an RGB or RGBA like array.

    This function tests whether an object can be treated as an RGB or RGBA array.

    Parameters
    ----------
    x : Any
        Object to check for RGB or RGBA properties

    Returns
    -------
    bool
        True if c is an RGB or RGBA array, False otherwise

    Examples
    --------
    >>> _is_rgb((1.0, 0.0, 0.0))  # True
    >>> _is_rgb((1.0, 0.0, 0.0, 1.0))  # True
    >>> _is_rgb('red')  # False
    """
    if not _is_arraylike(x):
        return False
    x_list = list(x)
    if len(x_list) not in [3, 4]:
        return False
    if all(isinstance(i, int) for i in x_list):
        return False
    flag_ok = True
    try:
        flag_ok = all(0 <= i <= 1 for i in x_list)
    except:
        flag_ok = False
    return flag_ok


def _is_rgb255(x: Any) -> bool:
    """
    Checks if an object is an RGB or RGBA like array with values in [0, 255].

    Parameters
    ----------
    x : Any
        Object to check for RGB or RGBA properties.

    Returns
    -------
    bool
        True if c is an RGB or RGBA array in [0, 255], False otherwise.
    """
    if not _is_arraylike(x) or not all(isinstance(i, int) for i in x):
        return False
    if len(x) not in [3, 4]:
        return False
    flag_ok = True
    try:
        flag_ok = all(0 <= i <= 255 for i in x)
    except:
        flag_ok = False
    return flag_ok


def _get_color_type(c: Any) -> Optional[str]:
    """
    Determines the internal color type of a given input.

    This function inspects the input `c` to identify its color format based on a
    predefined set of types: 'name', 'hex', 'hexa', 'rgb', 'rgba', 'rgb255',
    'rgba255', 'rgb255 formatted', 'rgba255 formatted', 'hsl formatted', 
    'hls formatted', 'hsv formatted', 'oklch formatted'.

    Parameters
    ----------
    c : Any
        The color input to analyze. This can be a string (e.g., 'red', '#FF0000',
        'hsv(0, 1, 1)'), a tuple, or a list (e.g., (1, 0, 0), [255, 0, 0]).

    Returns
    -------
    str or None
        The name of the color type if `c` matches a known format, otherwise None.
    """
    if isinstance(c, str):
        # Check for hex color
        if _is_hex(c):
            return 'hexa' if len(c) in [5, 9] else 'hex'
        # CSS-like function strings
        if '(' in c and ')' in c:
            channels = _parse_css_channels(c)
            num_channels = len(channels)
            if c.startswith('rgb'):
                if num_channels == 3:
                    return "rgb255 formatted"
                elif num_channels == 4:
                    return "rgba255 formatted"
            elif c.startswith(('hsl', 'hls', 'hsv', 'oklch')):
                if num_channels == 3:
                    return f"{c.split('(')[0].strip()} formatted"
        if _is_named_color(c):
            return 'name'
    elif _is_arraylike(c):
        if _is_rgb(c):
            return 'rgba' if len(c) == 4 else 'rgb|hls|hsl|hsv|oklch'
        if _is_rgb255(c):
            return 'rgba255' if len(c) == 4 else 'rgb255'

    return None


def _parse_css_channels(s: str, normalize: bool = False) -> List[float]:
    """
    Parses the channel values from a CSS-like color string.
    e.g., 'rgb(255, 0, 0)' -> (255, 0, 0)
    e.g., 'hls(200, 100%, 50%)' -> (200, 1.0, 0.5)
    e.g., 'hsl200, 50%, 100%)' -> (200, 1.0, 0.5)

    Parameters
    ----------
    s : str
        The CSS-like color string to parse.
    normalize : bool, default=False
        If True, normalize the channel values to [0, 1].

    Returns
    -------
    list of float
        The parsed channel values.
    """
    err_msg = "Could not parse color string: '{s}'. Please check for invalid characters or incorrect formatting. Expected a format like 'rgb(255, 0, 0)' or 'hsl(200, 100%, 50%)'."
    
    # Extract content between parentheses
    match = re.search(r'\((.*)\)', s)
    if not match:
        raise ValueError(err_msg)

    content = match.group(1)

    # Split by comma or space, and filter out empty strings
    parts = re.split(r'[\s,]+', content.strip())

    values = []
    try:
        for part in parts:
            if not part:
                continue
            if part.endswith('%'):
                values.append(float(part[:-1]))
            else:
                values.append(float(part))
    except ValueError:
        raise ValueError(err_msg)
    values = tuple(values)
    # Correction: rgb255 to int
    if s.startswith('rgb'):
        values = tuple([int(v) for v in values])
    # Correction: hsl to hls (hsl is not a standard color format)
    if s.startswith('hsl') or s.startswith('hls') or s.startswith('hsv') or s.startswith('oklch'):
        values = tuple([float(v) for v in values])
    # Corrrection: Check for invalid values
    flag_ok = True
    if any(v < 0 for v in values):
        flag_ok = False
    elif s.startswith('oklch'):
        if values[0] > 100 or values[1] > 1 or values[2] > 360:
            flag_ok = False
    elif s.startswith('hsl') or s.startswith('hls') or s.startswith('hsv'):
        if values[0] > 360 or values[1] > 100 or values[2] > 100:
            flag_ok = False
    if not flag_ok:
        raise ValueError(err_msg)
    # Correction: normalize
    if normalize:
        if s.startswith('rgb'):
            values = tuple([min(max(v / 255, 0.0), 1.0) for v in values])
        elif s.startswith('oklch'):
            values = [values[0] / 100, values[1], values[2] / 360]
            values = tuple([min(max(v, 0.0), 1.0) for v in values])
        else:
            # hsl or hls or hsv
            values = [values[0] / 360, values[1] / 100, values[2] / 100]
            values = tuple([min(max(v, 0.0), 1.0) for v in values])
    return values


def _to_formatted_rgb(c):
    """
    Converts an RGB or RGBA color to a CSS-like formatted string.

    Parameters
    ----------
    c : tuple or list
        An RGB or RGBA color tuple with integer values in [0, 255].

    Returns
    -------
    str
        A CSS-like formatted string, e.g., "rgb(255, 0, 0)" or "rgba(255, 0, 0, 1.0)".
    """
    ctype = _get_color_type(c)
    foramtted_rgb = None
    if ctype in ['rgb|hls|hsl|hsv|oklch', 'rgba']:
        ch = [min(max(int(255 * c_), 0), 255) for c_ in c]
        foramtted_rgb = 'rgb(' + ', '.join([str(c_) for c_ in ch]) + ')'
    elif ctype in ['rgb255', 'rgba255']:
        foramtted_rgb = 'rgb(' + ', '.join([str(c_) for c_ in c]) + ')'
    elif ctype in ['rgb255 formatted', 'rgba255 formatted']:
        foramtted_rgb = c
    else:
        raise ValueError(f"Invalid input: expected rgb|hls|hsl|hsv|oklch or rgba, got {ctype}")
    return foramtted_rgb


def _to_formatted_hls(c):
    """
    Converts an HLS color to a CSS-like formatted string.

    Parameters
    ----------
    c : tuple or list
        An HLS color tuple with values in the range [0, 1].

    Returns
    -------
    str
        A CSS-like formatted string, e.g., "hls(240, 50%, 75%)".
    """
    ctype = _get_color_type(c)
    foramtted_hls = None
    if ctype == 'rgb|hls|hsl|hsv|oklch':
        ch = [360 * c[0],100 * c[1], 100 * c[2]]
        foramtted_hls = f'hls({ch[0]:.2f}, {ch[1]:.2f}%, {ch[2]:.2f}%)'
    elif ctype == 'hls formatted':
        foramtted_hls = c
    elif ctype == 'hsl formatted':
        ch = _parse_css_channels(c)
        ch = (ch[0], ch[2], ch[1])
        foramtted_hls = f'hls({ch[0]:.2f}, {ch[1]:.2f}%, {ch[2]:.2f}%)'
    else:
        raise ValueError(f"Invalid input: expected rgb|hls|hsl|hsv|oklch, got {ctype}")
    return foramtted_hls


def _to_formatted_hsl(c):
    """
    Converts an HSL color to a CSS-like formatted string.

    Parameters
    ----------
    c : tuple or list
        An HSL color tuple with values in the range [0, 1].

    Returns
    -------
    str
        A CSS-like formatted string, e.g., "hsl(240, 100%, 50%)".
    """
    ctype = _get_color_type(c)
    foramtted_hsl = None
    if ctype == 'rgb|hls|hsl|hsv|oklch':
        ch = [360 * c[0],100 * c[1], 100 * c[2]]
        foramtted_hsl = f'hsl({ch[0]:.2f}, {ch[1]:.2f}%, {ch[2]:.2f}%)'
    elif ctype == 'hsl formatted':
        foramtted_hsl = c
    elif ctype == 'hls formatted':
        ch = _parse_css_channels(c)
        ch = (ch[0], ch[2], ch[1])
        foramtted_hsl = f'hsl({ch[0]:.2f}, {ch[1]:.2f}%, {ch[2]:.2f}%)'
    else:
        raise ValueError(f"Invalid input: expected rgb|hls|hsl|hsv|oklch, got {ctype}")
    return foramtted_hsl


def _to_formatted_hsv(c):
    """
    Converts an HSV color to a CSS-like formatted string.

    Parameters
    ----------
    c : tuple or list
        An HSV color tuple with values in the range [0, 1].

    Returns
    -------
    str
        A CSS-like formatted string, e.g., "hsv(240, 100%, 100%)".
    """
    ctype = _get_color_type(c)
    foramtted_hsv = None
    if ctype == 'rgb|hls|hsl|hsv|oklch':
        ch = [360 * c[0],100 * c[1], 100 * c[2]]
        foramtted_hsv = f'hsv({ch[0]:.2f}, {ch[1]:.2f}%, {ch[2]:.2f}%)'
    elif ctype == 'hsv formatted':
        foramtted_hsv = c
    else:
        raise ValueError(f"Invalid input: expected rgb|hls|hsl|hsv|oklch, got {ctype}")
    return foramtted_hsv


def _to_formatted_oklch(c):
    """
    Converts an OKLCH color to a CSS-like formatted string.

    Parameters
    ----------
    c : tuple or list
        An OKLCH color tuple.

    Returns
    -------
    str
        A CSS-like formatted string, e.g., "oklch(52.63% 0.26 229.23)".
    """
    ctype = _get_color_type(c)
    foramtted_oklch = None
    if ctype == 'rgb|hls|hsl|hsv|oklch':
        ch = [100 * c[0], c[1], 360 * c[2]]
        foramtted_oklch = f'oklch({ch[0]:.2f}% {ch[1]:.2f} {ch[2]:.2f})'
    elif ctype == 'oklch formatted':
        foramtted_oklch = c
    else:
        raise ValueError(f"Invalid input: expected rgb|hls|hsl|hsv|oklch, got {ctype}")
    return foramtted_oklch

    
# --- Precise Conversion Functions --- #

@convert_lists
def hex_to_rgb(c, keep_alpha=True):
    """
    Converts a hex color string to an RGB or RGBA tuple.

    Parameters
    ----------
    c : str
        The hex color string (e.g., '#FF0000', '#FF0000AA').
    keep_alpha : bool, default=True
        If True and the hex string has an alpha component, it will be included
        in the output tuple.

    Returns
    -------
    tuple or None
        The color as an RGB or RGBA tuple with float values in [0, 1].
    """
    ctype = _get_color_type(c)
    rgb = None
    if ctype in ['hex', 'hexa']:
        keep = len(c) in [5, 9] and keep_alpha
        rgb = mc.to_rgba(c) if keep else mc.to_rgb(c)
    else:
        raise ValueError(f"Invalid input: expected hex or hexa, got {ctype}")
    return rgb


@convert_lists
def rgb_to_hex(c, keep_alpha=True):
    """
    Converts an RGB or RGBA tuple to a hex color string.

    Parameters
    ----------
    c : tuple
        The RGB or RGBA color tuple with float values in [0, 1].
    keep_alpha : bool, default=True
        If True and the input tuple has an alpha component, it will be included
        in the output hex string.

    Returns
    -------
    str or None
        The color as a hex string (e.g., '#ff0000', '#ff0000aa').
    """
    ctype = _get_color_type(c)
    hx = None
    if ctype in ['rgb|hls|hsl|hsv|oklch', 'rgba']:
        keep = len(c) > 3 and keep_alpha
        hx = mc.to_hex(c, keep_alpha=keep).upper()
    elif ctype in ['rgb255', 'rgba255']:
        ch = [min(max(int(c_ / 255.0), 0.0), 1.0) for c_ in c]
        keep = len(ch) > 4 and keep_alpha
        hx = mc.to_hex(ch, keep_alpha=keep).upper()
    elif ctype in ['rgb255 formatted', 'rgba255 formatted']:
        ch = _parse_css_channels(c)
        ch = [min(max(int(c_ / 255.0), 0.0), 1.0) for c_ in ch]
        keep = len(ch) > 4 and keep_alpha
        hx = mc.to_hex(ch, keep_alpha=keep).upper()
    else:
        raise ValueError(f"Invalid input: expected rgb or rgba, got {ctype}")
    return hx


@convert_lists
def rgb255_to_rgb(c, keep_alpha=True):
    """
    Converts an RGB or RGBA tuple from [0, 255] to [0, 1] scale.

    Parameters
    ----------
    c : tuple
        The RGB or RGBA color tuple with integer values in [0, 255].
    keep_alpha : bool, default=True
        If True, preserves the alpha channel if available.

    Returns
    -------
    tuple or None
        The color as an RGB or RGBA tuple with float values in [0, 1].
    """
    ctype = _get_color_type(c)
    rgb = None
    if ctype in ['rgb|hls|hsl|hsv|oklch', 'rgba']:
        n = 3 + int(keep_alpha)
        rgb = c[:n]
    elif ctype in ['rgb255', 'rgba255']:
        n = 3 + int(keep_alpha)
        rgb = tuple([min(max(np.round(val / 255, 4), 0.0), 1.0) for val in c[:n]])
    elif ctype in ['rgb255 formatted', 'rgba255 formatted']:
        n = 3 + int(keep_alpha)
        ch = _parse_css_channels(c)
        ch = [min(max(int(c_), 0), 255) for c_ in ch][:n]
        rgb = _to_formatted_rgb(ch)
    else:
        raise ValueError(f"Invalid input: expected rgb or rgba, got {ctype}")
    return rgb


@convert_lists
def rgb_to_rgb255(c, keep_alpha=True):
    """
    Converts an RGB or RGBA tuple from [0, 1] to [0, 255] scale.

    Parameters
    ----------
    c : tuple
        The RGB or RGBA color tuple with float values in [0, 1].
    keep_alpha : bool, default=True
        If True, preserves the alpha channel if available.

    Returns
    -------
    tuple or None
        The color as an RGB or RGBA tuple with integer values in [0, 255].
    """
    ctype = _get_color_type(c)
    rgb = None
    if ctype in ['rgb|hls|hsl|hsv|oklch', 'rgba']:
        n = 3 + int(keep_alpha)
        rgb = tuple([min(max(int(round(val * 255)), 0), 255) for val in c[:n]])
    elif ctype in ['rgb255', 'rgba255']:
        n = 3 + int(keep_alpha)
        rgb = c[:n]
    elif ctype in ['rgb255 formatted', 'rgba255 formatted']:
        n = 3 + int(keep_alpha)
        ch = _parse_css_channels(c)
        ch = [min(max(int(c_), 0), 255) for c_ in ch][:n]
        rgb = _to_formatted_rgb(ch)
    else:
        raise ValueError(f"Invalid input: expected rgb or rgba, got {ctype}")
    return rgb


@convert_lists
def hls_to_rgb(c):
    """
    Converts an HLS color to RGB format.

    Parameters
    ----------
    c : tuple
        The HLS color tuple (Hue, Lightness, Saturation).

    Returns
    -------
    tuple or None
        The color as an RGB tuple with float values in [0, 1].
    """
    ctype = _get_color_type(c)
    rgb = None
    if ctype == 'rgb|hls|hsl|hsv|oklch':
        rgb = colorsys.hls_to_rgb(*c)
    elif ctype == 'hls formatted':
        ch = _parse_css_channels(c, normalize=True)
        rgb = colorsys.hls_to_rgb(*ch)
        rgb = _to_formatted_rgb(rgb)
    elif ctype == 'hsl formatted':
        ch = _parse_css_channels(c, normalize=True)
        ch = (ch[0], ch[2], ch[1])
        rgb = colorsys.hls_to_rgb(*ch)
        rgb = _to_formatted_rgb(rgb)
    else:
        raise ValueError(f"Invalid input: expected hls or hsl, got {ctype}")
    return rgb


@convert_lists
def rgb_to_hls(c):
    """
    Converts an RGB color to HLS format.

    Parameters
    ----------
    c : tuple
        The RGB color tuple with float values in [0, 1].

    Returns
    -------
    tuple or None
        The color in HLS format (Hue, Lightness, Saturation).
    """
    ctype = _get_color_type(c)
    hls = None
    if ctype in ['rgb|hls|hsl|hsv|oklch', 'rgba']:
        hls = colorsys.rgb_to_hls(*c[:3])
    elif ctype in ['rgb255', 'rgba255']:
        ch = [min(max(int(c_ / 255.0), 0.0), 1.0) for c_ in c]
        hls = colorsys.rgb_to_hls(*ch[:3])
    elif ctype in ['rgb255 formatted', 'rgba255 formatted']:
        ch = _parse_css_channels(c, normalize=True)
        hls = colorsys.rgb_to_hls(*ch[:3])
        hls = _to_formatted_hls(hls)
    else:
        raise ValueError(f"Invalid input: expected rgb or rgba, got {ctype}")
    return hls


@convert_lists
def hsl_to_rgb(c):
    """
    Converts an HSL color to RGB format.

    Note: HSL is sometimes used interchangeably with HLS, but the order of
    Saturation and Lightness is swapped. This function expects (H, S, L).

    Parameters
    ----------
    c : tuple
        The HSL color tuple (Hue, Saturation, Lightness).

    Returns
    -------
    tuple or None
        The color as an RGB tuple with float values in [0, 1].
    """
    ctype = _get_color_type(c)
    rgb = None
    if ctype == 'rgb|hls|hsl|hsv|oklch':
        ch = (c[0], c[2], c[1])
        rgb = colorsys.hls_to_rgb(*ch)
    elif ctype == 'hls formatted':
        ch = _parse_css_channels(c, normalize=True)
        rgb = colorsys.hls_to_rgb(*ch)
        rgb = _to_formatted_rgb(rgb)
    elif ctype == 'hsl formatted':
        ch = _parse_css_channels(c, normalize=True)
        ch = (ch[0], ch[2], ch[1])
        rgb = colorsys.hls_to_rgb(*ch)
        rgb = _to_formatted_rgb(rgb)
    else:
        raise ValueError(f"Invalid input: expected hls or hsl, got {ctype}")
    return rgb


@convert_lists
def rgb_to_hsl(c):
    """
    Converts an RGB color to HSL format.

    Note: HSL is often used interchangeably with HLS, but the order of
    Saturation and Lightness is swapped. This function returns (H, S, L).

    Parameters
    ----------
    c : tuple
        The RGB color tuple with float values in [0, 1].

    Returns
    -------
    tuple or None
        The color in HSL format (Hue, Saturation, Lightness).
    """
    ctype = _get_color_type(c)
    hsl = None
    if ctype in ['rgb|hls|hsl|hsv|oklch', 'rgba']:
        hsl = colorsys.rgb_to_hls(*c[:3])
        hsl = (hsl[0], hsl[2], hsl[ 1])
    elif ctype in ['rgb255', 'rgba255']:
        ch = [min(max(int(c_ / 255.0), 0.0), 1.0) for c_ in c]
        hsl = colorsys.rgb_to_hls(*ch[:3])
        hsl = (hsl[0], hsl[2], hsl[1])
    elif ctype in ['rgb255 formatted', 'rgba255 formatted']:
        ch = _parse_css_channels(c, normalize=True)
        hls = colorsys.rgb_to_hls(*ch[:3])
        hls = (hls[0], hls[2], hls[1])
        hsl = _to_formatted_hsl(hls)
    else:
        raise ValueError(f"Invalid input: expected rgb or rgba, got {ctype}")
    return hsl


@convert_lists
def hsv_to_rgb(c):
    """
    Converts an HSV color to RGB format.

    Parameters
    ----------
    c : tuple
        The HSV color tuple (Hue, Saturation, Value).

    Returns
    -------
    tuple or None
        The color as an RGB tuple with float values in [0, 1].
    """
    ctype = _get_color_type(c)
    rgb = None
    if ctype == 'rgb|hls|hsl|hsv|oklch':
        rgb = colorsys.hsv_to_rgb(*c)
    elif ctype == 'hsv formatted':
        ch = _parse_css_channels(c, normalize=True)
        rgb = colorsys.hsv_to_rgb(*ch)
        rgb = _to_formatted_rgb(rgb)
    else:
        raise ValueError(f"Invalid input: expected hsv, got {ctype}")
    return rgb


@convert_lists
def rgb_to_hsv(c):
    """
    Converts an RGB color to HSV format.

    Parameters
    ----------
    c : tuple
        The RGB color tuple with float values in [0, 1].

    Returns
    -------
    tuple or None
        The color in HSV format (Hue, Saturation, Value).
    """
    ctype = _get_color_type(c)
    hsv = None
    if ctype in ['rgb|hls|hsl|hsv|oklch', 'rgba']:
        hsv = mc.rgb_to_hsv(c[:3])
    elif ctype in ['rgb255', 'rgba255']:
        ch = [min(max(int(c_ / 255.0), 0.0), 1.0) for c_ in c]
        hsv = mc.rgb_to_hsv(ch[:3])
    elif ctype in ['rgb255 formatted', 'rgba255 formatted']:
        ch = _parse_css_channels(c, normalize=True)
        hsv = mc.rgb_to_hsv(ch[:3])
        hsv = _to_formatted_hsv(hsv)
    else:
        raise ValueError(f"Invalid input: expected rgb or rgba, got {ctype}")
    return hsv


@convert_lists
def oklch_to_rgb(c):
    """
    Converts an OKLCH color to RGB or RGBA format.

    Parameters
    ----------
    oklch : tuple
        OKLCH color as (L, C, H) or (L, C, H, A).

    Returns
    -------
    tuple or None
        RGB or RGBA color with values in [0, 1].
    """
    ctype = _get_color_type(c)
    rgb = None
    if ctype == 'rgb|hls|hsl|hsv|oklch':
        rgb = _oklch_to_rgb(c)
    elif ctype == 'oklch formatted':
        ch = _parse_css_channels(c, normalize=True)
        rgb = _oklch_to_rgb(ch)
        rgb = _to_formatted_rgb(rgb)
    else:
        raise ValueError(f"Invalid input: expected oklch, got {ctype}")
    return rgb


def rgb_to_oklch(c):
    """
    Convert an RGB or RGBA color to OKLCH format.

    Parameters
    ----------
    rgb : tuple
        RGB or RGBA color with values in [0, 1].

    Returns
    -------
    tuple or None
        OKLCH color as (L, C, H) or (L, C, H, A).
    """
    ctype = _get_color_type(c)
    oklch = None
    if ctype in ['rgb|hls|hsl|hsv|oklch', 'rgba']:
        oklch = _rgb_to_oklch(c[:3])
    elif ctype in ['rgb255', 'rgba255']:
        ch = [min(max(int(c_ / 255.0), 0.0), 1.0) for c_ in c]
        oklch = _rgb_to_oklch(ch[:3])
    elif ctype in ['rgb255 formatted', 'rgba255 formatted']:
        ch = _parse_css_channels(c, normalize=True)
        oklch = _rgb_to_oklch(ch[:3])
        oklch = _to_formatted_oklch(oklch)
    else:
        raise ValueError(f"Invalid input: expected rgb or rgba, got {ctype}")
    return oklch


def _oklch_to_rgb(oklch):
    """
    Converts an OKLCH color to RGB or RGBA format.

    Parameters
    ----------
    oklch : tuple
        OKLCH color as (L, C, H) or (L, C, H, A).

    Returns
    -------
    tuple
        RGB or RGBA color with values in [0, 1].
    """
    # Utility function to convert linear RGB to sRGB
    def _linear_to_rgb(c):
        """Convert linear RGB to sRGB"""
        if c <= 0.0031308:
            return 12.92 * c
        else:
            return 1.055 * (c ** (1/2.4)) - 0.055

    # 1. Check if is grey
    L, C, H = oklch[:3]
    is_grey = True if abs(C) < 1e-5 else False

    # 2. Convert H to radians
    h_rad = 2 * np.pi * H
    
    # 3. Calculate a and b from C and H
    a = C * np.cos(h_rad)
    b = C * np.sin(h_rad)
    
    # 4. Convert to OKLab L*a*b*
    L_oklab = L
    a_oklab = a
    b_oklab = b
    
    # 5. Convert to OKLab LMS
    l = L_oklab + 0.3963377774 * a_oklab + 0.2158037573 * b_oklab
    m = L_oklab - 0.1055613458 * a_oklab - 0.0638541728 * b_oklab
    s = L_oklab - 0.0894841775 * a_oklab - 1.2914855480 * b_oklab
    
    # 6. Apply inverse non-linearity (cube)
    l = l ** 3
    m = m ** 3
    s = s ** 3
    
    # 7. Convert to XYZ
    x = 1.2270138511 * l - 0.5577999806 * m + 0.2812561490 * s
    y = -0.0405801784 * l + 1.1122568696 * m - 0.0716766787 * s
    z = -0.0763812845 * l - 0.4214819784 * m + 1.5861632204 * s
    
    # 8. Convert to linear RGB
    r_lin = 3.2409699419 * x - 1.5373831776 * y - 0.4986107603 * z
    g_lin = -0.9692436363 * x + 1.8759673955 * y + 0.0415550574 * z
    b_lin = 0.0556300797 * x - 0.2039769589 * y + 1.0569715142 * z
    
    # 9. Convert to sRGB
    r = _linear_to_rgb(r_lin)
    g = _linear_to_rgb(g_lin)
    b = _linear_to_rgb(b_lin)

    # 10. Clip to sRGB gamut
    r_clip = min(max(r, 0.0), 1.0)
    g_clip = min(max(g, 0.0), 1.0)
    b_clip = min(max(b, 0.0), 1.0)

    # 11. If the color was grayscale, ensure the output is pure gray
    if is_grey:
        gray = (r_clip + g_clip + b_clip) / 3
        return (gray, gray, gray)
    
    return r_clip, g_clip, b_clip


def _rgb_to_oklch(rgb):
    """
    Converts an RGB or RGBA color to OKLCH format.

    Parameters
    ----------
    rgb : tuple
        RGB or RGBA color with values in [0, 1].

    Returns
    -------
    tuple
        OKLCH color as (L, C, H) or (L, C, H, A).
    """
    # Utility function to convert sRGB to linear RGB
    def _rgb_to_linear(c):
        """Convert sRGB to linear RGB"""
        if c <= 0.04045:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    # 1. Check if is grey
    r, g, b = rgb[:3]
    is_grey = True if abs(r - g) < 1e-5 and abs(g - b) < 1e-5 else False
    
    # 2. sRGB to linear sRGB
    r_lin = _rgb_to_linear(r)
    g_lin = _rgb_to_linear(g)
    b_lin = _rgb_to_linear(b)

    # 3. linear sRGB to XYZ
    x = 0.4124564 * r_lin + 0.3575761 * g_lin + 0.1804375 * b_lin
    y = 0.2126729 * r_lin + 0.7151522 * g_lin + 0.0721750 * b_lin
    z = 0.0193339 * r_lin + 0.1191920 * g_lin + 0.9503041 * b_lin

    # 4. XYZ to LMS
    l = 0.8189330101 * x + 0.3618667424 * y - 0.1288597137 * z
    m = 0.0329845436 * x + 0.9292868466 * y + 0.0372156131 * z
    s = 0.0482003018 * x + 0.2643662691 * y + 0.6338517070 * z

    # 5. Apply non-linearity (cube root)
    l_ = l ** (1/3)
    m_ = m ** (1/3)
    s_ = s ** (1/3)

    # 6. LMS to Oklab
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_

    # 7. Oklab to Oklch
    C = np.sqrt(a**2 + b**2)
    H = np.degrees(np.arctan2(b, a)) / 360

    # 8. Apply corrections
    L = min(max(np.round(L, 4), 0.0), 1.0)
    C = min(max(np.round(C, 4), 0.0), 1.0)
    H = min(max(np.round(H, 4), 0.0), 1.0)
    if is_grey:
        C = 0.0
        H = 0.0

    return (L, C, H)


# --- Generic Conversion Functions --- #

@convert_lists
def to_rgb(c, keep_alpha=True, formatted=False):
    """
    Converts any supported color format to an RGB or RGBA tuple.

    This function automatically detects the input color format and converts it to an
    RGB or RGBA tuple with float values in the range [0, 1].

    Parameters
    ----------
    c : any
        The input color. Can be a named color, hex string, or a tuple/list in
        RGB, RGBA, HSV, HLS, or OKLCH format.
    keep_alpha : bool, default=True
        If True, the alpha channel is preserved if the input color has one.
        This flag is ignored for color types that do not support alpha.
    formatted : bool, default=False
        If True, returns a formatted string like "rgb(1.000, 0.000, 0.000)"
        instead of a tuple.

    Returns
    -------
    tuple or str
        The converted color as an RGB/RGBA tuple or a formatted string.

    Examples
    --------
    >>> to_rgb("red")
    (1.0, 0.0, 0.0)
    >>> to_rgb("#00ff00")
    (0.0, 1.0, 0.0)
    >>> to_rgb((0, 0, 255), formatted=True)
    'rgb(0.000, 0.000, 1.000)'
    """
    n = 3 + int(keep_alpha)
    ctype = _get_color_type(c)
    rgb = None
    if ctype == 'name':
        rgb = mc.to_rgb(c)
    elif ctype in ['hex', 'hexa']:
        rgb = mc.to_rgba(c) if ctype == 'hexa' and keep_alpha else mc.to_rgb(c)
    elif ctype in ['rgb|hls|hsl|hsv|oklch', 'rgba']:
        rgb = c[:n]
    elif ctype in ['rgb255', 'rgba255']:
        rgb = tuple([min(max(np.round(val / 255, 4), 0.0), 1.0) for val in c[:n]])
    elif ctype in ['rgb255 formatted', 'rgba255 formatted']:
        rgb = _parse_css_channels(c, normalize=True)[:n]
    elif ctype == 'hsv formatted':
        ch = _parse_css_channels(c, normalize=True)
        rgb = hsv_to_rgb(ch)
    elif ctype == 'hls formatted':
        ch = _parse_css_channels(c, normalize=True)
        rgb = hls_to_rgb(ch)
    elif ctype == 'hsl formatted':
        ch = _parse_css_channels(c, normalize=True)
        rgb = hsl_to_rgb(ch)
    elif ctype == 'oklch formatted':
        ch = _parse_css_channels(c, normalize=True)
        rgb = oklch_to_rgb(ch)
    else:
        raise ValueError(f"Invalid input: expected rgb or rgba, got {ctype}")

    rgb = tuple([min(max(np.round(val, 4), 0.0), 1.0) for val in rgb])

    if formatted:
        rgb = _to_formatted_rgb(rgb)

    return rgb


@convert_lists
def to_rgb255(c, keep_alpha=True, formatted=False):
    """
    Converts any supported color format to an RGB or RGBA tuple with integer values in [0, 255].

    Parameters
    ----------
    c : any
        The input color.
    keep_alpha : bool, default=True
        If True, preserves the alpha channel if available.
    formatted : bool, default=False
        If True, returns a formatted string like "rgb(255, 0, 0)".

    Returns
    -------
    tuple or str
        The converted color as an RGB/RGBA tuple or a formatted string.
    """
    rgb = to_rgb(c, keep_alpha=keep_alpha)
    rgb255 = rgb_to_rgb255(rgb, keep_alpha=keep_alpha)
    if formatted:
        rgb255 = _to_formatted_rgb(rgb255)
    return rgb255


@convert_lists
def to_hex(c, keep_alpha=None):
    """
    Converts any supported color format to a hex color string.

    Parameters
    ----------
    c : any
        The input color.
    keep_alpha : bool, default=True
        If True, includes the alpha channel in the hex string (e.g., '#RRGGBBAA').

    Returns
    -------
    str
        The hex color string.
    """
    rgb = to_rgb(c, keep_alpha=True) # Always get alpha if available for hex conversion
    if keep_alpha is None:
        # If keep_alpha is not specified, we only include alpha in the hex
        # if the original color had it.
        ctype = _get_color_type(c)
        if ctype in ['rgba', 'rgba255']:
            keep_alpha = True
        elif isinstance(c, str) and ctype == 'hex' and len(c) > 7:
            keep_alpha = True
        elif isinstance(c, (list, tuple)) and len(c) == 4:
            keep_alpha = True
        else:
            keep_alpha = False
    return rgb_to_hex(rgb, keep_alpha=keep_alpha)


@convert_lists
def to_hls(c, formatted=False):
    """
    Converts any supported color format to an HLS tuple.

    Parameters
    ----------
    c : any
        The input color.
    formatted : bool, default=False
        If True, returns a formatted string like "hls(235, 51%, 23%)".

    Returns
    -------
    tuple or str
        The converted color as an HLS tuple or a formatted string.
    """
    rgb = to_rgb(c, keep_alpha=False)
    hls = rgb_to_hls(rgb)
    if formatted:
        hls = _to_formatted_hls(hls)
    return hls


@convert_lists
def to_hsl(c, formatted=False):
    """
    Converts any supported color format to an HSL tuple.

    Parameters
    ----------
    c : any
        The input color.
    formatted : bool, default=False
        If True, returns a formatted string like "hsl(235, 23%, 51%)".

    Returns
    -------
    tuple or str
        The converted color as an HSL tuple or a formatted string.
    """
    rgb = to_rgb(c, keep_alpha=False)
    hsl = rgb_to_hsl(rgb)
    if formatted:
        hsl = _to_formatted_hsl(hsl)
    return hsl


@convert_lists
def to_hsv(c, formatted=False):
    """
    Converts any supported color format to an HSV tuple.

    Parameters
    ----------
    c : any
        The input color.
    formatted : bool, default=False
        If True, returns a formatted string like "hsv(235, 23%, 51%)".

    Returns
    -------
    tuple or str
        The converted color as an HSV tuple or a formatted string.
    """
    rgb = to_rgb(c, keep_alpha=False)
    hsv = rgb_to_hsv(rgb)
    if formatted:
        hsv = _to_formatted_hsv(hsv)
    return hsv


@convert_lists
def to_oklch(c, formatted=False):
    """
    Converts any supported color format to an OKLCH tuple.

    Parameters
    ----------
    c : any
        The input color.
    formatted : bool, default=False
        If True, returns a formatted string like "oklch(52.63% 0.26 229.23)".

    Returns
    -------
    tuple or str
        The converted color as an OKLCH tuple or a formatted string.
    """
    rgb = to_rgb(c, keep_alpha=False)
    oklch = rgb_to_oklch(rgb)
    if formatted:
        oklch = _to_formatted_oklch(oklch)
    return oklch



import types
__all__ = [name for name, thing in globals().items()
          if not (name.startswith("_") or isinstance(thing, types.ModuleType))]
del types

