"""
Output management component for handling image and GIF generation.
"""

import numpy as np
from typing import Optional, Dict, Any
from utils.create_painted_png import CreateOutputImage
from utils.create_paint_progress_gif import CreateOutputGIF
from utils.utilities import save_rgba_array_as_png
from ..config import OutputConfig


class OutputManager:
    """
    Manages output generation including final images and progress GIFs.
    Coordinates between high-resolution image creation and progress recording.
    """
    
    def __init__(self, config: OutputConfig, is_multiprocessing_worker: bool = False):
        self.config = config
        self.is_multiprocessing_worker = is_multiprocessing_worker
        self.gif_creator = None
        self.image_creator = None
        self._initialized = False
    
    def setup_output_generators(self, texture_dict: Dict[int, Dict[str, Any]], 
                               canvas_height: int, canvas_width: int, 
                               target: np.ndarray, output_image_size: int):
        """
        Setup output generators for image and GIF creation.
        
        Args:
            texture_dict: Dictionary of loaded textures
            canvas_height: Height of the canvas
            canvas_width: Width of the canvas
            target: Target RGBA image array
            output_image_size: Desired size of output image longer side
        """
        try:
            # Setup GIF creator if enabled and not in multiprocessing worker
            if (self.config.create_progress_gif and 
                not self.is_multiprocessing_worker and 
                self.config.gif_name.strip()):
                
                self.gif_creator = CreateOutputGIF(
                    fps=self.config.gif_fps,
                    is_create_gif=True,
                    gif_file_name=self.config.gif_name
                )
            
            # Setup high-resolution image creator
            # Use synchronous mode if in multiprocessing worker to avoid conflicts
            use_worker_process = not self.is_multiprocessing_worker
            
            self.image_creator = CreateOutputImage(
                texture_dict=texture_dict,
                original_height=canvas_height,
                original_width=canvas_width,
                desired_length_of_longer_side=output_image_size,
                target_rgba=target,
                use_worker_process=use_worker_process
            )
            
            self._initialized = True
            
        except Exception as e:
            raise RuntimeError(f"Failed to setup output generators: {e}")
    
    def record_frame(self, canvas: np.ndarray):
        """
        Record current canvas state for progress GIF.
        
        Args:
            canvas: Current canvas RGBA array
        """
        if self.gif_creator is not None:
            try:
                self.gif_creator.enqueue_frame(canvas)
            except Exception as e:
                if not self.is_multiprocessing_worker:
                    print(f"Warning: Failed to record GIF frame: {e}")
    
    def record_intermediate_frame(self, canvas: np.ndarray, probability: float = 0.25):
        """
        Record intermediate frame with given probability to avoid GIF bloat.
        
        Args:
            canvas: Intermediate canvas state
            probability: Probability of recording this frame (0.0 to 1.0)
        """
        if self.gif_creator is not None:
            import random
            if random.random() < probability:
                self.record_frame(canvas)
    
    def enqueue_shape_for_output(self, optimization_result) -> bool:
        """
        Enqueue optimized shape for high-resolution output image.
        
        Args:
            optimization_result: Result from HillClimber.optimize_shape()
            
        Returns:
            True if successfully enqueued, False otherwise
        """
        if not self._initialized or self.image_creator is None:
            return False
        
        try:
            job = {
                "best_rect_list": optimization_result.best_rect_list,
                "texture_key": optimization_result.texture_key,
                "rgb": optimization_result.rgb
            }
            self.image_creator.enqueue(job)
            return True
        except Exception as e:
            if not self.is_multiprocessing_worker:
                print(f"Warning: Failed to enqueue shape for output: {e}")
            return False
    
    def finalize_and_save(self, output_folder: str, filename: str) -> bool:
        """
        Finalize all output generation and save results.
        
        Args:
            output_folder: Folder to save output files
            filename: Base filename for output
            
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        try:
            # Finalize and save high-resolution image
            if self.image_creator is not None:
                output_rgba = self.image_creator.finish()
                save_rgba_array_as_png(
                    output_rgba, 
                    filename, 
                    output_folder, 
                    is_append_datetime=self.config.append_datetime
                )
                print(f"✓ Saved high-resolution image: {filename}")
            
            # Finalize GIF creation
            if self.gif_creator is not None:
                self.gif_creator.end_process()
                print(f"✓ Saved progress GIF: {self.config.gif_name}")
                
        except Exception as e:
            print(f"Error finalizing output: {e}")
            success = False
        finally:
            self.cleanup()
        
        return success
    
    def cleanup(self):
        """Clean up all output generators and resources"""
        try:
            if self.gif_creator is not None:
                self.gif_creator.end_process()
                self.gif_creator = None
            
            if self.image_creator is not None:
                # Image creator cleanup is handled by its own context management
                self.image_creator = None
                
            self._initialized = False
            
        except Exception as e:
            print(f"Warning: Error during output cleanup: {e}")
    
    def is_ready(self) -> bool:
        """
        Check if output manager is ready for use.
        
        Returns:
            True if properly initialized, False otherwise
        """
        return self._initialized and self.image_creator is not None
    
    def should_create_gif(self) -> bool:
        """
        Check if GIF creation is enabled and configured.
        
        Returns:
            True if GIF should be created, False otherwise
        """
        return (self.config.create_progress_gif and 
                not self.is_multiprocessing_worker and
                self.config.gif_name.strip() != "")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.cleanup() 