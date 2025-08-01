#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains functions to manipulate colors.
"""

import os
import colorsys
import numpy as np
import matplotlib.pyplot as plt
from cycler import cycler
import matplotlib.colors as mc
from matplotlib import colormaps
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Colormap
from matplotlib.patches import Rectangle
from matplotlib.axes import Axes
from .utils import _aspect_ratio, _is_cmap
from .palette import generate_stepwise_palette
from .colortypes import _is_arraylike, _get_color_type, _is_color, _is_rgb
from .colortypes import _to_formatted_rgb, _to_formatted_hls, _to_formatted_hsl, _to_formatted_hsv, _to_formatted_oklch
from .colortypes import to_hex, to_rgb, to_rgb255, to_hsv, to_hls, to_oklch, rgb_to_rgb255
from .utils import get_colors, _is_qualitative
from typing import Union, Optional, Tuple, List, Any

import warnings
warnings.filterwarnings("ignore")


def show_colors(
    c: Optional[Union[Colormap, str, List[str], Tuple[float, ...], List[Tuple[float, ...]]]] = None,
    names: Optional[List[str]] = None,
    title: str = "",
    size: Optional[Tuple[int, int]] = None,
    fmt: str = 'hex',
    verbose: bool = True,
    ax: Optional[plt.Axes] = None
) -> None:
    """
    Displays a set of colors as a grid layout with color names.

    This function creates a visualization of colors, either from a list, a single color,
    or a colormap. The colors are displayed in a grid with their hex values, and the
    text color is automatically chosen for readability based on the background color.

    Parameters
    ----------
    c : list of str or tuple, str or tuple, or matplotlib.colors.Colormap, optional
        Input colors to display. Can be:
        - A colormap name or instance
        - A single color str or rgb tuple
        - A list of colors str or rgb tuples
        If None, the matplotlib default color palettes will be shown.
    names : list of str, optional
        List of color names. If not provided, the hex values will be used.
    title : str, default=''
        Title to display above the color grid
    size : tuple of int, optional
        Size of the color grid (width, height)
    fmt: str, default='hex'
        Output format of color names ('hex', 'rgb', 'hsv', 'hsl')
    verbose : bool, default=True
        If True, prints the list of colors to the console
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, a new figure is created.

    Returns
    -------
    None
        Displays the color visualization using matplotlib

    Examples
    --------
    >>> show_colors(['#FF0000', '#00FF00', '#0000FF'])  # Display RGB colors
    >>> show_colors('viridis')  # Display viridis colormap colors
    >>> show_colors('viridis', size=(10, 5))  # Custom size
    >>> show_colors(None)  # Display matplotlib default color palettes
    """
    def _to_255(x):
        x255 = tuple([int(np.round(x_ * 255)) for x_ in x])
        return x255
    def _to_name(x: Tuple[float, ...]) -> str:
        name = [f'{int(np.round(x_ * 255)):3d}' for x_ in x]
        name = '  ' + ' '.join(name)
        return name
    # If None or empty list, show default colors
    if c is None:
        list_colors()
        return
    if _is_arraylike(c) and len(c) == 0:
        list_colors()
        return
    # Type-safe color extraction
    colors: List[Union[str, Tuple[float, ...]]]
    colormap_title = title
    # If c is a colormap, extract colors
    if _is_cmap(c):
        colors = get_colors(c, exclude_extreme=False)
        if not title:
            colormap_title = c if isinstance(c, str) else c.name
    # If color or list of colors, convert to list
    elif _is_arraylike(c) and not _is_rgb(c):
        colors = c
    elif _is_color(c):
        colors = [c]
    else:
        raise ValueError("Input must be a colormap, a color name, or a list of colors.")
    # Convert colors to RGB tuples
    rgbcolors = [to_rgb(color) for color in colors]
    # Format color names
    if fmt == 'hex':
        colors = [to_hex(color) for color in colors]
        cnames = colors
    elif fmt == 'rgb':
        colors = rgbcolors
        cnames = [_to_name(color) for color in colors if isinstance(color, tuple)]
    elif fmt == 'hsv':
        colors = [colorsys.rgb_to_hsv(*color) for color in rgbcolors]
        cnames = [_to_name(color) for color in rgbcolors if isinstance(color, tuple)]
    elif fmt == 'hsl':
        colors = [colorsys.rgb_to_hls(*color) for color in rgbcolors]
        cnames = [_to_name(color) for color in rgbcolors if isinstance(color, tuple)]
    if verbose:
        if fmt == 'hex':
            print(colors)
        else:
            print([_to_255(color) for color in rgbcolors])
    d = 0.05
    width = 1 - 2 * d
    if size is None:
        n, m = _aspect_ratio(len(rgbcolors), lmin=12)
        size = (2*n+4,2*m)
    else:
        n, m = size
        m = int(np.ceil(len(rgbcolors) / n))
        size = (2*n+4,2*m)
    fontsize = 12 if size[1] < 2 else 28
    # Display colors
    new_figure = ax is None
    if new_figure:
        plt.figure(figsize=size, facecolor="#00000000")
    else:
        ax.set_facecolor("#00000000")
    plt.title(colormap_title, fontsize=fontsize, color="grey")
    for k, rgb in enumerate(rgbcolors):
        i = k % n
        j = k // n
        if rgb is not None:
            r = Rectangle((i, -j), width, -width, facecolor=rgb, fill=True)
            plt.gca().add_patch(r)
            h, s, v = to_hsv(rgb)
            h, l, s = to_hls(rgb)
            fontcolor = "white" if v < 0.4 or l < 0.3 else "black"
            x, y = i + 0.55 - 2 * d, -j - 0.5
            name = names[k] if names is not None and k < len(names) else (cnames[k] if k < len(cnames) else "")
            if name is None:
                name = ""
            plt.text(x, y, str(name), fontsize=20, color=fontcolor, ha="center", va="center")
    plt.xlim(-d, n - d)
    plt.ylim(-m + d, d)
    plt.gca().set_axis_off()
    plt.tight_layout()
    if new_figure:
        plt.show()
        plt.close()
    return


def list_colors() -> None:
    """
    Displays a list of default colors as a grid layout with their names.

    This function creates a visualization of colors, either from a dictionary,
    or from the default color palettes. The colors are displayed in a grid with
    their hex values, and the text color is automatically chosen for readability
    based on the background color.

    Returns
    -------
    None
        Displays the color visualization using matplotlib
    """
    groups = {
        'Reds': [0.000, 0.050],
        'Oranges': [0.050, 0.110],
        'Yellows': [0.110, 0.150],
        'Yellow-Greens': [0.150, 0.220],
        'Greens': [0.220, 0.440],
        'Cyans': [0.440, 0.530],
        'Blues': [0.530, 0.730],
        'Violets': [0.730, 0.880],
        'Purples': [0.800, 1.100],
    }
    dcts = {
        'Base Colors': mc.BASE_COLORS,
        'Tableau Palette': mc.TABLEAU_COLORS,
        'CSS Colors': mc.CSS4_COLORS,
        'XKCD Colors': mc.XKCD_COLORS,
    }
    size = (10,1) # width, height
    for title, dct in dcts.items():
        
        cname = np.array(list(dct.keys()))
        color = np.array(list(dct.values()))
        hue, lightness, saturation = np.array([to_hls(v) for v in color]).T
    
        # Show small palettes 
        if len(color) < 20:
            subtitle = f'{title}'
            value = hue + (saturation > 0).astype(float)
            idx = np.argsort(value)
            cnames = cname[idx]
            colors = color[idx]
            hexnames = [to_hex(c) for c in colors]
            cnames = [f'{cnames[i]}\n{hexnames[i]}' for i in range(len(colors))]
            show_colors(colors, names=cnames, size=size, title=subtitle)

        # Show large palettes by hue groups
        else:
            # Show grays
            subtitle = f'{title} (Grays)'
            mask = saturation == 0
            cnames = cname[mask]
            colors = color[mask]
            lights = lightness[mask]
            idx = np.argsort(lights)
            cnames = cnames[idx]
            colors = colors[idx]
            if title.startswith('CSS'):
                cnames = [f'{cnames[i]}\n{colors[i]}' for i in range(len(colors))]
            else:
                cnames = [f'xkcd:\n{cnames[i][5:]}\n{colors[i]}' for i in range(len(colors))]
            show_colors(colors, names=cnames, size=size, title=subtitle)

            # Show color groups by hue
            for group, bins in groups.items():
                subtitle = f'{title} ({group})'
                hue0, hue1 = bins
                mask = (hue >= hue0) & (hue < hue1) & (saturation > 0)
                cnames = cname[mask]
                colors = color[mask]
                lights = lightness[mask]
                idx = np.argsort(lights)
                cnames = cnames[idx]
                colors = colors[idx]
                if title.startswith('CSS'):
                    cnames = [f'{cnames[i]}\n{colors[i]}' for i in range(len(colors))]
                else:
                    cnames = [f'xkcd:\n{cnames[i][5:]}\n{colors[i]}' for i in range(len(colors))]
                show_colors(colors, names=cnames, size=size, title=subtitle)

    return


def set_color_cycler(c: Union[List[str], str, Colormap], n: int = 6, globally: bool = False) -> None:
    """
    Sets the color cycler for matplotlib.

    This function configures the color cycling behavior for the current matplotlib
    axis using either a list of colors or a colormap. The colors will be used in
    sequence when plotting multiple lines or other elements.

    Parameters
    ----------
    c : list of str, str, or matplotlib.colors.Colormap
        Input colors to use in the cycler. Can be:
        - A list of color strings or rgb tuples
        - A colormap name or instance
    n : int, default=6
        Number of colors to extract from the colormap if a colormap is provided.
        If a list of colors is provided, this parameter is ignored.
    globally : bool, default=False
        If True, set the color cycler for all matplotlib axes in current python session.
        To reset to defaults use: plt.rcdefaults()

    Returns
    -------
    None
        This function does not return anything; it modifies the matplotlib state.

    Examples
    --------
    >>> set_color_cycler(['red', 'green', 'blue'])  # Use specific colors
    >>> set_color_cycler('viridis', n=5)  # Use 5 colors from viridis
    >>> plt.plot(x1, y1)  # Will use first color
    >>> plt.plot(x2, y2)  # Will use second color
    """
    try:
        if isinstance(c, str):
            c = colormaps[c]
        if isinstance(c, Colormap):
            colors = generate_stepwise_palette(c, n, use_hue=False)
            m = len(colors) // 2
            colors1, colors2 = colors[:m], colors[m:]
            colors = []
            while colors1 or colors2:
                if colors1:
                    colors.append(colors1.pop(0))
                if colors2:
                    colors.append(colors2.pop(0))
        else:
            colors = c
        # Set color cycler globally or locally
        if globally:
            plt.rcParams['axes.prop_cycle'] = cycler(color=colors)
        else:
            plt.gca().set_prop_cycle(cycler(color=colors))
    except:
        raise ValueError("Invalid color input. Must be a list of colors, a colormap name, or a Colormap instance.")
    return


def lighten(
    c: Union[Colormap, str, List[str], Tuple[float, ...], List[Tuple[float, ...]]],
    factor: float = 0.1,
    keep_alpha: bool = False,
    mode: str = 'hls'
) -> Union[str, List[str], Tuple[float, ...], List[Tuple[float, ...]], Colormap, ListedColormap, LinearSegmentedColormap, None]:
    """
    Lightens color(s) or a colormap by increasing lightness.

    This function takes colors or a colormap and returns lighter versions by
    increasing their lightness in HLS color space. 

    Parameters
    ----------
    c : list of str or tuple, str or tuple, or matplotlib.colors.Colormap
        Input colors to display. Can be:
        - A colormap name or instance
        - A single color str or rgb tuple
        - A list of colors str or rgb tuples
    factor : float, default=0.2
        Increment in lightness between 0 and 1:
    keep_alpha : bool, default=False
        If True, keep the alpha channel
    mode : str, default='hls'
        If 'hls' or 'hsl', use HLS color space to lighten the colors
        If 'hsv', use HSV color space to lighten the colors

    Returns
    -------
    list of str or tuple, str or tuple, or matplotlib.colors.Colormap
        Lightened version of the input color or colors.
        Returns same type as input.

    Examples
    --------
    >>> lighten('#FF0000', factor=0.5)  # Lighten red
    >>> lighten(['#FF0000', '#00FF00'], factor=0.3)  # Lighten multiple colors
    >>> lighten('viridis', factor=0.3)  # Lighten entire colormap
    """
    if mode not in ['hls', 'hsl', 'hsv']:
        raise ValueError("mode must be 'hls' or 'hsv'")
    factor = np.clip(factor, 0, 1)
    try:
        colors = None
        category = None
        if _is_cmap(c):
            if isinstance(c, str):
                c = colormaps[c]
            colors = get_colors(c, exclude_extreme=False)
            if not _is_qualitative(c):
                colors = get_colors(c, 256, exclude_extreme=False)
            category = "cmap"
        elif _is_color(c):
            colors = [c]
            category = _get_color_type(c)
        elif _is_arraylike(c):
            colors = c
            category = _get_color_type(c[0])
    except:
        colors = None
        category = None
    if colors is None:
        return None
    if len(colors) > 1:
        colors = [lighten(color, factor, keep_alpha, mode) for color in colors]
        if category == 'cmap':
            name = c.name + "_light"
            if _is_qualitative(c):
                colors = ListedColormap(colors, name=name)
            else:
                colors = LinearSegmentedColormap.from_list(name, colors)
    else:
        try:
            rgb = to_rgb(colors[0], keep_alpha=True)
            alpha = rgb[3] if len(rgb) == 4 else None
            if mode == 'hsv':
                hsv = np.array(to_hsv(rgb))
                hsv[2] = np.clip(hsv[2] + factor, 0, 1)
                rgb = mc.hsv_to_rgb(hsv[:3])
            elif mode in ['hls', 'hsl']:
                hls = np.array(to_hls(rgb))
                hls[1] = np.clip(hls[1] + factor, 0, 1)
                rgb = colorsys.hls_to_rgb(*hls[:3])
            rgb = rgb + (alpha,) if alpha is not None else rgb
            rgb = tuple([float(np.round(x, 4)) for x in rgb])
            # Format output
            colors = _format_output_color(rgb, category)
        except:
            colors = None
    return colors


def darken(
    c: Union[Colormap, str, List[str], Tuple[float, ...], List[Tuple[float, ...]]],
    factor: float = 0.1,
    keep_alpha: bool = False,
    mode: str = 'hls'
) -> Union[str, List[str], Tuple[float, ...], List[Tuple[float, ...]], Colormap, ListedColormap, LinearSegmentedColormap, None]:
    """
    Darkens color(s) or a colormap by decreasing lightness.

    This function takes colors or a colormap and returns darker versions by
    decreasing their lightness in HLS color space. 

    Parameters
    ----------
    c : list of str or tuple, str or tuple, or matplotlib.colors.Colormap
        Input colors to display. Can be:
        - A colormap name or instance
        - A single color str or rgb tuple
        - A list of colors str or rgb tuples
    factor : float, default=0.2
        Decrement in lightness between 0 and 1:
    keep_alpha : bool, default=False
        If True, keep the alpha channel
    mode : str, default='hls'
        If 'hls' or 'hsl', use HLS color space to darken the colors
        If 'hsv', use HSV color space to darken the colors

    Returns
    -------
    list of str or tuple, str or tuple, or matplotlib.colors.Colormap
        Darkened version of the input color or colors.
        Returns same type as input.

    Examples
    --------
    >>> darken('#FF0000', factor=0.5)  # Darken red
    >>> darken(['#FF0000', '#00FF00'], factor=0.3)  # Darken multiple colors
    >>> darken('viridis', factor=0.3)  # Darken entire colormap
    """
    if mode not in ['hls', 'hsl', 'hsv']:
        raise ValueError("mode must be 'hls' or 'hsv'")
    factor = np.clip(factor, 0, 1)
    try:
        colors = None
        category = None
        if _is_cmap(c):
            if isinstance(c, str):
                c = colormaps[c]
            colors = get_colors(c, exclude_extreme=False)
            if not _is_qualitative(c):
                colors = get_colors(c, 256, exclude_extreme=False)
            category = "cmap"
        elif _is_color(c):
            colors = [c]
            category = _get_color_type(c)
        elif _is_arraylike(c):
            colors = c
            category = _get_color_type(c[0])
    except:
        colors = None
        category = None
    if colors is None:
        return None
    if len(colors) > 1:
        colors = [darken(color, factor, keep_alpha, mode) for color in colors]
        if category == 'cmap':
            name = c.name + "_dark"
            if _is_qualitative(c):
                colors = ListedColormap(colors, name=name)
            else:
                colors = LinearSegmentedColormap.from_list(name, colors)
    else:
        try:
            rgb = to_rgb(colors[0], keep_alpha=True)
            alpha = rgb[3] if len(rgb) == 4 else None
            if mode == 'hsv':
                hsv = np.array(to_hsv(rgb))
                hsv[2] = np.clip(hsv[2] - factor, 0, 1)
                rgb = mc.hsv_to_rgb(hsv[:3])
            elif mode in ['hls', 'hsl']:
                hls = np.array(to_hls(rgb))
                hls[1] = np.clip(hls[1] - factor, 0, 1)
                rgb = colorsys.hls_to_rgb(*hls[:3])
            rgb = rgb + (alpha,) if alpha is not None else rgb
            rgb = tuple([float(np.round(x, 4)) for x in rgb])
            # Format output
            colors = _format_output_color(rgb, category)
        except:
            colors = None
    return colors

def saturate(
    c: Union[Colormap, str, List[str], Tuple[float, ...], List[Tuple[float, ...]]],
    factor: float = 0.1,
    keep_alpha: bool = False,
    mode: str = 'hls'
) -> Union[str, List[str], Tuple[float, ...], List[Tuple[float, ...]], Colormap, ListedColormap, LinearSegmentedColormap, None]:
    """
    Saturates color(s) or a colormap by increasing saturation.

    This function takes colors or a colormap and returns more saturated versions by
    increasing their saturation in HLS color space. 

    Parameters
    ----------
    c : list of str or tuple, str or tuple, or matplotlib.colors.Colormap
        Input colors to display. Can be:
        - A colormap name or instance
        - A single color str or rgb tuple
        - A list of colors str or rgb tuples
    factor : float, default=0.2
        Increment in saturation between 0 and 1:
    keep_alpha : bool, default=False
        If True, keep the alpha channel
    mode : str, default='hls'
        If 'hls' or 'hsl', use HLS color space to saturate the colors
        If 'hsv', use HSV color space to saturate the colors

    Returns
    -------
    list of str or tuple, str or tuple, or matplotlib.colors.Colormap
        Saturated version of the input color or colors.
        Returns same type as input.

    Examples
    --------
    >>> saturate('#FF0000', factor=0.5)  # Saturate red
    >>> saturate(['#FF0000', '#00FF00'], factor=0.3)  # Saturate multiple colors
    >>> saturate('viridis', factor=0.3)  # Saturate entire colormap
    """
    if mode not in ['hls', 'hsl', 'hsv']:
        raise ValueError("mode must be 'hls' or 'hsv'")
    factor = np.clip(factor, 0, 1)
    try:
        colors = None
        category = None
        if _is_cmap(c):
            if isinstance(c, str):
                c = colormaps[c]
            colors = get_colors(c, exclude_extreme=False)
            if not _is_qualitative(c):
                colors = get_colors(c, 256, exclude_extreme=False)
            category = "cmap"
        elif _is_color(c):
            colors = [c]
            category = _get_color_type(c)
        elif _is_arraylike(c):
            colors = c
            category = _get_color_type(c[0])
    except:
        colors = None
        category = None
    if colors is None:
        return None
    if len(colors) > 1:
        colors = [saturate(color, factor, keep_alpha, mode) for color in colors]
        if category == 'cmap':
            name = c.name + "_saturated"
            if _is_qualitative(c):
                colors = ListedColormap(colors, name=name)
            else:
                colors = LinearSegmentedColormap.from_list(name, colors)
    else:
        try:
            rgb = to_rgb(colors[0], keep_alpha=True)
            alpha = rgb[3] if len(rgb) == 4 else None
            if mode == 'hsv':
                hsv = np.array(to_hsv(rgb))
                hsv[1] = np.clip(hsv[1] + factor, 0, 1)
                rgb = mc.hsv_to_rgb(hsv[:3])
            elif mode in ['hls', 'hsl']:
                hls = np.array(to_hls(rgb))
                hls[2] = np.clip(hls[2] + factor, 0, 1)
                rgb = colorsys.hls_to_rgb(*hls[:3])
            rgb = rgb + (alpha,) if alpha is not None else rgb
            rgb = tuple([float(np.round(x, 4)) for x in rgb])
            # Format output
            colors = _format_output_color(rgb, category)
        except:
            colors = None
    return colors


def desaturate(
    c: Union[Colormap, str, List[str], Tuple[float, ...], List[Tuple[float, ...]]],
    factor: float = 0.1,
    keep_alpha: bool = False,
    mode: str = 'hls'
) -> Union[str, List[str], Tuple[float, ...], List[Tuple[float, ...]], Colormap, ListedColormap, LinearSegmentedColormap, None]:
    """
    Desaturates color(s) or a colormap by decreasing saturation.

    This function takes colors or a colormap and returns less saturated versions by
    decreasing their saturation in HLS color space. 

    Parameters
    ----------
    c : list of str or tuple, str or tuple, or matplotlib.colors.Colormap
        Input colors to display. Can be:
        - A colormap name or instance
        - A single color str or rgb tuple
        - A list of colors str or rgb tuples
    factor : float, default=0.2
        Decrement in saturation between 0 and 1:
    keep_alpha : bool, default=False
        If True, keep the alpha channel
    mode : str, default='hls'
        If 'hls' or 'hsl', use HLS color space to desaturate the colors
        If 'hsv', use HSV color space to desaturate the colors

    Returns
    -------
    list of str or tuple, str or tuple, or matplotlib.colors.Colormap
        Desaturated version of the input color or colors.
        Returns same type as input.

    Examples
    --------
    >>> desaturate('#FF0000', factor=0.5)  # Desaturate red
    >>> desaturate(['#FF0000', '#00FF00'], factor=0.3)  # Desaturate multiple colors
    >>> desaturate('viridis', factor=0.3)  # Desaturate entire colormap
    """
    if mode not in ['hls', 'hsl', 'hsv']:
        raise ValueError("mode must be 'hls' or 'hsv'")
    factor = np.clip(factor, 0, 1)
    try:
        colors = None
        category = None
        if _is_cmap(c):
            if isinstance(c, str):
                c = colormaps[c]
            colors = get_colors(c, exclude_extreme=False)
            if not _is_qualitative(c):
                colors = get_colors(c, 256, exclude_extreme=False)
            category = "cmap"
        elif _is_color(c):
            colors = [c]
            category = _get_color_type(c)
        elif _is_arraylike(c):
            colors = c
            category = _get_color_type(c[0])
    except:
        colors = None
        category = None
    if colors is None:
        return None
    if len(colors) > 1:
        colors = [desaturate(color, factor, keep_alpha, mode) for color in colors]
        if category == 'cmap':
            name = c.name + "_desaturated"
            if _is_qualitative(c):
                colors = ListedColormap(colors, name=name)
            else:
                colors = LinearSegmentedColormap.from_list(name, colors)
    else:
        try:
            rgb = to_rgb(colors[0], keep_alpha=True)
            alpha = rgb[3] if len(rgb) == 4 else None
            if mode == 'hsv':
                hsv = np.array(to_hsv(rgb))
                hsv[1] = np.clip(hsv[1] - factor, 0, 1)
                rgb = mc.hsv_to_rgb(hsv[:3])
            elif mode in ['hls', 'hsl']:
                hls = np.array(to_hls(rgb))
                hls[2] = np.clip(hls[2] - factor, 0, 1)
                rgb = colorsys.hls_to_rgb(*hls[:3])
            rgb = rgb + (alpha,) if alpha is not None else rgb
            rgb = tuple([float(np.round(x, 4)) for x in rgb])
            # Format output
            colors = _format_output_color(rgb, category)
        except:
            colors = None
    return colors


def _format_output_color(rgb, category):
    """ 
    Formats output color based on category. 

    Parameters
    ----------
    rgb : tuple or list
        An RGB or RGBA color tuple with values in the range [0, 1].

    Returns
    -------
    str
        A CSS-like formatted string, e.g., "rgb(255, 0, 0)" or "rgba(255, 0, 0, 1.0)".
    """
    output = None
    if category in ['hex', 'hexa', 'name']:
        output = to_hex(rgb, keep_alpha=True)
    elif category in ['rgb|hls|hsl|hsv|oklch', 'rgba']:
        output = rgb
    elif category in ['rgb255', 'rgba255']:
        output = rgb_to_rgb255(rgb, keep_alpha=True)
    elif category in ['rgb255 formatted', 'rgba255 formatted']:
        output = _to_formatted_rgb(rgb)
    elif category == 'hls formatted':
        output = _to_formatted_hls(rgb)
    elif category == 'hsl formatted':
        output = _to_formatted_hsl(rgb)
    elif category == 'hsv formatted':
        output = _to_formatted_hsv(rgb)
    elif category == 'oklch formatted':
        output = _to_formatted_oklch(rgb)
    return output


import types
__all__ = [name for name, thing in globals().items()
          if not (name.startswith("_") or isinstance(thing, types.ModuleType))]
del types

