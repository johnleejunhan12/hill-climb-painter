"""
Texture management component for loading and organizing textures.
"""

import random
import concurrent.futures
import os
import numpy as np
from typing import Dict, List, Tuple, Any
from utils.utilities import get_texture_dict, import_image_as_normalized_rgba_fast
from ..config import ImageConfig


class TextureManager:
    """
    Manages texture loading, organization, and selection.
    Encapsulates texture-related operations that were previously scattered.
    """
    
    def __init__(self, max_workers: int = 4):
        self._texture_dict = None
        self._num_textures = 0
        self.max_workers = max_workers  # For parallel loading
    
    def load_textures_fast(self, texture_paths: List[str], opacity: int) -> Dict[int, Dict[str, Any]]:
        """
        Load textures using parallel processing for improved performance.
        
        Args:
            texture_paths: List of texture file paths
            opacity: Texture opacity percentage (1-100)
            
        Returns:
            Dictionary mapping indices to texture data
        """
        if not texture_paths:
            raise ValueError("No texture paths provided")
        
        texture_dict = {}
        
        # Use ThreadPoolExecutor for I/O bound operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all loading tasks
            future_to_index = {
                executor.submit(self._load_single_texture_fast, path, opacity): i 
                for i, path in enumerate(texture_paths)
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    texture_data = future.result()
                    if texture_data is not None:
                        texture_dict[index] = texture_data
                except Exception as e:
                    print(f"Warning: Failed to load texture {texture_paths[index]}: {e}")
        
        self._texture_dict = texture_dict
        self._num_textures = len(texture_dict)
        
        if self._num_textures == 0:
            raise ValueError("No textures loaded successfully")
        
        print(f"✓ Fast loaded {self._num_textures} textures using {self.max_workers} threads")
        return texture_dict
    
    def _load_single_texture_fast(self, filepath: str, opacity: int) -> Dict[str, Any]:
        """
        Load a single texture file with optimization.
        
        Args:
            filepath: Path to texture file
            opacity: Opacity percentage
            
        Returns:
            Texture data dictionary or None if failed
        """
        try:
            if not os.path.exists(filepath):
                return None
            
            # Load image using fast method
            texture_rgba = import_image_as_normalized_rgba_fast(filepath)
            
            # Apply opacity
            opacity_factor = opacity / 100.0
            texture_rgba[:, :, 3] *= opacity_factor
            
            # Convert to grayscale+alpha format expected by the painter
            grayscale = 0.299 * texture_rgba[:, :, 0] + 0.587 * texture_rgba[:, :, 1] + 0.114 * texture_rgba[:, :, 2]
            texture_greyscale_alpha = np.stack([grayscale, texture_rgba[:, :, 3]], axis=-1)
            
            return {
                'texture_greyscale_alpha': texture_greyscale_alpha,
                'texture_height': texture_rgba.shape[0],
                'texture_width': texture_rgba.shape[1]
            }
            
        except Exception as e:
            print(f"Error loading texture {filepath}: {e}")
            return None
    
    def load_textures(self, texture_paths: List[str], config: ImageConfig) -> Dict[int, Dict[str, Any]]:
        """
        Load textures from file paths into organized dictionary.
        
        Args:
            texture_paths: List of paths to texture files
            config: Image configuration containing opacity settings
            
        Returns:
            Dictionary mapping texture indices to texture data:
            {
                0: {'texture_greyscale_alpha': array, 'texture_height': int, 'texture_width': int},
                1: {'texture_greyscale_alpha': array, 'texture_height': int, 'texture_width': int},
                ...
            }
            
        Raises:
            ValueError: If no textures found or loading fails
        """
        try:
            # Use existing utility function but adapt for file paths if needed
            self._texture_dict, self._num_textures = get_texture_dict(config.texture_opacity)
            
            if self._num_textures == 0:
                raise ValueError("No texture files found or loaded successfully")
            
            return self._texture_dict
            
        except Exception as e:
            raise ValueError(f"Failed to load textures: {e}")
    
    def load_textures_from_paths(self, texture_paths: List[str], opacity: int) -> Dict[int, Dict[str, Any]]:
        """
        Load textures from specific file paths.
        This is an alternative method for when we have explicit paths rather than using a folder.
        
        Args:
            texture_paths: List of texture file paths
            opacity: Texture opacity percentage (1-100)
            
        Returns:
            Texture dictionary similar to load_textures()
            
        Raises:
            ValueError: If no valid textures found
        """
        # TODO: Implement direct path loading if needed
        # For now, delegate to existing function that scans texture folder
        return self.load_textures(texture_paths, ImageConfig(200, opacity, 1200))
    
    def get_random_texture(self) -> Tuple[int, Dict[str, Any]]:
        """
        Get a random texture from loaded textures.
        
        Returns:
            Tuple of (texture_key, texture_data)
            
        Raises:
            RuntimeError: If no textures have been loaded
        """
        if self._texture_dict is None or self._num_textures == 0:
            raise RuntimeError("No textures loaded. Call load_textures() first.")
        
        texture_key = random.randint(0, self._num_textures - 1)
        texture_data = self._texture_dict[texture_key]
        
        return texture_key, texture_data
    
    def get_texture_by_key(self, key: int) -> Dict[str, Any]:
        """
        Get specific texture by its key.
        
        Args:
            key: Texture key/index
            
        Returns:
            Texture data dictionary
            
        Raises:
            KeyError: If texture key doesn't exist
            RuntimeError: If no textures loaded
        """
        if self._texture_dict is None:
            raise RuntimeError("No textures loaded. Call load_textures() first.")
        
        if key not in self._texture_dict:
            raise KeyError(f"Texture key {key} not found")
        
        return self._texture_dict[key]
    
    def get_texture_info(self, key: int) -> Tuple[Any, int, int]:
        """
        Get texture information in format expected by existing code.
        
        Args:
            key: Texture key/index
            
        Returns:
            Tuple of (texture_greyscale_alpha, texture_height, texture_width)
        """
        texture_data = self.get_texture_by_key(key)
        return (
            texture_data['texture_greyscale_alpha'],
            texture_data['texture_height'],
            texture_data['texture_width']
        )
    
    def get_num_textures(self) -> int:
        """
        Get the number of loaded textures.
        
        Returns:
            Number of textures
        """
        return self._num_textures
    
    def get_texture_dict(self) -> Dict[int, Dict[str, Any]]:
        """
        Get the complete texture dictionary.
        
        Returns:
            Complete texture dictionary
            
        Raises:
            RuntimeError: If no textures loaded
        """
        if self._texture_dict is None:
            raise RuntimeError("No textures loaded. Call load_textures() first.")
        
        return self._texture_dict
    
    def is_loaded(self) -> bool:
        """
        Check if textures have been loaded.
        
        Returns:
            True if textures are loaded, False otherwise
        """
        return self._texture_dict is not None and self._num_textures > 0 