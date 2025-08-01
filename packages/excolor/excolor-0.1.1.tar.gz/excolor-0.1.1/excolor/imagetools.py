#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains functions to manipulate images.
"""

import io
import requests
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.figure import Figure
import matplotlib.colors as mc
from matplotlib.axes import Axes
from typing import List, Callable, Tuple, Optional

import warnings
warnings.filterwarnings("ignore")


def _to_prime_factors(n: int) -> List[int]:
    """
    Decomposes an integer into its prime factors.

    This function takes an integer and returns a list of its prime factors.
    It uses trial division to find the prime factors.

    Parameters
    ----------
    n : int
        The integer to decompose into prime factors

    Returns
    -------
    factors : List[int]
        A list of prime factors of n

    Examples
    --------
    >>> _to_prime_factors(12)
    [2, 2, 3]
    >>> _to_prime_factors(100)
    [2, 2, 5, 5]
    """
    if n <= 2:
        factors = [n]
    else:
        factors = []
        i = 2
        while i * i <= n:
            if n % i:
                i += 1
            else:
                n //= i
                factors.append(i)
        factors.append(int(n))
    return factors


def _to_combinations(x: List[int]) -> List[List[int]]:
    """
    Generates all combinations of a list of integers.

    This function takes a list of integers and returns all possible combinations
    of the integers. It uses a recursive approach to generate all combinations.

    Parameters
    ----------
    x : List[int]
        The list of integers to generate combinations from

    Returns
    -------
    cs : List[List[int]]
        A list of all possible combinations of the integers in x

    Examples
    --------
    >>> _to_combinations([1, 2, 3])
    [[1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
    """
    if len(x) == 0:
        return [[]]
    comb = []
    for c in _to_combinations(x[1:]):
        comb += [c, c+[x[0]]]
    return comb


def _find_common_divisors(x: int, y: int) -> np.ndarray:
    """
    Finds all common divisors of two integers.

    This function takes two integers and returns a list of their common divisors.
    It uses trial division to find the common divisors.

    Parameters
    ----------
    x : int
        The first integer
    y : int
        The second integer

    Returns
    -------
    divisors : List[int]
        A list of common divisors of x and y

    Examples
    --------
    >>> _find_common_divisors(12, 18)
    [1, 2, 3, 6]
    """
    gcd = np.gcd(x, y)
    factors = _to_prime_factors(gcd)
    combs = _to_combinations(factors)
    divisors = np.unique([np.prod(c) for c in combs if len(c) > 0])
    return divisors


def pixels_to_size_and_dpi(size: Tuple[int, int], exact: bool = True) -> Tuple[Tuple[int, int], int]:
    """
    Converts pixel dimensions to optimal size in inches and DPI.

    This function takes pixel dimensions and converts them to physical size (in inches)
    and DPI (dots per inch) while maintaining the aspect ratio. It ensures the output
    size is at least 5 inches in the smaller dimension by adjusting the DPI if necessary.

    Parameters
    ----------
    size : Tuple[int, int]
        Image dimensions in pixels (width, height)
    exact : bool, default True
        If True, the size will match the target size exactly

    Returns
    -------
    Tuple[Tuple[int, int], int]
        A tuple containing:
        - Tuple[int, int]: Optimal size in inches (width, height)
        - int: DPI (dots per inch)

    Examples
    --------
    >>> pixels_to_size_and_dpi((1200, 800))  # ((6, 4), 200)
    >>> pixels_to_size_and_dpi((300, 300))   # ((5, 5), 60)
    """
    # Find optimal size
    x, y = size

    if x <= 0 or y <= 0:
        return (0, 0), 1
    
    # Generate size for DPI values in range 20 - 300
    dpi = 10 * np.arange(2,31)
    xs = np.ceil(x / dpi).astype(int)
    ys = np.ceil(y / dpi).astype(int)

    # Calculate error between target size and actual size
    err1 = np.abs(dpi * dpi * (xs * ys) - (x * y)) / (x * y)
    
    # Calculate error between target size and (5 x 5)
    err2 = np.abs((xs * ys) - 25) / 25
    
    # Calculate combined error
    err = 0.5 * (err1 + err2)
    
    # Select size and DPI by minimum of combined error
    k = np.argmin(err)
    dpi_ = int(dpi[k])
    inches_ = (int(xs[k]), int(ys[k]))
    
    # FInd exact size based on Greatest Common Divisor
    dpi = _find_common_divisors(*size)
    
    # Select exact DPI closest to optimal DPI
    err = np.abs(dpi - dpi_)
    k = np.argmin(err)
    dpi = int(dpi[k])
    inches = (int(x // dpi), int(y // dpi))

    # If exact == False and DPI falls outside 20 - 300 range, select optimal
    if dpi < 20 or dpi > 300:
        if not exact:
            dpi = dpi_
            inches = inches_
            
    return inches, dpi


def remove_margins() -> None:
    """ 
    Removes figure margins in matplotlib to keep only the plot area.

    This function removes all margins and axes from the current matplotlib figure,
    leaving only the plot area visible. It is useful for creating clean, borderless
    visualizations.

    Returns
    -------
    None

    Examples
    --------
    >>> plt.figure()
    >>> plt.plot([1, 2, 3])
    >>> remove_margins()  # Removes all margins and axes
    >>> plt.show()
    """
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    plt.margins(0,0)
    plt.axis("off")
    return


def load_image(fname: str) -> Image.Image:
    """
    Loads an image from a file or URL.

    Parameters
    ----------
    fname : str 
        Image path or url

    Returns
    -------
    img : PIL.PngImagePlugin.PngImageFile
        Image

    Examples
    --------
    >>> img = load_image("https://example.com/image.png")
    >>> img = load_image("image.png")
    """
    if fname.find("http://") == 0 or fname.find("https://") == 0:
        img = Image.open(requests.get(fname, stream=True).raw)
    else:
        img = Image.open(fname)
    return img


def img2arr(img: Image.Image) -> np.ndarray:
    """
    Converts a PIL Image to a numpy array.

    Notes
    -----
    Image dimensions are (y, x). Image y axis goes from top to bottom.
    Array dimensions are transposed to (x, y)
    Array y axis is reversed and goes from bottom to top.

    Parameters
    ----------
    img : PIL.Image.Image
        The image to convert

    Returns
    -------
    arr : numpy.ndarray
        The converted image
    """
    # Reverse y axis
    arr = np.array(img)[::-1,...]

    # Transpose array dimensions
    if arr.ndim == 2:
        arr = arr.transpose(1, 0)
    elif arr.ndim == 3:
        arr = arr.transpose(1, 0, 2)
    return arr


def arr2img(arr: np.ndarray) -> Image.Image:
    """
    Converts a numpy array to a PIL Image.

    Notes
    -----
    Array dimensions are (x, y). Array y axis goes from bottom to top.
    Image dimensions are transposed to (y, x). Image y axis goes from top to bottom.

    Parameters
    ----------
    arr : numpy.ndarray
        The array to convert

    Returns
    -------
    img : PIL.Image.Image
    """
    # Reverse y axis and transpose array dimensions
    if arr.ndim == 2:
        arr = arr[:,::-1].transpose(1, 0)
        img = Image.fromarray(arr)
    elif arr.ndim == 3:
        arr = arr[:,::-1,...].transpose(1, 0, 2)
        img = Image.fromarray(arr)
    return img


def mask2img(mask: np.ndarray) -> Image.Image:
    """
    Converts a binary numpy array to a PIL Image.

    Notes
    -----
    Array dimensions are (x, y). Array y axis goes from bottom to top.
    Image dimensions are transposed to (y, x). Image y axis goes from top to bottom.
    Array values are in range 0 - 1.

    Parameters
    ----------
    mask : numpy.ndarray
        The mask to convert

    Returns
    -------
    img : PIL.Image.Image
    """
    # Convert to uint8, reverse y axis and transpose array dimensions
    arr = np.clip(255 * (1 - mask), 0, 255).astype(np.uint8)
    return arr2img(arr)


def fig2img(fig: Optional[Figure] = None) -> Image.Image:
    """
    Converts a Matplotlib figure to a PIL Image and return it

    Parameters
    ----------
    fig : matplotlib.figure.Figure or None
        The figure to convert. If None, use plt.gcf()

    Returns
    -------
    img : PIL.Image.Image
        The converted image
    """
    if fig is None:
        fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    img = Image.open(buf)
    return img


def fig2img_from_canvas(fig: Optional[Figure] = None) -> Image.Image:
    """
    Converts a Matplotlib figure to a PIL Image from the canvas and return it

    Parameters
    ----------
    fig : matplotlib.figure.Figure or None
        The figure to convert. If None, use plt.gcf()

    Returns
    -------
    img : PIL.Image.Image
        The converted image
    """
    if fig is None:
        fig = plt.gcf()
    fig.canvas.draw()
    img = np.asarray(fig.canvas.renderer._renderer)
    img = Image.fromarray(img)
    return img


def add_layer(fig: Figure, size: Tuple[int, int], layer: Image.Image, start: Tuple[int, int] = (0, 0)) -> None:
    """
    Adds a layer to an image using plt.imshow().

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The base figure
    size : Tuple[int, int]
        The size of the figure canvas in pixels
    layer : PIL.Image.Image
        The layer to add
    start : Tuple[int, int], default (0, 0)
        The starting position of the layer in the image
    """
    #Calculate position and size of layer [left, bottom, width, height] in figure fraction
    width, height = size
    x = start[0] / width
    y = start[1] / height
    w = layer.size[0] / width
    h = layer.size[1] / height

    # Add layer to figure
    ax = fig.add_axes([x, y, w, h])
    ax.imshow(np.array(layer))
    ax.axis('off')  # Hide axes for clean display
    return


def _find_midpoint(data: np.ndarray) -> np.ndarray:
    """
    Identifies midpoint in a distribution of color intensities.

    This function analyzes a distribution of color intensities to find 
    midpoint. Uses a multi-scale approach with adaptive window size.

    Parameters
    ----------
    data : numpy.ndarray
        1D array of color intensity values to analyze

    Returns
    -------
    numpy.ndarray
        Array of intensity values at which peaks are found.
        Returns at least 2 peaks if found, otherwise returns [0, 1].

    Examples
    --------
    >>> # Find peaks in a bimodal distribution
    >>> rng = np.random.default_rng(0)
    >>> data = np.concatenate([rng.normal(0.2, 0.1, 100),
    ...                       rng.normal(0.8, 0.1, 100)])
    >>> peaks = find_peaks(data)
    >>> # Find peaks in a uniform distribution
    >>> rng = np.random.default_rng(0)
    >>> data = rng.random(200)
    >>> peaks = find_peaks(data)  # Likely returns [0, 1]
    """
    values = np.clip(data.flatten(), 0, 1)
    bins = np.round(np.linspace(-0.1,1.1,121), 2)
    idx = 0.5 * (bins[:-1] + bins[1:])
    hist, _ = np.histogram(values, bins)
    windows = np.logspace(0,6,13,base=2)[::-1]
    peaks = np.arange(2)
    midpoint = 0.5
    for window in windows:
        w = np.hanning(max(1, window))
        smooth = np.convolve(hist, w/np.sum(w), mode="same")
        smooth = smooth * np.sum(hist) / np.sum(smooth)
        diff = np.diff(smooth)
        mask = (diff[:-1] > 0) & (diff[1:] <= 0)
        if np.sum(mask) >= 2:
            imax = idx[1:-1][mask]
            err = hist > 5 * smooth
            imax = np.concatenate([imax, idx[err]])
            imax = np.unique(imax)
            i = np.argmax(np.diff(imax))
            peaks = np.array([imax[i], imax[i+1]])
            midpoint = np.mean(peaks)
            break
    return midpoint


def colorize_image(image, facecolor="blue", backgroundcolor=None, contrast=0.5):
    """
    Colorizes a b&w image

    Parameters
    ----------
    image : str or PIL.PngImagePlugin.PngImageFile
        Image or file path
    facecolor : str or tuple of float
        Face color. Can be:
        - A color name (e.g., 'red')
        - A hex string (e.g., '#FF0000')
        - An RGB tuple (e.g., (1.0, 0.0, 0.0))
    backgroundcolor : str or tuple of float or None, default None
        Background color. Can be:
        - A color name (e.g., 'red')
        - A hex string (e.g., '#FF0000')
        - An RGB tuple (e.g., (1.0, 0.0, 0.0))
    contrast : float, default 0.5
        Contrast of the colorized image (0 - 1)

    Returns
    -------
    img : PIL.PngImagePlugin.PngImageFile
        Colorized image

    """
    # Read image and convert to numpy array
    img = image
    if isinstance(img, str):
        img = load_image(img)
    x = np.asarray(img).astype(float)
    # Calculate color intensity
    has_alpha = x.ndim == 3 and x.shape[2] % 2 == 0
    if has_alpha:
        x = x[...,-1]
    else:
        x = np.mean(x, axis=2)
    x = 1 - x / 255
    # Find intensity midpoint and range
    x0 = _find_midpoint(x)
    dx = x0 if x0 <= 0.5 else 1 - x0
    contrast = np.clip(contrast, 0.01, 0.99)
    dx = dx * (1 - contrast)
    # Normalize intensity range
    x = (x - x0) / dx
    x[x < 0] = 0
    x[x > 1] = 1
    # Calc RGBA channels based on color fractions
    c1 = mc.to_rgba(facecolor)
    c0 = mc.to_rgba(backgroundcolor) if backgroundcolor is not None else (0.,0.,0.,0.)
    rgba = [x * c1[i] + (1 - x) * c0[i] for i in range(4)]
    rgba = np.stack(rgba, 2)
    rgba = 255 * np.clip(rgba, 0, 1)
    img = Image.fromarray(rgba.astype(np.uint8))
    return img


def resize_image(image, size):
    """
    Resizes an image to the specified size

    Parameters
    ----------
    image : str or PIL.PngImagePlugin.PngImageFile
        Image or file path
    size : float or tuple of int
        If float, the image is resized to the specified scale factor.
        If tuple, the image is resized to the specified size in pixels (width, height).

    Returns
    -------
    img : PIL.PngImagePlugin.PngImageFile
        Resized image
    """
    # Read image and convert to numpy array
    img = image
    if isinstance(img, str):
        img = load_image(img)
    # Resize image
    if isinstance(size, (float, int)):
        size = (int(img.size[0] * size), int(img.size[1] * size))
    img = img.resize(size)
    return img

def greyscale_image(image):
    """
    Converts an image to greyscale keeping channels

    Parameters
    ----------
    image : str or PIL.PngImagePlugin.PngImageFile
        Image or file path

    Returns
    -------
    img : PIL.PngImagePlugin.PngImageFile
        Greyscaled image

    """
    # Read image and convert to numpy array
    img = image
    if isinstance(img, str):
        img = load_image(img)
    x = np.asarray(img).astype(float)
    if x.ndim == 3 and x.shape[2] > 1:
        y = np.mean(x[:, :, :3], axis=2)
        y = np.clip(y, 0, 255)
        for i in range(3):
            x[:, :, i] = y
    grayscale = Image.fromarray(x.astype(np.uint8))
    return grayscale


""" Aliases for functions """
grayscale_image: Callable[..., None] = greyscale_image


import types
__all__ = [name for name, thing in globals().items()
          if not (name.startswith("_") or isinstance(thing, types.ModuleType))]
del types
