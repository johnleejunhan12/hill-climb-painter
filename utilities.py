import numpy as np
from PIL import Image
from matplotlib import pyplot as plt
import os
import warnings
import numba as nb

# helper functions
@nb.njit(cache=True)
def clamp_int(x, low, high):
    """
    Clamps x(int) in range [low(int), high(int)]

    Parameters:
        x: Integer to be clamped
        low: Inclusive lower bound
        high: Inclusive higher bound

    Returns:
        clamped x(int)
    """
    if x < low:
        return low
    elif x > high:
        return high
    else:
        return x



# Import image functions
def import_image_as_normalized_rgba(filepath: str) -> np.ndarray:
    """
    Reads a PNG or JPG file and returns a normalized RGBA image as a float32 numpy array.
    JPGs will have alpha=1 added, and a warning will be issued.

    Parameters:
        filepath (str): Path to the image file (.png or .jpg/.jpeg).

    Returns:
        np.ndarray: Normalized RGBA image of shape (H, W, 4), dtype np.float32.

    Raises:
        ValueError: If the file is not a PNG or JPG.
    """
    ext = os.path.splitext(filepath)[-1].lower()

    if ext == ".png":
        return import_png_as_normalized_rgba(filepath)

    elif ext in [".jpg", ".jpeg"]:
        warnings.warn("JPEG does not support alpha. An alpha channel of 1.0 will be added.")
        with Image.open(filepath) as img:
            img = img.convert("RGB")
            rgb = np.array(img).astype(np.float32) / 255.0
            h, w, _ = rgb.shape
            alpha = np.ones((h, w, 1), dtype=np.float32)
            rgba = np.concatenate([rgb, alpha], axis=-1)
            return rgba

    else:
        raise ValueError("Only PNG and JPG/JPEG files are supported.")

def import_png_as_normalized_rgba(filepath: str) -> np.ndarray:
    """
    Reads a PNG file and returns a normalized RGBA image as a float32 numpy array.

    Parameters:
        filepath (str): Path to the PNG file.

    Returns:
        np.ndarray: Normalized RGBA image of shape (H, W, 4), dtype np.float32.

    Raises:
        ValueError: If the file is not a PNG.
    """
    if not filepath.lower().endswith(".png"):
        raise ValueError("Only PNG files are supported.")

    with Image.open(filepath) as img:
        img = img.convert("RGBA")
        rgba = np.array(img).astype(np.float32) / 255.0
        return rgba

def composite_over_white(rgba: np.ndarray) -> np.ndarray:
    """
    Composites an RGBA image over a white background, ensuring resulting alpha is 1.

    Parameters:
        rgba (np.ndarray): Normalized RGBA image of shape (H, W, 4), dtype np.float32.

    Returns:
        np.ndarray: Composited RGBA image over white, with alpha=1 everywhere.
    """
    rgb = rgba[..., :3]
    alpha = rgba[..., 3:4]

    # Composite: result = alpha * fg + (1 - alpha) * white
    white_rgb = np.ones_like(rgb)
    composited_rgb = alpha * rgb + (1 - alpha) * white_rgb

    # Set alpha to 1
    composited_rgba = np.concatenate([composited_rgb, np.ones_like(alpha)], axis=-1)
    return composited_rgba

def rgba_to_grayscale_alpha(rgba: np.ndarray) -> np.ndarray:
    """
    Converts a normalized RGBA image to a (H, W, 2) array of grayscale intensity and alpha.

    Parameters:
        rgba (np.ndarray): Normalized RGBA image of shape (H, W, 4), dtype np.float32.

    Returns:
        np.ndarray: Array of shape (H, W, 2) with grayscale and alpha, dtype np.float32.

    Raises:
        ValueError: If the input is not a float32 RGBA image of shape (H, W, 4).
    """
    if rgba.ndim != 3 or rgba.shape[2] != 4:
        raise ValueError("Input must be an (H, W, 4) RGBA image.")
    if rgba.dtype != np.float32:
        raise ValueError("Input array must be of dtype np.float32.")

    r, g, b, a = rgba[..., 0], rgba[..., 1], rgba[..., 2], rgba[..., 3]
    grayscale = 0.299 * r + 0.587 * g + 0.114 * b

    grayscale_alpha = np.stack([grayscale, a], axis=-1)
    return grayscale_alpha

def get_target(filepath):
    """
    Reads a PNG or JPG file and into a normalized RGBA image as a float32 numpy array, then
    composes it over white background and return the resulting fully opaque rgba array

    Parameters:
        filepath (str): Path to the image file (.png or .jpg/.jpeg).

    Returns:
        np.ndarray: Normalized RGBA image of shape (H, W, 4), dtype np.float32.
    """
    return composite_over_white(import_image_as_normalized_rgba(filepath))

def get_texture(filepath):
    """
    Reads a PNG file and returns a normalized RGBA image as a float32 numpy array and
    converts array to a (H, W, 2) array of grayscale intensity and alpha.

    Parameters:
        filepath (str): Path to the PNG file.

    Returns:
        np.ndarray: Normalized RGBA image of shape (H, W, 2), dtype np.float32.
    """
    return rgba_to_grayscale_alpha(import_png_as_normalized_rgba(filepath))




def print_image_array(image_array, title=None):
    """
    Display an image array using matplotlib.

    Supports:
    - (H, W, 2): grayscale + alpha
    - (H, W, 3): RGB
    - (H, W, 4): RGBA

    Args:
        image_array (np.ndarray): Image array to display.
        title (str, optional): Title for the plot.
    """
    shape = image_array.shape

    if shape[-1] == 2:
        # Case 1: (H, W, 2) – grayscale + alpha
        grayscale = image_array[..., 0]
        alpha = image_array[..., 1]
        rgb = np.stack([grayscale] * 3, axis=-1)
        plt.imshow(rgb, alpha=alpha)

    elif shape[-1] == 3 or shape[-1] == 4:
        # Case 2: (H, W, 3) or (H, W, 4) – use directly
        plt.imshow(image_array)

    else:
        raise ValueError(f"Unsupported array shape: {shape}")

    if title:
        plt.title(title)
    plt.axis('off')
    plt.show()

def get_height_width_of_array(image_array):
    """
    Returns the height and width of an image array.

    Supports:
    - (H, W, 2): grayscale + alpha
    - (H, W, 3): RGB
    - (H, W, 4): RGBA

    Args:
        image_array (np.ndarray): Image array with shape (H, W, C)

    Returns:
        (int, int): height, width

    Raises:
        ValueError: If array shape is unsupported
    """
    if image_array.ndim != 3 or image_array.shape[2] not in [2, 3, 4]:
        raise ValueError(f"Unsupported array shape: {image_array.shape}")

    height, width = image_array.shape[:2]
    return int(height), int(width)

def create_white_canvas(height, width, shortest_side_px):
    """
    Creates a fully opaque white canvas as a normalized float32 RGBA NumPy array.

    The canvas size is scaled so that the shortest side equals shortest_side_px,
    and the other side is scaled proportionally to maintain aspect ratio.

    Args:
        height (int): Original height of the image.
        width (int): Original width of the image.
        shortest_side_px (int): Target size of the shortest side after scaling.

    Returns:
        np.ndarray: White canvas of shape (canvas_height, canvas_width, 4), dtype float32,
                    values in [0,1], fully opaque.
    """
    # Determine which side is shorter
    if height <= width:
        scale = shortest_side_px / height
    else:
        scale = shortest_side_px / width

    # Calculate new dimensions
    canvas_height = int(round(height * scale))
    canvas_width = int(round(width * scale))

    # Create white canvas: RGB = 1.0 (white), Alpha = 1.0 (opaque)
    canvas = np.ones((canvas_height, canvas_width, 4), dtype=np.float32)

    return canvas