import numpy as np
from PIL import Image
import glob
import os
import re
import warnings
import numba as nb
from matplotlib import pyplot as plt
from datetime import datetime
import shutil
from pathlib import Path


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
def save_rgba_array_as_png(rgba_array, name_of_png, output_full_folder_path, is_append_datetime=True):
    """
    Save a normalized RGBA numpy array as a PNG file in the specified folder.
         
    Parameters:
        rgba_array (np.ndarray): A numpy array of shape (height, width, 4) with
                                dtype=np.float32, values normalized to [0, 1]
        name_of_png (str): Name of the output PNG file (with or without .png extension)
        output_full_folder_path (str): The folder path where the PNG should be saved
        is_append_datetime (bool): If True, appends datetime to filename to ensure uniqueness.
                               If False, uses original filename and overwrites existing files.
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_full_folder_path, exist_ok=True)
         
    # Remove .png extension if present to work with base name
    if name_of_png.endswith('.png'):
        base_name = name_of_png[:-4]
    else:
        base_name = name_of_png
         
    # Generate final filename based on append_datetime setting
    if is_append_datetime:
        # Generate timestamp string (YYYYMMDD_HHMMSS_microseconds)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_filename = f"{base_name}_{timestamp}.png"
    else:
        # Use original filename (will overwrite if exists)
        final_filename = base_name + '.png'
         
    # Construct full output path
    full_output_path = os.path.join(output_full_folder_path, final_filename)
         
    # Convert normalized float32 array to uint8 (0-255 range)
    rgba_uint8 = (rgba_array * 255).astype(np.uint8)
         
    # Create PIL Image from array and save
    image = Image.fromarray(rgba_uint8, mode='RGBA')
    image.save(full_output_path)

    print(f"png file saved to {full_output_path}")
    
    

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
        # warnings.warn("JPEG does not support alpha. An alpha channel of 1.0 will be added.")
        print(f"JPG does not support alpha. An alpha channel of 1.0 will be added.")
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


def get_target_image_as_rgba(filepath, resize_target_shorter_side_of_target=200):
    """
    Loads and processes a single target image from the specified filepath
    
    Parameters:
        filepath (str): Path to the PNG or JPG image file (must include extension)
        resize_target_shorter_side_of_target (int): Optional target size for the shortest side of the image (default: 200)
    
    Returns:
        np.ndarray: Normalized RGBA image of shape (H, W, 4), dtype np.float32.
    
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        ValueError: If the file extension is not .png or .jpg
    """
    allowed_exts = ('.png', '.jpg', '.jpeg')
    
    # Check if file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Check file extension
    if not filepath.lower().endswith(allowed_exts):
        raise ValueError(f"File must have .png, .jpg, or .jpeg extension. Got: {filepath}")
    
    # Process the image
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



def create_gif_from_pngs(png_filepath: str, export_gif_full_file_path: str, frames_per_second: float = 10.0, file_name: str = "output.gif") -> str:
    """
    Reads all PNG files in a specified directory and creates an animated GIF.
    
    Args:
        png_filepath (str): Directory path containing PNG files to be converted
        export_gif_full_file_path (str): Full directory path where the GIF will be saved
        frames_per_second (float): Frame rate for the GIF animation (default: 10.0)
        file_name (str): Output filename for the GIF (with or without .gif extension)
    
    Returns:
        str: Full path to the created GIF file
    
    Raises:
        FileNotFoundError: If the specified PNG directory doesn't exist
        ValueError: If no PNG files are found in the directory, or if export directory doesn't exist or is invalid
        Exception: If there's an error creating the GIF
    """

    def natural_sort_key(s):
        """
        Key function for natural sorting (alphanumeric order).
        """
        return [int(text) if text.isdigit() else text.lower() 
                for text in re.split('([0-9]+)', s)]
        
    # Validate input directory containing PNG files
    if not os.path.exists(png_filepath):
        raise FileNotFoundError(f"PNG directory '{png_filepath}' does not exist")
    
    if not os.path.isdir(png_filepath):
        raise ValueError(f"'{png_filepath}' is not a directory")
    
    # Find all PNG files in the directory
    png_pattern = os.path.join(png_filepath, "*.png")
    png_files = glob.glob(png_pattern)
    
    if not png_files:
        raise ValueError(f"No PNG files found in directory '{png_filepath}'")
    
    # Sort files using natural (alphanumeric) sorting
    png_files.sort(key=natural_sort_key)
    
    # Ensure file_name has .gif extension
    if not file_name.lower().endswith('.gif'):
        file_name += '.gif'
    
    # Validate export directory
    if not os.path.exists(export_gif_full_file_path):
        raise FileNotFoundError(f"Export directory '{export_gif_full_file_path}' does not exist")
    if not os.path.isdir(export_gif_full_file_path):
        raise ValueError(f"'{export_gif_full_file_path}' is not a directory")
    
    # Create full output path
    output_path = os.path.join(export_gif_full_file_path, file_name)
    
    try:
        # Load all PNG images
        images = []
        for png_file in png_files:
            img = Image.open(png_file)
            # Convert to RGB if necessary (GIF doesn't support RGBA)
            if img.mode in ('RGBA', 'LA'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            images.append(img)
        
        # Calculate duration per frame in milliseconds
        duration_ms = int(1000 / frames_per_second)
        
        # Create and save GIF
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            duration=duration_ms,
            loop=0,  # 0 means infinite loop
            optimize=True
        )
        
        print(f"GIF created successfully: {output_path}")
        print(f"Total frames: {len(images)}")
        print(f"Frame rate: {frames_per_second} FPS")
        print(f"Duration per frame: {duration_ms} ms")
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Error creating GIF: {str(e)}")



def extract_gif_frames_to_output_folder_and_get_approx_fps(full_path_to_gif, max_number_of_extracted_frames, output_folder):
    """
    Extract frames from a GIF file and save them as PNG files in an a specified output folder.
    Returns either the original FPS (if all frames are extracted) or an approximate FPS (if frames are reduced).
    
    Args:
        full_path_to_gif (str): Full path to the GIF file (must have .gif extension)
        max_number_of_extracted_frames (int): Maximum number of frames to extract (should be greater than 1 if not error is raised)
        outut_folder (str):  Full path to the output folder (assume that output folder already exists and is empty)
        
    Returns:
        fps_info (float): Original FPS if all frames extracted, otherwise approximate FPS
    """
    # Validate input parameter
    if max_number_of_extracted_frames <= 1:
        raise ValueError("max_number_of_extracted_frames should be greater than one")

    
    # Initialize variables
    original_fps = None
    approximate_fps = None
    total_frames = 0
    
    # Check if input GIF exists
    if not os.path.exists(full_path_to_gif):
        raise FileNotFoundError(f"Error: GIF file '{full_path_to_gif}' not found.")
    
    try:
        # Open the GIF file
        with Image.open(full_path_to_gif) as gif:
            # Count total frames
            try:
                while True:
                    gif.seek(total_frames)
                    total_frames += 1
            except EOFError:
                pass
            # Raise error if the number of frames is zero
            if total_frames == 0:
                raise ValueError("Total frames of gif is zero")
            else:
                print(f"Number of frames in GIF: {total_frames}")
            
            # Get original FPS information
            gif.seek(0)
            duration = gif.info.get('duration', 100)  # Default to 100ms if not specified
            original_fps = 1000 / duration  # Convert milliseconds to FPS
            print(f"Original GIF FPS: {original_fps:.2f}")

            # Determine which frames to extract
            if total_frames <= max_number_of_extracted_frames:
                frames_to_extract = list(range(total_frames))
                # Return original FPS since we're keeping all frames
                fps_to_return = original_fps
            else:
                frames_to_extract = []
                step = (total_frames - 1) / (max_number_of_extracted_frames - 1)
                
                for i in range(max_number_of_extracted_frames):
                    frame_index = round(i * step)
                    frames_to_extract.append(frame_index)
                
                # Ensure unique frame indices
                frames_to_extract = list(set(frames_to_extract))
                frames_to_extract.sort()
                
                # Fill with remaining frames if needed
                if len(frames_to_extract) < max_number_of_extracted_frames:
                    remaining_frames = [i for i in range(total_frames) if i not in frames_to_extract]
                    frames_to_extract.extend(remaining_frames[:max_number_of_extracted_frames - len(frames_to_extract)])
                    frames_to_extract.sort()
                
                # Calculate approximate FPS (original FPS * reduction factor)
                reduction_factor = len(frames_to_extract) / total_frames
                approximate_fps = original_fps * reduction_factor
                print(f"Approximate FPS with reduced frames: {approximate_fps:.2f}")
                fps_to_return = approximate_fps
            
            # Extract and save frames
            base_name = os.path.splitext(os.path.basename(full_path_to_gif))[0]
            extracted_count = 0
            
            for frame_index in frames_to_extract:
                try:
                    gif.seek(frame_index)
                    frame = gif.copy()
                    
                    # Convert to RGB if necessary
                    if frame.mode != 'RGB':
                        frame = frame.convert('RGB')
                    
                    # Create PNG filename and path
                    png_filename = f"{base_name}_frame_{frame_index:04d}.png"
                    png_path = os.path.join(output_folder, png_filename)
                    
                    # Save frame as PNG
                    frame.save(png_path, 'PNG')
                    extracted_count += 1
                    
                except Exception as e:
                    print(f"Error extracting frame {frame_index}: {e}")
            
            print(f"Successfully extracted {extracted_count} frames to '{output_folder}'")
            
    except Exception as e:
        print(f"Error processing GIF file: {e}")
        quit()
    
    return fps_to_return


def get_target_full_filepath():
    """
    Returns the full filepath of the item in target folder and a boolean flag to determine if item has a .gif extension
    A folder called target is created if it does not already exist, and error will be raised since the target folder is empty

    Error will be raised if:
        1) Target folder is empty
        2) Target folder contains more than one item 
        3) The item does not have a '.png', '.jpg', '.jpeg', '.gif' extension

    Returns:
        file_path (str): Full filepath of the target png/jpg/jpeg/gif
        is_gif (bool): Flag to indicate that the target has .gif extension
    """

    # Define the target folder path
    target_folder = os.path.join(os.getcwd(), 'target')
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif'}
    
    # Check if target folder exists, if not create it
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Get all items in the target folder
    items = [f for f in os.listdir(target_folder) if not f.startswith('.')]  # ignore hidden files

    # Raise error if there are no items found
    if items == []:
        raise FileNotFoundError("No image or gif in target folder")


    # Check number of items in the folder
    if len(items) != 1:
        raise ValueError("Multiple targets detected, please put single image or gif file")
    
    # Get the single file
    file_name = items[0]
    file_path = os.path.join(target_folder, file_name)
    file_extension = Path(file_name).suffix.lower()
    
    # Check file extension
    if file_extension not in allowed_extensions:
        raise ValueError("invalid image/gif extension")
    
    # Determine if the file is a gif
    is_gif = (file_extension == '.gif')
    
    return file_path, is_gif


def get_output_folder_full_filepath():
    """
    Gets the full filepath of the "output" folder in the current working directory.
    Creates the folder if it does not already exist.
    
    Returns:
        str: Full absolute path to the output folder
    """
    import os
    
    # Get the current working directory
    current_dir = os.getcwd()
    
    # Create the full path to the output folder
    output_folder = os.path.join(current_dir, "output")
    
    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    return output_folder

