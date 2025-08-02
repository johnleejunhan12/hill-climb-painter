import numpy as np



class VectorField():
    def __init__(self, is_enabled, vector_field_function, canvas_height, canvas_width, center_x, center_y):
        # boolean flag to check if the vector field should affect rotation of rectangles
        self.is_enabled = is_enabled
        # function that maps (x,y) coordinate to vector (f(x,y), g(x,y))
        self.vector_field_function = vector_field_function

        # height and width of canvas
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width

        self.center_x = center_x
        self.center_y = center_y

    def update_center(self, center_x: float, center_y: float):
        """Update vector field center coordinates for dynamic per-frame processing"""
        self.center_x = center_x
        self.center_y = center_y

    def get_vector_field_theta(self, x, y):
        # translate (x,y) to position relative to current center
        x -= self.center_x
        y -= self.center_y

        x, y = self.vector_field_function(x,y)

        # Handle zero vector case
        if x == 0 and y == 0:
            return 0
        # Use np.arctan2 which returns the angle of vector in range [-π, π]
        # with the correct sign based on the quadrant
        return np.arctan2(y, x)
    




