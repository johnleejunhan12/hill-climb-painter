from utils.utilities import get_approximate_fps_if_reduced, is_gif, get_output_folder_full_filepath, get_target_image_as_rgba, get_texture_dict


class PainterPrototype:
    def __init__(self, ui_param_dict, full_target_filepath, texture_filepath_list, painted_gif_frames_full_folder_path, original_gif_frames_filepath_list=None):
        """
        Painter that paints images to output folder

        Parameters:
            ui_param_dict (dict): Dictionary obtained from user interface
            full_target_filepath (str): Full filepath of target, which could have '.png', .jpg', '.jpeg', '.gif' extension
            texture_filepath (list): 
        
        """
        # Get full filepath of target, which could have '.png', .jpg', '.jpeg', '.gif' extension, check its type
        self.full_target_filepath, self.is_target_gif = full_target_filepath, is_gif(full_target_filepath)
        # Get full filepath of output folder in same working directory. a folder called "output" will be created if it does not already exist.
        self.output_folder_full_filepath = get_output_folder_full_filepath()
        # Get list of filepaths of the original gif frames
        self.list_of_png_full_file_path = original_gif_frames_filepath_list
        # Initialize folder path to store painted gif frames
        self.painted_gif_frames_full_folder_path = painted_gif_frames_full_folder_path

        # Initialize parameters from UI
        def init_params():
            # Params not part of UI but for debugging
            self.is_print_hill_climb_progress_in_console = True
            self.is_append_datetime = False
            self.frames_per_second_of_painting_progress_gif = 100
            self.percentage_of_cpu_to_use = 0.8  # Percentage of CPU to use for multiprocessing

            # Parameter tab:
            # 1) Computation size (single slider)
            self.resize_target_shorter_side_of_target = ui_param_dict["computation_size"]
            assert isinstance(self.resize_target_shorter_side_of_target, int), "computation_size must be int"
            assert self.resize_target_shorter_side_of_target > 10, "computation_size too small"

            # 2) Add N textures (single slider)
            self.num_shapes_to_draw = ui_param_dict["num_textures"]
            assert isinstance(self.num_shapes_to_draw, int) and self.num_shapes_to_draw > 0, "num_textures must be positive int"

            # 3) Num of hill climb iterations (dual slider)
            self.min_hill_climb_iterations = ui_param_dict["hill_climb_min_iterations"]
            self.max_hill_climb_iterations = ui_param_dict["hill_climb_max_iterations"]
            assert isinstance(self.min_hill_climb_iterations, int) and self.min_hill_climb_iterations > 0, "hill_climb_min_iterations must be positive int"
            assert isinstance(self.max_hill_climb_iterations, int) and self.max_hill_climb_iterations >= self.min_hill_climb_iterations, "hill_climb_max_iterations must be >= min"

            # 4) Texture opacity percentage from 1 to 100% (single slider)
            self.texture_opacity_percentage = ui_param_dict["texture_opacity"]
            assert isinstance(self.texture_opacity_percentage, int) and 1 <= self.texture_opacity_percentage <= 100, "texture_opacity must be int in [1,100]"

            # 5) Initial texture width to ? pixels (single slider)
            self.initial_random_rectangle_pixel_width = ui_param_dict["initial_texture_width"]
            assert isinstance(self.initial_random_rectangle_pixel_width, int) and self.initial_random_rectangle_pixel_width > 0, "initial_texture_width must be positive int"

            # 6) Allow size of texture to vary during optimization (checkbox)
            is_uniform_texture_size = ui_param_dict["uniform_texture_size"]
            assert isinstance(is_uniform_texture_size, bool), "uniform_texture_size must be bool"
            self.is_scaling_allowed_during_mutation = not is_uniform_texture_size

            if not self.is_target_gif:
                # 7) Display painting progress (toggle visibility checkbox)
                self.is_show_pygame_display_window = ui_param_dict["display_painting_progress"]
                assert isinstance(self.is_show_pygame_display_window, bool), "display_painting_progress must be bool"

                # 7.i) Show improvement of individual textures (checkbox)
                self.is_display_rectangle_improvement = ui_param_dict["display_placement_progress"]
                assert isinstance(self.is_display_rectangle_improvement, bool), "display_placement_progress must be bool"

                # 7.ii) Display final image after painting (checkbox)
                self.is_display_final_image = ui_param_dict["display_final_image"]
                assert isinstance(self.is_display_final_image, bool), "display_final_image must be bool"

            # 8) Allow early termination of hill climbing (toggle visibility checkbox)
            self.is_prematurely_terminate_hill_climbing_if_stuck_in_local_minima = ui_param_dict["allow_early_termination"]
            assert isinstance(self.is_prematurely_terminate_hill_climbing_if_stuck_in_local_minima, bool), "allow_early_termination must be bool"

            # 8.i) Terminate after N failed iterations where there is no improvement (single slider)
            self.fail_threshold_before_terminating_hill_climb = ui_param_dict["failed_iterations_threshold"]
            assert isinstance(self.fail_threshold_before_terminating_hill_climb, int) and self.fail_threshold_before_terminating_hill_climb >= 0, "failed_iterations_threshold must be non-negative int"

            # 9) Enable vector field (toggle visibility checkbox)
            self.is_enable_vector_field = ui_param_dict["enable_vector_field"]
            assert isinstance(self.is_enable_vector_field, bool), "enable_vector_field must be bool"

            # 9i) Edit vector field equation (button)
            self.vector_field_f = ui_param_dict["vector_field_f"]
            self.vector_field_g = ui_param_dict["vector_field_g"]
            assert isinstance(self.vector_field_f, str), "vector_field_f must be str"
            assert isinstance(self.vector_field_g, str), "vector_field_g must be str"

            self.vector_field_function = ui_param_dict["vector_field_function"]
            assert callable(self.vector_field_function), "vector_field_function must be callable"

            # 9ii) Shift vector field origin (button)
            self.coordinates = ui_param_dict["vector_field_origin_shift"]
            assert isinstance(self.coordinates, list) and all(isinstance(x, list) and len(x) == 2 and all(isinstance(i, int) for i in x) for x in self.coordinates), "vector_field_origin_shift must be list of [int, int]"


            if not self.is_target_gif:
                # Output tab (For png, jpg, jpeg case)
                # 1) Output image size ? px (single slider)
                self.desired_length_of_longer_side_in_painted_image = ui_param_dict["output_image_size"]
                assert isinstance(self.desired_length_of_longer_side_in_painted_image, int) and self.desired_length_of_longer_side_in_painted_image > 0, "output_image_size must be positive int"

                # 2) Name of output image (text box input)
                self.image_name = ui_param_dict["output_image_name"]
                assert isinstance(self.image_name, str), "output_image_name must be str"

                # 3) Create GIF of painting progress (toggle visibility checkbox)
                self.is_create_painting_progress_gif = ui_param_dict["create_gif_of_painting_progress"]
                assert isinstance(self.is_create_painting_progress_gif, bool), "create_gif_of_painting_progress must be bool"

                # 3.i) GIF filename
                self.painting_progress_gif_name = ui_param_dict["painting_progress_gif_name"]
                assert isinstance(self.painting_progress_gif_name, str), "painting_progress_gif_name must be str"


            else:
                # Output tab (For gif case)
                # 1) Paint N out of total number frames from target GIF
                self.recreate_number_of_frames_in_original_gif = ui_param_dict["num_frames_to_paint"]
                assert isinstance(self.recreate_number_of_frames_in_original_gif, int) and self.recreate_number_of_frames_in_original_gif > 1, "recreate_number_of_frames_in_original_gif must be int greater than 1"

                # 2) Painted GIF filename
                self.gif_painting_of_target_gif = ui_param_dict["painted_gif_name"]
                assert isinstance(self.gif_painting_of_target_gif, str), "gif_painting_of_target_gif must be str"

                # 3) Enable multiprocessing for batch frame processing 
                self.is_enable_multiprocessing_for_batch_frame_processing = ui_param_dict["enable_multiprocessing"]
                assert isinstance(self.is_enable_multiprocessing_for_batch_frame_processing, bool), "is_enable_multiprocessing_for_batch_frame_processing must be bool"     
        init_params()

        def enforce_param_dependencies():
            if self.is_target_gif:
                self.is_create_painting_progress_gif = False
                self.is_display_rectangle_improvement = False
                if self.is_enable_multiprocessing_for_batch_frame_processing:
                    self.is_show_pygame_display_window = False  # Disable pygame display for multiprocessing

                self.approx_fps = get_approximate_fps_if_reduced(
                    full_path_to_gif=self.full_target_filepath,
                    max_number_of_extracted_frames=self.recreate_number_of_frames_in_original_gif
                )

            if not self.is_enable_vector_field:
                self.coordinates = None  # Disable vector field origin shift if not enabled
                self.vector_field_function = None  # Disable vector field function if not enabled

            if self.is_enable_vector_field:
                assert self.vector_field_function is not None, "vector_field_function must be set if enable_vector_field is True"
                assert self.coordinates is not None or self.coordinates != [[]], "coordinates must be set if enable_vector_field is True"
                assert self.vector_field_f is not None or self.vector_field_f != "", "vector_field_f must be set if enable_vector_field is True"
                assert self.vector_field_g is not None or self.vector_field_g != "", "vector_field_g must be set if enable_vector_field is True"

        enforce_param_dependencies()


    def print_custom_attributes(self):
        # Get all instance attributes (including built-ins)
        all_attrs = vars(self)
        
        # Filter out built-in attributes (start/end with '__')
        custom_attrs = {
            key: value 
            for key, value in all_attrs.items() 
            if not (key.startswith('__') and key.endswith('__'))
        }
        
        # print("Custom attributes (from __init__ and later):", custom_attrs)

        for key, value in custom_attrs.items():
            print(f"{key}: {value} (type: {type(value)})\n")

    @staticmethod
    def paint_worker(args):
        print_custom_attributes()

    def run(self):
        if self.is_target_gif:
            if self.is_enable_multiprocessing_for_batch_frame_processing:
                import multiprocessing

                # Prepare arguments for each process
                args_list = []
                for i, png_full_file_path in enumerate(self.list_of_png_full_file_path):
                    args_list.append((i, png_full_file_path, self.painted_gif_frames_full_folder_path, self.coordinates))

                num_workers = max(1, int(multiprocessing.cpu_count() * self.percentage_of_cpu_to_use))
                num_workers = min(num_workers, len(args_list))
                print(f"Using {num_workers} workers for multiprocessing")
                # Create a pool of workers and map the paint_worker function to the arguments
                with multiprocessing.Pool(processes=num_workers) as pool:
                    pool.map(self.paint_worker, args_list)


        #     else:
        #         # For each png file in original_gif_frames folder, create a painted png and export them to painted_gif_frames folder
        #         for i, png_full_file_path in enumerate(list_of_png_full_file_path):
        #             # Translate origin of vector field to the selected coordinates
        #             if is_enable_vector_field and coordinates is not None:
        #                 field_center_x, field_center_y = coordinates[0]
        #             paint_target_image(png_full_file_path, painted_gif_frames_full_folder_path, filename_of_exported_png=str(i))

        #     # Read the painted pngs from painted_gif_frames folder and create the final gif in output folder
        #     create_gif_from_pngs(painted_gif_frames_full_folder_path, output_folder_full_filepath, approx_fps, file_name=gif_painting_of_target_gif)

        # else:
        #     # Allow user to select center of vector field
        #     if is_enable_vector_field:
        #         coord_selector_UI = CoordinateSelectorUI(full_target_filepath, resize_target_shorter_side_of_target)
        #         coordinates = coord_selector_UI.run()
        #         if coordinates is not None:
        #             field_center_x, field_center_y = coordinates[0]
        #     # recreate the image
        #     paint_target_image(full_target_filepath, output_folder_full_filepath, filename_of_exported_png=image_name)
        

if __name__ == "__main__":
    from user_interface.vector_field_equation_ui import VectorFieldVisualizer
    vector_field_function = VectorFieldVisualizer.get_function_from_string_equations("x","y")

    # # non - gif case 
    # param_dict = {'computation_size': 263, 'num_textures': 557, 'hill_climb_min_iterations': 50, 'hill_climb_max_iterations': 50, 'texture_opacity': 100, 'initial_texture_width': 146, 'uniform_texture_size': False, 'allow_early_termination': True, 'failed_iterations_threshold': 108, 'enable_vector_field': True, 'vector_field_f': '-x+y', 'vector_field_g': '-x-y', 'vector_field_function': vector_field_function, 'vector_field_origin_shift': [[83, 107]], 'display_painting_progress': True, 'display_placement_progress': True, 'display_final_image': True, 'output_image_size': 2096, 'output_image_name': 'painted_image_output', 'create_gif_of_painting_progress': False, 'painting_progress_gif_name': ''}
    # TARGET_FILEPATH = "C:\\Git Repos\\hill-climb-painter\\target\\owl.png"
    # TEXTURE_FILEPATH_LIST = ['C:\\Git Repos\\hill-climb-painter\\texture\\circle.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\rectangle.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\square.png']
    # ORIGINAL_GIF_FRAMES_FILE_PATH_LIST = None
    # Painter(param_dict, TARGET_FILEPATH, TEXTURE_FILEPATH_LIST, ORIGINAL_GIF_FRAMES_FILE_PATH_LIST)

    # gif case
    param_dict = {'computation_size': 263, 'num_textures': 557, 'hill_climb_min_iterations': 50, 'hill_climb_max_iterations': 50, 'texture_opacity': 100, 'initial_texture_width': 146, 'uniform_texture_size': True, 'allow_early_termination': True, 'failed_iterations_threshold': 108, 'enable_vector_field': True, 'vector_field_f': '-x+y', 'vector_field_g': '-x-y', 'vector_field_function': vector_field_function, 'vector_field_origin_shift': [[135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114], [135, 114]], 'num_frames_to_paint': 20, 'painted_gif_name': 'painted_gif_output', 'enable_multiprocessing': True}
    TARGET_FILEPATH = "C:\\Git Repos\\hill-climb-painter\\target\\shrek-somebody-ezgif.com-crop (1).gif"
    TEXTURE_FILEPATH_LIST = ['C:\\Git Repos\\hill-climb-painter\\texture\\circle.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\rectangle.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\square.png']
    PAINTED_GIF_FRAMES_FULL_FOLDER_PATH="C:\\Git Repos\\hill-climb-painter\\painted_gif_frames"

    # original gif frames may be None
    ORIGINAL_GIF_FRAMES_FILE_PATH_LIST = ['C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0000.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0001.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0002.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0003.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0004.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0005.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0006.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0007.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0008.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0009.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0010.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0011.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0012.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0013.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0014.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0015.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0016.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0017.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0018.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0019.png']
    mypainter = Painter(param_dict, TARGET_FILEPATH, TEXTURE_FILEPATH_LIST, PAINTED_GIF_FRAMES_FULL_FOLDER_PATH, ORIGINAL_GIF_FRAMES_FILE_PATH_LIST)
    mypainter.print_custom_attributes()
    mypainter.run()

