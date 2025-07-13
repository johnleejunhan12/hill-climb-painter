import numpy as np
from matplotlib import pyplot as plt
from numpy.ma.core import ones_like, zeros_like

from utilities import *
from rectangle import *



resize_target_shorter_side = 200
target_image_filepath = "target_image/circles.png"
texture_image_filepath = "texture_image/stroke3.png"

texture_greyscale_alpha = get_texture(texture_image_filepath)


def test_texture_coloring(texture_filepath, rgb = (1,0,1)):
    texture_greyscale_alpha = get_texture(texture_filepath)
    texture_height, texture_width = get_height_width_of_array(texture_greyscale_alpha)
    greyscale = texture_greyscale_alpha[:,:,0]
    alpha = texture_greyscale_alpha[:,:,1]
    new = np.zeros((texture_height,texture_width, 4))
    new[:,:,0] = rgb[0] * greyscale
    new[:,:,1] = rgb[1] * greyscale
    new[:,:,2] = rgb[2] * greyscale
    new[:,:,3] = alpha
    return new


# rgb = (1,0,0)
# stroke1 = test_texture_coloring("texture_image/stroke1.png", rgb)
# stroke2 = test_texture_coloring("texture_image/stroke3.png", rgb)
# stroke3 = test_texture_coloring("texture_image/what.png", rgb)
# fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 5))
#
# ax1.imshow(stroke1)
# ax1.axis('off')
#
# ax2.imshow(stroke2)
# ax2.axis('off')
#
# ax3.imshow(stroke3)
# ax3.axis('off')
#
# plt.tight_layout()
# plt.show()


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
    average_rgb = get_average_rgb_value(target_rgba, texture_greyscale_alpha, scanline_x_intersects, y_min, *random_rect_list)
    # draw the rectangle with its average rgba value
    draw_x_intersects_on_bg_debug(current_rgba, scanline_x_intersects, y_min, average_rgb, 1)


