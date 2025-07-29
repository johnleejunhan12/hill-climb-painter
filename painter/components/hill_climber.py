"""
Hill climbing optimization component for shape placement and optimization.
"""

import random
import numpy as np
from typing import Optional, Tuple, Dict, Any, List
from utils.rectangle import (
    create_random_rectangle, 
    get_mutated_rectangle_copy,
    get_score_avg_rgb_ymin_and_scanline_xintersect,
    update_canvas_with_best_rect,
    draw_texture_on_canvas
)
from utils.utilities import get_num_hill_climb_steps
from utils.vector_field import VectorField
from ..config import HillClimbConfig
from dataclasses import dataclass

# Forward declaration to avoid circular imports
if False:
    from .display_manager import DisplayManager
    from .output_manager import OutputManager


class ShapeOptimizationResult:
    """Result of optimizing a single shape"""
    def __init__(self, best_rect_list: list, texture_key: int, rgb: np.ndarray, 
                 score: float, iterations_performed: int, converged: bool):
        self.best_rect_list = best_rect_list
        self.texture_key = texture_key
        self.rgb = rgb
        self.score = score
        self.iterations_performed = iterations_performed
        self.converged = converged


class HillClimber:
    """
    Hill climbing optimization for shape placement and refinement.
    Encapsulates the iterative optimization logic that was in the main loop.
    """
    
    def __init__(self, config: HillClimbConfig, multiprocessing_enabled: bool = False, 
                 display_manager: Optional['DisplayManager'] = None,
                 output_manager: Optional['OutputManager'] = None,
                 visualization_fps: int = 30,
                 gif_probability: float = 0.8):
        self.config = config
        self.multiprocessing_enabled = multiprocessing_enabled
        self.display_manager = display_manager
        self.output_manager = output_manager
        # Track last update time for frame rate limiting
        self._last_intermediate_update_time = 0.0
        # Configurable visualization frame rate
        self.visualization_fps = visualization_fps
        self.min_interval = 1.0 / max(1, visualization_fps)  # Prevent division by zero
        # Configurable GIF recording probability
        self.gif_probability = gif_probability
    
    def optimize_shape(self, target: np.ndarray, texture_key: int, texture_data: Dict[str, Any],
                      canvas: np.ndarray, vector_field: Optional[VectorField], 
                      shape_index: int) -> ShapeOptimizationResult:
        """
        Optimize placement and properties of a single shape using hill climbing.
        
        Args:
            target: Target RGBA image array
            texture_key: Key identifying the texture to use
            texture_data: Dictionary containing texture information
            canvas: Current canvas state
            vector_field: Optional vector field for guidance
            shape_index: Index of current shape (for iteration scaling)
            
        Returns:
            ShapeOptimizationResult containing optimization results
        """
        # Extract texture information
        texture_greyscale_alpha = texture_data['texture_greyscale_alpha']
        texture_height = texture_data['texture_height']
        texture_width = texture_data['texture_width']
        
        # Get canvas dimensions
        canvas_height, canvas_width = canvas.shape[:2]
        
        # Create initial random rectangle
        best_rect_list = create_random_rectangle(
            canvas_height, canvas_width, texture_height, texture_width,
            vector_field, self.config.initial_texture_width
        )
        
        # Score the initial rectangle
        highscore, rgb_of_best_rect, y_min_best, scanline_x_intersects_best = \
            get_score_avg_rgb_ymin_and_scanline_xintersect(
                best_rect_list, target, texture_greyscale_alpha, canvas
            )
        
        # Calculate number of iterations for this shape
        num_iterations = get_num_hill_climb_steps(
            shape_index, self.config.num_textures,
            self.config.min_iterations, self.config.max_iterations
        )
        
        # Perform hill climbing optimization
        optimization_result = self._perform_hill_climbing(
            best_rect_list, highscore, rgb_of_best_rect,
            target, texture_greyscale_alpha, canvas, vector_field,
            canvas_height, canvas_width, num_iterations
        )
        
        return ShapeOptimizationResult(
            best_rect_list=optimization_result['best_rect'],
            texture_key=texture_key,
            rgb=optimization_result['best_rgb'],
            score=optimization_result['best_score'],
            iterations_performed=optimization_result['iterations'],
            converged=optimization_result['converged']
        )
    
    def _perform_hill_climbing(self, initial_rect: list, initial_score: float, initial_rgb: np.ndarray,
                              target: np.ndarray, texture_greyscale_alpha: np.ndarray, 
                              canvas: np.ndarray, vector_field: Optional[VectorField],
                              canvas_height: int, canvas_width: int, max_iterations: int) -> Dict[str, Any]:
        """
        Perform the hill climbing optimization iterations.
        
        Returns:
            Dictionary containing optimization results
        """
        best_rect_list = initial_rect
        highscore = initial_score
        rgb_of_best_rect = initial_rgb
        fail_count = 0
        iterations_performed = 0
        
        for iteration in range(max_iterations):
            iterations_performed = iteration + 1
            
            # Check for early termination (only if enabled)
            if self.config.allow_early_termination and fail_count > self.config.fail_threshold:
                if not self.multiprocessing_enabled:
                    print(f"Early termination at iteration {iteration} (fail_count: {fail_count})")
                break
            
            # Mutate the rectangle
            mutated_rect_list = get_mutated_rectangle_copy(
                best_rect_list, canvas_height, canvas_width, 
                vector_field, self.config.allow_scaling
            )
            
            # Score the mutated rectangle
            new_score, rgb_of_mutated_rect, y_min_mutated, scanline_x_intersects_mutated = \
                get_score_avg_rgb_ymin_and_scanline_xintersect(
                    mutated_rect_list, target, texture_greyscale_alpha, canvas
                )
            
            # Update if improvement found
            if new_score > highscore:
                highscore = new_score
                best_rect_list = mutated_rect_list
                rgb_of_best_rect = rgb_of_mutated_rect
                fail_count = 0  # Reset fail count on improvement
                
                # Rate-limited intermediate visualization (configurable FPS for smooth updates)
                import time
                current_time = time.time()
                
                should_update_display = (current_time - self._last_intermediate_update_time) >= self.min_interval
                
                # Create intermediate canvas for visualization (if needed)
                intermediate_canvas = None
                if should_update_display and ((self.display_manager and self.display_manager.supports_improvements()) or self.output_manager):
                    intermediate_canvas = self.create_intermediate_canvas(
                        canvas, mutated_rect_list, texture_greyscale_alpha, 
                        rgb_of_mutated_rect, y_min_mutated, scanline_x_intersects_mutated
                    )
                    self._last_intermediate_update_time = current_time
                
                # Show intermediate optimization progress if enabled
                if should_update_display and self.display_manager and self.display_manager.supports_improvements():
                    self.display_manager.update_intermediate_display(intermediate_canvas)
                
                # Record intermediate frames for GIF with configurable probability
                if should_update_display and self.output_manager and intermediate_canvas is not None:
                    self.output_manager.record_intermediate_frame(intermediate_canvas, probability=self.gif_probability)
            else:
                fail_count += 1
        
        return {
            'best_rect': best_rect_list,
            'best_rgb': rgb_of_best_rect,
            'best_score': highscore,
            'iterations': iterations_performed,
            'converged': self.config.allow_early_termination and fail_count > self.config.fail_threshold
        }
    
    def apply_shape_to_canvas(self, canvas: np.ndarray, target: np.ndarray,
                             optimization_result: ShapeOptimizationResult,
                             texture_greyscale_alpha: np.ndarray) -> np.ndarray:
        """
        Apply the optimized shape to the canvas.
        
        Args:
            canvas: Current canvas to modify
            target: Target image for reference
            optimization_result: Result from optimize_shape()
            texture_greyscale_alpha: Texture data
            
        Returns:
            Updated canvas with shape applied
        """
        update_canvas_with_best_rect(
            optimization_result.best_rect_list,
            target,
            texture_greyscale_alpha,
            canvas
        )
        return canvas
    
    def create_intermediate_canvas(self, canvas: np.ndarray, rect_list: list,
                                  texture_greyscale_alpha: np.ndarray, rgb: np.ndarray,
                                  y_min: int, scanline_x_intersects: np.ndarray) -> np.ndarray:
        """
        Create intermediate canvas for visualization during optimization.
        
        Args:
            canvas: Base canvas
            rect_list: Rectangle parameters
            texture_greyscale_alpha: Texture data
            rgb: RGB color values
            y_min: Minimum Y coordinate
            scanline_x_intersects: X intersection data
            
        Returns:
            Canvas with shape temporarily applied
        """
        return draw_texture_on_canvas(
            texture_greyscale_alpha, canvas.copy(), scanline_x_intersects,
            y_min, rgb, *rect_list
        )
    
    def get_progress_info(self, shape_index: int) -> Dict[str, Any]:
        """
        Get progress information for current shape.
        
        Args:
            shape_index: Index of current shape
            
        Returns:
            Dictionary with progress information
        """
        progress_percentage = (shape_index + 1) / self.config.num_textures
        num_iterations = get_num_hill_climb_steps(
            shape_index, self.config.num_textures,
            self.config.min_iterations, self.config.max_iterations
        )
        
        return {
            'shape_index': shape_index,
            'progress_percentage': progress_percentage,
            'num_iterations': num_iterations,
            'total_shapes': self.config.num_textures
        }
    
    def should_print_progress(self) -> bool:
        """Check if progress should be printed"""
        return True  # Hill climber always prints critical information 