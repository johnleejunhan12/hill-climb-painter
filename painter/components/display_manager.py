"""
Display management component for handling visualization during painting.
"""

import numpy as np
from typing import Optional
from utils.pygame_display import PygameDisplayProcess
from ..config import DisplayConfig


class DisplayManager:
    """
    Manages display and visualization during the painting process.
    Handles pygame display windows and matplotlib final image display.
    """
    
    def __init__(self, config: DisplayConfig, canvas_height: int, canvas_width: int):
        self.config = config
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.pygame_display = None
        self._initialize_displays()
    
    def _initialize_displays(self):
        """Initialize display components based on configuration"""
        if self.config.show_pygame:
            try:
                self.pygame_display = PygameDisplayProcess(
                    self.canvas_height, 
                    self.canvas_width, 
                    True  # is_show_display
                )
            except Exception as e:
                print(f"Warning: Failed to initialize pygame display: {e}")
                self.pygame_display = None
    
    def update_display(self, canvas: np.ndarray):
        """
        Update the pygame display with current canvas state.
        
        Args:
            canvas: Current canvas RGBA array to display
        """
        if self.pygame_display is not None:
            try:
                self.pygame_display.update_display(canvas)
            except Exception as e:
                print(f"Warning: Failed to update pygame display: {e}")
    
    def update_intermediate_display(self, canvas: np.ndarray):
        """
        Update display with intermediate optimization results.
        Only updates if show_improvements is enabled.
        
        Args:
            canvas: Intermediate canvas state to display
        """
        if self.config.show_improvements and self.pygame_display is not None:
            self.update_display(canvas)
    
    def show_final_image(self, canvas: np.ndarray):
        """
        Show final painted image using matplotlib.
        
        Args:
            canvas: Final canvas RGBA array to display
        """
        if self.config.show_final:
            try:
                from matplotlib import pyplot as plt
                plt.imshow(canvas)
                plt.title("Final Painted Image")
                plt.axis('off')
                plt.show()
            except Exception as e:
                print(f"Warning: Failed to show final image: {e}")
    
    def was_closed(self) -> bool:
        """
        Check if the pygame window was closed by user.
        
        Returns:
            True if window was closed, False otherwise
        """
        if self.pygame_display is not None:
            return self.pygame_display.was_closed()
        return False
    
    def close(self):
        """Close all display windows and cleanup resources"""
        if self.pygame_display is not None:
            try:
                self.pygame_display.close()
            except Exception as e:
                print(f"Warning: Error closing pygame display: {e}")
            finally:
                self.pygame_display = None
    
    def print_progress(self, message: str):
        """
        Print progress message if enabled.
        
        Args:
            message: Progress message to print
        """
        if self.config.print_progress:
            print(message)
    
    def is_display_active(self) -> bool:
        """
        Check if any display is currently active.
        
        Returns:
            True if pygame display is active, False otherwise
        """
        return self.pygame_display is not None
    
    def supports_improvements(self) -> bool:
        """
        Check if intermediate improvements should be displayed.
        
        Returns:
            True if improvement display is enabled, False otherwise
        """
        return self.config.show_improvements and self.is_display_active()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.close() 