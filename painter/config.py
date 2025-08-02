"""
Configuration management for the painting algorithm.
Provides structured configuration objects that replace global variables.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple


@dataclass
class ImageConfig:
    """Configuration for image processing and sizing"""
    computation_size: int
    texture_opacity: int
    output_image_size: int
    
    def validate(self) -> List[str]:
        """Validate image configuration parameters"""
        errors = []
        if self.computation_size <= 10:
            errors.append("Computation size must be > 10")
        if not (1 <= self.texture_opacity <= 100):
            errors.append("Texture opacity must be between 1-100")
        if self.output_image_size <= 0:
            errors.append("Output image size must be positive")
        return errors


@dataclass  
class HillClimbConfig:
    """Configuration for hill climbing optimization"""
    num_textures: int
    min_iterations: int
    max_iterations: int
    initial_texture_width: int
    allow_scaling: bool
    fail_threshold: int
    allow_early_termination: bool
    
    def validate(self) -> List[str]:
        """Validate hill climbing configuration parameters"""
        errors = []
        if self.num_textures <= 0:
            errors.append("Number of textures must be positive")
        if self.min_iterations <= 0:
            errors.append("Min iterations must be positive")
        if self.max_iterations < self.min_iterations:
            errors.append("Max iterations must be >= min iterations")
        if self.initial_texture_width <= 0:
            errors.append("Initial texture width must be positive")
        if self.fail_threshold < 0:
            errors.append("Fail threshold must be non-negative")
        return errors


@dataclass
class VectorFieldConfig:
    """Configuration for vector field guidance"""
    enabled: bool
    f_equation: str = ""
    g_equation: str = ""
    center_x: float = 0
    center_y: float = 0
    all_frame_coordinates: Optional[List[List[float]]] = None  # [[x1,y1], [x2,y2], ...] for GIF frames
    
    def get_coordinates_for_frame(self, frame_index: int) -> Tuple[float, float]:
        """Get vector field center coordinates for specific frame"""
        if not self.all_frame_coordinates or frame_index >= len(self.all_frame_coordinates):
            return self.center_x, self.center_y
        coords = self.all_frame_coordinates[frame_index]
        if len(coords) >= 2:
            return float(coords[0]), float(coords[1])
        return self.center_x, self.center_y
    
    def validate(self) -> List[str]:
        """Validate vector field configuration"""
        errors = []
        if self.enabled:
            if not self.f_equation.strip():
                errors.append("F equation cannot be empty when vector field is enabled")
            if not self.g_equation.strip():
                errors.append("G equation cannot be empty when vector field is enabled")
        return errors


@dataclass
class DisplayConfig:
    """Configuration for display and visualization options"""
    show_pygame: bool
    show_improvements: bool
    show_final: bool
    print_progress: bool
    
    def validate(self) -> List[str]:
        """Validate display configuration"""
        # Display config rarely has validation errors
        return []


@dataclass
class OutputConfig:
    """Configuration for output generation"""
    image_name: str
    create_progress_gif: bool
    gif_name: str
    gif_fps: int
    append_datetime: bool
    
    def validate(self) -> List[str]:
        """Validate output configuration"""
        errors = []
        if not self.image_name.strip():
            errors.append("Image name cannot be empty")
        if self.create_progress_gif and not self.gif_name.strip():
            errors.append("GIF name cannot be empty when creating progress GIF")
        if self.gif_fps <= 0:
            errors.append("GIF FPS must be positive")
        return errors


@dataclass
class MultiprocessingConfig:
    """Configuration for multiprocessing options"""
    enabled: bool
    cpu_usage_percentage: float = 0.8
    
    def validate(self) -> List[str]:
        """Validate multiprocessing configuration"""
        errors = []
        if not (0.1 <= self.cpu_usage_percentage <= 1.0):
            errors.append("CPU usage percentage must be between 0.1 and 1.0")
        return errors


class PaintingConfig:
    """
    Aggregates all configuration objects and provides factory methods 
    to create configurations from UI dictionaries.
    """
    
    def __init__(self, image_config: ImageConfig, hill_climb_config: HillClimbConfig,
                 vector_field_config: VectorFieldConfig, display_config: DisplayConfig,
                 output_config: OutputConfig, multiprocessing_config: MultiprocessingConfig,
                 visualization_fps: int = 20, gif_probability: float = 0.8):
        self.image = image_config
        self.hill_climb = hill_climb_config
        self.vector_field = vector_field_config
        self.display = display_config
        self.output = output_config
        self.multiprocessing = multiprocessing_config
        self.visualization_fps = visualization_fps
        self.gif_probability = gif_probability
        
        # Validate all configurations
        self._validate_all()
    
    def _validate_all(self):
        """Validate all configuration components"""
        all_errors = []
        all_errors.extend(self.image.validate())
        all_errors.extend(self.hill_climb.validate())
        all_errors.extend(self.vector_field.validate())
        all_errors.extend(self.display.validate())
        all_errors.extend(self.output.validate())
        all_errors.extend(self.multiprocessing.validate())
        
        if all_errors:
            raise ValueError(f"Configuration validation errors: {'; '.join(all_errors)}")
    
    @classmethod
    def from_ui_dict(cls, ui_dict: Dict[str, Any], is_gif_target: bool = False) -> 'PaintingConfig':
        """
        Create PaintingConfig from UI parameter dictionary.
        
        Args:
            ui_dict: Dictionary containing UI parameters
            is_gif_target: Whether the target is a GIF (affects available parameters)
            
        Returns:
            PaintingConfig instance
        """
        image_config = cls._create_image_config(ui_dict)
        hill_climb_config = cls._create_hill_climb_config(ui_dict)
        vector_field_config = cls._create_vector_field_config(ui_dict)
        display_config = cls._create_display_config(ui_dict, is_gif_target)
        output_config = cls._create_output_config(ui_dict, is_gif_target)
        multiprocessing_config = cls._create_multiprocessing_config(ui_dict, is_gif_target)
        
        # Extract visualization parameters
        visualization_fps = ui_dict.get("intermediate_frame_generation_fps", 20)
        gif_probability = ui_dict.get("probability_of_writing_intermediate_frame_to_gif", 0.8)
        
        return cls(
            image_config, hill_climb_config, vector_field_config,
            display_config, output_config, multiprocessing_config,
            visualization_fps, gif_probability
        )
    
    @staticmethod
    def _create_image_config(ui_dict: Dict[str, Any]) -> ImageConfig:
        """Create ImageConfig from UI dictionary"""
        return ImageConfig(
            computation_size=ui_dict["computation_size"],
            texture_opacity=ui_dict["texture_opacity"],
            output_image_size=ui_dict.get("output_image_size", 1200)  # Default for GIF case
        )
    
    @staticmethod
    def _create_hill_climb_config(ui_dict: Dict[str, Any]) -> HillClimbConfig:
        """Create HillClimbConfig from UI dictionary"""
        return HillClimbConfig(
            num_textures=ui_dict["num_textures"],
            min_iterations=ui_dict["hill_climb_min_iterations"],
            max_iterations=ui_dict["hill_climb_max_iterations"],
            initial_texture_width=ui_dict["initial_texture_width"],
            allow_scaling=not ui_dict["uniform_texture_size"],  # UI uses inverse logic
            fail_threshold=ui_dict["failed_iterations_threshold"],
            allow_early_termination=ui_dict.get("allow_early_termination", False)
        )
    
    @staticmethod
    def _create_vector_field_config(ui_dict: Dict[str, Any]) -> VectorFieldConfig:
        """Create VectorFieldConfig from UI dictionary"""
        coordinates = ui_dict.get("vector_field_origin_shift", [[0, 0]])
        
        # Safely extract first coordinate for backward compatibility
        center_x, center_y = 0, 0
        if coordinates and len(coordinates) > 0 and len(coordinates[0]) >= 2:
            center_x, center_y = coordinates[0][0], coordinates[0][1]
        
        return VectorFieldConfig(
            enabled=ui_dict["enable_vector_field"],
            f_equation=ui_dict.get("vector_field_f", ""),
            g_equation=ui_dict.get("vector_field_g", ""),
            center_x=float(center_x),
            center_y=float(center_y),
            all_frame_coordinates=coordinates  # Store all coordinates for per-frame processing
        )
    
    @staticmethod
    def _create_display_config(ui_dict: Dict[str, Any], is_gif_target: bool) -> DisplayConfig:
        """Create DisplayConfig from UI dictionary"""
        # Disable printing when multiprocessing is enabled (checked below)
        multiprocessing_enabled = ui_dict.get("enable_multiprocessing", False) if is_gif_target else False
        
        return DisplayConfig(
            show_pygame=ui_dict.get("display_painting_progress", False) and not is_gif_target,
            show_improvements=ui_dict.get("display_placement_progress", False) and not is_gif_target,
            show_final=ui_dict.get("display_final_image", True) and not is_gif_target,
            print_progress=ui_dict.get("print_progress", True) and not multiprocessing_enabled
        )
    
    @staticmethod
    def _create_output_config(ui_dict: Dict[str, Any], is_gif_target: bool) -> OutputConfig:
        """Create OutputConfig from UI dictionary"""
        if is_gif_target:
            return OutputConfig(
                image_name=ui_dict.get("painted_gif_name", "painted_gif_output"),
                create_progress_gif=False,  # Disabled for GIF targets
                gif_name="",
                gif_fps=100,  # Default
                append_datetime=False  # Default
            )
        else:
            return OutputConfig(
                image_name=ui_dict.get("output_image_name", "image_output"),
                create_progress_gif=ui_dict.get("create_gif_of_painting_progress", False),
                gif_name=ui_dict.get("painting_progress_gif_name", ""),
                gif_fps=100,  # Default, not typically in UI
                append_datetime=False  # Default, not typically in UI
            )
    
    @staticmethod
    def _create_multiprocessing_config(ui_dict: Dict[str, Any], is_gif_target: bool) -> MultiprocessingConfig:
        """Create MultiprocessingConfig from UI dictionary"""
        return MultiprocessingConfig(
            enabled=ui_dict.get("enable_multiprocessing", False) if is_gif_target else False,
            cpu_usage_percentage=0.8  # Default
        )
    
    def to_serializable_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a serializable dictionary for multiprocessing.
        This allows passing config data between processes without pickle issues.
        """
        return {
            'image': {
                'computation_size': self.image.computation_size,
                'texture_opacity': self.image.texture_opacity,
                'output_image_size': self.image.output_image_size
            },
            'hill_climb': {
                'num_textures': self.hill_climb.num_textures,
                'min_iterations': self.hill_climb.min_iterations,
                'max_iterations': self.hill_climb.max_iterations,
                'initial_texture_width': self.hill_climb.initial_texture_width,
                'allow_scaling': self.hill_climb.allow_scaling,
                'fail_threshold': self.hill_climb.fail_threshold,
                'allow_early_termination': self.hill_climb.allow_early_termination
            },
            'vector_field': {
                'enabled': self.vector_field.enabled,
                'f_equation': self.vector_field.f_equation,
                'g_equation': self.vector_field.g_equation,
                'center_x': self.vector_field.center_x,
                'center_y': self.vector_field.center_y,
                'all_frame_coordinates': self.vector_field.all_frame_coordinates
            },
            'display': {
                'show_pygame': self.display.show_pygame,
                'show_improvements': self.display.show_improvements,
                'show_final': self.display.show_final,
                'print_progress': self.display.print_progress
            },
            'output': {
                'image_name': self.output.image_name,
                'create_progress_gif': self.output.create_progress_gif,
                'gif_name': self.output.gif_name,
                'gif_fps': self.output.gif_fps,
                'append_datetime': self.output.append_datetime
            },
            'multiprocessing': {
                'enabled': self.multiprocessing.enabled,
                'cpu_usage_percentage': self.multiprocessing.cpu_usage_percentage
            },
            'visualization': {
                'fps': self.visualization_fps,
                'gif_probability': self.gif_probability
            }
        }
    
    @classmethod
    def from_serializable_dict(cls, data: Dict[str, Any]) -> 'PaintingConfig':
        """Recreate PaintingConfig from serializable dictionary"""
        image_config = ImageConfig(**data['image'])
        hill_climb_config = HillClimbConfig(**data['hill_climb'])
        vector_field_config = VectorFieldConfig(**data['vector_field'])
        display_config = DisplayConfig(**data['display'])
        output_config = OutputConfig(**data['output'])
        multiprocessing_config = MultiprocessingConfig(**data['multiprocessing'])
        
        # Extract visualization parameters with defaults for backwards compatibility
        visualization_data = data.get('visualization', {})
        visualization_fps = visualization_data.get('fps', 20)
        gif_probability = visualization_data.get('gif_probability', 0.8)
        
        return cls(
            image_config, hill_climb_config, vector_field_config,
            display_config, output_config, multiprocessing_config,
            visualization_fps, gif_probability
        ) 