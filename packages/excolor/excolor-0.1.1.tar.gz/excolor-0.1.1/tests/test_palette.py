import os
import pytest
import excolor as ec

def test_generate_palette_linear_debug():
    """
    Test the generate_palette function with mode='linear' and debug=True.
    """
    color = 'blue'
    n = 10
    mode = 'linear'
    
    debug_file = f"debug_{mode}.jpg"
    # Clean up file from previous runs if it exists
    if os.path.exists(debug_file):
        os.remove(debug_file)

    palette = ec.generate_palette(color, n=n, mode=mode, debug=True)

    # 1. Check if the output is a list of n hex strings
    assert isinstance(palette, list)
    assert len(palette) == n
    for c in palette:
        assert isinstance(c, str)
        assert c.startswith('#')
        assert len(c) == 7

    # 2. Check if the debug file was created
    assert os.path.exists(debug_file)

    # 3. The path goes from white to black, so check the start and end colors
    assert palette[0] == '#ffffff'
    assert palette[-1] == '#000000'

    # Clean up the created file
    os.remove(debug_file)


def test_generate_palette_circle_debug():
    """
    Test the generate_palette function with mode='circle' and debug=True.
    """
    color = 'blue'
    n = 10
    mode = 'circle'
    
    debug_file = f"debug_{mode}.jpg"
    # Clean up file from previous runs if it exists
    if os.path.exists(debug_file):
        os.remove(debug_file)

    palette = ec.generate_palette(color, n=n, mode=mode, debug=True)

    # 1. Check if the output is a list of n hex strings
    assert isinstance(palette, list)
    assert len(palette) == n
    for c in palette:
        assert isinstance(c, str)
        assert c.startswith('#')
        assert len(c) == 7

    # 2. Check if the debug file was created
    assert os.path.exists(debug_file)

    # 3. The path goes from white to black, so check the start and end colors
    # Note: For non-linear paths, start/end may not be pure white/black due to sampling.
    # We can check that they are very close.
    assert palette[0] == '#ffffff' # Start should be white
    assert palette[-1] == '#000000' # End should be black

    # Clean up the created file
    os.remove(debug_file)


def test_generate_palette_superellipse_debug():
    """
    Test the generate_palette function with mode='superellipse' and debug=True.
    """
    color = 'blue'
    n = 10
    mode = 'superellipse'
    
    debug_file = f"debug_{mode}.jpg"
    # Clean up file from previous runs if it exists
    if os.path.exists(debug_file):
        os.remove(debug_file)

    palette = ec.generate_palette(color, n=n, mode=mode, debug=True)

    # 1. Check if the output is a list of n hex strings
    assert isinstance(palette, list)
    assert len(palette) == n
    for c in palette:
        assert isinstance(c, str)
        assert c.startswith('#')
        assert len(c) == 7

    # 2. Check if the debug file was created
    assert os.path.exists(debug_file)

    # 3. The path goes from white to black, so check the start and end colors
    assert palette[0] == '#ffffff'
    assert palette[-1] == '#000000'

    # Clean up the created file
    os.remove(debug_file)

