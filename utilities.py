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


def resize_rgba(rgba_array, resize_shortest_side=200):
    """
    Resize an RGBA image array while preserving aspect ratio.

    Parameters:
        rgba_array (numpy.ndarray): Normalized RGBA image of shape (H, W, 4), dtype np.float32.
        resize_shortest_side (int):  optional target size for the shortest side of the image (default: 200)

    Returns:
        numpy.ndarray: Resized RGBA array with preserved aspect ratio
    """
    if rgba_array.ndim != 3 or rgba_array.shape[2] != 4:
        raise ValueError("Input array must have shape (h, w, 4)")

    h, w = rgba_array.shape[:2]

    # Calculate the scale factor based on the shortest side
    if h < w:
        scale_factor = resize_shortest_side / h
    else:
        scale_factor = resize_shortest_side / w

    # Calculate new dimensions
    new_h = int(h * scale_factor)
    new_w = int(w * scale_factor)

    # Convert normalized array to 8-bit for PIL
    rgba_uint8 = (rgba_array * 255).astype(np.uint8)

    # Create PIL Image from array
    pil_image = Image.fromarray(rgba_uint8, mode='RGBA')

    # Resize using PIL's high-quality Lanczos resampling
    resized_pil = pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Convert back to normalized numpy array
    resized_array = np.array(resized_pil).astype(np.float32) / 255.0

    return resized_array

def get_target(filepath, resize_shorter_side):
    """
    Reads a PNG or JPG file and into a normalized RGBA image as a float32 numpy array, then
    composes it over white background and return the resulting fully opaque rgba array

    Parameters:
        filepath (str): Path to the image file (.png or .jpg/.jpeg).

    Returns:
        np.ndarray: Normalized RGBA image of shape (H, W, 4), dtype np.float32.
    """
    target = composite_over_white(import_image_as_normalized_rgba(filepath))
    resized_target = resize_rgba(target, resize_shortest_side=resize_shorter_side)
    return resized_target

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

