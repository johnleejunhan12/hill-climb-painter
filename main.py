import numpy as np
from matplotlib import pyplot as plt
from numpy.ma.core import ones_like, zeros_like
from utilities import *
from rectangle import *
from pygame_display import *
from file_operations import *
from select_coordinate_ui import CoordinateSelectorUI
from vector_field import VectorField
from output_image import CreateOutputImage
from output_gif import CreateOutputGIF
from numba_warmup import warmup_numba
import random

import cProfile
import pstats


# Hill climb parameters:
is_print_hill_climb_progress = False
num_shapes_to_draw = 1000
min_hill_climb_iterations = 1
max_hill_climb_iterations = 50

is_prematurely_terminate_hill_climbing_if_stuck_in_local_minima = True
fail_threshold_before_terminating_hill_climb = 100

# Rectangle parameters:
initial_random_rectangle_pixel_width = 20
is_scaling_allowed_during_mutation= True

# Parameters for target:
resize_target_shorter_side_of_target = 300

# Image output parameters:
desired_length_of_longer_side_in_output = 1200
image_name = "image_output"
is_display_final_image = False
is_append_datetime = False # add date and time at the end of image_name

# Multiprocessing flag for batch frame processing
default_is_enable_multiprocessing = True
is_enable_multiprocessing_for_batch_frame_processing = default_is_enable_multiprocessing

# Top-level worker function for multiprocessing (must be at module scope for Windows compatibility)
def paint_worker(args):
    idx, png_full_file_path, painted_gif_frames_full_folder_path, coordinates = args
    if is_enable_vector_field and coordinates is not None:
        global field_center_x, field_center_y
        field_center_x, field_center_y = coordinates[idx]
    paint_target_image(png_full_file_path, painted_gif_frames_full_folder_path, filename_of_exported_png=str(idx))


# There are two methods of creating gif:
# 1) Create gif as more shapes are drawn to canvas (single painting)
is_create_painting_progress_gif = False
frames_per_second = 200
gif_name = "gif_output"

# OR...

# 2) Create gif from series of completed paintings
recreate_number_of_frames_in_original_gif = 200
gif_painting_of_gif_name = "sunset_paintstrokes"

# Pygame display parameters
is_show_pygame_display_window = True
is_display_rectangle_improvement = False

# vector field parameters
is_enable_vector_field = True
field_center_x, field_center_y = 0,0



def vector_field_function(x,y):
    # Returns a vector given an x and y coordinate
    # (p, q) = (f(x,y), g(x,y))

    # Radial sink with rotational twist example:

    # Set radial convergence
    a = -3
    # a<0: converge inwards
    # a=0: no convergence/divergence
    # a>0: diverge outwards

    # Set rotational behavior
    b = 0
    # b<0: clockwise
    # b=0: no rotation
    # b>0: anticlockwise

    p = a*x - b*y
    q = b*x + a*y


    return (p,q)





def paint_target_image(target_image_full_filepath, png_output_folder_full_path, filename_of_exported_png):
    """
    Paints a target image using a hill climbing algorithm and texture overlays, then saves the result as a PNG.

    This function:
        - Loads a target image and resizes it for painting.
        - Loads a set of texture images to use as paint strokes.
        - Initializes a blank canvas with the average color of the target image.
        - Optionally applies a vector field to guide the painting process.
        - Iteratively adds shapes (rectangles with textures) to the canvas, optimizing their placement and color using a hill climbing algorithm.
        - Optionally displays the painting process in a Pygame window and/or records a GIF of the progress.
        - Saves the final painted image as a PNG to the specified output folder.
        - Handles all necessary output, display, and cleanup.

    Parameters:
        target_image_full_filepath (str): Full path to the image to be painted (input target image).
        png_output_folder_full_path (str): Full path to the folder where the PNG painting should be exported.
        filename_of_exported_png (str): Filename for the exported PNG painting (with or without extension).

    Returns:
        None

    Side Effects:
        - Writes PNG file to disk in the specified output folder.
        - Optionally displays a Pygame window and/or a matplotlib window.
        - Optionally creates a GIF of the painting process.
        - Prints progress and status messages

    """
    print(f"Painting image from {target_image_full_filepath}")

    # Import target as numpy arrays
    target_rgba = get_target_image_as_rgba(target_image_full_filepath, resize_target_shorter_side_of_target)

    
    # Import multiple texture png from texture folder into dictionary of numpy arrays in the form of
    # {
    # 0: {'texture_greyscale_alpha': texture_greyscale_alpha, 'texture_height': 385, 'texture_width': 1028}, 
    # 1: {'texture_greyscale_alpha': texture_greyscale_alpha, 'texture_height': 408, 'texture_width': 933}} 
    # }
    texture_dict, num_textures = get_texture_dict()

    if num_textures == 0:
        raise ValueError("No texture pngs found in texture folder.")

    # Create opaque rgba canvas of same size as target_rgba. All rgb values of blank canvas is the average rgb color of the target image
    current_rgba = np.ones(target_rgba.shape, dtype=np.float32)
    canvas_height, canvas_width = get_height_width_of_array(target_rgba)
    average_rgb = get_average_rgb_of_rgba_image(target_rgba)
    current_rgba[:,:,0:3] *= average_rgb

    # Instantiate vector field
    vector_field = VectorField(is_enable_vector_field, vector_field_function, canvas_height, canvas_width, field_center_x, field_center_y)


    # keep track of all best scoring rectangle_list and corresponding texture
    # best_rect_with_texture = []

    # Only initialize pygame display if not in multiprocessing batch mode
    pygame_display_window = None
    from __main__ import is_enable_multiprocessing_for_batch_frame_processing
    if not is_enable_multiprocessing_for_batch_frame_processing:
        pygame_display_window = PygameDisplayProcess(canvas_height, canvas_width, is_show_pygame_display_window)

    # initialize gif generator
    gif_creator = CreateOutputGIF(fps=frames_per_second, is_create_gif=is_create_painting_progress_gif, gif_file_name=gif_name)

    # Use synchronous mode if in a multiprocessing worker
    use_worker_process = not is_enable_multiprocessing_for_batch_frame_processing if 'is_enable_multiprocessing_for_batch_frame_processing' in globals() else True
    create_image_output = CreateOutputImage(texture_dict, canvas_height, canvas_width, desired_length_of_longer_side_in_output, target_rgba, use_worker_process=use_worker_process)

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

        # Keep track of how many times hill climbing algorithm fails to improve
        fail_count = 0

        # Perform hill climbing algorithm
        if is_print_hill_climb_progress:
            print(f"shape index: {shape_index:<5}  % of max iterations = {(shape_index + 1) / num_shapes_to_draw:.2f}  hill climb iterations per shape = {num_hill_climb_iterations}")
        for _ in range(num_hill_climb_iterations):
            # Stop prematurely after n failed iterations
            if fail_count > fail_threshold_before_terminating_hill_climb:
                # print(f"Terminated at iteration: {_}")
                break
            # Mutate the rectangle
            mutated_rect_list = get_mutated_rectangle_copy(best_rect_list, canvas_height, canvas_width, vector_field, is_scaling_allowed_during_mutation)
            # Score the mutated rectangle
            new_score, rgb_of_mutated_rect, y_min_mutated, scanline_x_intersects_mutated = get_score_avg_rgb_ymin_and_scanline_xintersect(mutated_rect_list, target_rgba, texture_greyscale_alpha, current_rgba)
            # update the highscore and best_rect_list if new score is higher
            if new_score > highscore:
                highscore = new_score
                best_rect_list = mutated_rect_list
                rgb_of_best_rect = rgb_of_mutated_rect
                # reset fail count
                fail_count = 0

                # Update pygame display and the gif whenever there is an improvement
                if is_display_rectangle_improvement:
                    intermediate_canvas = draw_texture_on_canvas(texture_greyscale_alpha, current_rgba.copy(), scanline_x_intersects_mutated, y_min_mutated, rgb_of_mutated_rect, *mutated_rect_list)
                    if pygame_display_window is not None:
                        pygame_display_window.update_display(intermediate_canvas)

                    # 25% chance of recording any intermediate frames produced so that gif will not be too large
                    if random.random() < 0.25:
                        gif_creator.enqueue_frame(intermediate_canvas)
            else:
                # increment number of times the hill climbing algorithm failed to improve
                fail_count += 1
                

        
        # Update current_rgba with the best rectangle texture
        update_canvas_with_best_rect(best_rect_list, target_rgba, texture_greyscale_alpha, current_rgba)

        # Enqueue to gif creator 
        gif_creator.enqueue_frame(current_rgba)

        # # Append the best rectangle list with its corresponding texture and color to the best_textured_rect
        # best_rect_with_texture.append({"best_rect_list":best_rect_list,"texture_key": texture_key, "rgb": rgb_of_best_rect})

        # Enqueue job for output image generation
        create_image_output.enqueue({"best_rect_list":best_rect_list,"texture_key": texture_key, "rgb": rgb_of_best_rect})

        # Update pygame display when new rectangle is drawn onto canvas
        if pygame_display_window is not None:
            pygame_display_window.update_display(current_rgba)

        # If pygame window is closed, terminate the outer loop and export the output prematurely
        if pygame_display_window is not None and pygame_display_window.was_closed():
            print("User closed pygame window. Shape adding loop terminated.")
            break
    # End pygame display process
    if pygame_display_window is not None:
        pygame_display_window.close()

    # Display the final image if user wants to
    if is_display_final_image:
        plt.imshow(current_rgba)
        plt.show()

    # Save the output and end safely the process.
    output_rgba = create_image_output.finish() 
    save_rgba_array_as_png(output_rgba, filename_of_exported_png, png_output_folder_full_path, is_append_datetime=is_append_datetime)

    # Safely end process of gif_creator
    gif_creator.end_process()



if __name__ == "__main__":
    warmup_numba()

    # Get full filepath of target, which could have '.png', .jpg', '.jpeg', '.gif' extension
    full_target_filepath, is_target_gif = get_target_full_filepath()

    # Get full filepath of output folder in same working directory. a folder called "output" will be created if it does not already exist.
    output_folder_full_filepath = get_output_folder_full_filepath()

    if is_target_gif:
        # Configure some global parameters to optimize for speed:
        is_create_painting_progress_gif = False
        is_display_rectangle_improvement = False
        if is_enable_multiprocessing_for_batch_frame_processing:
            is_show_pygame_display_window = False  # Disable pygame display for multiprocessing

        # Create two folders to store original gif frames and painted frames. Folders are created if they do not already exist.
        original_gif_frames_full_folder_path = create_folder("original_gif_frames")
        painted_gif_frames_full_folder_path = create_folder("painted_gif_frames")
        # Clear the contents of these two folders accumulated from previous run
        clear_folder_contents(original_gif_frames_full_folder_path)
        clear_folder_contents(painted_gif_frames_full_folder_path)

        # Export gif frames as png file into the original_gif_frames folder and find the approximate fps of the gif.
        # If max_number_of_extracted_frames is lesser than number of frames in the gif, approx_fps will be smaller than the number of frames in gif to keep total duration roughly the same
        approx_fps = extract_gif_frames_to_output_folder_and_get_approx_fps(
            full_path_to_gif=full_target_filepath,
            max_number_of_extracted_frames=recreate_number_of_frames_in_original_gif,
            output_folder=original_gif_frames_full_folder_path
        )

        # Create a list of full filepath to pngs inside the original_gif_frames
        list_of_png_full_file_path = []

        for item in sorted(os.listdir(original_gif_frames_full_folder_path), key=lambda x: x.lower()):
            if item.lower().endswith('.png'):
                full_path = os.path.join(original_gif_frames_full_folder_path, item)
                list_of_png_full_file_path.append(full_path) 
                
        if is_enable_vector_field:
            coord_selector_UI = CoordinateSelectorUI(list_of_png_full_file_path, resize_target_shorter_side_of_target)
            coordinates = coord_selector_UI.run()

        if is_enable_multiprocessing_for_batch_frame_processing:
            import multiprocessing

            # Prepare arguments for each process
            args_list = []
            for i, png_full_file_path in enumerate(list_of_png_full_file_path):
                args_list.append((i, png_full_file_path, painted_gif_frames_full_folder_path, coordinates if is_enable_vector_field else None))

            num_workers = max(1, int(multiprocessing.cpu_count() * 0.8))
            num_workers = min(num_workers, len(args_list))
            with multiprocessing.Pool(processes=num_workers) as pool:
                pool.map(paint_worker, args_list)
        else:
            # For each png file in original_gif_frames folder, create a painted png and export them to painted_gif_frames folder
            for i, png_full_file_path in enumerate(list_of_png_full_file_path):
                # Translate origin of vector field to the selected coordinates
                if is_enable_vector_field and coordinates is not None:
                    field_center_x, field_center_y = coordinates[0]
                paint_target_image(png_full_file_path, painted_gif_frames_full_folder_path, filename_of_exported_png=str(i))

        # Read the painted pngs from painted_gif_frames folder and create the final gif in output folder
        create_gif_from_pngs(painted_gif_frames_full_folder_path, output_folder_full_filepath, approx_fps, file_name=gif_painting_of_gif_name)

    else:
        # Allow user to select center of vector field
        if is_enable_vector_field:
            coord_selector_UI = CoordinateSelectorUI(full_target_filepath, resize_target_shorter_side_of_target)
            coordinates = coord_selector_UI.run()
            if coordinates is not None:
                field_center_x, field_center_y = coordinates

        # recreate the image
        paint_target_image(full_target_filepath, output_folder_full_filepath, filename_of_exported_png=image_name)
    

# Debugging
# if __name__ == "__main__":
#     with cProfile.Profile() as profile:
#         main()

#     with open("profile_stats.txt", "w") as f:
#         print("Logged runtime stats")
#         stats = pstats.Stats(profile, stream=f)
#         stats.sort_stats(pstats.SortKey.TIME)
#         stats.print_stats("main|rectangle|utilities|output_gif|output_image")


