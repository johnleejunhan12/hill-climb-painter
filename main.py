import numpy as np
from matplotlib import pyplot as plt
from utilities import *
from rectangle import *

@nb.njit(cache=True)
def draw_x_intersects_on_bg_debug(background, scanline_x_intersects, poly_y_min, polygon_color, polygon_alpha):
    for i in range(scanline_x_intersects.shape[0]):
        # Get scanline x intersects
        line_start = scanline_x_intersects[i,0]
        line_end = scanline_x_intersects[i,1]
        # case where there is no intersect
        if line_start == -1 or line_end == -1:
            continue

        # Get y value of scanline
        y =  i + poly_y_min

        for x in range(line_start, line_end+1):
            # Get rgba of front pixel
            rf, gf, bf = polygon_color[0], polygon_color[1], polygon_color[2]
            af = polygon_alpha
            # Get rgba of back pixel
            rb, gb, bb, ab =  background[y, x ,0], background[y, x ,1], background[y, x ,2], background[y, x ,3]
            # If front and back alpha is both 0, the resulting alpha is zero, ignore this pixel and continue
            if af == 0 and ab == 0:
                continue
            # Find the resulting alpha value and color
            alpha = af + ab * (1 - af)
            r = (rf * af + rb*ab*(1-af)) / alpha
            g = (gf * af + gb*ab*(1-af)) / alpha
            b = (bf * af + bb*ab*(1-af)) / alpha
            # Set the background color to the new r,g,b and alpha value
            background[y, x ,0] = r
            background[y, x ,1] = g
            background[y, x ,2] = b
            background[y, x ,3] = alpha


shortest_side_px = 200
target_image_filepath = "target_image/die.png"
texture_image_filepath = "texture_image/stroke1.png"


if __name__ == "__main__":
    # Import images as numpy array
    target_rgba = get_target(target_image_filepath)
    texture_greyscale_alpha = get_texture(texture_image_filepath)

    # Get height and width of arrays
    target_height, target_width = get_height_width_of_array(target_rgba)
    texture_height, texture_width = get_height_width_of_array(texture_greyscale_alpha)

    # Create current canvas
    current_rgba = create_white_canvas(target_height, target_width, shortest_side_px)
    canvas_height, canvas_width = get_height_width_of_array(current_rgba)

    # # create a new rgba array of size (h,w,4)
    # r,g,b = 1,0,1
    # test_texture_color = np.zeros((texture_height,texture_width,4))
    # test_texture_color[:,:,0] = texture_greyscale_alpha[:,:,0] * r
    # test_texture_color[:,:,1] = texture_greyscale_alpha[:,:,0] * g
    # test_texture_color[:,:,2] = texture_greyscale_alpha[:,:,0] * b
    # test_texture_color[:,:,3] = texture_greyscale_alpha[:,:,1]
    # print_image_array(test_texture_color)
    # quit(

    # # Create random rectangle
    # rect_list = create_random_rectangle(canvas_height, canvas_width, texture_height, texture_width)
    #
    # # Get mutated copy of rectangle
    # mutated_rect_list = get_mutated_rectangle_copy(rect_list, canvas_height, canvas_width)

    print(canvas_height, canvas_width)

    mutated_rect_list = [0,0,100,200, -0.234 ]
    # Get vertices of rectangle
    rect_vertices = rectangle_to_polygon(mutated_rect_list)
    display_rectangle_vertices_debug(rect_vertices)

    y_min, y_max, scanline_x_intersects = get_y_index_bounds_and_scanline_x_intersects(rect_vertices, canvas_height, canvas_width)

    print_image_array(current_rgba)

    print(scanline_x_intersects)
    draw_x_intersects_on_bg_debug(current_rgba, scanline_x_intersects, y_min, np.array([1,0,0]), np.float32(1))
    print_image_array(current_rgba)

    # rect_list = [100, 100, 30, 60, -np.pi/3]
    # rect_vertices = rectangle_to_polygon(rect_list)
    # display_rectangle_vertices_debug(rect_vertices)


