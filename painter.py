class Painter:
    def __init__(self, params):
        # Initialize parameters, keyerror must occur if any parameters are not present
        # Print to console parameters (DEBUG)
        self.is_print_hill_climb_progress_in_console = True

        # Parameter tab:
        # 1) Computation size (single slider)
        self.resize_target_shorter_side_of_target = params["computation_size"]
        assert type(self.resize_target_shorter_side_of_target) is int, f"computation_size is not int"
        assert self.resize_target_shorter_side_of_target > 10, "computation_size size too small"
        
        # 2) Add N textures (single slider)
        self.num_shapes_to_draw = params["num_textures"]

        # 3) Num of hill climb iterations (dual slider)
        min_hill_climb_iterations = params["hill_climb_min_iterations"]
        max_hill_climb_iterations = params["hill_climb_max_iterations"]

        # 4) Texture opacity percentage from 1 to 100% (single slider)
        texture_opacity_percentage = params["texture_opacity"]

        # 5) Initial texture width to ? pixels (single slider)

        # 6) Allow size of texture to vary during optimization (checkbox) equivalent to NOT make all textures the same size

        # 7) Display painting progress (toggle visibility checkbox)

        # 7.i) Show improvement of individual textures (checkbox)

        # 7.ii) Display final image after painting (checkbox initialized only if the target is not a gif)


        # 8) Allow early termination of hill climbing (toggle visibility checkbox)

        # 8.i) Terminate after N failed iterations where there is no improvement (single slider)

        # 9) Enable vector field (toggle visibility checkbox)

        # 9) Enable vector field (toggle visibility checkbox)
        is_enable_vector_field = True
        # 9i) Edit vector field equation (button)

        # Output tab (For png, jpg, jpeg case)
        # 1) Output image size ? px (single slider)

        # 2) Name of output image (text box input)

        # 3) Create GIF of painting progress (toggle visibility checkbox)

        # 3.i) GIF filename


        # Output tab (For gif case)
        # 1) Paint N out of total number frames from target GIF
        N = 200 # placeholder for testing, this is upper limit, can exceed number of frames in original GIF
        recreate_number_of_frames_in_original_gif = N

        # 2) Painted GIF filename

        # 3) Enable multiprocessing for batch frame processing 



        # Other parameters not part of UI:
        is_append_datetime = False # Adds date time to image output
        frames_per_second_of_painting_progress_gif = 100 # This is not part of the UI.
