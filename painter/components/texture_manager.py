"""
Texture management component for loading and organizing textures.
"""

import random
from typing import Dict, List, Tuple, Any
from utils.utilities import get_texture_dict
from ..config import ImageConfig


class TextureManager:
    """
    Manages texture loading, organization, and selection.
    Encapsulates texture-related operations that were previously scattered.
    """
    
    def __init__(self):
        self._texture_dict = None
        self._num_textures = 0
    
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