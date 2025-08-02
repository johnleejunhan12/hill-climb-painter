from PIL import Image, ImageEnhance
import os
import numpy as np
from numba import jit

@jit(nopython=True)
def rgb_to_hsv_array(rgb_array):
    """
    Convert RGB array to HSV using numba for speed.
    Input: RGB array of shape (height, width, 3) with values 0-255
    Output: HSV array of shape (height, width, 3) with H: 0-360, S,V: 0-100
    """
    h, w, _ = rgb_array.shape
    hsv_array = np.zeros_like(rgb_array, dtype=np.float32)
    
    for i in range(h):
        for j in range(w):
            r, g, b = rgb_array[i, j] / 255.0
            
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            diff = max_val - min_val
            
            # Value
            v = max_val * 100
            
            # Saturation
            if max_val == 0:
                s = 0
            else:
                s = (diff / max_val) * 100
            
            # Hue
            if diff == 0:
                h_val = 0
            elif max_val == r:
                h_val = (60 * ((g - b) / diff) + 360) % 360
            elif max_val == g:
                h_val = (60 * ((b - r) / diff) + 120) % 360
            else:  # max_val == b
                h_val = (60 * ((r - g) / diff) + 240) % 360
            
            hsv_array[i, j, 0] = h_val
            hsv_array[i, j, 1] = s
            hsv_array[i, j, 2] = v
    
    return hsv_array


@jit(nopython=True)
def hsv_to_rgb_array(hsv_array):
    """
    Convert HSV array to RGB using numba for speed.
    Input: HSV array of shape (height, width, 3) with H: 0-360, S,V: 0-100
    Output: RGB array of shape (height, width, 3) with values 0-255
    """
    h, w, _ = hsv_array.shape
    rgb_array = np.zeros_like(hsv_array, dtype=np.uint8)
    
    for i in range(h):
        for j in range(w):
            h_val, s, v = hsv_array[i, j]
            s = s / 100.0
            v = v / 100.0
            
            c = v * s
            x = c * (1 - abs(((h_val / 60) % 2) - 1))
            m = v - c
            
            if 0 <= h_val < 60:
                r, g, b = c, x, 0
            elif 60 <= h_val < 120:
                r, g, b = x, c, 0
            elif 120 <= h_val < 180:
                r, g, b = 0, c, x
            elif 180 <= h_val < 240:
                r, g, b = 0, x, c
            elif 240 <= h_val < 300:
                r, g, b = x, 0, c
            else:  # 300 <= h_val < 360
                r, g, b = c, 0, x
            
            rgb_array[i, j, 0] = int((r + m) * 255)
            rgb_array[i, j, 1] = int((g + m) * 255)
            rgb_array[i, j, 2] = int((b + m) * 255)
    
    return rgb_array


@jit(nopython=True)
def shift_hue_array(hsv_array, hue_shift_degrees):
    """
    Shift hue values in HSV array using numba for speed.
    """
    h, w, _ = hsv_array.shape
    shifted_array = hsv_array.copy()
    
    for i in range(h):
        for j in range(w):
            # Shift hue and wrap around 0-360 range
            new_h = (hsv_array[i, j, 0] + hue_shift_degrees) % 360
            shifted_array[i, j, 0] = new_h
    
    return shifted_array


def hue_shift(image, hue_shift_degrees):
    """
    Shift the hue of an image by the specified degrees using numba-accelerated functions.
    
    Args:
        image: PIL Image object
        hue_shift_degrees: Degrees to shift hue (0-360)
    
    Returns:
        PIL Image with shifted hue
    """
    # Convert PIL image to numpy array
    rgb_array = np.array(image)
    
    # Convert to HSV using numba
    hsv_array = rgb_to_hsv_array(rgb_array)
    
    # Shift hue using numba
    shifted_hsv = shift_hue_array(hsv_array, hue_shift_degrees)
    
    # Convert back to RGB using numba
    shifted_rgb = hsv_to_rgb_array(shifted_hsv)
    
    # Convert back to PIL Image
    return Image.fromarray(shifted_rgb)


def create_gif_from_image(image_path, num_frames, fps, scale=1.0):
    """
    Creates a GIF with N identical frames from a single image.
    
    Args:
        image_path (str): Path to the input image file
        num_frames (int): Number of identical frames in the GIF
        fps (int): Frames per second for the GIF
        scale (float): Scale factor for resizing (1.0 = original size, 0.5 = half size, etc.)
    
    Returns:
        str: Path to the created GIF file
    """
    try:
        # Open the input image
        img = Image.open(image_path)
        
        # Convert to RGB if necessary (GIF supports RGB and P modes)
        if img.mode not in ['RGB', 'P']:
            img = img.convert('RGB')
        
        # Scale the image if scale factor is not 1.0
        if scale != 1.0:
            new_width = int(img.width * scale)
            new_height = int(img.height * scale)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        print(f"Creating {num_frames} rainbow frames...")
        
        # Create frames with rainbow hue shifts
        frames = []
        for i in range(num_frames):
            # Calculate hue shift for this frame (full 360° rotation across all frames)
            hue_shift_degrees = (i * 360) / num_frames
            
            # Create frame with shifted hue (numba-accelerated)
            shifted_frame = hue_shift(img, hue_shift_degrees)
            frames.append(shifted_frame)
            
            # Progress indicator
            if (i + 1) % max(1, num_frames // 10) == 0:
                print(f"  Generated frame {i + 1}/{num_frames}")
        
        # Get the original filename without extension
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Create output filename in the current working directory
        if scale != 1.0:
            output_path = f"{base_name}_{num_frames}frames_{fps}fps_scale{scale}_rainbow.gif"
        else:
            output_path = f"{base_name}_{num_frames}frames_{fps}fps_rainbow.gif"
        
        # Calculate duration per frame in milliseconds
        duration_ms = int(1000 / fps)
        
        # Save as GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration_ms,
            loop=0  # 0 means infinite loop
        )
        
        print(f"GIF created successfully: {output_path}")
        return output_path
        
    except FileNotFoundError:
        print(f"Error: Image file '{image_path}' not found.")
        return None
    except Exception as e:
        print(f"Error creating GIF: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    # Example: create a 60-frame rainbow GIF at 15 FPS scaled to 50% size
    # Note: First run will be slower due to numba compilation, subsequent runs much faster
    print("Note: First run will compile numba functions and be slower.")
    gif_path = create_gif_from_image("rainy_street.jpg", 100, 15, scale=0.5)
    if gif_path:
        print(f"Rainbow GIF saved as: {gif_path}")