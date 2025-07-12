import numpy as np
from matplotlib import pyplot as plt
from numpy.ma.core import ones_like

from utilities import *
from rectangle import *



resize_target_shorter_side = 200
target_image_filepath = "target_image/circles.png"
texture_image_filepath = "texture_image/stroke1.png"



if __name__ == "__main__":
    # Import images as numpy array
    target_rgba = get_target(target_image_filepath, resize_target_shorter_side)
    print_image_array(target_rgba)
    texture_greyscale_alpha = get_texture(texture_image_filepath)

    # Get height and width of arrays
    texture_height, texture_width = get_height_width_of_array(texture_greyscale_alpha)

    # Create current rgba blank canvas that is fully white and opaque with same size as target_rgba
    current_rgba = ones_like(target_rgba)
    canvas_height, canvas_width = get_height_width_of_array(current_rgba)

    # Create random rectangle
    random_rect_list = create_random_rectangle(canvas_height, canvas_width, texture_height, texture_width)
    # Get its vertices and scanline x intersects
    rect_vertices = rectangle_to_polygon(random_rect_list)
    y_min, y_max, scanline_x_intersects = get_y_index_bounds_and_scanline_x_intersects(rect_vertices, canvas_height, canvas_width)
    # Find average rgba value
    rect_x_center, rect_y_center, rect_height, rect_width, rect_theta = random_rect_list
    average_rgb = get_average_rgb_value(target_rgba, texture_greyscale_alpha, scanline_x_intersects, y_min, rect_x_center, rect_y_center, rect_height, rect_width, rect_theta)
    # draw the rectangle with its average rgba value
    draw_x_intersects_on_bg_debug(current_rgba, scanline_x_intersects, y_min, average_rgb, 1)


