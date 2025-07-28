"""
Factory for creating painting engines with proper dependency injection.
"""

from .config import PaintingConfig
from .painting_engine import PaintingEngine


class PaintingEngineFactory:
    """
    Factory for creating PaintingEngine instances with proper dependency injection.
    Provides different creation methods for various use cases.
    """
    
    @staticmethod
    def create_from_config(config: PaintingConfig, is_multiprocessing_worker: bool = False) -> PaintingEngine:
        """
        Create a PaintingEngine from configuration.
        
        Args:
            config: Complete painting configuration
            is_multiprocessing_worker: Whether this engine runs in a worker process
            
        Returns:
            Configured PaintingEngine instance
        """
        return PaintingEngine(config, is_multiprocessing_worker)
    
    @staticmethod
    def create_from_ui_dict(ui_dict: dict, is_gif_target: bool = False, 
                           is_multiprocessing_worker: bool = False) -> PaintingEngine:
        """
        Create a PaintingEngine directly from UI dictionary.
        
        Args:
            ui_dict: UI parameter dictionary
            is_gif_target: Whether target is a GIF file
            is_multiprocessing_worker: Whether this engine runs in a worker process
            
        Returns:
            Configured PaintingEngine instance
            
        Raises:
            ValueError: If configuration validation fails
        """
        config = PaintingConfig.from_ui_dict(ui_dict, is_gif_target)
        return PaintingEngine(config, is_multiprocessing_worker)
    
    @staticmethod
    def create_worker_engine(config_dict: dict) -> PaintingEngine:
        """
        Create a PaintingEngine for multiprocessing worker from serialized config.
        
        Args:
            config_dict: Serialized configuration dictionary
            
        Returns:
            PaintingEngine configured for worker process
        """
        config = PaintingConfig.from_serializable_dict(config_dict)
        return PaintingEngine(config, is_multiprocessing_worker=True)
    
    @staticmethod
    def create_default_engine() -> PaintingEngine:
        """
        Create a PaintingEngine with default configuration for testing.
        
        Returns:
            PaintingEngine with default settings
        """
        default_ui_dict = {
            'computation_size': 200,
            'num_textures': 50,
            'hill_climb_min_iterations': 20,
            'hill_climb_max_iterations': 50,
            'texture_opacity': 100,
            'initial_texture_width': 20,
            'uniform_texture_size': False,
            'failed_iterations_threshold': 100,
            'enable_vector_field': False,
            'vector_field_f': '',
            'vector_field_g': '',
            'vector_field_origin_shift': [[0, 0]],
            'display_painting_progress': True,
            'display_placement_progress': False,
            'display_final_image': False,
            'output_image_name': 'default_output',
            'create_gif_of_painting_progress': False,
            'painting_progress_gif_name': ''
        }
        
        return PaintingEngineFactory.create_from_ui_dict(default_ui_dict)
    
    @staticmethod
    def validate_ui_dict(ui_dict: dict, is_gif_target: bool = False) -> list:
        """
        Validate UI dictionary without creating an engine.
        
        Args:
            ui_dict: UI parameter dictionary to validate
            is_gif_target: Whether target is a GIF file
            
        Returns:
            List of validation error messages (empty if valid)
        """
        try:
            PaintingConfig.from_ui_dict(ui_dict, is_gif_target)
            return []
        except ValueError as e:
            return [str(e)] 