class Painter:
    def __init__(self, params, ):
        # Initialize parameters, keyerror must occur if any parameters are not present

        # Print to console parameters (DEBUG)
        self.is_print_hill_climb_progress_in_console = True
        # Other parameters not part of UI:
        self.is_append_datetime = False # Adds date time to image output
        self.frames_per_second_of_painting_progress_gif = 100 # Not part of UI

        # Parameter tab:
        # 1) Computation size (single slider)
        self.resize_target_shorter_side_of_target = params["computation_size"]
        assert isinstance(self.resize_target_shorter_side_of_target, int), "computation_size must be int"
        assert self.resize_target_shorter_side_of_target > 10, "computation_size too small"

        # 2) Add N textures (single slider)
        self.num_shapes_to_draw = params["num_textures"]
        assert isinstance(self.num_shapes_to_draw, int) and self.num_shapes_to_draw > 0, "num_textures must be positive int"

        # 3) Num of hill climb iterations (dual slider)
        self.min_hill_climb_iterations = params["hill_climb_min_iterations"]
        self.max_hill_climb_iterations = params["hill_climb_max_iterations"]
        assert isinstance(self.min_hill_climb_iterations, int) and self.min_hill_climb_iterations > 0, "hill_climb_min_iterations must be positive int"
        assert isinstance(self.max_hill_climb_iterations, int) and self.max_hill_climb_iterations >= self.min_hill_climb_iterations, "hill_climb_max_iterations must be >= min"

        # 4) Texture opacity percentage from 1 to 100% (single slider)
        self.texture_opacity_percentage = params["texture_opacity"]
        assert isinstance(self.texture_opacity_percentage, int) and 1 <= self.texture_opacity_percentage <= 100, "texture_opacity must be int in [1,100]"

        # 5) Initial texture width to ? pixels (single slider)
        self.initial_random_rectangle_pixel_width = params["initial_texture_width"]
        assert isinstance(self.initial_random_rectangle_pixel_width, int) and self.initial_random_rectangle_pixel_width > 0, "initial_texture_width must be positive int"

        # 6) Allow size of texture to vary during optimization (checkbox)
        is_uniform_texture_size = params["uniform_texture_size"]
        assert isinstance(is_uniform_texture_size, bool), "uniform_texture_size must be bool"
        self.is_scaling_allowed_during_mutation = not is_uniform_texture_size

        # 7) Display painting progress (toggle visibility checkbox)
        self.is_show_pygame_display_window = params["display_painting_progress"]
        assert isinstance(self.is_show_pygame_display_window, bool), "display_painting_progress must be bool"

        # 7.i) Show improvement of individual textures (checkbox)
        self.is_display_rectangle_improvement = params["display_placement_progress"]
        assert isinstance(self.is_display_rectangle_improvement, bool), "display_placement_progress must be bool"

        # 7.ii) Display final image after painting (checkbox)
        self.is_display_final_image = params["display_final_image"]
        assert isinstance(self.is_display_final_image, bool), "display_final_image must be bool"

        # 8) Allow early termination of hill climbing (toggle visibility checkbox)
        self.is_prematurely_terminate_hill_climbing_if_stuck_in_local_minima = params["allow_early_termination"]
        assert isinstance(self.is_prematurely_terminate_hill_climbing_if_stuck_in_local_minima, bool), "allow_early_termination must be bool"

        # 8.i) Terminate after N failed iterations where there is no improvement (single slider)
        self.fail_threshold_before_terminating_hill_climb = params["failed_iterations_threshold"]
        assert isinstance(self.fail_threshold_before_terminating_hill_climb, int) and self.fail_threshold_before_terminating_hill_climb >= 0, "failed_iterations_threshold must be non-negative int"

        # 9) Enable vector field (toggle visibility checkbox)
        self.is_enable_vector_field = params["enable_vector_field"]
        assert isinstance(self.is_enable_vector_field, bool), "enable_vector_field must be bool"

        # 9i) Edit vector field equation (button)
        self.vector_field_f = params["vector_field_f"]
        self.vector_field_g = params["vector_field_g"]
        assert isinstance(self.vector_field_f, str), "vector_field_f must be str"
        assert isinstance(self.vector_field_g, str), "vector_field_g must be str"

        self.vector_field_function = params["vector_field_function"]
        assert callable(self.vector_field_function), "vector_field_function must be callable"

        # 9ii) Shift vector field origin (button)
        self.vector_field_origin_shift = params["vector_field_origin_shift"]
        assert isinstance(self.vector_field_origin_shift, list) and all(isinstance(x, list) and len(x) == 2 and all(isinstance(i, int) for i in x) for x in self.vector_field_origin_shift), "vector_field_origin_shift must be list of [int, int]"



        # Output tab (For png, jpg, jpeg case)
        # 1) Output image size ? px (single slider)
        self.desired_length_of_longer_side_in_painted_image = params["output_image_size"]
        assert isinstance(self.desired_length_of_longer_side_in_painted_image, int) and self.desired_length_of_longer_side_in_painted_image > 0, "output_image_size must be positive int"

        # 2) Name of output image (text box input)
        self.image_name = params["output_image_name"]
        assert isinstance(self.image_name, str), "output_image_name must be str"

        # 3) Create GIF of painting progress (toggle visibility checkbox)
        self.is_create_painting_progress_gif = params["create_gif_of_painting_progress"]
        assert isinstance(self.is_create_painting_progress_gif, bool), "create_gif_of_painting_progress must be bool"

        # 3.i) GIF filename
        self.painting_progress_gif_name = params["painting_progress_gif_name"]
        assert isinstance(self.painting_progress_gif_name, str), "painting_progress_gif_name must be str"


        # Output tab (For gif case)
        # 1) Paint N out of total number frames from target GIF
        self.recreate_number_of_frames_in_original_gif = params["num_frames_to_paint"]
        assert isinstance(self.recreate_number_of_frames_in_original_gif, int) and self.recreate_number_of_frames_in_original_gif > 1, "recreate_number_of_frames_in_original_gif must be int greater than 1"

        # 2) Painted GIF filename
        self.gif_painting_of_target_gif = params["painted_gif_name"]
        assert isinstance(self.gif_painting_of_target_gif, str), "gif_painting_of_target_gif must be str"

        # 3) Enable multiprocessing for batch frame processing 
        self.is_enable_multiprocessing_for_batch_frame_processing = params["enable_multiprocessing"]
        assert isinstance(self.is_enable_multiprocessing_for_batch_frame_processing, bool), "is_enable_multiprocessing_for_batch_frame_processing must be bool"









        # Print all parameters for debugging
        print("Painter parameters (DEBUG):")
        for k, v in params.items():
            print(f"  {k}: {v}")
