#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains functions to convert color to a palette of darker shades and lighter tints.
"""

import re
import math
import numpy as np
import matplotlib.pyplot as plt
import colorsys
from cycler import cycler
import matplotlib.colors as mc
from matplotlib.axes import Axes
from typing import Any, Optional
from .colortypes import to_hex, to_rgb, to_hls, to_oklch, to_rgb255
from .utils import get_colors, get_color_name, interpolate_colors



def generate_palette(color: Any, n=10, mode='superellipse', power=3, debug=False) -> list[str]:
    """
    Generates a palette of darker shades and lighter tints for a given color.

    Parameters
    ----------
    color : Any
        The input color. Can be a named color, hex string, or a tuple/list in
        RGB, RGBA, HSV, HLS, or OKLCH format.
    n : int, default=10
        The number of colors to generate in the palette.
    mode : str, default='superellipse'
        The mode of the palette generation. Can be 'superellipse', 'circle', or 'linear'.
    power : float, default=2
        The power of superellipse to traverse the RGB space from black to white.
    debug : bool, default=False
        If True, show the debug information.

    Returns
    -------
    list
        A list of colors in the palette.
    """
    # Initialize the palette
    palette = []

    # Start and end points of the palette path
    black = np.array([0.0, 0.0, 0.0])
    white = np.array([1.0, 1.0, 1.0])

    # Convert color to rgb
    rgb = np.array(to_rgb(color))

    # Special case: if the color is black, white or grey, return the greyscale palette
    if np.isclose(rgb[0], rgb[1], atol=1e-05) and np.isclose(rgb[1], rgb[2], atol=1e-05):
        return [mc.to_hex(rgb * (i + 1) / n) for i in range(n)]

    # Step 1: Create 2d (u,v) plane passing through black, white and the given color
    # Vector u: from black to white (this defines our u-axis)
    u = white - black
    u = u / np.linalg.norm(u)
    
    # Vector v: perpendicular to u, pointing to the same half-space as base
    v = rgb - black
    v = v - u * np.dot(u, v)
    v = v / np.linalg.norm(v) # We are sure it is not zero, because rgb is not on the greyscale line

    # Step 2: Find black, white, and rgb coordinates in the (u,v) plane
    black_uv = np.array([0.0, 0.0])
    white_uv = np.array([np.dot(white - black, u), np.dot(white - black, v)])
    rgb_uv = np.array([np.dot(rgb - black, u), np.dot(rgb - black, v)])

    # Step 3: Create a path traversing the black, rgb, and white points in the (u,v) plane
    npoints = max(1000, n * 10)
    if mode == 'linear':
        path = _generate_linear_path(black_uv, white_uv, rgb_uv, npoints)
    elif mode == 'circle' or mode == 'circular':
        path = _generate_circle_path(black_uv, white_uv, rgb_uv, npoints)
    elif mode == 'superellipse':
        path = _generate_superellipse_path(black_uv, white_uv, rgb_uv, npoints, power)
    else:
        raise ValueError(f"Unknown mode: {mode}. Supported modes are 'linear', 'circle', 'superellipse'.")

    # Step 4: Sample n equidistant points from the path
    path_points = np.array([p[:2] for p in path])
    path_lengths = np.array([p[2] for p in path])
    total_path_length = path_lengths[-1]

    # Create n target lengths, spaced according to the sampling method
    target_lengths = np.linspace(0, total_path_length, n)

    # Interpolate to find the (u, v) coordinates at the target lengths
    sampled_u = np.round(np.interp(target_lengths, path_lengths, path_points[:, 0]), 5)
    sampled_v = np.round(np.interp(target_lengths, path_lengths, path_points[:, 1]), 5)
    sampled_points_uv = np.vstack([sampled_u, sampled_v]).T

    if debug:
        _debug_image(mode, path_points, sampled_points_uv, black_uv, white_uv, rgb_uv, color, n)

    # Step 5: Convert sampled (u,v) points back to RGB, clip, and format as hex
    for point_uv in sampled_points_uv:
        rgb_color = black + point_uv[0] * u + point_uv[1] * v
        rgb_clipped = np.clip(rgb_color, 0, 1)
        palette.append(mc.to_hex(rgb_clipped))

    return palette


def _generate_linear_path(p1, p2, p3, npoints):
    """
    Generates a linear path from p2 to p1 through p3.

    The path consists of two segments: from p2 (white) to p3 (color) and
    from p3 (color) to p1 (black).

    Parameters
    ----------
    p1 : np.ndarray
        The coordinates of the first point (black) in the 2D plane.
    p2 : np.ndarray
        The coordinates of the second point (white) in the 2D plane.
    p3 : np.ndarray
        The coordinates of the third point (the color) in the 2D plane.
    npoints : int
        The number of points to generate along the path.

    Returns
    -------
    list of tuple
        A list of (u, v, length) tuples representing the points on the path
        and their cumulative distance from the start.
    """
    # Calculate segment lengths
    len1 = np.linalg.norm(p3 - p2)
    len2 = np.linalg.norm(p1 - p3)
    total_len = len1 + len2

    # Allocate points proportionally to segment lengths
    n1 = max(2, int(round(npoints * len1 / total_len)))
    n2 = max(2, int(round(npoints * len2 / total_len)))

    # Path is two segments: p2->p3 and p3->p1
    path_segment1 = np.linspace(p2, p3, n1)
    path_segment2 = np.linspace(p3, p1, n2)[1:]  # Exclude first point to avoid duplicating p3
    path_points = np.vstack([path_segment1, path_segment2])

    # Calculate cumulative arc length
    lengths = np.cumsum(np.linalg.norm(np.diff(path_points, axis=0), axis=1))
    lengths = np.insert(lengths, 0, 0)

    return list(zip(path_points[:, 0], path_points[:, 1], lengths))


def _generate_circle_path(p1, p2, p3, npoints):
    """
    Generates a circular path from p2 (white) to p1 (black) through p3 (color).

    The path is an arc of a circle that passes through the three given points.

    Parameters
    ----------
    p1 : np.ndarray
        The coordinates of the first point (black) in the 2D plane.
    p2 : np.ndarray
        The coordinates of the second point (white) in the 2D plane.
    p3 : np.ndarray
        The coordinates of the third point (the color) in the 2D plane.
    npoints : int
        The number of points to generate along the path.

    Returns
    -------
    list of tuple
        A list of (u, v, length) tuples representing the points on the path
        and their cumulative distance from the start.
    """
    # p1: black_uv, p2: white_uv, p3: rgb_uv
    # The center of the circle must be equidistant from all three points.
    # The u-coordinate of the center is halfway between black and white.
    center_u = p2[0] / 2.0
    
    # The v-coordinate is found by equating the distance from the center to black and the color.
    # (center_u - p1[0])^2 + (center_v - p1[1])^2 = (center_u - p3[0])^2 + (center_v - p3[1])^2
    # Since p1 is origin (0,0), this simplifies things.
    # center_u^2 + center_v^2 = (center_u - p3[0])^2 + (center_v - p3[1])^2
    # After expanding and simplifying:
    # 2 * center_v * p3[1] = p3[0]**2 - 2 * center_u * p3[0] + p3[1]**2
    # Note: p3[1] (v-coord of color) is guaranteed not to be zero.
    center_v = (p3[0]**2 - 2 * center_u * p3[0] + p3[1]**2) / (2 * p3[1])
    center = np.array([center_u, center_v])
    
    # Radius is the distance from the center to any point (e.g., p1 at origin).
    radius = np.linalg.norm(center)

    # Calculate the angles for the start (white) and end (black) points.
    angle_start = np.arctan2(p2[1] - center_v, p2[0] - center_u)
    angle_end = np.arctan2(p1[1] - center_v, p1[0] - center_u)

    # Ensure angles are in a consistent range for interpolation [0, 2*pi]
    if angle_end < angle_start:
        angle_end += 2 * np.pi

    # Generate angles for the path
    angles = np.linspace(angle_start, angle_end, npoints)
    
    # Generate points on the circle
    u_coords = center_u + radius * np.cos(angles)
    v_coords = center_v + radius * np.sin(angles)
    path_points = np.vstack([u_coords, v_coords]).T
    
    # Calculate cumulative arc length (length = radius * angle_in_radians)
    arc_lengths = radius * np.abs(angles - angle_start)
    
    return list(zip(u_coords, v_coords, arc_lengths))


def _generate_superellipse_path(p1, p2, p3, npoints, power):
    """
    Generates a superellipse path from p2 (white) to p1 (black) through p3 (color).

    Parameters
    ----------
    p1 : np.ndarray
        The coordinates of the first point (black) in the 2D plane.
    p2 : np.ndarray
        The coordinates of the second point (white) in the 2D plane.
    p3 : np.ndarray
        The coordinates of the third point (the color) in the 2D plane.
    npoints : int
        The number of points to generate along the path.
    power : float
        The exponent for the superellipse equation.

    Returns
    -------
    list of tuple
        A list of (u, v, length) tuples representing the points on the path
        and their cumulative distance from the start.
    """
    # p1: black_uv, p2: white_uv, p3: rgb_uv
    # Center of the superellipse is halfway between black and white.
    center = (p1 + p2) / 2.0
    a = np.linalg.norm(p2 - center)

    # Shift coordinates so the center is at the origin.
    p3_shifted = p3 - center

    # Calculate b so the curve passes through the color point.
    # |x/a|^p + |y/b|^p = 1  =>  b = |y| / (1 - |x/a|^p)^(1/p)
    # Clip the argument of the root to avoid math errors with floating point inaccuracies.
    x_term = np.abs(p3_shifted[0] / a) ** power
    term_to_root = np.clip(1.0 - x_term, 1e-9, 1.0)
    b = np.abs(p3_shifted[1]) / (term_to_root ** (1.0 / power))

    # Generate points using the parametric equation for a superellipse.
    # The path from white to black corresponds to t from 0 to pi.
    t = np.linspace(0, np.pi, npoints)

    # Parametric equations (with sign correction for cos)
    r = power
    u_coords_centered = a * np.sign(np.cos(t)) * (np.abs(np.cos(t)) ** (2.0 / r))
    v_coords_centered = b * (np.sin(t) ** (2.0 / r)) # sin(t) is non-negative for t in [0, pi]

    # Shift points back to the original coordinate system.
    u_coords = u_coords_centered + center[0]
    v_coords = v_coords_centered + center[1]
    path_points = np.vstack([u_coords, v_coords]).T

    # Calculate cumulative arc length by summing segment lengths.
    lengths = np.cumsum(np.linalg.norm(np.diff(path_points, axis=0), axis=1))
    lengths = np.insert(lengths, 0, 0)

    return list(zip(u_coords, v_coords, lengths))

def _debug_image(mode, path_points, sampled_points, p1, p2, p3, color, n):
    """
    Generates a debug image of the palette generation path.

    Saves a JPEG file showing the full path, sampled points, and key color points
    in the 2D projection plane.

    Parameters
    ----------
    mode : str
        The palette generation mode (e.g., 'linear', 'circle').
    path_points : np.ndarray
        The array of points defining the full generation path.
    sampled_points : np.ndarray
        The array of points sampled from the path.
    p1 : np.ndarray
        Coordinates of the 'black' point.
    p2 : np.ndarray
        Coordinates of the 'white' point.
    p3 : np.ndarray
        Coordinates of the 'color' point.
    color : Any
        The original input color, used for plotting.
    n : int
        The number of sampled points.
    """
    plt.figure(figsize=(8, 8))
    # Plot the full path
    plt.plot(path_points[:, 0], path_points[:, 1], 'k-', lw=1, label='Full Path')
    # Plot the sampled points
    plt.scatter(sampled_points[:, 0], sampled_points[:, 1], c='red', s=50, zorder=5, label=f'{n} Sampled Points')
    # Plot key points
    plt.scatter(p1[0], p1[1], c='black', s=100, zorder=5, label='Black')
    plt.scatter(p2[0], p2[1], c='lightgray', s=100, zorder=5, edgecolor='black', label='White')
    # Use a list for the color to avoid UserWarning
    plt.scatter(p3[0], p3[1], c=[to_rgb(color)], s=100, zorder=5, edgecolor='black', label='Color')

    plt.xlabel('u-axis')
    plt.ylabel('v-axis')
    plt.title(f'Palette Generation Path (mode={mode})')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.axis('equal')
    plt.savefig(f"debug_{mode}.jpg", dpi=150)
    plt.close()

def generate_primary_palette(color: Any, mode='superellipse', power=3, fmt="hex", fname=None) -> list:
    """
    Generates a broad palette suitable for primary CSS styling.

    This function creates a 9-color palette balanced around the mid-tones.

    Parameters
    ----------
    color : Any
        The base color for the palette.
    mode : str, default='superellipse'
        The palette generation mode.
    power : float, default=3
        The superellipse power.
    fmt : str, default='hex'
        The output format for the palette if printed/saved ('hex', 'rgb', 'hls', 'oklch').
    fname : str, optional
        The filename to save the CSS palette to. If None, prints to stdout.

    Returns
    -------
    list
        A list of 9 hex color strings.
    """
    palette = generate_palette(color, n=51, mode=mode, power=power, debug=False)
    #sliced_palette = palette[::4]
    sliced_palette = palette[::4][1:10]
    _format_and_output_palette(sliced_palette, color, fmt, fname, kind="primary")
    return sliced_palette

def generate_background_palette(color: Any, mode='superellipse', power=3, fmt="hex", fname=None) -> list:
    """
    Generates a palette of darker shades suitable for backgrounds.

    This function creates a 9-color palette weighted towards darker tones.

    Parameters
    ----------
    color : Any
        The base color for the palette.
    mode : str, default='superellipse'
        The palette generation mode.
    power : float, default=3
        The superellipse power.
    fmt : str, default='hex'
        The output format for the palette if printed/saved ('hex', 'rgb', 'hls', 'oklch').
    fname : str, optional
        The filename to save the CSS palette to. If None, prints to stdout.

    Returns
    -------
    list
        A list of 9 hex color strings.
    """
    palette = generate_palette(color, n=51, mode=mode, power=power, debug=False)
    sliced_palette = palette[::-1][::2][1:10][::-1]
    _format_and_output_palette(sliced_palette, color, fmt, fname, kind="background")
    return sliced_palette

def generate_foreground_palette(color: Any, mode='superellipse', power=3, fmt="hex", fname=None) -> list:
    """
    Generates a palette of lighter tints suitable for foregrounds.

    This function creates a 9-color palette weighted towards lighter tones.

    Parameters
    ----------
    color : Any
        The base color for the palette.
    mode : str, default='superellipse'
        The palette generation mode.
    power : float, default=3
        The superellipse power.
    fmt : str, default='hex'
        The output format for the palette if printed/saved ('hex', 'rgb', 'hls', 'oklch').
    fname : str, optional
        The filename to save the CSS palette to. If None, prints to stdout.

    Returns
    -------
    list
        A list of 9 hex color strings.
    """
    palette = generate_palette(color, n=51, mode=mode, power=power, debug=False)
    sliced_palette = palette[::2][1:10]
    _format_and_output_palette(sliced_palette, color, fmt, fname, kind="foreground")
    return sliced_palette

def _format_and_output_palette(palette: list, color: Any, fmt: str, fname: Optional[str], kind: str = "primary"):
    """
    Formats a palette into CSS variables and prints or saves it.

    Parameters
    ----------
    palette : list
        The list of hex color strings to format.
    color : Any
        The original base color (used for naming if palette is empty).
    fmt : str
        The CSS color format ('hex', 'rgb', 'hls', 'oklch').
    fname : str or None
        If a string, the path to save the output file. If None, prints to stdout.
    kind : str, default='primary'
        The kind of palette, used for CSS variable naming (e.g., '--primary-color-1').
    """
    if not palette:
        print("Warning: Cannot format an empty palette.")
        return

    if fmt not in ["hex", "rgb", "hls", "oklch"]:
        print(f"Warning: format '{fmt}' not recognized. Defaulting to 'hex'.")
        fmt = "hex"

    # Name palette by its middle color
    i = len(palette) // 2
    color_name = get_color_name(palette[i])
    
    css_lines = [f"/* {color_name.title()} color palette */", ":root {"]
    for i, p_color in enumerate(palette, 1):
        if fmt == 'hex':
            value = to_hex(p_color)
        elif fmt == 'rgb':
            value = to_rgb255(p_color, formatted=True)
        elif fmt == 'hls':
            value = to_hls(p_color, formatted=True)
        elif fmt == 'oklch':
            value = to_oklch(p_color, formatted=True)
        css_lines.append(f"  --{kind}-color-{i}: {value};")
    css_lines.append("}")

    output_str = "\n".join(css_lines)

    if fname:
        try:
            with open(fname, 'w') as f:
                f.write(output_str)
            print(f"Palette saved to {fname}")
        except Exception as e:
            print(f"An error occurred while saving the palette to {fname}: {e}")
    else:
        print(output_str)


def generate_stepwise_palette(cmap, n=6, exclude_extreme=True, use_hue=True):
    """
    Generates a stepwise color palette from a given colormap.

    This function analyzes the hue and lightness trends of a colormap to create a
    perceptually balanced, stepwise palette. It identifies whether the colormap is
    sequential or diverging and samples colors accordingly.

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap
        The input colormap to generate the palette from.
    n : int, default=6
        The desired number of colors in the final palette.
    exclude_extreme : bool, default=True
        If True, removes the very light and very dark colors from the ends of the palette.
    use_hue : bool, default=True
        If True, considers hue trends in addition to lightness to determine the
        colormap structure.

    Returns
    -------
    list
        A list of hex color strings representing the generated palette.
    """
    n_ext = 2 * n - 2
    colors = get_colors(cmap, n=n_ext)
    channels = ["hue", "lightness", "saturation"]
    hls = np.stack([to_hls(c) for c in colors]).T
    
    # Correct for hue discontinuity
    hls[0] = np.unwrap(hls[0], period=1)
    
    # Find lightness midpoint
    m = _find_midpoint(hls[1])
    
    # Lightness trends
    score1, trend1 = _find_monotonic_trend(hls[1][:m])
    score2, trend2 = _find_monotonic_trend(hls[1][m + 1:])
    score = min(score1, score2)
    category = "lightness"
    
    # Hue trends
    if use_hue:
        hue_score1, hue_trend1 = _find_monotonic_trend(hls[0][:m])
        hue_score2, hue_trend2 = _find_monotonic_trend(hls[0][m + 1:])
        hue_score = min(hue_score1, hue_score2)
        if hue_score > score:
            score = hue_score
            trend1 = hue_trend1
            trend2 = hue_trend2
            category = "hue"
    
    # Correction of midpoint
    if m % 2 == 0:
        if m < len(colors) / 2:
            m += 1
        else:
            m -= 1

    # Flip colors
    flip = False
    if category == "hue" and trend1 * trend2 > 0:
        flip = True
    if category == "lightness" and trend1 * trend2 < 0:
        flip = True
    palette = colors
    if flip:
        idx = np.arange(len(colors))
        if category == "lightness" and trend1 < 0:
            idx = np.concatenate([idx[:m][::-1], idx[m:]])
        else:
            idx = np.concatenate([idx[:m], idx[m:][::-1]])
        palette = np.asarray(colors)[idx].tolist()
    
    # Remove extremely dark and light colors if requested
    palette1, palette2 = palette[:m], palette[m:]
    if exclude_extreme:
        palette1 = _remove_extremes(palette1)
        palette2 = _remove_extremes(palette2)
    palette1, palette2 = palette1[::2], palette2[::2]
    palette = palette1 + palette2
    
    return palette


def _find_monotonic_trend(x):
    """
    Analyzes the monotonic trend of a 1D array.

    This function fits linear and quadratic models to the input data to determine
    the strength (R-squared) and direction of its monotonic trend.

    Parameters
    ----------
    x : np.ndarray
        A 1D numpy array of numerical data.

    Returns
    -------
    tuple
        A tuple containing:
        - score (float): The coefficient of determination (R-squared) of the best fit.
        - trend (float): The direction of the trend (positive or negative).
    """
    
    # Helper function to calculate coefficient of determination R2
    def calc_r2(x, x_fit):
        ss_res = np.sum((x - x_fit) ** 2)
        ss_tot = np.sum((x - np.mean(x)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        return r2
    
    # Initialize with zeros
    score, trend = 0.0, 0.0
    
    # Skip if too short array
    if len(x) <= 1:
        return score, trend
    
    # Linear fit
    t = np.linspace(0, 1, len(x))
    p = np.polyfit(t, x, 1)
    if abs(p[0]) > 1e-5:
        x_fit = np.polyval(p, t)
        score = calc_r2(x, x_fit)
        trend = x_fit[-1] - x_fit[0]

    # Try quadratic fit
    try:
        if len(x) > 2:
            p = np.polyfit(t, x, 2)
            if abs(p[0]) > 1e-5:
                t0 = -p[1] / (2 * p[0])
                if t0 < 0.1 or t0 > 0.9:
                    x_fit = np.polyval(p, t)
                    r2 = calc_r2(x, x_fit)
                    if r2 > score:
                        score = r2
    except:
        pass
    
    return score, trend


def _find_midpoint(x):
    """
    Finds the midpoint of a 1D array, biased towards the min/max if they are central.

    This function is used to identify the center of a diverging colormap.

    Parameters
    ----------
    x : np.ndarray
        A 1D numpy array, typically representing lightness values of a colormap.

    Returns
    -------
    int
        The index of the calculated midpoint.
    """
    n = len(x)
    midpoint = n // 2 + n % 2
    if n > 5:
        t = np.linspace(0, 1, len(x))
        i_min, i_max = np.argmin(x), np.argmax(x)
        t_min, t_max = t[i_min], t[i_max]
        if 0.3 < t_min < 0.7 and (t_max < 0.3 or t_max > 0.7):
            midpoint = i_min
        if 0.3 < t_max < 0.7 and (t_min < 0.3 or t_min > 0.7):
            midpoint = i_max
    return midpoint


def _remove_extremes(colors):
    """
    Removes extreme light and dark colors from a list of colors.

    This function filters a list of colors to exclude those with very low or
    very high lightness values. If filtering reduces the list too much, it
    re-interpolates the remaining colors to the original list size.

    Parameters
    ----------
    colors : list
        A list of hex color strings.

    Returns
    -------
    list
        A list of hex color strings with extremes removed or interpolated.
    """
    n = len(colors)
    hls = np.stack([to_hls(c) for c in colors]).T
    mask = (hls[1] > 0.2) & (hls[1] < 0.8)
    if np.sum(mask) < 2:
        mask = (hls[1] > 0.1) & (hls[1] < 0.8)
    if np.sum(mask) < 2:
        mask = (hls[1] > 0.1) & (hls[1] < 0.9)
    if np.sum(mask) < 2:
        mask = (hls[1] > 0.05) & (hls[1] < 0.9)
    if np.sum(mask) < 2:
        mask = (hls[1] > 0.05) & (hls[1] < 0.95)
    palette = [c for c in colors]
    if np.sum(mask) >= 2 and np.sum(mask) < n:
        palette = np.asarray(colors)[mask].tolist()
        palette = interpolate_colors(palette, n)
    return palette


import types
__all__ = [name for name, thing in globals().items()
          if not (name.startswith("_") or isinstance(thing, types.ModuleType))]
del types

