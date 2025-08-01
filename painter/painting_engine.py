"""
Main painting engine that orchestrates all components to perform the painting algorithm.
"""

import numpy as np
from typing import List, Optional, Tuple
from .config import PaintingConfig
import math
from .components.image_processor import ImageProcessor
from .components.texture_manager import TextureManager
from .components.vector_field_factory import VectorFieldFactory
from .components.hill_climber import HillClimber
from .components.display_manager import DisplayManager
from .components.output_manager import OutputManager


class PaintingEngine:
    """
    Main painting engine that coordinates all components to execute the painting algorithm.
    Provides a clean interface for painting single images or batch processing.
    """
    
    def __init__(self, config: PaintingConfig, is_multiprocessing_worker: bool = False, hill_climber: Optional['HillClimber'] = None):
        self.config = config
        self.is_multiprocessing_worker = is_multiprocessing_worker
        self.multiprocessing_enabled = config.multiprocessing.enabled
        
        # Initialize core components
        self.image_processor = ImageProcessor()
        self.texture_manager = TextureManager()
        self.vector_field_factory = VectorFieldFactory()
        
        self.hill_climber = hill_climber or HillClimber(
            config.hill_climb, 
            config.multiprocessing.enabled,
            visualization_fps=config.visualization_fps,
            gif_probability=config.gif_probability
        )
        
        # Display and output managers will be initialized per paint operation
        self.display_manager = None
        self.output_manager = None
        
        # UI parameters for configuration access (set by factory)
        self.ui_dict = None
        
        # Pre-computed frame positions for power law method
        self._power_law_frame_positions = None
    
    def paint_image(self, target_path: str, texture_paths: List[str], 
                   output_folder: str, filename: str) -> bool:
        """
        Paint a single image using the configured algorithm.
        
        Args:
            target_path: Path to target image file
            texture_paths: List of texture file paths
            output_folder: Folder to save output
            filename: Output filename
            
        Returns:
            True if painting completed successfully, False otherwise
        """
        try:
            # 1. Load and setup data
            print(f"🎨 Starting painting process for: {target_path}")
            target, canvas, texture_dict, vector_field = self._setup_painting_data(
                target_path, texture_paths
            )
            
            if target is None:
                return False
            
            # 2. Setup display and output managers
            canvas_height, canvas_width = self.image_processor.get_canvas_dimensions(target)
            
            with DisplayManager(self.config.display, canvas_height, canvas_width, self.multiprocessing_enabled) as display_mgr, \
                 OutputManager(self.config.output, self.is_multiprocessing_worker) as output_mgr:
                
                self.display_manager = display_mgr
                self.output_manager = output_mgr
                
                # Update hill climber with the managers for intermediate display updates
                self.hill_climber.display_manager = display_mgr
                self.hill_climber.output_manager = output_mgr
                
                # Setup output generators
                output_mgr.setup_output_generators(
                    texture_dict, canvas_height, canvas_width, target, 
                    self.config.image.output_image_size
                )
                
                # Configure intermediate frame skipping for power law method
                if (self.ui_dict and 
                    self.ui_dict.get("is_enable_smaller_gif_export_size", False) and 
                    self.ui_dict.get("create_gif_of_painting_progress", False) and 
                    not self.ui_dict.get("display_placement_progress", True)):
                    # Disable intermediate frame recording when power law skipping is active
                    output_mgr._skip_intermediate_frames = True
                    frame_cap = self.ui_dict.get("enable_smaller_gif_frame_cap", 40)
                    extra_frames = self.ui_dict.get("enable_smaller_gif_number_of_extra_frames_at_end", 0)
                    print(f"🎯 Power law frame skipping enabled - targeting {frame_cap} frames + {extra_frames} extra end frames, intermediate frames disabled")
                
                # 3. Execute main painting loop
                success = self._execute_painting_loop(
                    target, canvas, texture_dict, vector_field
                )
                
                if success:
                    # 4. Show final result and save outputs
                    display_mgr.show_final_image(canvas)
                    success = output_mgr.finalize_and_save(output_folder, filename)
                
                return success
                
        except Exception as e:
            if not self.multiprocessing_enabled:
                print(f"❌ Painting failed: {e}")
            return False
        finally:
            # Cleanup is handled by context managers
            self.display_manager = None
            self.output_manager = None
    
    def _setup_painting_data(self, target_path: str, texture_paths: List[str]) -> Tuple[
        Optional[np.ndarray], Optional[np.ndarray], 
        Optional[dict], Optional[object]
    ]:
        """
        Load and prepare all data needed for painting.
        
        Returns:
            Tuple of (target, canvas, texture_dict, vector_field)
        """
        try:
            # Load target image
            target = self.image_processor.load_target(target_path, self.config.image)
            if not self.multiprocessing_enabled:
                print(f"✓ Loaded target image: {target.shape}")
            
            # Create canvas
            canvas = self.image_processor.create_canvas(target)
            print(f"✓ Created canvas: {canvas.shape}")
            
            # Load textures
            texture_dict = self.texture_manager.load_textures(texture_paths, self.config.image)
            print(f"✓ Loaded {self.texture_manager.get_num_textures()} textures")
            
            # Create vector field if enabled
            vector_field = None
            if self.config.vector_field.enabled:
                canvas_height, canvas_width = self.image_processor.get_canvas_dimensions(target)
                vector_field = self.vector_field_factory.create_from_config(
                    self.config.vector_field, canvas_height, canvas_width
                )
                if vector_field:
                    print(f"✓ Created vector field: f='{self.config.vector_field.f_equation}', "
                          f"g='{self.config.vector_field.g_equation}'")
                else:
                    print("⚠ Vector field creation failed, proceeding without")
            
            return target, canvas, texture_dict, vector_field
            
        except Exception as e:
            print(f"❌ Failed to setup painting data: {e}")
            return None, None, None, None
    
    def _execute_painting_loop(self, target: np.ndarray, canvas: np.ndarray,
                              texture_dict: dict, vector_field) -> bool:
        """
        Execute the main painting loop with hill climbing optimization.
        
        Args:
            target: Target RGBA image
            canvas: Canvas to paint on
            texture_dict: Dictionary of textures
            vector_field: Optional vector field for guidance
            
        Returns:
            True if loop completed successfully, False if interrupted
        """
        try:
            total_shapes = self.config.hill_climb.num_textures
            print(f"🔄 Starting painting loop: {total_shapes} shapes to paint")
            
            for shape_index in range(total_shapes):
                # Check if user closed display window
                if self.display_manager and self.display_manager.was_closed():
                    if not self.multiprocessing_enabled:
                        print("🛑 User closed display window. Stopping painting.")
                    return True  # Consider this a successful early termination
                
                # Get random texture
                texture_key, texture_data = self.texture_manager.get_random_texture()
                
                # Print progress
                if self.display_manager and not self.multiprocessing_enabled:
                    progress = self.hill_climber.get_progress_info(shape_index)
                    self.display_manager.print_progress(
                        f"Shape {shape_index + 1}/{total_shapes} "
                        f"({progress['progress_percentage']:.1%}): "
                        f"{progress['num_iterations']} iterations planned"
                    )
                
                # Optimize shape placement
                optimization_result = self.hill_climber.optimize_shape(
                    target, texture_key, texture_data, canvas, vector_field, shape_index
                )
                
                # Apply shape to canvas
                self.hill_climber.apply_shape_to_canvas(
                    canvas, target, optimization_result, 
                    texture_data['texture_greyscale_alpha']
                )
                
                # Update displays and outputs
                if self.display_manager:
                    self.display_manager.update_display(canvas)
                
                if self.output_manager:
                    # Use conditional frame recording based on configuration
                    if self._should_record_frame(shape_index, total_shapes):
                        self.output_manager.record_frame(canvas)
                    self.output_manager.enqueue_shape_for_output(optimization_result)
            
            if not self.multiprocessing_enabled:
                print(f"✅ Painting loop completed: {total_shapes} shapes painted")
            return True
            
        except Exception as e:
            if not self.multiprocessing_enabled:
                print(f"❌ Error in painting loop: {e}")
            return False
    
    def validate_inputs(self, target_path: str, texture_paths: List[str], 
                       output_folder: str) -> List[str]:
        """
        Validate input parameters before starting painting.
        
        Args:
            target_path: Path to target image
            texture_paths: List of texture paths
            output_folder: Output folder path
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check target path
        if not target_path or not target_path.strip():
            errors.append("Target path cannot be empty")
        
        # Check texture paths
        if not texture_paths or len(texture_paths) == 0:
            errors.append("At least one texture path must be provided")
        
        # Check output folder
        if not output_folder or not output_folder.strip():
            errors.append("Output folder cannot be empty")
        
        return errors
    
    def _compute_power_law_frame_positions(self, total_shapes: int, target_frames: int, power: float = 2.5) -> set:
        """
        Pre-compute frame positions using power law distribution.
        
        Args:
            total_shapes: Total number of shapes to be painted
            target_frames: Desired number of frames (~40)
            power: Power law exponent (higher = more frames at start)
            
        Returns:
            Set of shape indices where frames should be recorded
        """
        positions = set()
        for i in range(target_frames):
            normalized = i / (target_frames - 1) if target_frames > 1 else 0
            powered = normalized ** power
            position = int(powered * (total_shapes - 1))
            positions.add(position)
        return positions
    
    def _should_record_frame_power_law(self, shape_index: int, total_shapes: int) -> bool:
        """
        Determine if current shape should be recorded using power law method.
        
        Args:
            shape_index: Current shape index (0-based)
            total_shapes: Total number of shapes
            
        Returns:
            True if frame should be recorded
        """
        # Lazy initialization of frame positions
        if self._power_law_frame_positions is None:
            target_frames = self.ui_dict.get("enable_smaller_gif_frame_cap", 40)
            self._power_law_frame_positions = self._compute_power_law_frame_positions(total_shapes, target_frames)
        
        return shape_index in self._power_law_frame_positions
    
    def _should_record_frame_power_law_with_extra_end_frames(self, shape_index: int, total_shapes: int) -> bool:
        """
        Determine if current shape should be recorded using power law method with extra end frames.
        
        Args:
            shape_index: Current shape index (0-based)
            total_shapes: Total number of shapes
            
        Returns:
            True if frame should be recorded
        """
        # First check if it's a normal power law frame
        is_power_law_frame = self._should_record_frame_power_law(shape_index, total_shapes)
        
        # Check if we should add extra frames at the end
        extra_frames_count = self.ui_dict.get("enable_smaller_gif_number_of_extra_frames_at_end", 0)
        
        if extra_frames_count > 0:
            # Record extra frames at the very end to prolong the final state
            is_in_final_frames = shape_index >= (total_shapes - extra_frames_count)
            return is_power_law_frame or is_in_final_frames
        
        return is_power_law_frame
    
    def _should_record_frame(self, shape_index: int, total_shapes: int) -> bool:
        """
        Determine if current frame should be recorded based on configuration.
        
        Args:
            shape_index: Current shape index
            total_shapes: Total number of shapes
            
        Returns:
            True if frame should be recorded
        """
        # Check conditions for smaller gif export
        if (self.ui_dict and 
            self.ui_dict.get("is_enable_smaller_gif_export_size", False) and 
            self.ui_dict.get("create_gif_of_painting_progress", False) and 
            not self.ui_dict.get("display_placement_progress", True)):
            
            # Use power law method with extra frames at end
            return self._should_record_frame_power_law_with_extra_end_frames(shape_index, total_shapes)
        
        # Default behavior: record all frames when gif creation is enabled
        return True
    
    def get_config_summary(self) -> dict:
        """
        Get a summary of current configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        return {
            'image': {
                'computation_size': self.config.image.computation_size,
                'texture_opacity': self.config.image.texture_opacity,
                'output_image_size': self.config.image.output_image_size
            },
            'hill_climb': {
                'num_textures': self.config.hill_climb.num_textures,
                'iterations_range': f"{self.config.hill_climb.min_iterations}-{self.config.hill_climb.max_iterations}",
                'allow_scaling': self.config.hill_climb.allow_scaling,
                'fail_threshold': self.config.hill_climb.fail_threshold
            },
            'vector_field': {
                'enabled': self.config.vector_field.enabled,
                'equations': f"f={self.config.vector_field.f_equation}, g={self.config.vector_field.g_equation}" if self.config.vector_field.enabled else "disabled"
            },
            'output': {
                'create_gif': self.config.output.create_progress_gif,
                'gif_name': self.config.output.gif_name if self.config.output.create_progress_gif else "none"
            }
        } 