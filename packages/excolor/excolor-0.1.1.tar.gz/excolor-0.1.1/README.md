[![Python Versions](https://img.shields.io/pypi/pyversions/excolor?style=plastic)](https://pypi.org/project/excolor/)
[![PyPI](https://img.shields.io/pypi/v/excolor?style=plastic)](https://pypi.org/project/excolor/)
[![License](https://img.shields.io/pypi/l/excolor?style=plastic)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/excolor/badge/?version=latest)](https://excolor.readthedocs.io/en/latest/?badge=latest)


<h1><p align="left">
  <img src="https://github.com/timpyrkov/excolor/blob/master/img/logo.png?raw=true" alt="ExColor logo" height="30" style="vertical-align: middle; margin-right: 10px;">
  <span style="font-size:2.5em; vertical-align: middle;"><b>ExColor</b></span>
</p></h1>


# Installation

```
pip install excolor
```


# Extra colormaps (gruvbox and more)

New colormaps: BrBu, BrGn, OrBu, OrGn, PiBu, rtd, artdeco, cyberpunk, synthwave, gruvbox, cobalt, noctis, monokai, oceanic.

```
import excolor

cmap = plt.get_cmap("gruvbox")
cmap
```

`Gruvbox`<br>
![](https://github.com/timpyrkov/excolor/blob/master/img/colormap.png?raw=true)

# Generate color palettes

Mode "superellipse" defines the path from black to white. Higher degree produces more vibrant colors.

```
# Seed color
color = '#D65D0E'

colors = excolor.generate_palette(color, mode='superellipse', power=2)

excolor.show_colors(colors)
```

`['#FFFFFF', '#FFEDCC', '#FFCE95', '#FFAA61', '#FD8435', '#D85F10', '#AA3C00', '#751D00', '#390600', '#000000']`<br>
![](https://github.com/timpyrkov/excolor/blob/master/img/palette.png?raw=true)

```
# Generate palette for primary CSS colors
primary_colors = excolor.generate_primary_palette(color)

excolor.show_colors(primary_colors)
```

`/* Pastel Orange color palette */`<br>
`:root {`<br>
`  --primary-color-1: #FFF8DD;`<br>
`  --primary-color-2: #FFE8B4;`<br>
`  --primary-color-3: #FFCF8B;`<br>
`  --primary-color-4: #FFB266;`<br>
`  --primary-color-5: #FF9547;`<br>
`  --primary-color-6: #F2792A;`<br>
`  --primary-color-7: #D55C0D;`<br>
`  --primary-color-8: #B74000;`<br>
`  --primary-color-9: #942500;`<br>
`}`<br>
![](https://github.com/timpyrkov/excolor/blob/master/img/palette_primary.png?raw=true)


```
# Generate palette for background CSS colors
background_colors = excolor.generate_background_palette(color)

excolor.show_colors(background_colors)
```

`/* Reddy Brown color palette */`<br>
`:root {`<br>
`  --background-color-1: #B74000;`<br>
`  --background-color-2: #A63200;`<br>
`  --background-color-3: #942500;`<br>
`  --background-color-4: #801800;`<br>
`  --background-color-5: #6B0D00;`<br>
`  --background-color-6: #540400;`<br>
`  --background-color-7: #3D0000;`<br>
`  --background-color-8: #270000;`<br>
`  --background-color-9: #130000;`<br>
`}`<br>
![](https://github.com/timpyrkov/excolor/blob/master/img/palette_background.png?raw=true)


```
# Generate palette for foreground CSS colors
foreground_colors = excolor.generate_foreground_palette(color)

excolor.show_colors(foreground_colors)
```

`/* Circus color palette */`<br>
`:root {`<br>
`  --foreground-color-1: #FFFCEF;`<br>
`  --foreground-color-2: #FFF8DD;`<br>
`  --foreground-color-3: #FFF2CA;`<br>
`  --foreground-color-4: #FFE8B4;`<br>
`  --foreground-color-5: #FFDC9F;`<br>
`  --foreground-color-6: #FFCF8B;`<br>
`  --foreground-color-7: #FFC078;`<br>
`  --foreground-color-8: #FFB266;`<br>
`  --foreground-color-9: #FFA456;`<br>
`}`<br>
![](https://github.com/timpyrkov/excolor/blob/master/img/palette_foreground.png?raw=true)

# Colorize image

```
url = "https://github.com/timpyrkov/excolor/blob/master/img/image_bw.png?raw=true"

# Load image from url (image_bw.png from github repository)
img = excolor.load_image(url)

# Show source grayscale image
plt.figure(figsize=(6,6), facecolor="#00000000")
plt.imshow(img)
plt.axis("off")
plt.show()

# Colorize image
light, dark = "#FBF1C6", "#665C54"
img = excolor.colorize_image(url, dark, light)

# Show colorized image
plt.figure(figsize=(6,6), facecolor="#00000000")
plt.imshow(img)
plt.axis("off")
plt.show()
```

![](https://github.com/timpyrkov/excolor/blob/master/img/source_greyscale.png?raw=true)
![](https://github.com/timpyrkov/excolor/blob/master/img/arrow.png?raw=true)
![](https://github.com/timpyrkov/excolor/blob/master/img/target_colorize.png?raw=true)


# Greyscale image, keep channels

```
url = "https://github.com/timpyrkov/excolor/blob/master/img/image_color.png?raw=true"

# Load image from url (image_color.png from github repository)
img = excolor.load_image(url)

# Show source image
plt.figure(figsize=(6,6), facecolor="#00000000")
plt.imshow(img)
plt.axis("off")
plt.show()

# Convert to greyscale
greyscaled = excolor.greyscale_image(url)

# Show greyscale image
plt.figure(figsize=(6,6), facecolor="#00000000")
plt.imshow(greyscaled)
plt.axis("off")
plt.show()

print("Source image array shape:", np.asarray(img).shape)
print("Greyscaled image array shape:", np.asarray(greyscaled).shape)
```

![](https://github.com/timpyrkov/excolor/blob/master/img/source_color.png?raw=true)
![](https://github.com/timpyrkov/excolor/blob/master/img/arrow.png?raw=true)
![](https://github.com/timpyrkov/excolor/blob/master/img/target_greyscale.png?raw=true)

`Source image array shape: (240, 320, 3)`<br>
`Greyscaled image array shape: (240, 320, 3)`<br>

# Low-polygonal

```
url = "https://github.com/timpyrkov/excolor/blob/master/img/image_gruvbox.png?raw=true"

# Load image from url (image_gruvbox.png from github repository)
img = excolor.load_image(url)

# Show source image
plt.figure(figsize=(6,6), facecolor="#00000000")
plt.imshow(img)
plt.axis("off")
plt.show()

# Convert to low-polygonal image
img = excolor.triangle_wallpaper(img=img, density=30, distortion=0.4, size=(640,480))

# Show low-polygonal image
plt.figure(figsize=(6,6), facecolor="#00000000")
plt.imshow(img)
plt.axis("off")
plt.show()
```

![](https://github.com/timpyrkov/excolor/blob/master/img/source_color.png?raw=true)
![](https://github.com/timpyrkov/excolor/blob/master/img/arrow.png?raw=true)
![](https://github.com/timpyrkov/excolor/blob/master/img/target_polygonal.png?raw=true)


# Wallpaper

Draw patches distorted by Perlin noise.

```
img = excolor.perlin_wallpaper("gruvbox", n=5, size=(720, 480))
img
```

![](https://github.com/timpyrkov/excolor/blob/master/img/wallpaper.png?raw=true)

# Documentation

[https://excolor.readthedocs.io](https://excolor.readthedocs.io)