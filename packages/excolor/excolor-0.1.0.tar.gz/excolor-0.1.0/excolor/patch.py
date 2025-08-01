#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
This module contains functions to create patches.
"""

import numpy as np
import cv2 
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.colors import Colormap
from matplotlib.axes import Axes
from typing import List, Tuple, Union, Optional
from .gradient import fill_gradient
from .colortypes import to_rgb
from .imagetools import pixels_to_size_and_dpi, remove_margins, add_layer
from .imagetools import fig2img, img2arr, arr2img, mask2img

import warnings
warnings.filterwarnings("ignore")


class Patch:
    """
    A class representing a patch that can be drawn on images.

    A patch is defined by either a set of coordinates or a mask image,
    and can be filled with solid colors or gradients. It can also cast
    shadows or glows on images.

    Attributes
    ----------
    bbox : List[Tuple[int, int]]
        Bounding box of the patch [(x0, y0), (x1, y1)]
    mask : numpy.ndarray
        Binary mask where 1 indicates inside area and 0 outside
    start : Tuple[int, int]
        Starting position (x, y) of the patch
    """

    def __init__(
        self,
        coords: Optional[List[Tuple[int, int]]] = None,
        img: Optional[Image.Image] = None,
        start: Optional[Tuple[int, int]] = None
    ):
        """
        Initializes a Patch from coordinates or mask.

        Parameters
        ----------
        coords : List[Tuple[int, int]], optional
            List of (x, y) coordinates defining the patch boundary
        img : PIL.Image.Image, optional
            Image where black pixels define the patch area
        start : Tuple[int, int], optional
            Starting position (x, y) for the mask. Required if mask is provided.

        Raises
        ------
        ValueError
            If neither coords nor mask is provided
            If mask is provided without start_pos
        """
        if coords is None and img is None:
            raise ValueError("Either coords or mask must be provided")
        if img is not None and start is None:
            raise ValueError("start must be provided when using img")
        if img is not None and coords is not None:
            raise ValueError("coords must not be provided when using img")

        if coords is not None:
            # Calculate bounding box from coordinates
            coords = np.array(coords)
            if len(coords) == 0:
                coords = np.array([[0, 0]])
            x0, y0 = np.min(coords, axis=0)
            x1, y1 = np.max(coords, axis=0)
            size = (int(x1 - x0), int(y1 - y0))
            self.inches, self.dpi = pixels_to_size_and_dpi(size, exact=True)
            self.size = (int(self.inches[0] * self.dpi), int(self.inches[1] * self.dpi))
            self.width, self.height = self.size
            self.start = (int(x0), int(y0))
            self.end = (int(x0 +self.width), int(y0 + self.height))
            self.bbox = [self.start, self.end]
            self.mask = None
            if self.inches[0] > 0 and self.inches[1] > 0:
                self._calculate_mask_from_coords(coords)
        else:
            # Use provided mask and position
            self.size = img.size
            self.width, self.height = self.size
            self.start = start
            self.end = (int(start[0] + self.width), int(start[1] + self.height))
            self.bbox = [self.start, self.end]
            self._calculate_mask_from_img(img)

        # Calculate size of the patch
        self.size = (self.bbox[1][0] - self.bbox[0][0], self.bbox[1][1] - self.bbox[0][1])
        self.fill = None
        self.shadow = None
        return


    def _calculate_mask_from_coords(self, coords: np.ndarray) -> None:
        """
        Calculates binary mask from coordinates using matplotlib polygon filling.

        Notes
        -----
        The mask is a 2D binary array (1 - inside, 0 - outside).
        The mask is array (x, y), y axis goes from bottom to top. 
        Transpose it to convert to image dimensions (y, x), 
        Then reverse y axis  to make it go from top to bottom.

        Parameters
        ----------
        coords : numpy.ndarray
            Array of (x, y) coordinates
        """
        # Create a figure with the exact size needed
        fig = plt.figure(figsize=self.inches, dpi=self.dpi, facecolor='w')
        
        # Set xlim and ylim to the size of the patch
        plt.xlim(0, self.inches[0] * self.dpi)
        plt.ylim(0, self.inches[1] * self.dpi)

        # Move the patch to the image origin
        coords[:, 0] -= self.bbox[0][0]
        coords[:, 1] -= self.bbox[0][1]

        # Fill the polygon
        plt.fill(coords[:, 0], coords[:, 1], color='black')
        
        # Convert to PIL Image
        remove_margins()
        img = fig2img(fig)
        plt.close(fig)
        
        # Convert to binary mask
        arr = img2arr(img)
        self.mask = (arr[..., 0] < 128).astype(np.uint8)
        return


    def _calculate_mask_from_img(self, img: Image.Image) -> None:
        """
        Calculates binary mask from image.

        Notes
        -----
        The mask is a 2D binary array (1 - inside, 0 - outside).
        The mask is array (x, y), y axis goes from bottom to top. 
        Transpose it to convert to image dimensions (y, x), 
        Then reverse y axis  to make it go from top to bottom.

        Parameters
        ----------
        img : PIL.Image.Image
            Image to calculate mask from
        """
        if img.mode == 'RGBA':
            # If alpha channel is present, use it to create mask
            arr = img2arr(img)
            self.mask = (arr[..., 3] > 0).astype(np.uint8)
        else:
            # If no alpha channel, convert to grayscale and use threshold
            arr = img2arr(img.convert('L'))
            self.mask = (arr < 128).astype(np.uint8)
        return


    def fill_solid(self, color: str) -> Image.Image:
        """
        Fills the patch with a solid color.

        Parameters
        ----------
        color : str
            Color to fill the patch with. Can be:
            - Color name (e.g., 'red')
            - Hex string (e.g., '#FF0000')

        Returns
        -------
        PIL.Image.Image
            Image of the filled patch with transparency
        """
        img = Image.new('RGBA', (self.width, self.height), color)
        img.putalpha(mask2img(1 - self.mask))
        self.fill = img
        return img


    def fill_gradient(
        self,
        colors: Union[List[str], str, Colormap],
        angle: float = 0,
    ) -> Image.Image:
        """
        Fills the patch with a gradient.

        Parameters
        ----------
        colors : str or List[str] or Colormap
            Colormap or color or list of colors for the gradient
        angle : float, default=0
            Angle of the gradient in degrees

        Returns
        -------
        PIL.Image.Image
            Image of the gradient-filled patch with transparency
        """
        img = fill_gradient(colors, (self.width, self.height), angle=angle, show=False)
        img.putalpha(mask2img(1 - self.mask))
        self.fill = img
        return img


    def _create_full_image_mask(self, img: Image.Image) -> np.ndarray:
        """
        Creates a binary mask for the entire image.

        This method creates a binary mask for the entire image, handling cases where
        parts of the patch's bounding box may fall outside the image boundaries.

        Notes
        -----
        The mask is a 2D binary array (1 - inside, 0 - outside).
        The mask is array (x, y), y axis goes from bottom to top. 
        Transpose it to convert to image dimensions (y, x), 
        Then reverse y axis  to make it go from top to bottom.

        Parameters
        ----------
        img : PIL.Image.Image
            The image to create the mask for

        Returns
        -------
        numpy.ndarray
            Binary mask array of the same size as the image
        """
        # Create an empty array of the same size as the image
        arr = np.zeros(img.size, dtype=float)

        # Get image dimensions
        img_width, img_height = arr.shape

        # Calculate valid slice ranges for the mask
        x_start = max(0, self.bbox[0][0])
        y_start = max(0, self.bbox[0][1])
        x_end = min(img_width, self.bbox[1][0])
        y_end = min(img_height, self.bbox[1][1])

        # Calculate corresponding slice ranges for the patch mask
        mask_x_start = max(0, x_start - self.bbox[0][0])
        mask_y_start = max(0, y_start - self.bbox[0][1])
        mask_x_end = min(self.mask.shape[0], x_end - self.bbox[0][0])
        mask_y_end = min(self.mask.shape[1], y_end - self.bbox[0][1])

        # Only proceed if there is an overlap between the patch and the image
        if y_start < y_end and x_start < x_end:
            # Fill the valid area with the corresponding part of the mask
            arr[x_start:x_end, y_start:y_end] = self.mask[mask_x_start:mask_x_end, mask_y_start:mask_y_end]

        return arr


    def _create_blurred_mask(
        self, 
        img: Image.Image, 
        kernel: Tuple[int, int] = (31, 31), 
        sigma: float = 10
    ) -> np.ndarray:
        """
        Creates a blurred binary mask for shadow or glow.
        Returns a 2D array of the same size as the image.
        """
        # Create a binary mask for the entire image
        arr = self._create_full_image_mask(img)

        # Apply Gaussian blur
        kernel = (int(kernel[0] / 2) * 2 + 1, int(kernel[1] / 2) * 2 + 1)
        arr = cv2.GaussianBlur(arr, kernel, sigma)

        return arr


    def cast_shadow(
        self,
        img: Image.Image,
        kernel: Tuple[int, int] = (31, 31),
        sigma: float = 10,
        color: str = "#000000"
    ) -> Image.Image:
        """
        Casts a shadow of the patch.

        Note:
        -----
        Returns only shadow image. 
        Use add_layer() to add shadow to an image.

        Parameters
        ----------
        img : PIL.Image.Image
            Image to cast shadow onto
        kernel : Tuple[int, int], default=(31, 31)
            Size of the Gaussian kernel
        sigma : float, default=10
            Standard deviation of the Gaussian kernel
        color : str, default="#000000"
            Color of the shadow

        Returns
        -------
        PIL.Image.Image
            Image with shadow cast
        """
        # Create a blurred binary mask for shadow
        arr = self._create_blurred_mask(img, kernel, sigma)

        # Create color channels
        rgb = to_rgb(color)
        shadow = [rgb[i] * np.ones_like(arr) for i in range(3)]

        # Add alpha channel
        shadow.append(arr)
        shadow = np.stack(shadow, axis=2)

        # Convert binary array to image
        shadow = np.clip(255 * shadow, 0, 255).astype(np.uint8)
        shadow = arr2img(shadow)
        self.shadow = shadow
        return shadow
    

    def get_average_color(self, img: Image.Image) -> str:
        """
        Calculates the average color of the area where the patch will be placed.

        Parameters
        ----------
        img : PIL.Image.Image
            Image to analyze

        Returns
        -------
        str
            Average color as hex string
        """
        arr = img2arr(img)
        mask = self._create_full_image_mask(img) > 0.5

        rgb = (0, 0, 0)
        if np.sum(mask) > 0:
            if len(arr.shape) == 2:  # Grayscale
                rgb = [np.mean(arr[mask])] * 3
            else:  # RGB
                rgb = [np.mean(arr[..., i][mask]) for i in range(3)]

        color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        return color


    def get_centroid_color(self, img: Image.Image) -> str:
        """
        Calculates the color of the centroid of the patch.

        Parameters
        ----------
        img : PIL.Image.Image
            Image to analyze

        Returns
        -------
        str
            Centroid color as hex string
        """
        arr = img2arr(img)
        mask = self._create_full_image_mask(img) > 0.5

        rgb = (0, 0, 0)
        if np.sum(mask) > 0:
            centroid = np.mean(np.argwhere(mask), axis=0).astype(int)
            if len(arr.shape) == 2:  # Grayscale
                rgb = arr[centroid[0], centroid[1]] * np.ones(3)
            else:  # RGB
                rgb = arr[centroid[0], centroid[1]]

        color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        return color


    def get_darkest_color(self, img: Image.Image) -> str:
        """
        Calculates the darkest color of the area where the patch will be placed.

        Parameters
        ----------
        img : PIL.Image.Image
            Image to analyze

        Returns
        -------
        str
            Darkest color as hex string
        """
        arr = img2arr(img)
        mask = self._create_full_image_mask(img) > 0.5

        rgb = (0, 0, 0)
        if np.sum(mask) > 0:
            if len(arr.shape) == 2:  # Grayscale
                rgb = [np.min(arr[mask])] * 3
            else:  # RGB
                rgb = np.stack([arr[..., i][mask].flatten() for i in range(3)])
                intensity = np.mean(rgb, axis=0)
                k = np.argmin(intensity)
                rgb = rgb[:,k]

        color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        return color

    def get_lightest_color(self, img: Image.Image) -> str:
        """
        Calculates the lightest color of the area where the patch will be placed.

        Parameters
        ----------
        img : PIL.Image.Image
            Image to analyze

        Returns
        -------
        str
            Lightest color as hex string
        """
        arr = img2arr(img)
        mask = self._create_full_image_mask(img) > 0.5

        rgb = (0, 0, 0)
        if np.sum(mask) > 0:
            if len(arr.shape) == 2:  # Grayscale
                rgb = [np.max(arr[mask])] * 3
            else:  # RGB
                rgb = np.stack([arr[..., i][mask].flatten() for i in range(3)])
                intensity = np.mean(rgb, axis=0)
                k = np.argmax(intensity)
                rgb = rgb[:,k]

        color = '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        return color



    def draw(self, fig: Figure, size: Tuple[int, int]) -> None:
        """
        Draws the patch fill and shadow on an image.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            Figure to draw on
        size : Tuple[int, int]
            The size of the figure canvas in pixels
        """
        if self.shadow is not None:
            add_layer(fig, size, self.shadow, (0, 0))

        if self.fill is not None:
            add_layer(fig, size, self.fill, self.start)

        return



import types
__all__ = [name for name, thing in globals().items()
          if not (name.startswith("_") or isinstance(thing, types.ModuleType))]
del types

