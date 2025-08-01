#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains functions to manipulate colormaps.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mc
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Colormap
from matplotlib.axes import Axes
from .colortypes import to_hex, to_rgb
from .colortools import show_colors, darken
from .utils import get_colors, _is_qualitative, _is_divergent, _is_cyclic
from typing import Union, Tuple, List, Callable, Optional

import warnings
warnings.filterwarnings("ignore")


def _get_cmap_list() -> List[str]:
    """
    Gets a list of all registered colormaps in matplotlib.

    Returns
    -------
    cmaps : list of str
        List of colormap names
    """
    cmaps: List[str] = []
    cmaps_r = [cmap for cmap in plt.colormaps() if cmap.endswith('_r')]
    for cmap in plt.colormaps():
        if not cmap in cmaps_r:
            cmaps.append(cmap)
            cmap_r = f'{cmap}_r'
            if cmap_r in cmaps_r:
                cmaps.append(cmap_r)
    return cmaps


def _get_cmap_categories(cmap: Union[str, Colormap]) -> List[str]:
    """
    Gets the kind of a colormap.

    This function determines the kind of a colormap based on its properties.

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap
        Colormap name or instance to determine the kind of

    Returns
    -------
    kind : list of str
        List of kinds of the colormap
    """
    cmap = plt.get_cmap(cmap)
    categories: List[str] = []
    if _is_qualitative(cmap):
        categories.append('Qualitative')
    else:
        categories.append('Continuous')
    if _is_divergent(cmap):
        categories.append('Divergent')
    if _is_cyclic(cmap):
        categories.append('Cyclic')
    return categories


def _register_cmap(cmap: Colormap) -> None:
    """
    Registers a matplotlib colormap in the current session.

    This function attempts to register a colormap with matplotlib's colormap registry.
    If the colormap is already registered or if registration fails for any reason,
    the function will silently continue.

    Parameters
    ----------
    cmap : matplotlib.colors.Colormap
        Colormap to register

    Returns
    -------
    None

    Examples
    --------
    >>> custom_cmap = LinearSegmentedColormap.from_list('custom', ['red', 'white', 'blue'])
    >>> _register_cmap(custom_cmap)
    >>> plt.get_cmap('custom')  # Now available
    """
    try:
        plt.colormaps.register(cmap)
    except:
        pass


def _add_extended_colormaps() -> None:
    """
    Extends the list of registered colormaps.

    This function adds a variety of custom colormaps to matplotlib's registry,
    including:
    - Sequential versions (warm and cold)
    - Color combinations (BrBu, BrGn, OrBu, OrGn, PiBu)
    - Gruvbox themes (light, normal, dark)
    - Art deco and cyberpunk inspired colormaps
    - Aquamarine variations (light, normal, dark)

    Each colormap is registered in both its original and reversed form.

    Returns
    -------
    None

    Examples
    --------
    >>> _add_extended_colormaps()
    >>> plt.get_cmap('gruvbox')  # Now available
    >>> plt.get_cmap('cyberpunk')  # Now available
    """
    # Add continuous colormaps
    color_dict = {
        "warm": plt.get_cmap("coolwarm")(np.linspace(0.5, 1, 128)),
        "cold": plt.get_cmap("coolwarm_r")(np.linspace(0.5, 1, 128)),
    }
    for name, colors in color_dict.items():
        try:    
            cmap = LinearSegmentedColormap.from_list(name, colors)
            _register_cmap(cmap)
            cmap = LinearSegmentedColormap.from_list(name + "_r", colors[::-1])
            _register_cmap(cmap)
        except:
            pass
    # Add qualitative colormaps
    color_dict = {
        "BrBu": ["#9B2227", "#BA3F04", "#CA6705", "#EE9B04", "#EAD7A4", "#93D3BD", "#4BB3A9", "#039396", "#027984", "#015F72"],
        "BrGn": ["#9B2227", "#BA3F04", "#CA6705", "#EE9B04", "#EAD7A4", "#CAB67B", "#A99945", "#897C0F", "#736E12", "#5E6014"],
        "OrBu": ["#B97401", "#DC8D01", "#FAC316", "#F8E584", "#F8FFC9", "#638094", "#4C6E83", "#3E596D", "#374053"],
        "OrGn": ["#B97401", "#DC8D01", "#FAC316", "#F8E584", "#F1FFC1", "#7DA4A4", "#628E8E", "#467171", "#284C4C"],
        "PiBu": ["#7D433D", "#A45040", "#C45D47", "#DD6850", "#CAA59F", "#4C8A9A", "#427283", "#385B6C", "#2E4355"],
        "rtd": ["#206390", "#2980BA", "#419AD5", "#6BB0DE", "#94C6E8", "#FFFFFF", "#EEFFCC", "#DDFF99", "#CCFF66", "#BBFF33"],
        "artdeco": ["#9F1B10", "#D88533", "#E8B055", "#D9B97B", "#B6BEAA", "#768C86", "#365861", "#204755", "#0A3649"],
        "cyberpunk": ["#55D6F5", "#5C9BE8", "#6260DC", "#522FAA", "#42007A", "#4F057A", "#5D097C", "#A917BE", "#F225FF"],
        "synthwave": ["#5C9BE8", "#5368C4", "#4B35A0", "#42007A", "#550584", "#680B8E", "#7B1098", "#A75466", "#D19536", "#FBD606"],
        "gruvbox_light": ["#E34039", "#F17626", "#F8B533", "#C4C221", "#87B189", "#57A6A9", "#C284A0"],
        "gruvbox": ["#CC241D", "#D65D0E", "#D79921", "#98971A", "#689D6A", "#458588", "#B16286"],
        "cobalt": ["#FB94FF", "#FA841A", "#FFC619", "#3AD900", "#0088FF"],
        "noctis": ["#9F1C17", "#E66533", "#FFC180", "#49E9A6", "#14A5FF"],
        "monokai": ["#F92672", "#FD971D", "#E69F66", "#E6DB74", "#A6E22E", "#66D9EF", "#AE81FF"],
        "oceanic": ["#7239D2", "#5F52CC", "#4C6CC5", "#3985BF", "#269FB9", "#13B9B2", "#00D2AC"],
    }
    for name, colors in color_dict.items():
        try:
            cmap = ListedColormap(colors, name=name)
            _register_cmap(cmap)
            cmap = ListedColormap(colors[::-1], name=name + "_r")
            _register_cmap(cmap)
        except:
           pass
    return


def show_colorbar(cmap: Union[str, Colormap], ax: Optional[plt.Axes] = None) -> None:
    """
    Displays a colormap as a colorbar.

    This function creates a visualization of a colormap as a horizontal colorbar
    with labeled ticks. The colorbar shows the full range of the colormap from
    0 to 1, with major ticks at 0, 0.5, and 1.

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap
        Colormap name or instance to display
    ax : matplotlib.axes.Axes, optional
        Axes to plot on. If None, a new figure is created.

    Returns
    -------
    None
        Displays the colorbar visualization using matplotlib.

    Examples
    --------
    >>> show_cbar('viridis')  # Display viridis colormap as colorbar
    >>> show_cbar(plt.cm.viridis)  # Same as above, using colormap instance
    """
    cmap = plt.get_cmap(cmap)
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    new_figure = ax is None
    if new_figure:
        plt.figure(figsize=(12,2), facecolor="#00000000")
    else:
        ax.set_facecolor("#00000000")
    plt.title(f'{cmap.name}  colorbar', fontsize=20, color="grey", pad=16)
    plt.imshow(gradient, aspect="auto", cmap=cmap)
    plt.xticks([0, 127, 255], ["0", "0.5", "1"], fontsize=16, color="grey")
    plt.yticks([])
    for e in ["top", "bottom", "right", "left"]:
        plt.gca().spines[e].set_color("#00000000")
    plt.tight_layout()
    if new_figure:
        plt.show()
        plt.close()
    return


def show_cmap(cmap: Union[str, Colormap], verbose: bool = True) -> None:
    """
    Displays a colormap's colorbar, sample colors, and background color.

    This function displays a colormap's colorbar, sample colors, and background color.
    If verbose is True, it also prints information about the colormap's properties.

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap
        Colormap name or instance to display
    verbose : bool, default=True
        If True, print information about the colormap.

    Returns
    -------
    None
        Displays the colormap and its properties using matplotlib.

    Examples
    --------
    >>> show_cmap('viridis')  # Display with default sampling
    >>> gradient = np.logspace(0, -2, 10)  # Custom logarithmic sampling
    >>> show_cmap('viridis', gradient)
    """
    cmap = plt.get_cmap(cmap)
    if verbose:
        print(cmap.name)
        print()
        categories = _get_cmap_categories(cmap)
        for category in ['Qualitative', 'Continuous', 'Divergent', 'Cyclic']:
            if category in categories:
                print(f'{category}: True')
            else:
                print(f'{category}: False')
        show_colorbar(cmap)
    colors = get_colors(cmap, exclude_extreme=False)
    colors = [to_hex(c) for c in colors]
    print(f'{len(colors)} sample colors:')
    show_colors(colors, title=f'{cmap.name}  sample colors') # type: ignore
    plt.show()
    plt.close()
    if verbose:
        bg_color = get_bgcolor(cmap)
        print(f'Background color: {bg_color}')
        show_colors([bg_color], title=f'{cmap.name}  background', size=(2, 1))
        plt.show()
        plt.close()
    return


def list_cmaps(category: str = 'All', display: bool = False) -> None:
    """
    Lists and shows all registered colormaps.

    This function prints a list of all available colormaps in matplotlib,
    along with their properties (e.g., Qualitative, Continuous, Divergent, Cyclic).
    If a category other than 'All' is provided, the colormaps are displayed as a grid.

    Parameters
    ----------
    category : str, default='All'
        'All' : list all colormaps
        'Qualitative' : list only qualitative colormaps
        'Continuous' : list only continuous colormaps
        'Divergent' : list only divergent colormaps
        'Cyclic' : list only cyclic colormaps
    display : bool, default=False
        If True, display the colormaps as a grid.

    Returns
    -------
    None

    Examples
    --------
    >>> list_cmaps()  # List all colormaps
    >>> list_cmaps("Qualitative")  # List and display each colormap
    """
    # Get sorted list of colormaps
    cmaps = _get_cmap_list()
    # Output cmap info for each colormap
    for cmap in cmaps:
        categories = _get_cmap_categories(cmap)
        if category != 'All':
            if category not in categories:
                continue
        categories = [f'{k:10}' for k in categories]
        prtstr = f'{cmap:20}' + (' ').join(categories)
        print(prtstr)
        if display:
            show_colorbar(cmap)
    return


def list_qualitative_cmaps(display: bool = False) -> None:
    """
    Displays all qualitative colormaps in a grid layout.

    This function creates a grid of all qualitative colormaps available in matplotlib.
    The grid is displayed using matplotlib.

    Parameters
    ----------
    display : bool, default=False
        If True, display the colormaps as a grid.

    Returns
    -------
    None
        Displays the grid of qualitative colormaps using matplotlib 

    Examples
    --------
    >>> show_qualitative_cmaps()  # Display all qualitative colormaps
    """
    list_cmaps(category='Qualitative', display=display)
    return


def list_continuous_cmaps(display: bool = False) -> None:
    """
    Displays all continuous colormaps in a grid layout.

    This function creates a grid of all continuous colormaps available in matplotlib.
    The grid is displayed using matplotlib.

    Parameters
    ----------
    display : bool, default=False
        If True, display the colormaps as a grid.

    Returns
    -------
    None
        Displays the grid of continuous colormaps using matplotlib

    Examples
    --------
    >>> show_continuous_cmaps()  # Display all continuous colormaps
    """ 
    list_cmaps(category='Continuous', display=display)
    return  


def list_divergent_cmaps(display: bool = False) -> None:
    """
    Displays all divergent colormaps in a grid layout.

    This function creates a grid of all divergent colormaps available in matplotlib.
    The grid is displayed using matplotlib.

    Parameters
    ----------
    display : bool, default=False
        If True, display the colormaps as a grid.
    
    Returns
    -------
    None
        Displays the grid of divergent colormaps using matplotlib

    Examples
    --------
    >>> show_divergent_cmaps()  # Display all divergent colormaps
    """
    list_cmaps(category='Divergent', display=display)
    return


def list_cyclic_cmaps(display: bool = False) -> None:
    """
    Displays all cyclic colormaps in a grid layout.

    This function creates a grid of all cyclic colormaps available in matplotlib.
    The grid is displayed using matplotlib.

    Parameters
    ----------
    display : bool, default=False
        If True, display the colormaps as a grid.
    
    Returns
    -------
    None
        Displays the grid of cyclic colormaps using matplotlib

    Examples
    --------
    >>> show_cyclic_cmaps()  # Display all cyclic colormaps
    """
    list_cmaps(category='Cyclic', display=display)
    return


def logscale_cmap(cmap: Union[str, Colormap], norders: int = 3) -> Colormap:
    """
    Creates a logarithmic colormap by extending the input colormap with interpolated colors.

    This function takes a colormap and creates a new colormap with colors interpolated
    on a logarithmic scale. This is useful for visualizing data with a large dynamic range.

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap
        Input colormap name or instance
    norders : int, default=3
        Number of orders of magnitude to span in the logarithmic scale.
        The resulting colormap will have 2 * norders colors.

    Returns
    -------
    matplotlib.colors.Colormap
        A new colormap with colors interpolated on a logarithmic scale.
        The name of the new colormap will be 'log_' prefixed to the original name.

    Examples
    --------
    >>> cmap = logscale_cmap('viridis', norders=2)
    >>> plt.imshow(data, cmap=cmap)
    """
    cmap = plt.get_cmap(cmap)
    name = f"log_{cmap.name}"
    gradient = np.logspace(0, -norders, 2 * norders)
    colors = cmap(gradient)
    cmod = LinearSegmentedColormap.from_list(name, colors)
    return cmod


def get_bgcolor(cmap: Union[str, Colormap]) -> str:
    """
    Gets background color for a given colormap.

    Parameters
    ----------
    cmap : str or matplotlib.colors.Colormap
        Colormap name or instance. If a string is provided, it will be converted to a Colormap object.

    Returns
    -------
    color : str
        Background color in hex format.
        The color is determined by:
        - Predefined background colors for known colormaps
        - The darkest color from the colormap, darkened by 80% for unknown colormaps

    Examples
    --------
    >>> get_bgcolor('viridis')
    '#0E0717'
    >>> get_bgcolor(plt.cm.viridis)
    '#0E0717'
    """
    cmap = plt.get_cmap(cmap)
    bg_color_dict = {
        "gruvbox": "#1D2021",
        "gruvbox_dark": "#1D2021",
        "gruvbox_light": "#FBF1C7",
        "cobalt": "#122738",
        "noctis": "#03181B",
        "monokai": "#272822",
    }
    if cmap.name in bg_color_dict:
        color = bg_color_dict[cmap.name]
    else:
        # Get darkest color and darken it by 0.3
        colors = get_colors(cmap)
        h, s, v = np.array([mc.rgb_to_hsv(mc.to_rgb(c)) for c in colors]).T
        darkest_color = colors[np.argmin(v)]
        color: str = darken(darkest_color, 0.3) # type: ignore
    return color


""" Aliases for functions """
def show_cmaps(category: str = 'All'):
    """Alias for show_colormaps(display=True)."""
    return show_colormaps(category=category, display=True)


def show_qualitative_cmaps(category: str = 'All'):
    """Alias for list_qualitative_cmaps(display=True)."""
    return list_qualitative_cmaps(display=True)


def show_continuous_cmaps(category: str = 'All'):
    """Alias for list_continuous_cmaps(display=True)."""
    return list_continuous_cmaps(display=True)


def show_divergent_cmaps(category: str = 'All'):
    """Alias for list_divergent_cmaps(display=True)."""
    return list_divergent_cmaps(display=True)


def show_cyclic_cmaps(category: str = 'All'):
    """Alias for list_cyclic_cmaps(display=True)."""
    return list_cyclic_cmaps(display=True)


# Inherit docstring from show_colormaps
show_cmaps.__doc__ = list_cmaps.__doc__
show_qualitative_cmaps.__doc__ = list_qualitative_cmaps.__doc__
show_continuous_cmaps.__doc__ = list_continuous_cmaps.__doc__
show_divergent_cmaps.__doc__ = list_divergent_cmaps.__doc__
show_cyclic_cmaps.__doc__ = list_cyclic_cmaps.__doc__

show_colormap: Callable[..., None] = show_cmap
show_qualitative_colormaps: Callable[..., None] = show_qualitative_cmaps
show_continuous_colormaps: Callable[..., None] = show_continuous_cmaps
show_divergent_colormaps: Callable[..., None] = show_divergent_cmaps
show_cyclic_colormaps: Callable[..., None] = show_cyclic_cmaps
list_colormaps: Callable[..., None] = list_cmaps
list_qualitative_colormaps: Callable[..., None] = list_qualitative_cmaps
list_continuous_colormaps: Callable[..., None] = list_continuous_cmaps
list_divergent_colormaps: Callable[..., None] = list_divergent_cmaps
list_cyclic_colormaps: Callable[..., None] = list_cyclic_cmaps

import types
__all__ = [name for name, thing in globals().items()
          if not (name.startswith("_") or isinstance(thing, types.ModuleType))]
del types
