
import os
import pytest
import numpy as np
from matplotlib.colors import ListedColormap
from excolor import get_color_name, lighten, darken, saturate, desaturate, to_rgb

def test_get_color_name_exact_match():
    """Tests that an exact hex color returns the correct name."""
    assert get_color_name('#FF0000') == 'red'
    assert get_color_name("#F0F8FF").lower() == "aliceblue"
    assert get_color_name('#008000') == 'green'

def test_get_color_name_case_insensitivity():
    """Tests that the function is case-insensitive for hex codes."""
    assert get_color_name('#ff0000') == 'red'
    assert get_color_name('#FF0000') == 'red'

def test_get_color_name_closest_match():
    """Tests that a non-exact hex color returns the closest named color."""
    # Very close to white
    assert get_color_name('#FEFEFE') == 'pale grey'
    # Very close to black
    assert get_color_name('#010101') == 'black'
    # A color closer to darkcyan than any other color
    assert get_color_name('#018B8C') == 'dark cyan'

# --- Tests for Color Manipulation Functions ---

@pytest.mark.parametrize("color_input, factor, expected_output", [
    ("red", 0.2, '#ff6666'),
    ("#ff0000", 0.2, '#ff6666'),
    ((1.0, 0.0, 0.0), 0.2, (1.0, 0.4, 0.4)),
    ((255, 0, 0), 0.2, (255, 102, 102)),
    ("rgb(255, 0, 0)", 0.2, "rgb(255, 102, 102)"),
])
def test_lighten_single_color(color_input, factor, expected_output):
    """Tests lighten() with single color inputs in various formats."""
    result = lighten(color_input, factor)
    if isinstance(result, str):
        assert result.lower() == expected_output.lower()
    else:
        assert np.allclose(result, expected_output, atol=1e-2)

@pytest.mark.parametrize("color_input, factor, expected_output", [
    ("red", 0.2, '#990000'),
    ("#ff0000", 0.2, '#990000'),
    ((1.0, 0.0, 0.0), 0.2, (0.6, 0.0, 0.0)),
    ((255, 0, 0), 0.2, (153, 0, 0)),
    ("rgb(255, 0, 0)", 0.2, "rgb(153, 0, 0)"),
])
def test_darken_single_color(color_input, factor, expected_output):
    """Tests darken() with single color inputs in various formats."""
    result = darken(color_input, factor)
    if isinstance(result, str):
        assert result == expected_output
    else:
        assert np.allclose(result, expected_output, atol=1e-2)

@pytest.mark.parametrize("color_input, factor, expected_output", [
    ("#808080", 0.5, '#c04141'),
    ((0.5, 0.5, 0.5), 0.5, (0.75, 0.25, 0.25)),
])
def test_saturate_single_color(color_input, factor, expected_output):
    """Tests saturate() with single color inputs."""
    result = saturate(color_input, factor)
    if isinstance(result, str):
        assert result.lower() == expected_output.lower()
    else:
        assert np.allclose(result, expected_output, atol=1e-2)

@pytest.mark.parametrize("color_input, factor, expected_output", [
    ("red", 0.5, '#bf4040'),
    ((1.0, 0.0, 0.0), 0.5, (0.75, 0.25, 0.25)),
])
def test_desaturate_single_color(color_input, factor, expected_output):
    """Tests desaturate() with single color inputs."""
    result = desaturate(color_input, factor)
    if isinstance(result, str):
        assert result.lower() == expected_output.lower()
    else:
        assert np.allclose(result, expected_output, atol=1e-2)

def test_lighten_list():
    """Tests that lighten() works correctly on a list of colors."""
    colors = ["red", (0, 1, 0)]
    result = lighten(colors, 0.2)
    assert len(result) == 2
    assert result[0].lower() == '#ff6666'
    assert to_rgb(result[1])[1] > to_rgb((0, 1, 0))[1]

def test_darken_colormap():
    """Tests that darken() works correctly on a colormap object."""
    cmap = ListedColormap(["red", "blue"])
    result = darken(cmap, 0.2)
    assert isinstance(result, ListedColormap)
    assert result.name == cmap.name + "_dark"
    # Check if the new colors are darker
    original_colors_rgb = [to_rgb(c) for c in cmap.colors]
    darkened_colors_rgb = [to_rgb(c) for c in result.colors]
    assert darkened_colors_rgb[0][0] < original_colors_rgb[0][0]
