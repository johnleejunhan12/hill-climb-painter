"""
Core components for the painting algorithm.
Each component handles a specific aspect of the painting process.
"""

from .image_processor import ImageProcessor
from .texture_manager import TextureManager
from .vector_field_factory import VectorFieldFactory
from .hill_climber import HillClimber
from .display_manager import DisplayManager
from .output_manager import OutputManager

__all__ = [
    'ImageProcessor',
    'TextureManager', 
    'VectorFieldFactory',
    'HillClimber',
    'DisplayManager',
    'OutputManager'
] 