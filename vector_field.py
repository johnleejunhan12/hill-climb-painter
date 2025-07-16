import numpy as np



class VectorField():
    def __init__(self, is_enabled, vector_field_function, canvas_height, canvas_width, 
                 is_custom_vector_field_center, is_middle_canvas_vector_field_center, center_x, center_y):
        # boolean flag to check if the vector field should affect rotation of rectangles
        self.is_enabled = is_enabled
        # function that maps (x,y) coordinate to vector (f(x,y), g(x,y))
        self.vector_field_function = vector_field_function

        # height and width of canvas
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width

        if is_custom_vector_field_center: # flag to translate origin of vector field to (center_x, center_y)
            self.center_x = center_x
            self.center_y = center_y
        elif is_middle_canvas_vector_field_center: # flag to translate origin of vector field to center of canvas
            self.center_x = canvas_width // 2
            self.center_y = canvas_height // 2
        else: # Keep the vector field origin the same at (0,0)
            self.center_x = 0
            self.center_y = 0


    def get_vector_field_theta(self, x, y):
        # translate (x,y) to position relative to (0,0)
        x -= self.center_x
        y -= self.center_y
        # Handle zero vector case
        if x == 0 and y == 0:
            return 0
        # Use np.arctan2 which returns the angle in range [-π, π]
        # with the correct sign based on the quadrant
        return np.arctan2(y, x)
    





# Init vector field class whose attributes are vector field equation (f(x,y),g(x,y)) translated by (center_x,center_y)
# Field equation strings are converted to code

# Create method to return theta given (x,y)

# Update the create random rect and mutate rect functions to include is_using_vector_field




