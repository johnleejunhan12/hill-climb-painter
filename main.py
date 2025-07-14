import numpy as np
from matplotlib import pyplot as plt
from numpy.ma.core import ones_like, zeros_like
from utilities import *
from rectangle import *
from numba_warmup import warmup_numba

import cProfile
import pstats


# Hill climb parameters:
num_shapes_to_draw = 1000
min_hill_climb_iterations = 50
max_hill_climb_iterations = 500

# Rectangle parameters:
initial_random_rectangle_pixel_width = 50

# Parameters for target:
target_image_filepath = "target_image/rainy_street.jpg"
resize_target_shorter_side_of_target = 500

# Parameters for texture:
texture_image_filepath = "texture_image/stroke3.png"


# Texture debug functions
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

def debug_texture_color():
    rgb = (1,0,0)
    stroke1 = test_texture_coloring("texture_image/stroke1.png", rgb)
    stroke2 = test_texture_coloring("texture_image/stroke3.png", rgb)
    stroke3 = test_texture_coloring("texture_image/what.png", rgb)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 5))

    ax1.imshow(stroke1)
    ax1.axis('off')

    ax2.imshow(stroke2)
    ax2.axis('off')

    ax3.imshow(stroke3)
    ax3.axis('off')

    plt.tight_layout()
    plt.show()


def debugging():
    resize_target_shorter_side = 200
    initial_random_rectangle_width = 50
    target_image_filepath = "target_image/circles.png"
    texture_image_filepath = "texture_image/what.png"

    # Import images as numpy array
    target_rgba = get_target(target_image_filepath, resize_target_shorter_side_of_target)
    #### print_image_array(target_rgba)
    texture_greyscale_alpha = get_texture(texture_image_filepath)

    # Get height and width of arrays
    texture_height, texture_width = get_height_width_of_array(texture_greyscale_alpha)

    # Create current rgba blank canvas that is fully white and opaque with same size as target_rgba
    current_rgba = np.ones(target_rgba.shape, dtype=np.float32)
    canvas_height, canvas_width = get_height_width_of_array(current_rgba)

    # Create random rectangle
    random_rect_list = create_random_rectangle(canvas_height, canvas_width, texture_height, texture_width,
                                               initial_random_rectangle_pixel_width)

    #### random_rect_list = [450,250, 200, 300, -0.1]
    # Get its vertices and scanline x intersects
    rect_vertices = rectangle_to_polygon(random_rect_list)
    y_min, y_max, scanline_x_intersects = get_y_index_bounds_and_scanline_x_intersects(rect_vertices, canvas_height,
                                                                                       canvas_width)
    # Find average rgba value
    average_rgb = get_average_rgb_value(target_rgba, texture_greyscale_alpha, scanline_x_intersects, y_min,
                                        *random_rect_list)

    ##### draw the rectangle with its average rgba value
    draw_x_intersects_on_bg_debug(current_rgba, scanline_x_intersects, y_min, average_rgb, 1)

    # Score how well the rectangle fits
    rect_score = get_score_of_rectangle(target_rgba, texture_greyscale_alpha, current_rgba, scanline_x_intersects,
                                        y_min,
                                        average_rgb, *random_rect_list)
    print(rect_score)

    # Draw the best rectangle onto the canvas
    draw_texture_on_canvas(texture_greyscale_alpha, current_rgba, scanline_x_intersects, y_min, average_rgb,
                           *random_rect_list)

    print_image_array(current_rgba)




def main():
    warmup_numba()

    # Import texture and target as numpy arrays
    target_rgba = get_target(target_image_filepath, resize_target_shorter_side_of_target)
    texture_greyscale_alpha = get_texture(texture_image_filepath)

    # Get height and width of arrays
    texture_height, texture_width = get_height_width_of_array(texture_greyscale_alpha)

    # Create current rgba blank canvas that is fully white and opaque with same size as target_rgba
    current_rgba = np.ones(target_rgba.shape, dtype=np.float32)
    canvas_height, canvas_width = get_height_width_of_array(current_rgba)

    # keep track of all best scoring rectangle_list
    best_rect = []

    for shape_index in range(num_shapes_to_draw):
        # Create initial random rectangle
        best_rect_list = create_random_rectangle(canvas_height, canvas_width, texture_height, texture_width,
                                                initial_random_rectangle_pixel_width)
        # Score the rectangle
        highscore = find_score_rect_list(best_rect_list, target_rgba, texture_greyscale_alpha, current_rgba)

        # Increase the number of hill climbing iterations linearly as more textures are drawn on current_rgba canvas
        num_hill_climb_iterations = get_num_hill_climb_steps(shape_index, num_shapes_to_draw, min_hill_climb_iterations, max_hill_climb_iterations)

        # Perform hill climbing algorithm
        print(f"shape index: {shape_index:<5}  % of max iterations = {(shape_index + 1) / num_shapes_to_draw:.2f}  num iterations per shape = {num_hill_climb_iterations}")
        for i in range(num_hill_climb_iterations):
            # Mutate the rectangle
            mutated_rect_list = get_mutated_rectangle_copy(best_rect_list, canvas_height, canvas_width)
            #### print(mutated_rect_list)
            # Score the mutated rectangle
            new_score = find_score_rect_list(mutated_rect_list, target_rgba, texture_greyscale_alpha, current_rgba)

            # update the highscore and best_rect_list if new score is higher
            if new_score > highscore:
                highscore = new_score
                best_rect_list = mutated_rect_list
        
        # Update current_rgba with the best rectangle texture
        update_canvas_with_best_rect(best_rect_list, target_rgba, texture_greyscale_alpha, current_rgba)

        # Append the best rectangle to the best_rect_list
        best_rect.append(best_rect_list)

    plt.imshow(current_rgba)
    plt.show()


if __name__ == "__main__":
    with cProfile.Profile() as profile:
        main()

    with open("profile_stats.txt", "w") as f:
        stats = pstats.Stats(profile, stream=f)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats("main|rectangle|utilities")