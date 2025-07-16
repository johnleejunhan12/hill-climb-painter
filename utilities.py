import numpy as np
from PIL import Image
import os
import warnings
import numba as nb
from matplotlib import pyplot as plt

# function to find number of hill climbing steps
def get_num_hill_climb_steps(iteration_index, num_shapes_to_draw, min_hill_climb_iterations, max_hill_climb_iterations):
    return max(int((iteration_index + 1)/num_shapes_to_draw * max_hill_climb_iterations), min_hill_climb_iterations)

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

# Export image functions 
def save_rgba_png(rgba_array, filename):
    """
    Save a normalized RGBA numpy array as a PNG file in the output folder.
    
    Parameters:
        rgba_array (np.ndarray): A numpy array of shape (height, width, 4) with
                                dtype=np.float32, values normalized to [0, 1]
        filename (str): Name of the output PNG file (with or without .png extension)
    """
    # Create output folder if it doesn't exist
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Add .png extension if not present
    if not filename.endswith('.png'):
        filename += '.png'
    
    # # Construct full output path
    full_output_path = os.path.join(output_dir, filename)
    
    # Convert normalized float32 array to uint8 (0-255 range)
    rgba_uint8 = (rgba_array * 255).astype(np.uint8)
    
    # Create PIL Image from array and save
    image = Image.fromarray(rgba_uint8, mode='RGBA')
    image.save(full_output_path)
    
    print(f"Image saved to: {full_output_path}")

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


def get_target(resize_target_shorter_side_of_target=200):
    """
    Uses the first jpg or png file found as target image
    Raises a warning if multiple images are in the folder
    Stops the script if there is no target image

    Parameters:
        resize_shortest_side (int):  optional target size for the shortest side of the image (default: 200)
    Returns:
        np.ndarray: Normalized RGBA image of shape (H, W, 4), dtype np.float32.
        
    """
    allowed_exts = ('.png', '.jpg')
    matches = []
    folder_path = "target"
    multiple_images_found = False
    with os.scandir(folder_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.lower().endswith(allowed_exts):
                matches.append(entry.name)
                if len(matches) > 1:
                    multiple_images_found = True
                    break  # Early exit after second match
    
    if not matches:
        warnings.warn("No PNG or JPG file found in target folder.")
        quit()

    # Take the first match as filepath
    filepath = "target\\" + matches[0]

    if multiple_images_found:
        warnings.warn(f"Multiple PNG or JPG files found in target folder. Using {filepath} as target image.")


    target = composite_over_white(import_image_as_normalized_rgba(filepath))
    resized_target = resize_rgba(target, resize_shortest_side=resize_target_shorter_side_of_target)
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


def get_texture_dict():
    """
    Imports all texture pngs from texture folder into greyscale alpha format and returns a dictionary containing numpy array and dimensions

    Returns:
        texture_dict (dict): 
        Example
        {
            0: {'texture_greyscale_alpha': texture_greyscale_alpha, 'texture_height': 385, 'texture_width': 1028}, 
            1: {'texture_greyscale_alpha': texture_greyscale_alpha, 'texture_height': 408, 'texture_width': 933}}
        }
        Note that texture_greyscale_alpha (np.ndarray) is Array of shape (H, W, 2) representing normalised grayscale and alpha, dtype np.float32.

        num_textures (int):
            number of textures in the folder
    """
    texture_dict = {}
    for i, filename in enumerate(os.listdir("texture")):
        texture_filepath = os.path.join("texture", filename)
        texture_greyscale_alpha = get_texture(texture_filepath)
        texture_height, texture_width = texture_greyscale_alpha.shape[0], texture_greyscale_alpha.shape[1]
        texture_dict[i] = {"texture_greyscale_alpha":texture_greyscale_alpha, 
                        "texture_height":texture_height, 
                        "texture_width":texture_width}
    num_textures = len(texture_dict)
    return texture_dict, num_textures


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



def get_average_rgb_of_rgba_image(rgba_image):
    """
    Compute the average RGB color of an RGBA image.
    
    Parameters:
        rgba_image (np.ndarray): Normalized RGBA image array of shape (h, w, 4)
                                with dtype np.float32 and values in [0, 1]
    
    Returns:
        np.ndarray: Average RGB color as a float32 array of length 3
    """
    # Extract RGB channels (ignore alpha channel)
    rgb_image = rgba_image[:, :, :3]
    
    # Compute mean across height and width dimensions
    avg_rgb = np.mean(rgb_image, axis=(0, 1))
    
    # Ensure output is float32
    return avg_rgb.astype(np.float32)

