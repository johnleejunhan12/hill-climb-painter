"""
Image processing component for loading targets and creating canvases.
"""

import numpy as np
from typing import Tuple
from utils.utilities import get_target_image_as_rgba, get_height_width_of_array, get_average_rgb_of_rgba_image
from ..config import ImageConfig


class ImageProcessor:
    """
    Handles image loading, resizing, and canvas creation.
    Encapsulates image processing operations that were previously global functions.
    """
    
    def load_target(self, filepath: str, config: ImageConfig) -> np.ndarray:
        """
        Load and resize target image for painting.
        
        Args:
            filepath: Path to target image file
            config: Image configuration containing computation size
            
        Returns:
            Normalized RGBA image as numpy array of shape (H, W, 4)
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image format is unsupported
        """
        try:
            target_rgba = get_target_image_as_rgba(filepath, config.computation_size)
            return target_rgba
        except Exception as e:
            raise ValueError(f"Failed to load target image from {filepath}: {e}")
    
    def create_canvas(self, target: np.ndarray) -> np.ndarray:
        """
        Create a blank canvas with the same dimensions as target, 
        filled with the target's average color.
        
        Args:
            target: Target RGBA image array
            
        Returns:
            Canvas RGBA array initialized with target's average color
        """
        # Create opaque canvas of same size as target
        canvas = np.ones(target.shape, dtype=np.float32)
        
        # Fill with average color of target
        average_rgb = get_average_rgb_of_rgba_image(target)
        canvas[:, :, 0:3] *= average_rgb
        
        return canvas
    
    def get_canvas_dimensions(self, target: np.ndarray) -> Tuple[int, int]:
        """
        Get canvas height and width from target image.
        
        Args:
            target: Target RGBA image array
            
        Returns:
            Tuple of (height, width)
        """
        return get_height_width_of_array(target)
    
    def validate_image_array(self, image: np.ndarray) -> bool:
        """
        Validate that image array has correct format.
        
        Args:
            image: Image array to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(image, np.ndarray):
            return False
        
        if len(image.shape) != 3:
            return False
        
        if image.shape[2] != 4:  # Must be RGBA
            return False
        
        if image.dtype != np.float32:
            return False
        
        return True 