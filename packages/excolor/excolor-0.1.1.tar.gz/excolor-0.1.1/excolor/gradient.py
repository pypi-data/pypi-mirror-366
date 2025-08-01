#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains functions to manipulate gradients.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mc
from matplotlib.colors import ListedColormap, Colormap
from matplotlib.patches import Rectangle
from matplotlib.axes import Axes
from .colortools import lighten, darken
from .colortypes import _get_color_type
from .cmaptools import get_bgcolor
from .utils import interpolate_colors
from typing import Union, Tuple, List, Optional
from PIL import Image

import warnings
warnings.filterwarnings("ignore")


def _get_gradient_colors(c: Union[List[str], str, Colormap], n: int = None) -> List[str]:
    """
    Converts a color string, a cmap, or a list of colors to a list of gradient colors.

    Parameters
    ----------
    c : list of str, str, or matplotlib.colors.Colormap
        Input colors or colormap. Can be:
        - A list of color strings
        - A color name (str)
        - A colormap name (str)
        - A Colormap instance
    n : int or None
        Number of colors to generate. Used if list of colors is not provided explicitly.

    Returns
    -------
    colors : list of str
        List of gradient colors

    Examples
    --------
    >>> colors = get_gradient_colors('gruvbox')
    >>> print(colors)
    """
    if _get_color_type(c) is None and isinstance(c, list):
        colors = c
    else:
        try:
            color = get_bgcolor(c)
        except:
            color = c
        colors = [lighten(color, 0.15), color, darken(color, 0.15), darken(color, 0.3)]
    if n is not None:
        if n <= 1:
            colors = [colors[max(0,1)]]
        else:
            colors = interpolate_colors(colors, n)
    return colors


def _set_gradient_sources(n: int, nx: int, ny: int, angle: float = 0) -> Tuple[np.ndarray, np.ndarray]:
    """
    Sets coordinates of color sources for background gradients in a circular pattern.
    
    Parameters
    ----------
    n : int
        Number of color sources to place around the circle
    nx : int
        Number of pixels along horizontal axis
    ny : int
        Number of pixels along vertical axis
    angle : float, default=0
        Angle = 0 means that first color source is at the right edge of the image.
        The angle increases in math style (counter-clockwise). 

    Returns
    -------
    x : numpy.ndarray
        X-coordinates of sources, centered around the middle of the image
    y : numpy.ndarray
        Y-coordinates of sources, centered around the middle of the image

    Notes
    -----
    The sources are placed on a circle with radius equal to half the diagonal
    of the image. The circle is centered at the middle of the image.
    """
    r = np.sqrt(nx**2 + ny**2) / 2
    phi0 = np.pi * angle / 180.0
    phi = phi0 + np.arange(n) * 2 * np.pi / n
    phi = - phi # reverse the direction to count angle in math style
    z = r * np.exp(1j * phi)
    x = z.real
    y = z.imag
    return x, y


def show_gradient_sources(c: Union[List[str], str, Colormap], nx: int = 160, ny: int = 90, angle: float = 0) -> None:
    """
    Visualizes the positions of color sources on a background grid.

    This function creates a plot showing where color sources would be placed
    for a given set of colors and image dimensions.

    Parameters
    ----------
    c : list of str, str, or matplotlib.colors.Colormap
        Input colors or colormap. Can be:
        - A list of color strings
        - A color name (str)
        - A colormap name (str)
        - A Colormap instance
    nx : int, default=160
        Number of pixels along horizontal axis
    ny : int, default=90
        Number of pixels along vertical axis
    angle : float, default=0
        Angle = 0 means that first color source is at the right edge of the image.
        The angle increases in math style (counter-clockwise). 

    Returns
    -------
    None
        Displays a matplotlib figure showing the color source positions

    Examples
    --------
    >>> show_gradient_sources(['#FF0000', '#00FF00', '#0000FF'])
    # Shows a plot with three color sources arranged in a circle
    """
    colors = _get_gradient_colors(c)
    n = len(colors)
    x, y = _set_gradient_sources(n, nx, ny, angle)
    x += nx/2
    y += ny/2
    plt.figure(figsize=(6,5), facecolor="w")
    r = Rectangle((0,0), nx, ny, edgecolor="k", fill=False)
    plt.gca().add_patch(r)
    cmap = ListedColormap(colors, "cmap")
    plt.scatter(x, y, c=np.arange(n), cmap=cmap, s=100)
    for i in range(n):
        dx = min(nx, ny) / 25
        plt.text(x[i] + dx, y[i], i + 1)
    plt.colorbar()
    plt.gca().invert_yaxis()
    plt.show()
    return


def fill_gradient(
    c: Union[List[str], str, Colormap],
    size: Tuple[int, int] = (1280, 720),
    angle: float = 0,
    show: Optional[bool] = None,
    fname: Optional[str] = None
) -> Image.Image:
    """
    Creates a gradient background image based on input colors or colormap.

    This function generates a smooth gradient background using color sources
    arranged in a circular pattern. The gradient is created by interpolating
    between the color sources using inverse distance weighting.

    Parameters
    ----------
    c : list of str, str, or matplotlib.colors.Colormap
        Input colors or colormap. Can be:
        - A list of color strings
        - A color name (str)
        - A colormap name (str)
        - A Colormap instance
    size : tuple of int, default=(1280, 720)
        Size of the output image in pixels (width, height)
    angle : float, default=0
        Angle = 0 means that first color source is at the right edge of the image.
        The angle increases in math style (counter-clockwise). 
    show : bool, optional
        Whether to display the generated image using matplotlib.
        If None, will show only if fname is None
    fname : str, optional
        If provided, saves the image to the specified file path.
        Supported formats: .png, .jpg, .svg

    Returns
    -------
    PIL.Image.Image
        The generated gradient background image in RGBA format

    Notes
    -----
    The function:
    1. Processes input colors to get a suitable palette
    2. Places color sources in a circular pattern
    3. Creates a gradient by interpolating between sources
    4. Optionally displays or saves the result

    Examples
    --------
    >>> img = background_gradient('viridis', size=(800, 600))
    >>> img.show()
    """
    epsilon = 1e-5
    # If only one color is given, expand it to darker and lighter
    colors = _get_gradient_colors(c)
    nx, ny = size
    n = len(colors)
    # Set color source coordinates
    x0, y0 = _set_gradient_sources(n, nx, ny, angle)
    a0 = np.arctan2(y0, x0)
    r0 = np.sqrt(x0**2 + y0**2)
    # Set pixel coordinates
    x = np.arange(nx) - (nx - 1) / 2
    y = np.arange(ny) - (ny - 1) / 2
    x, y = np.meshgrid(x, y, indexing="xy")
    x, y = x.flatten(), y.flatten()
    a = np.arctan2(y, x)
    r = np.sqrt(x**2 + y**2)
    # Iterate through color sources
    dist = []
    for i in range(n):
        a_ = a - a0[i]
        r_ = r * np.cos(a_)
        d = r0[i] - r_
        dist.append(d)
    d = np.stack(dist)
    f = np.power(d + epsilon, -1.2)
    f = f / np.sum(f, axis=0)
    # Calc color fractions
    rgb = np.stack([mc.to_rgb(color) for color in colors]).T
    rgba = [np.dot(rgb[i], f) for i in range(3)] + [np.ones(nx * ny)]
    rgba = np.stack([rgba[i].reshape(ny,nx) for i in range(4)], axis=2)
    rgba = np.clip(255 * rgba, 0, 255).astype(np.uint8)
    img = Image.fromarray(rgba, "RGBA")
    if fname is not None:
        if len(fname) < 5 or fname[-4:] not in [".png", ".jpg", ".svg"]:
            fname = f"{fname}.png"
        img.save(fname)
    if show is None and fname is None:
        show = True
    if show == True:
        plt.figure(facecolor="#00000000")
        plt.imshow(img)
        plt.gca().set_axis_off()
        plt.show()
    plt.close()
    return img


import types
__all__ = [name for name, thing in globals().items()
          if not (name.startswith("_") or isinstance(thing, types.ModuleType))]
del types
