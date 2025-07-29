"""
Painter package for hill-climb painting algorithm.
Provides clean OOP architecture for image painting with configurable parameters.
"""

from .config import PaintingConfig
from .painting_engine import PaintingEngine
from .factory import PaintingEngineFactory
from .orchestrator import PaintingOrchestrator
from .components.image_processor import ImageProcessor
from .components.texture_manager import TextureManager
from .components.vector_field_factory import VectorFieldFactory
from .components.hill_climber import HillClimber
from .components.display_manager import DisplayManager
from .components.output_manager import OutputManager

__all__ = [
    # Main interfaces
    'PaintingOrchestrator',
    'PaintingEngine',
    'PaintingEngineFactory',
    'PaintingConfig',
    
    # Core components
    'ImageProcessor', 
    'TextureManager',
    'VectorFieldFactory',
    'HillClimber',
    'DisplayManager',
    'OutputManager'
] 