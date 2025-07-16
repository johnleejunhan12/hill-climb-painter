import numpy as np
from matplotlib import pyplot as plt
from numpy.ma.core import ones_like, zeros_like
from utilities import *
from rectangle import *
from pygame_display import *
from vector_field import VectorField
from output_image import CreateOutputImage
from output_gif import CreateOutputGIF
from numba_warmup import warmup_numba
import random

import cProfile
import pstats



# Hill climb parameters:
num_shapes_to_draw = 5000
min_hill_climb_iterations = 1
max_hill_climb_iterations = 50

# Rectangle parameters:
initial_random_rectangle_pixel_width = 30
is_scaling_allowed_during_mutation= True

# Parameters for target:
resize_target_shorter_side_of_target = 400

# Image output parameters:
desired_length_of_longer_side_in_output = 3840
image_name = "image_output"

# GIF output parameters:
is_create_gif = False
frames_per_second = 120
gif_name = "gif_output"


# Pygame display parameters
is_show_pygame_display_window = True
is_display_rectangle_improvement = False

# vector field parameters
is_display_target_image_to_help_find_coords = False

is_enable_vector_field = True

is_enable_custom_vector_field_center = False
field_center_x, field_center_y = 157, 168

is_translate_vector_field_origin_to_canvas_center = True

def vector_field_function(x,y):
    # Returns a vector given an x and y coordinate
    # (p, q) = (f(x,y), g(x,y))

    # Radial sink with rotational twist:

    # Set radial convergence
    a = 1
    # a<0: converge inwards
    # a=0: no convergence/divergence
    # a>0: diverge outwards

    # Set rotational behavior
    b = 5
    # b<0: clockwise
    # b=0: no rotation
    # b>0: anticlockwise

    p = a*x - b*y
    q = b*x + a*y

    return (p,q)



def main():
    warmup_numba()
    # initialize gif_creator
    gif_creator = CreateOutputGIF(fps=frames_per_second, is_create_gif=is_create_gif, gif_file_name=gif_name)

    # Import target as numpy arrays
    target_rgba = get_target(resize_target_shorter_side_of_target)

    if is_display_target_image_to_help_find_coords:
        plt.imshow(target_rgba)
        plt.show()

    
    # Import multiple texture png from texture folder into dictionary of numpy arrays in the form of
    # {
    # 0: {'texture_greyscale_alpha': texture_greyscale_alpha, 'texture_height': 385, 'texture_width': 1028}, 
    # 1: {'texture_greyscale_alpha': texture_greyscale_alpha, 'texture_height': 408, 'texture_width': 933}} 
    # }
    texture_dict, num_textures = get_texture_dict()

    # Create opaque rggba canvas of same size as target_rgba. All rgb values of blank canvas is the average rgb color of the target image
    current_rgba = np.ones(target_rgba.shape, dtype=np.float32)
    canvas_height, canvas_width = get_height_width_of_array(target_rgba)
    average_rgb = get_average_rgb_of_rgba_image(target_rgba)
    current_rgba[:,:,0:3] *= average_rgb

    # Instantiate vector field
    vector_field = VectorField(is_enable_vector_field, vector_field_function, canvas_height, canvas_width, 
                 is_enable_custom_vector_field_center, is_translate_vector_field_origin_to_canvas_center, field_center_x, field_center_y)


    # keep track of all best scoring rectangle_list and corresponding texture
    # best_rect_with_texture = []

    # initialize pygame
    pygame_display_window = PygameDisplayProcess(canvas_height, canvas_width, is_show_pygame_display_window)

    # initialize asynchronous output generator
    create_output = CreateOutputImage(texture_dict, canvas_height, canvas_width, desired_length_of_longer_side_in_output, target_rgba)

    for shape_index in range(num_shapes_to_draw):
        # choose a random texture
        texture_key = random.randint(0, num_textures - 1)
        texture_value = texture_dict[texture_key]
        texture_greyscale_alpha, texture_height, texture_width = texture_value['texture_greyscale_alpha'], texture_value['texture_height'], texture_value['texture_width']

        # Create initial random rectangle
        best_rect_list = create_random_rectangle(canvas_height, canvas_width, texture_height, texture_width,vector_field, initial_random_rectangle_pixel_width)
        
        # Score the rectangle and get the average rgb value
        highscore, rgb_of_best_rect, y_min_best, scanline_x_intersects_best = get_score_avg_rgb_ymin_and_scanline_xintersect(best_rect_list, target_rgba, texture_greyscale_alpha, current_rgba)

        # Increase the number of hill climbing iterations linearly as more textures are drawn on current_rgba canvas
        num_hill_climb_iterations = get_num_hill_climb_steps(shape_index, num_shapes_to_draw, min_hill_climb_iterations, max_hill_climb_iterations)

        # Perform hill climbing algorithm
        print(f"shape index: {shape_index:<5}  % of max iterations = {(shape_index + 1) / num_shapes_to_draw:.2f}  hill climb iterations per shape = {num_hill_climb_iterations}")
        for _ in range(num_hill_climb_iterations):
            # Mutate the rectangle
            mutated_rect_list = get_mutated_rectangle_copy(best_rect_list, canvas_height, canvas_width, vector_field, is_scaling_allowed_during_mutation)
            # Score the mutated rectangle
            new_score, rgb_of_mutated_rect, y_min_mutated, scanline_x_intersects_mutated = get_score_avg_rgb_ymin_and_scanline_xintersect(mutated_rect_list, target_rgba, texture_greyscale_alpha, current_rgba)
            # update the highscore and best_rect_list if new score is higher
            if new_score > highscore:
                highscore = new_score
                best_rect_list = mutated_rect_list
                rgb_of_best_rect = rgb_of_mutated_rect

                # Update pygame display and the gif whenever there is an improvement (Optional)
                if is_display_rectangle_improvement :
                    intermediate_canvas = draw_texture_on_canvas(texture_greyscale_alpha, current_rgba.copy(), scanline_x_intersects_mutated, y_min_mutated, rgb_of_mutated_rect, *mutated_rect_list)
                    pygame_display_window.update_display(intermediate_canvas)

                    # Dont record all intermediate frames produced so that gif will not be too large
                    if _ % 4 == 0:
                        gif_creator.enqueue_frame(intermediate_canvas)

        
        # Update current_rgba with the best rectangle texture
        update_canvas_with_best_rect(best_rect_list, target_rgba, texture_greyscale_alpha, current_rgba)

        # Enqueue to gif creator 
        gif_creator.enqueue_frame(current_rgba)

        # # Append the best rectangle list with its corresponding texture and color to the best_textured_rect
        # best_rect_with_texture.append({"best_rect_list":best_rect_list,"texture_key": texture_key, "rgb": rgb_of_best_rect})

        # Enqueue job for output image generation
        create_output.enqueue({"best_rect_list":best_rect_list,"texture_key": texture_key, "rgb": rgb_of_best_rect})

        # Update pygame display when new rectangle is drawn onto canvas
        pygame_display_window.update_display(current_rgba)

        # If pygame window is closed, terminate the outer loop and export the output prematurely
        if pygame_display_window.was_closed():
            print("User closed pygame window. Shape adding loop terminated.")
            break
    
    # End pyggame display process
    pygame_display_window.close()

    # Display the final image
    plt.imshow(current_rgba)
    plt.show()

    # Save the output using the asynchronous output generator
    output_rgba = create_output.finish()
    save_rgba_png(output_rgba, image_name)

    # Safely end process of gif_creator
    gif_creator.end_process()

if __name__ == "__main__":
    with cProfile.Profile() as profile:
        main()

    with open("profile_stats.txt", "w") as f:
        print("Logged runtime stats")
        stats = pstats.Stats(profile, stream=f)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats("main|rectangle|utilities|output_gif|output_image")


