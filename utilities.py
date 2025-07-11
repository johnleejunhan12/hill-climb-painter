import numpy as np
from PIL import Image
from matplotlib import pyplot as plt


def import_image_as_rgba(image_path):
    """
    Import a PNG/JPG image as a normalized float32 RGBA array.

    Args:
        image_path (str): Path to the image file

    Returns:
        np.ndarray: Float32 array of shape (H, W, 4) with RGBA values in range [0, 1]
                   Alpha channel is always 1.0 (composited against white background)
    """
    # Open the image
    img = Image.open(image_path)

    # Convert to RGBA mode to handle transparency
    img_rgba = img.convert('RGBA')

    # Convert to numpy array
    img_array = np.array(img_rgba, dtype=np.float32)

    # Normalize to [0, 1] range
    img_array = img_array / 255.0

    # Extract RGB and alpha channels
    rgb = img_array[:, :, :3]  # RGB channels
    alpha = img_array[:, :, 3:4]  # Alpha channel (keep as 2D with last dim)

    # Composite against white background
    # Formula: result = alpha * foreground + (1 - alpha) * background
    white_background = np.ones_like(rgb)  # White background
    composited_rgb = alpha * rgb + (1 - alpha) * white_background

    # Create output array with RGB + alpha=1
    output = np.zeros((img_array.shape[0], img_array.shape[1], 4), dtype=np.float32)
    output[:, :, :3] = composited_rgb  # RGB channels
    output[:, :, 3] = 1.0  # Alpha always 1

    return output


def import_image_as_greyscale_alpha(image_path):
    """
    Import a PNG/JPG image as a normalized float32 greyscale array with alpha.

    Args:
        image_path (str): Path to the image file

    Returns:
        np.ndarray: Float32 array of shape (H, W, 2) with greyscale and alpha values in range [0, 1]
                   Channel 0: greyscale intensity (0 if alpha is 0)
                   Channel 1: alpha channel (1.0 for opaque pixels, original alpha for transparent)
    """
    # Load grayscale
    img_gray = Image.open(image_path).convert("L")
    gray_array = np.asarray(img_gray, dtype=np.float32) / 255.0

    # Load alpha channel from RGBA
    img_rgba = Image.open(image_path).convert("RGBA")
    alpha = img_rgba.getchannel("A")
    alpha_array = np.asarray(alpha, dtype=np.float32) / 255.0

    # Mask grayscale with alpha
    gray_array *= alpha_array

    # Stack grayscale and alpha into final (H, W, 2) array
    result = np.stack([gray_array, alpha_array], axis=-1)  # shape (H, W, 2)

    return result


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