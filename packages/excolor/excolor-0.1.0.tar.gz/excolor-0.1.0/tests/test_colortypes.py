import pytest
import numpy as np
from excolor import colortypes as ct

# Test cases for get_color_type
@pytest.mark.parametrize("color_input, expected_type", [
    # Named colors
    ("red", "name"),
    ("r", "name"),
    ("tab:blue", "name"),

    # Hex colors
    ("#FF0000", "hex"),
    ("#F00", "hex"),
    ("#FF0000AA", "hexa"),
    ("#F00A", "hexa"),

    # RGB/RGBA colors (float 0-1)
    ((1.0, 0.0, 0.0), "rgb|hls|hsl|hsv|oklch"),
    ([1.0, 0.0, 0.0], "rgb|hls|hsl|hsv|oklch"),
    ((1.0, 0.0, 0.0, 1.0), "rgba"),
    ([1.0, 0.0, 0.0, 1.0], "rgba"),

    # RGB/RGBA colors (int 0-255)
    ((1, 0, 0), "rgb255"),
    ((255, 0, 0), "rgb255"),
    ([255, 0, 0], "rgb255"),
    ((1, 0, 0, 0), "rgba255"),
    ((255, 0, 0, 255), "rgba255"),
    ([255, 0, 0, 255], "rgba255"),

    # Special string formats
    ("hsv(0, 1, 1)", "hsv formatted"),
    ("hsl(0, 1, 0.5)", "hsl formatted"),
    ("oklch(0.8, 0.1, 20)", "oklch formatted"),

    # Formatted string inputs
    ("rgb(255, 0, 0)", "rgb255 formatted"),
    ("hsv(0, 100%, 100%)", "hsv formatted"),
    ("hls(0, 50%, 100%)", "hls formatted"),
    ("hsl(0, 100%, 50%)", "hsl formatted"),
    ("oklch(62.8% 0.26 29.23)", "oklch formatted"),
    ("rgba(255, 0, 0, 0.5)", "rgba255 formatted"),

    # Invalid inputs
    ("not_a_color", None),
    ((1, 2, 3, 4, 5), None),
    ((256, 0, 0), None),
    ((1.1, 0.0, 0.0), None),
    ("#GGHHII", None)
])
def test_get_color_type(color_input, expected_type):
    assert ct._get_color_type(color_input) == expected_type

# --- Tests for generic conversion functions ---

@pytest.mark.parametrize("color_input, expected_rgb", [
    ("red", (1.0, 0.0, 0.0)),
    ("#00FF00", (0.0, 1.0, 0.0)),
    ("#0000FFA0", (0.0, 0.0, 1.0, 0.6274509803921569)),
    ((0, 255, 0), (0.0, 1.0, 0.0)),
    ((0, 255, 0, 128), (0.0, 1.0, 0.0, 0.5019607843137255)),
    ((0.0, 0.0, 1.0), (0.0, 0.0, 1.0)),
    ("hsv(0, 100%, 100%)", (1.0, 0.0, 0.0)),
    ("hls(0, 50%, 100%)", (1.0, 0.0, 0.0)),
    ("hsl(0, 100%, 50%)", (1.0, 0.0, 0.0)),

    # Formatted string inputs
    ("rgb(255, 0, 0)", (1.0, 0.0, 0.0)),
    ("hsv(0, 100%, 100%)", (1.0, 0.0, 0.0)),
    ("hls(0, 50%, 100%)", (1.0, 0.0, 0.0)),
    ("hsl(0, 100%, 50%)", (1.0, 0.0, 0.0)),
    ("oklch(62.8% 0.258 29.23)", (1.0, 0.0, 0.0)),
    ("rgba(0, 0, 255, 255)", (0.0, 0.0, 1.0, 1.0)),
])
def test_to_rgb(color_input, expected_rgb):
    result = ct.to_rgb(color_input)
    assert isinstance(result, tuple)
    assert np.allclose(result, expected_rgb, atol=1e-3)

def test_to_rgb_keep_alpha():
    assert np.allclose(ct.to_rgb("#FF000080", keep_alpha=True), (1.0, 0.0, 0.0, 0.50196078), atol=1e-3)
    assert np.allclose(ct.to_rgb("#FF000080", keep_alpha=False), (1.0, 0.0, 0.0), atol=1e-3)
    assert np.allclose(ct.to_rgb((255, 0, 0, 128), keep_alpha=True), (1.0, 0.0, 0.0, 0.50196078), atol=1e-3)
    assert np.allclose(ct.to_rgb((255, 0, 0, 128), keep_alpha=False), (1.0, 0.0, 0.0), atol=1e-3)

def test_to_rgb_formatted():
    assert ct.to_rgb("red", formatted=True) == "rgb(255, 0, 0)"
    assert ct.to_rgb("#FF000080", formatted=True) == "rgb(255, 0, 0, 128)"

@pytest.mark.parametrize("color_input, expected_hex", [
    ("red", "#FF0000"),
    ((0, 255, 0), "#00FF00"),
    ((0.0, 0.0, 1.0, 0.5), "#0000FF80"),
])
def test_to_hex(color_input, expected_hex):
    assert ct.to_hex(color_input) == expected_hex

def test_to_hex_keep_alpha():
    assert ct.to_hex((0., 0., 1., 0.5), keep_alpha=True) == "#0000FF80"
    assert ct.to_hex((0., 0., 1., 0.5), keep_alpha=False) == "#0000FF"

@pytest.mark.parametrize("color_input, expected_rgb255", [
    ("red", (255, 0, 0)),
    ("#00FF00", (0, 255, 0)),
    ((0.0, 0.0, 1.0), (0, 0, 255)),
    ((0.0, 0.0, 1.0, 0.5), (0, 0, 255, 128)),
])
def test_to_rgb255(color_input, expected_rgb255):
    assert ct.to_rgb255(color_input) == expected_rgb255

def test_to_rgb255_formatted():
    assert ct.to_rgb255("red", formatted=True) == "rgb(255, 0, 0)"
    assert ct.to_rgb255((0.0, 0.0, 1.0, 0.5), formatted=True) == "rgb(0, 0, 255, 128)"

def test_to_hsv():
    assert np.allclose(ct.to_hsv("red"), (0.0, 1.0, 1.0), atol=1e-3)
    assert ct.to_hsv("red", formatted=True) == "hsv(0.00, 100.00%, 100.00%)"

def test_to_hls():
    assert np.allclose(ct.to_hls("red"), (0.0, 0.5, 1.0), atol=1e-3)
    assert ct.to_hls("red", formatted=True) == "hls(0.00, 50.00%, 100.00%)"

def test_to_oklch():
    assert np.allclose(ct.to_oklch("red"), (0.628, 0.2576, 0.0812), atol=1e-3)
    assert ct.to_oklch("red", formatted=True) == "oklch(62.80% 0.26 29.23)"

def test_oklch_grayscale():
    """Test grayscale conversion for OKLCH."""
    # Test that a grayscale RGB converts to OKLCH with C~0
    gray_rgb = (0.5, 0.5, 0.5)
    l, c, h = ct.to_oklch(gray_rgb)
    assert np.isclose(c, 0.0, atol=1e-3)

    # Test that a grayscale OKLCH (C=0) converts to RGB with equal components
    # We must call the specific converter, as the generic `to_rgb` would misinterpret
    # the tuple as an RGB color.
    gray_oklch = (l, 0, 0)
    r, g, b = ct.oklch_to_rgb(gray_oklch)
    assert np.isclose(r, g) and np.isclose(g, b)


# --- Tests for Refactored CSS-like Formatting ---

@pytest.mark.parametrize("invalid_string", [
    "rgb(255, 0, abc)",
    "hsl(400, 100, 50%)",
    "hsv(400, 100%, 50,)",
    "oklch(97.49; 0.02; 228.96)",
])
def test_parsing_of_malformed_css_strings(invalid_string):
    """Tests that malformed CSS strings that are routed to the parser raise the correct error."""
    with pytest.raises(ValueError, match="Could not parse color string"):
        ct.to_rgb(invalid_string)


@pytest.mark.parametrize("invalid_string", [
    "rgb(255,0,0",
    "rgb 255 0 0",
])
def test_handling_of_invalid_strings(invalid_string):
    """Tests that invalid strings that are not routed to the parser raise the correct error."""
    with pytest.raises(ValueError, match=r"Invalid input: expected rgb or rgba, got None"):
        ct.to_rgb(invalid_string)

@pytest.mark.parametrize("color_input, converter, expected_output", [
    ("rgb(255, 0, 0)", ct.rgb_to_hls, "hls(0.00, 50.00%, 100.00%)"),
    ("rgb(255, 0, 0)", ct.rgb_to_hsl, "hsl(0.00, 100.00%, 50.00%)"),
    ("rgb(255, 0, 0)", ct.rgb_to_hsv, "hsv(0.00, 100.00%, 100.00%)"),
    ("hls(0, 50%, 100%)", ct.hls_to_rgb, "rgb(255, 0, 0)"),
    ("hsl(0, 100%, 50%)", ct.hsl_to_rgb, "rgb(255, 0, 0)"),
    ("hsv(0, 100%, 100%)", ct.hsv_to_rgb, "rgb(255, 0, 0)"),
    ("oklch(62.8% 0.26 29.23)", ct.oklch_to_rgb, "rgb(255, 0, 0)"),
])
def test_precise_conversions_formatted(color_input, converter, expected_output):
    """
    Tests that precise conversion functions preserve the formatted string style.
    """
    result = converter(color_input)
    # A simple string comparison should be sufficient here
    assert result == expected_output


@pytest.mark.parametrize("color_input, converter, expected_output", [
    ("red", ct.to_rgb, "rgb(255, 0, 0)"),
    ("red", ct.to_hls, "hls(0.00, 50.00%, 100.00%)"),
    ("red", ct.to_hsl, "hsl(0.00, 100.00%, 50.00%)"),
    ("red", ct.to_hsv, "hsv(0.00, 100.00%, 100.00%)"),
    ("red", ct.to_oklch, "oklch(62.80% 0.26 29.23)")
])
def test_generic_conversions_formatted(color_input, converter, expected_output):
    """
    Tests that generic `to_*` functions produce correct formatted strings.
    """
    result = converter(color_input, formatted=True)
    assert result == expected_output

