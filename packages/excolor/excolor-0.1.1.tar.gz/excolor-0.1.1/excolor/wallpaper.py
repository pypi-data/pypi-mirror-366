#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains functions to create wallpaper-like images.
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.colors as mc
from pythonperlin import perlin
from matplotlib.colors import LinearSegmentedColormap, Colormap
from matplotlib.axes import Axes
from typing import Union, Tuple, List, Optional, Any
from .patch import Patch
from .cmaptools import get_bgcolor
from .palette import generate_stepwise_palette
from .colortools import _is_cmap, get_colors, lighten, darken, to_rgb, to_hex
from .gradient import _get_gradient_colors, fill_gradient
from .imagetools import *
import random
import io
import cv2

import warnings
warnings.filterwarnings("ignore")




def _sigmoid(x: Union[float, np.ndarray], midpoint: float = 0.5, slope: float = 25) -> Union[float, np.ndarray]:
    """
    Sigmoid function for smooth transitions

    Parameters
    ----------
    x : float or np.ndarray
        Input value (0 to 1)
    midpoint : float, default 0.5
        Center of the transition (0 to 1)
    slope : float, default 25
        Steepness of the transition

    Returns
    -------
    float
        Sigmoid value (0 to 1)
    """
    return 1 / (1 + np.exp(-slope * (x - midpoint)))


def _get_circle_dots(r: float = 1, n: int = 360) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates points at equal arc length intervals on a circle.

    This function creates a set of points distributed evenly along the circumference
    of a circle. The points are generated using complex number representation and
    converted to Cartesian coordinates.

    Parameters
    ----------
    r : float, default=1
        Radius of the circle
    n : int, default=360
        Number of points to generate

    Returns
    -------
    Tuple[numpy.ndarray, numpy.ndarray]
        A tuple containing:
        - numpy.ndarray: X coordinates of points on the circle
        - numpy.ndarray: Y coordinates of points on the circle

    Examples
    --------
    >>> # Generate points on a unit circle
    >>> x, y = _get_circle_dots()
    >>> # Generate points on a circle with radius 2
    >>> x, y = _get_circle_dots(r=2)
    >>> # Generate fewer points
    >>> x, y = _get_circle_dots(n=100)
    """
    phi = np.linspace(0, 2 * np.pi, n + 1)[:-1]
    z = r * np.exp(1j * phi)
    x, y = z.real, z.imag
    return x, y
    

def _get_ellipse_dots(a: float = 5, b: float = 3, n: int = 360) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generates points at approximately equal arc length intervals on an ellipse.

    This function creates a set of points distributed along the circumference
    of an ellipse. The points are generated using a two-step process:
    1. First creates a high-density set of points
    2. Then selects points that are approximately equidistant along the arc

    Parameters
    ----------
    a : float, default=5
        Semi-major axis length
    b : float, default=3
        Semi-minor axis length
    n : int, default=360
        Number of points to generate

    Returns
    -------
    Tuple[numpy.ndarray, numpy.ndarray]
        A tuple containing:
        - numpy.ndarray: X coordinates of points on the ellipse
        - numpy.ndarray: Y coordinates of points on the ellipse

    Examples
    --------
    >>> # Generate points on a default ellipse (a=5, b=3)
    >>> x, y = _get_ellipse_dots()
    >>> # Generate points on a circle (a=b=1)
    >>> x, y = _get_ellipse_dots(a=1, b=1)
    >>> # Generate fewer points
    >>> x, y = _get_ellipse_dots(n=100)
    """
    # Initialize half of points with increased density
    x = np.linspace(a, -a, 20 * n)
    y = np.sqrt(a**2 - x**2) * b / a
    # Add lower half of points
    x = np.concatenate([x[:-1], x[::-1]])
    y = np.concatenate([y[:-1], -y[::-1]])
    # Calc distance between high-density points
    l = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
    # Calc distance between requested points
    dl = np.sum(l) / n
    # Find indices of equidistant points along the ellipse arc
    l = np.cumsum(l) % dl
    d = np.diff(l)
    mask = (d[1:-1] < d[:-2]) & (d[1:-1] < d[2:])
    idx = np.arange(len(mask)) + 2
    idx = np.concatenate([(0,), idx[mask]])
    x = x[idx]
    y = y[idx]
    return x, y


def _distort_radius(x: np.ndarray, y: np.ndarray, p: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Applies radial distortion to a set of 2D points.

    This function takes a set of (x, y) coordinates centered at the origin
    and applies a radial distortion by adding noise to the radius while
    preserving the angle of each point.

    Parameters
    ----------
    x : numpy.ndarray
        X coordinates of points (centered at origin)
    y : numpy.ndarray
        Y coordinates of points (centered at origin)
    p : numpy.ndarray
        Noise values to add to the radius of each point

    Returns
    -------
    Tuple[numpy.ndarray, numpy.ndarray]
        A tuple containing:
        - numpy.ndarray: Distorted X coordinates
        - numpy.ndarray: Distorted Y coordinates

    Examples
    --------
    >>> # Create points on a circle
    >>> x, y = get_circle_dots(r=1, n=100)
    >>> # Add random noise
    >>> rng = np.random.default_rng(0)
    >>> noise = rng.normal(0, 0.1, 100)
    >>> x_dist, y_dist = _distort_radius(x, y, noise)
    >>> # Add systematic distortion
    >>> distortion = np.sin(np.linspace(0, 2*np.pi, 100)) * 0.2
    >>> x_dist, y_dist = _distort_radius(x, y, distortion)
    """
    z = x + 1j * y
    phi = np.angle(z)
    r = np.abs(z) + p
    z = r * np.exp(1j * phi)
    x, y = z.real, z.imag
    return x, y


def sigmoid_wallpaper(
    colors: Union[List[str], str, Colormap],
    background: Union[str, Image.Image, None] = None,
    size: Tuple[int, int] = (1280, 720),
    n: int = 5,
    sigmoid_shift: Union[float, None] = None,
    sigmoid_span: Union[float, None] = None,
    midpoint: float = 0.5,
    slope: float = 25,
    shadow: bool = True,
    fname: Optional[str] = None,
) -> Image.Image:
    """
    Creates a wallpaper with sigmoid patches.

    This function generates a wallpaper with sigmoid patches, using the
    provided colors and background.

    Parameters
    ----------
    colors : list of str, str, matplotlib.colors.Colormap
        Input colors or colormap. Can be:
        - A list of color strings
        - A color name (str)
        - A colormap name (str)
        - A Colormap instance
    background : str, or PIL.Image.Image, optional
        Background color or image. Can be:
        - A color name or hex string
        - A PIL Image object
    size : tuple of int, default=(1280, 720)
        Size of the output image in pixels (width, height)
    n : int, default=5
        Number of color patches. Used if list of colors is not provided explicitly.
    sigmoid_shift : float, default=0.0
        Vertical shift of the sigmoid function (0 - 0.5)
    sigmoid_span : float, default=1.0
        Vertical span of the sigmoid function (0.6 - 1)
    midpoint : float, default=0.5
        Midpoint of the sigmoid function in fraction of the image width (0.2 - 0.8)
    slope : float, default=25
        Slope of the sigmoid function
    shadow : bool, default=True
        Whether to add a shadow to the wallpaper
    fname : str, optional
        If provided, saves the image to the specified file path

    Returns
    -------
    PIL.Image.Image
        The generated wallpaper as a PIL Image object. If `fname` is provided,
        the image is also saved to the specified file path.

    Examples
    --------
    >>> colors = ['#FF0000', '#00FF00', '#0000FF']
    >>> wallpaper = sigmoid_wallpaper(colors, size=(800, 600))
    >>> plt.imshow(wallpaper)
    >>> plt.show()
    """
    # Parse background image
    if isinstance(background, Image.Image):
        # resize background image
        if background.size != size:
            background = background.resize(size)
        # Flip vertically
        background = background.transpose(Image.FLIP_TOP_BOTTOM)
        
    # Parse colors and fill background
    if _is_cmap(colors):
        if background is None:
            background = Image.new("RGB", size, get_bgcolor(colors))
        colors = generate_stepwise_palette(colors, n)
    else:
        colors = _get_gradient_colors(colors, n)
        n = len(colors)
    if background is None:
        background = Image.new("RGB", size, 'black')
    else:
        background = Image.new("RGB", size, background)
        
    # Create sigmoid patches
    midpoint = np.clip(midpoint, 0.2, 0.8)
    midpoints = np.array([midpoint - 0.1 * i for i in range(n)])
    if midpoints.min() < 0.1:
        midpoints = np.linspace(0.1, midpoint, n)[::-1]
    midpoints = np.round(midpoints, 2)

    if sigmoid_shift is None:
        sigmoid_shifts = [0 for _ in range(n)]
    else:
        sigmoid_shift = np.clip(sigmoid_shift, 0.0, 0.5)
        sigmoid_shifts = np.array([sigmoid_shift + 0.05 * i for i in range(n)])
        if sigmoid_shifts.max() > 0.4:
            sigmoid_shifts = np.linspace(sigmoid_shift, 0.4, n)
        sigmoid_shifts = np.round(sigmoid_shifts, 2)

    if sigmoid_span is None:
        sigmoid_scales = [1 for _ in range(n)]
    elif sigmoid_shift is None:
        sigmoid_span = np.clip(sigmoid_span, 0.5, 1.0)
        sigmoid_spans = np.array([sigmoid_span + 0.05 * i for i in range(n)])
        if sigmoid_spans.max() > 1:
            sigmoid_spans = np.linspace(sigmoid_span, 1, n + 1)[:-1]
        sigmoid_spans = np.round(sigmoid_spans, 2)
        sigmoid_scales = sigmoid_spans
    else:
        sigmoid_scales = [sigmoid_span - sigmoid_shifts.max()] * n
        sigmoid_scales = np.round(sigmoid_scales, 2)

    # Creaate matplotlib figure
    inches, dpi = pixels_to_size_and_dpi(size, exact=True)
    fig = plt.figure(figsize=inches, dpi=dpi, facecolor='w')
    plt.xlim(0,size[0])
    plt.ylim(0,size[1])

    # Show background image
    wallpaper = background
    plt.imshow(wallpaper)
    remove_margins()

    # Draw sigmoid patches
    nx = 100
    epsilon = 0.02
    x_max = size[0] * (1 + epsilon)
    y_max = size[1] * (1 + epsilon)
    x_min = -size[0] * epsilon
    y_min = -size[1] * epsilon
    for i in range(n):
        # Generate sigmoid y values
        x = np.linspace(0, 1, nx + 1)
        y = _sigmoid(x, midpoints[i], slope)
        y = y * sigmoid_scales[i] + sigmoid_shifts[i]
        y = y * (1 + 2 * epsilon) - epsilon
        # Scale to image size
        x = (x * size[0]).astype(int)
        y = (y * size[1]).astype(int)
        # Add corner point coordinates to the patch
        x = np.concatenate([x, [x_max, x_min, x_min]])
        y = np.concatenate([y, [y_max, y_max, y_min]])
        coords = [(x[i], y[i]) for i in range(nx + 3)]
        # Create patch
        patch = Patch(coords)
        patch.fill_solid(colors[i])
        if shadow:
            sigma = 10 * size[1] / 100
            kernel = 20 * size[1] / 100
            kernel = (kernel, kernel)
            patch.cast_shadow(wallpaper, kernel=kernel, sigma=sigma)
        # Draw patch
        patch.draw(fig, size)

    # Convert figure to image
    wallpaper = fig2img(fig)
    plt.close(fig)

    # Save to file if provided
    if fname is not None:
        wallpaper.save(fname)

    return wallpaper


def perlin_wallpaper(
    colors: Union[List[str], str, Colormap],
    background: Union[str, Image.Image, None] = None,
    size: Tuple[int, int] = (1280, 720),
    n: int = 5,
    shadow: bool = True,
    center: Tuple[float, float] = (0, 0),
    seed: int = 0,
    fname: Optional[str] = None,
) -> Image.Image:
    """
    Creates a wallpaper with Perlin noise patches.

    This function generates a wallpaper with Perlin noise patches, using the
    provided colors and background.

    Parameters
    ----------
    colors : list of str, str, matplotlib.colors.Colormap
        Input colors or colormap. Can be:
        - A list of color strings
        - A color name (str)
        - A colormap name (str)
        - A Colormap instance
    background : str, or PIL.Image.Image, optional
        Background color or image. Can be:
        - A color name or hex string
        - A PIL Image object
    size : tuple of int, default=(1280, 720)
        Size of the output image in pixels (width, height)
    n : int, default=5
        Number of color patches. Used if list of colors is not provided explicitly.
    shadow : bool, default=True
        Whether to add a shadow to the wallpaper
    center : tuple of float, default=(0, 0)
        Coordinates of the circle center from the right bottom corner in pixels
    seed : int, default=0
        Random seed for the Perlin noise generation
    fname : str, optional
        If provided, saves the image to the specified file path

    Returns
    -------
    PIL.Image.Image
        The generated wallpaper as a PIL Image object. If `fname` is provided,
        the image is also saved to the specified file path.

    Examples
    --------
    >>> colors = ['#FF0000', '#00FF00', '#0000FF']
    >>> wallpaper = perlin_wallpaper(colors, size=(800, 600))
    >>> plt.imshow(wallpaper)
    >>> plt.show()
    """
    # Parse background image
    if isinstance(background, Image.Image):
        # resize background image
        if background.size != size:
            background = background.resize(size)
        # Flip vertically
        background = background.transpose(Image.FLIP_TOP_BOTTOM)
    elif isinstance(background, str):
        background = Image.new("RGB", size, background)
        
    # Parse colors and fill background
    if _is_cmap(colors):
        if background is None:
            background = Image.new("RGB", size, get_bgcolor(colors))
        colors = generate_stepwise_palette(colors, n)
    else:
        colors = _get_gradient_colors(colors)
        n = len(colors)
    if background is None:
        background = Image.new("RGB", size, 'black')

    # Calculate radius of perlin patches
    n_major = len(colors)
    x_max = size[0] + center[0]
    y_max = size[1] - center[1]
    r_max = np.sqrt(x_max**2 + y_max**2)
    r_min = 0.6 * r_max
    dr_major = (r_max - r_min) / n_major

    # Generate perlin noise
    dens = 20
    n = np.ceil(n_major * 6 / dens).astype(int) + 1
    p = perlin((n,36), dens=dens, seed=seed)[dens//2:]

    # Creaate matplotlib figure
    inches, dpi = pixels_to_size_and_dpi(size, exact=True)
    fig = plt.figure(figsize=inches, dpi=dpi, facecolor='w')
    plt.xlim(0,size[0])
    plt.ylim(0,size[1])

    # Show background image
    wallpaper = background
    plt.imshow(wallpaper)
    remove_margins()

    # Draw sigmoid patches
    epsilon = 0.02
    x_max = size[0] * (1 + epsilon)
    y_max = size[1] * (1 + epsilon)
    x_min = -size[0] * epsilon
    y_min = -size[1] * epsilon
    for i in range(n_major):
        k = 8 * i
        r = r_min + dr_major * i
        x, y = _get_circle_dots(r, n=720)
        scale = 15 * size[1] / 100
        x, y = _distort_radius(x, y, scale * p[k])
        x += size[0] + center[0]
        y += center[1]
        # Change angle direction to clockwise (so that the coords are oriented like in sigmoid_wallpaper)
        x = x[::-1]
        y = y[::-1]
        mask = (x >= x_min) & (x <= x_max) & (y >= y_min) & (y <= y_max)
        if any(mask):
            # Add corner point coordinates to the patch
            x = np.concatenate([x[mask], [x_max, x_min, x_min]])
            y = np.concatenate([y[mask], [y_max, y_max, y_min]])
            coords =[(x[i], y[i]) for i in range(len(x))]
            # Create patch
            patch = Patch(coords)
            patch.fill_solid(colors[i])
            if shadow:
                sigma = 10 * size[1] / 100
                kernel = 20 * size[1] / 100
                kernel = (kernel, kernel)
                patch.cast_shadow(wallpaper, kernel=kernel, sigma=sigma)
            # Draw patch
            patch.draw(fig, size)

    # Convert figure to image
    wallpaper = fig2img(fig)
    plt.close(fig)

    # Save to file if provided
    if fname is not None:
        wallpaper.save(fname)

    return wallpaper


def perlin_lines(
    colors: List[str],
    background: Union[str, Image.Image, None] = None,
    size: Tuple[int, int] = (1280, 720),
    n: int = 5,
    m: int = 5,
    center: Tuple[float, float] = (0, 0),
    seed: int = 0,
    fname: Optional[str] = None,
) -> Image.Image:
    """
    Creates a wallpaper with Perlin noise lines.

    This function generates a wallpaper with Perlin noise lines, using the
    provided colors and background.

    Parameters
    ----------
    colors : list of str, str, matplotlib.colors.Colormap
        Input colors or colormap. Can be:
        - A list of color strings
        - A color name (str)
        - A colormap name (str)
        - A Colormap instance
    background : str, or PIL.Image.Image, optional
        Background color or image. Can be:
        - A color name or hex string
        - A PIL Image object
    size : tuple of int, default=(1280, 720)
        Size of the output image in pixels (width, height)
    n : int, default=4
        Number of color line blocks. 
    m : int, default=5
        Number of lines in each block. Used if list of colors is not provided explicitly.
    center : tuple of float, default=(0, 0)
        Coordinates of the circle center from the right bottom corner in pixels
    seed : int, default=0
        Random seed for the Perlin noise generation
    fname : str, optional
        If provided, saves the image to the specified file path

    Returns
    -------
    PIL.Image.Image
        The generated wallpaper as a PIL Image object. If `fname` is provided,
        the image is also saved to the specified file path.

    Examples
    --------
    >>> colors = ['#FF0000', '#00FF00', '#0000FF']
    >>> wallpaper = perlin_lines(colors, size=(800, 600))
    >>> plt.imshow(wallpaper)
    >>> plt.show()
    """
    # Parse background image
    if isinstance(background, Image.Image):
        # resize background image
        if background.size != size:
            background = background.resize(size)
        # Flip vertically
        background = background.transpose(Image.FLIP_TOP_BOTTOM)

    # Parse colors and fill background
    if _is_cmap(colors):
        if background is None:
            background = Image.new("RGB", size, get_bgcolor(colors))
        colors = generate_stepwise_palette(colors, m)
    else:
        colors = _get_gradient_colors(colors)
        m = len(colors)
    if background is None:
        background = Image.new("RGB", size, 'black')

    # Calculate radius of perlin patches
    n_major = n
    n_minor = len(colors)
    x_max = size[0] + center[0]
    y_max = size[1] - center[1]
    r_max = np.sqrt(x_max**2 + y_max**2)
    r_min = 0.6 * r_max
    dr_major = (r_max - r_min) / n_major
    dr_minor = dr_major / (n_minor + 1)

    # Generate perlin noise
    dens = 20
    n = np.ceil(n_major * 6 / dens).astype(int) + 1
    p = perlin((n,36), dens=dens, seed=seed)[dens//2:]

    # Draw color line blocks
    wallpaper = background
    inches, dpi = pixels_to_size_and_dpi(size, exact=True)
    fig = plt.figure(figsize=inches, dpi=dpi, facecolor='#00000000')
    plt.xlim(0,size[0])
    plt.ylim(0,size[1])

    # Show background image
    wallpaper = background
    plt.imshow(wallpaper)
    remove_margins()

    # Draw color line blocks
    scale = 15 * size[1] / 100
    for i in range(n_major):
        for j in range(n_minor):
            k = n_minor * i + j
            r = r_min + dr_major * i + dr_minor * j
            x, y = _get_circle_dots(r, n=720)
            x, y = _distort_radius(x, y, scale * p[k])
            x += size[0] + center[0]
            y += center[1]
            lw = n_minor + 2 - 1 * (j % n_minor)
            plt.plot(x, y, lw=lw, color = colors[j])
    remove_margins()

    # Convert figure to image
    wallpaper = fig2img(fig)
    plt.close(fig)

    # Save to file if provided
    if fname is not None:
        wallpaper.save(fname)

    return wallpaper


def gradient_wallpaper(
    colors: Union[List[str], str, Colormap, None] = None,
    size: Tuple[int, int] = (1280, 720),
    angle: float = 0,
    img: Optional[Image.Image] = None,
    fname: Optional[str] = None,
) -> Image.Image:
    """
    Creates a wallpaper with a gradient background.

    This function generates a wallpaper with a gradient fill, using either
    provided colors or colors sampled from sectors of a reference image.

    Notes
    -----
    When using a reference image:
    1. The central rectangle (half width and height) is excluded
    2. 16 sectors are defined around the center
    3. Each sector's average color is calculated from the non-excluded area
    4. These colors are used as sources for the gradient

    Parameters
    ----------
    colors : list of str, str, matplotlib.colors.Colormap, or None, default=None
        Input colors or colormap. Can be:
        - A list of color strings
        - A color name (str)
        - A colormap name (str)
        - A Colormap instance
    size : tuple of int, default=(1280, 720)
        Size of the output image in pixels (width, height)
    angle : float, default=0
        Angle of the gradient in degrees. 0 means first color source is at the right edge.
        The angle increases in math style (counter-clockwise). 
    img : PIL.Image.Image or None, default=None
        Reference image. If provided, 16 colors will be sampled from image sectors.
    fname : str, optional
        If provided, saves the image to the specified file path

    Returns
    -------
    PIL.Image.Image
        The generated wallpaper as a PIL Image object. If `fname` is provided,
        the image is also saved to the specified file path.

    Examples
    --------
    >>> colors = ['#FF0000', '#00FF00', '#0000FF']
    >>> wallpaper = gradient_wallpaper(colors, size=(800, 600))
    >>> plt.imshow(wallpaper)
    >>> plt.show()
    """
    if colors is None and img is None:
        raise ValueError("Either colors or img must be provided")
    if colors is not None and img is not None:
        raise ValueError("colors must not be provided when using img")

    if img is not None:
        # Convert image to numpy array
        arr = img2arr(img)
        h, w = arr.shape[:2]
        center = np.array([w/2, h/2])
        
        # Create mask for the central rectangle to exclude
        mask = np.ones((h, w), dtype=bool)
        y, x = np.ogrid[:h, :w]
        mask[int(h/8):int(7*h/8), int(w/8):int(7*w/8)] = False
        
        # Calculate angles for 8 sources
        n_sources = 8

        source_angles = np.linspace(0, 2*np.pi, n_sources, endpoint=False) + np.pi / 2
        
        # Calculate sector angles (midpoints between sources)
        sector_angles = (source_angles + np.roll(source_angles, -1)) / 2
        
        # Initialize list for source colors
        colors = []
        
        # For each source
        for i in range(n_sources):
            # Calculate angles for this sector
            angle1 = sector_angles[i-1]  # Previous sector boundary
            angle2 = sector_angles[i]    # Next sector boundary
            
            # Create sector mask
            y_rel = y - center[1]
            x_rel = x - center[0]
            angles = np.arctan2(y_rel, x_rel) % (2*np.pi)
            
            # Handle sector that crosses 0/2π boundary
            if angle1 > angle2:
                sector_mask = (angles >= angle1) | (angles < angle2)
            else:
                sector_mask = (angles >= angle1) & (angles < angle2)
            
            # Combine with central rectangle mask
            sector_mask = sector_mask & mask
            
            # Calculate average color for this sector
            if np.any(sector_mask):
                if len(arr.shape) == 2:  # Grayscale
                    rgb = [np.mean(arr[sector_mask])] * 3
                else:  # RGB
                    rgb = [np.mean(arr[..., i][sector_mask]) for i in range(3)]
                rgb = tuple(np.clip(c / 255, 0, 1) for c in rgb)
            else:
                rgb = (0, 0, 0)  # Default if no pixels in sector
            
            colors.append(rgb)
        
        # Convert RGB tuples to hex colors
        colors = [mc.to_hex(c) for c in colors]
    
    # Create gradient wallpaper
    wallpaper = fill_gradient(colors, size=size, angle=angle, show=False, fname=fname)
    return wallpaper


def triangle_wallpaper(
    colors: Union[str, List[str], None] = None,
    size: Tuple[int, int] = (1280, 720),
    img: Optional[Image.Image] = None,
    density: Optional[int] = 10,
    padding: float = 0.1,
    distortion: float = 0.15,
    seed: int = 0,
    fname: Optional[str] = None,
) -> Image.Image:
    """
    Creates a wallpaper with a grid of distorted triangles.

    This function generates a wallpaper consisting of a grid of triangles that are
    randomly distorted and colored. The grid dimensions are calculated to maintain
    the aspect ratio of the requested image size.

    Parameters
    ----------
    colors : str or list of str or None, default=None
        List of colors for the triangles. If None, colors are sampled from the reference image.
    size : tuple of int, default=(1280, 720)
        Size of the output image in pixels (width, height)
    img : PIL.Image.Image or None, default=None
        Reference image. If provided, colors will be sampled from the image.
    density : int, optional
        Number of grid cells in the shorter dimension.
    padding : float, default=0.1
        Extra padding around the image to ensure coverage after distortion (0-1)
    distortion : float, default=0.15
        Amount of random distortion to apply to grid points (0-1)
    seed : int, default=0
        Random seed for the distortion and Perlin noise
    fname : str, optional
        If provided, saves the image to the specified file path

    Returns
    -------
    PIL.Image.Image
        The generated wallpaper as a PIL Image object. If `fname` is provided,
        the image is also saved to the specified file path.
    """
    if colors is None and img is None:
        raise ValueError("Either colors or img must be provided")
    if colors is not None and img is not None:
        raise ValueError("colors must not be provided when using img")

    # Set seed for reproducibility
    rng = np.random.default_rng(seed)

    # Convert single color to list of lighter and darker shades
    if colors is not None:
        colors = _get_gradient_colors(colors)

    # Calculate grid size
    aspect_ratio = size[0] / size[1]
    grid_size = (int(density * aspect_ratio), density)

    # Calculate perlin grid shape and density
    perlin_density = 3
    perlin_shape = (
        int(grid_size[0] // perlin_density + 1), 
        int(grid_size[1] // perlin_density + 1)
    )

    # Calculate grid with padding
    width_pad = int(size[0] * padding)
    height_pad = int(size[1] * padding)
    total_width = size[0] + 2 * width_pad
    total_height = size[1] + 2 * height_pad

    # Create grid points
    x = np.linspace(-width_pad, size[0] + width_pad, grid_size[0])
    y = np.linspace(-height_pad, size[1] + height_pad, grid_size[1])
    xs, ys = np.meshgrid(x, y)

    # Apply Perlin noise distortion to generate zs
    p = perlin(perlin_shape, dens=perlin_density, seed=seed)
    zs = p.T[:grid_size[1], :grid_size[0]] * (xs[0,1] - xs[0,0])

    # Apply random distortion to xs and ys
    max_distortion_x = total_width * distortion / grid_size[0]
    max_distortion_y = total_height * distortion / grid_size[1]
    xs += rng.uniform(-max_distortion_x, max_distortion_x, xs.shape)
    ys += rng.uniform(-max_distortion_y, max_distortion_y, ys.shape)
    
    # Calculate light direction vector (normalized)
    light_angle_rad = np.radians(0)
    light_elevation_rad = np.radians(30)
    light_dir = np.array([
        np.cos(light_elevation_rad) * np.cos(light_angle_rad),
        np.cos(light_elevation_rad) * np.sin(light_angle_rad),
        np.sin(light_elevation_rad)
    ])
    light_dir = light_dir / np.linalg.norm(light_dir)
    light_dir = np.array([1, 0, 0])

    # Create list to store triangle vertices and normals
    triangles = []
    normals = []

    # Generate triangles from grid points
    for i in range(grid_size[1] - 1):
        for j in range(grid_size[0] - 1):
            # First triangle
            v1 = np.array([xs[i, j], ys[i, j], zs[i, j]])
            v2 = np.array([xs[i, j+1], ys[i, j+1], zs[i, j+1]])
            v3 = np.array([xs[i+1, j], ys[i+1, j], zs[i+1, j]])
            
            # Calculate normal vector for first triangle
            edge1 = v2 - v1
            edge2 = v3 - v1
            normal = np.cross(edge1, edge2)
            normal = normal / np.linalg.norm(normal)
            
            triangle1 = [
                (v1[0], v1[1]),
                (v2[0], v2[1]),
                (v3[0], v3[1])
            ]
            triangles.append(triangle1)
            normals.append(normal)

            # Second triangle
            v1 = np.array([xs[i+1, j], ys[i+1, j], zs[i+1, j]])
            v2 = np.array([xs[i, j+1], ys[i, j+1], zs[i, j+1]])
            v3 = np.array([xs[i+1, j+1], ys[i+1, j+1], zs[i+1, j+1]])
            
            # Calculate normal vector for second triangle
            edge1 = v2 - v1
            edge2 = v3 - v1
            normal = np.cross(edge1, edge2)
            normal = normal / np.linalg.norm(normal)
            
            triangle2 = [
                (v1[0], v1[1]),
                (v2[0], v2[1]),
                (v3[0], v3[1])
            ]
            triangles.append(triangle2)
            normals.append(normal)

    # Create matplotlib figure
    inches, dpi = pixels_to_size_and_dpi(size, exact=True)
    fig = plt.figure(figsize=inches, dpi=dpi, facecolor='#00000000')
    plt.xlim(0, size[0])
    plt.ylim(0, size[1])
    remove_margins()

    # Draw triangle patches with lighting effect
    for triangle, normal in zip(triangles, normals):
        coords = np.array(triangle)
        patch = Patch(coords)
        
        # Assign random angle and color
        angle = rng.uniform(0, 360)
        if colors is None:
            img_ = resize_image(img, size)
            base_color = patch.get_centroid_color(img_)
        else:
            base_color = random.choice(colors)
            
        # Apply lighting effect
        intensity = np.dot(normal, light_dir)
        intensity = np.round(np.clip(intensity, -0.2, 0.2), 2)
        if intensity > 0:
            lit_color = lighten(base_color, intensity)
        else:
            lit_color = darken(base_color, -intensity)
        
        # Create gradient colors with lighting
        gradient_colors = [
            lighten(lit_color, 0.1),
            lit_color,
            darken(lit_color, 0.1)
        ]
        
        # Fill triangle with gradient
        patch.fill_gradient(gradient_colors, angle=angle)
        patch.draw(fig, size)

    # Convert figure to image
    wallpaper = fig2img(fig)
    plt.close(fig)

    # Create blurred background to fill gaps
    # Convert to numpy array for processing
    arr = np.array(wallpaper)
    
    # Create alpha mask from the original alpha channel
    alpha_mask = arr[..., 3] / 255.0
    
    # Create blurred version
    blur_sigma = 10
    kernel_size = int(2 * blur_sigma + 1) | 1  # Ensure odd kernel size
    blurred = cv2.GaussianBlur(arr, (kernel_size, kernel_size), blur_sigma)
    
    # Handle color channels separately to preserve transparency
    result = np.zeros_like(arr)
    
    # Blend RGB channels
    for i in range(3):
        # Original color where alpha is high, blurred color where alpha is low
        result[..., i] = (arr[..., i] * alpha_mask + 
                         blurred[..., i] * (1 - alpha_mask)).astype(np.uint8)
    
    # Keep original alpha channel but fill gaps
    result[..., 3] = np.maximum(arr[..., 3], 
                               blurred[..., 3]).astype(np.uint8)

    # Convert back to PIL Image
    wallpaper = Image.fromarray(result)

    # Save to file if provided
    if fname is not None:
        wallpaper.save(fname)
    
    return wallpaper


import types
__all__ = [name for name, thing in globals().items()
          if not (name.startswith("_") or isinstance(thing, types.ModuleType))]
del types
