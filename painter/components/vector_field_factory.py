"""
Vector field factory component for creating vector fields from configurations.
"""

from typing import Optional
from utils.vector_field import VectorField
from ..config import VectorFieldConfig


class VectorFieldFactory:
    """
    Factory for creating vector field objects from configuration.
    Handles the complexity of vector field creation and equation parsing.
    """
    
    def create_from_config(self, config: VectorFieldConfig, canvas_height: int, canvas_width: int) -> Optional[VectorField]:
        """
        Create a VectorField object from configuration.
        
        Args:
            config: Vector field configuration
            canvas_height: Height of the canvas
            canvas_width: Width of the canvas
            
        Returns:
            VectorField object if enabled, None otherwise
            
        Raises:
            ValueError: If vector field equations are invalid
        """
        if not config.enabled:
            return None
        
        # Create vector field function from string equations
        vector_field_function = self._create_function_from_equations(
            config.f_equation, config.g_equation
        )
        
        if vector_field_function is None:
            raise ValueError(f"Invalid vector field equations: f='{config.f_equation}', g='{config.g_equation}'")
        
        # Create and return VectorField object
        return VectorField(
            is_enabled=True,
            vector_field_function=vector_field_function,
            canvas_height=canvas_height,
            canvas_width=canvas_width,
            center_x=config.center_x,
            center_y=config.center_y
        )
    
    def _create_function_from_equations(self, f_equation: str, g_equation: str):
        """
        Create vector field function from string equations.
        
        Args:
            f_equation: String equation for f(x,y) component
            g_equation: String equation for g(x,y) component
            
        Returns:
            Vector field function or None if invalid
        """
        try:
            from user_interface.vector_field_equation_ui import VectorFieldVisualizer
            return VectorFieldVisualizer.get_function_from_string_equations(
                f_equation, g_equation
            )
        except Exception as e:
            print(f"Warning: Failed to create vector field function: {e}")
            return None
    
    def validate_equations(self, f_equation: str, g_equation: str) -> bool:
        """
        Validate vector field equations without creating the function.
        
        Args:
            f_equation: String equation for f(x,y) component
            g_equation: String equation for g(x,y) component
            
        Returns:
            True if equations are valid, False otherwise
        """
        try:
            from user_interface.vector_field_equation_ui import VectorFieldVisualizer
            function = VectorFieldVisualizer.get_function_from_string_equations(
                f_equation, g_equation
            )
            return function is not None
        except Exception:
            return False
    
    def create_default_vector_field(self, canvas_height: int, canvas_width: int, 
                                  center_x: float = 0, center_y: float = 0) -> VectorField:
        """
        Create a default vector field (radial sink).
        
        Args:
            canvas_height: Height of the canvas
            canvas_width: Width of the canvas
            center_x: X coordinate of field center
            center_y: Y coordinate of field center
            
        Returns:
            VectorField with default configuration
        """
        def default_vector_field_function(x, y):
            """Default radial sink vector field"""
            a = -1.0  # Convergence factor
            return a * x, a * y
        
        return VectorField(
            is_enabled=True,
            vector_field_function=default_vector_field_function,
            canvas_height=canvas_height,
            canvas_width=canvas_width,
            center_x=center_x,
            center_y=center_y
        )
    
    def create_from_function(self, vector_field_function, canvas_height: int, canvas_width: int,
                           center_x: float = 0, center_y: float = 0) -> VectorField:
        """
        Create vector field from an existing function.
        
        Args:
            vector_field_function: Function that takes (x, y) and returns (p, q)
            canvas_height: Height of the canvas
            canvas_width: Width of the canvas
            center_x: X coordinate of field center
            center_y: Y coordinate of field center
            
        Returns:
            VectorField object
        """
        return VectorField(
            is_enabled=True,
            vector_field_function=vector_field_function,
            canvas_height=canvas_height,
            canvas_width=canvas_width,
            center_x=center_x,
            center_y=center_y
        ) 