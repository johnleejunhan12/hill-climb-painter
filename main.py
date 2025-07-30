from user_interface.target_texture_select_ui import TargetTextureSelectorUI
from utils.file_operations import *
from user_interface.parameter_ui import *
from utils.utilities import extract_gif_frames_to_output_folder_and_get_approx_fps 
from painter import PaintingOrchestrator


def get_target_and_textures():
    # 1) Create target and texture folders, will not be modified if already exist
    target_folder_fullpath = create_folder("target")
    texture_folder_fullpath = create_folder("texture")

    # 1) Get full filepath of target and textures (if any) in respective target folder and texture folder
    # 1a) If there is more than one file with valid extention in target, do not select any (this case should never happen unless user goes out of their way to place multiple files in target)
    num_targets = count_image_files(target_folder_fullpath)
    if num_targets != 1:
        initial_target_filepath = None
    else:
        initial_target_filepath = get_first_image_file(target_folder_fullpath)
    
    # 1b) Check for invalid files or no files in texture folder
    if not all_files_are_png(texture_folder_fullpath): # Case where either there are no png files or there exists at least one file that is non png
        initial_texture_list = None
    else:
        initial_texture_list = get_image_file_paths(texture_folder_fullpath)

    select_target_and_texture_ui = TargetTextureSelectorUI(is_prompt_user_before_quit = True,
                                                           initial_selected_image_path=initial_target_filepath,
                                                           initial_selected_texture_paths=initial_texture_list)
    
    user_selection_start_of_script = select_target_and_texture_ui.run_and_get_selection()
    if user_selection_start_of_script is None:
        print("User did not select anything, terminate the script")
        quit()
    else:
        target_image_full_filepath, list_of_texture_images_full_path = user_selection_start_of_script
        print("User has selected")
    clear_folder_contents(target_folder_fullpath, exclude_files=target_image_full_filepath)

    target = copy_and_paste_file(target_image_full_filepath, target_folder_fullpath)

    textures = []
    clear_folder_contents(texture_folder_fullpath, exclude_files=list_of_texture_images_full_path)
    for texture_path in list_of_texture_images_full_path:
        textures.append(copy_and_paste_file(texture_path, texture_folder_fullpath))

    # Extract gif frames for UI (if target is GIF)
    def is_gif_file(filepath):
        # Get the file extension (lowercase to handle .GIF, .gif, etc.)
        file_ext = os.path.splitext(filepath)[1].lower()
        return file_ext == '.gif'

    original_gif_frames = None

    # Create two folders to store original gif frames and painted frames. Folders are created if they do not already exist.
    original_gif_frames_full_folder_path = create_folder("original_gif_frames")
    painted_gif_frames_full_folder_path = create_folder("painted_gif_frames")

    if is_gif_file(target):
        # Clear the contents of these two folders accumulated from previous run
        clear_folder_contents(original_gif_frames_full_folder_path)
        clear_folder_contents(painted_gif_frames_full_folder_path)

        # Export all gif frames as png file into the original_gif_frames folder and find the approximate fps of the gif.
        # Extract ALL frames for UI purposes (coordinate selection, etc.)
        
        approx_fps = extract_gif_frames_to_output_folder_and_get_approx_fps(
            full_path_to_gif=target,
            max_number_of_extracted_frames=10000000000,   # Extract all frames for UI
            output_folder=original_gif_frames_full_folder_path
        )

        # Create a list of full filepath to pngs inside the original_gif_frames
        original_gif_frames = []

        for item in sorted(os.listdir(original_gif_frames_full_folder_path), key=lambda x: x.lower()):
            if item.lower().endswith('.png'):
                full_path = os.path.join(original_gif_frames_full_folder_path, item)
                original_gif_frames.append(full_path) 

    return target, textures, original_gif_frames, painted_gif_frames_full_folder_path


def select_frame_indices_for_painting(total_frames, num_frames_to_paint):
    """
    Select frame indices using the same algorithm as extract_gif_frames_to_output_folder_and_get_approx_fps.
    This ensures consistent frame sampling logic.
    
    Args:
        total_frames (int): Total number of available frames
        num_frames_to_paint (int): Number of frames to select for painting
        
    Returns:
        list: Sorted list of frame indices to paint
    """
    if total_frames <= num_frames_to_paint:
        # Use all available frames
        return list(range(total_frames))
    else:
        # Sample frames evenly using the same algorithm as the utility function
        frames_to_extract = []
        step = (total_frames - 1) / (num_frames_to_paint - 1)
        
        for i in range(num_frames_to_paint):
            frame_index = round(i * step)
            frames_to_extract.append(frame_index)
        
        # Ensure unique frame indices
        frames_to_extract = list(set(frames_to_extract))
        frames_to_extract.sort()
        
        # Fill with remaining frames if needed (edge case handling)
        if len(frames_to_extract) < num_frames_to_paint:
            remaining_frames = [i for i in range(total_frames) if i not in frames_to_extract]
            frames_to_extract.extend(remaining_frames[:num_frames_to_paint - len(frames_to_extract)])
            frames_to_extract.sort()
        
        return frames_to_extract




def run_painting_algorithm(param_dict):
    """
    Execute the painting algorithm using the new OOP architecture.
    
    Args:
        param_dict: Dictionary containing UI parameters
    """
    param_dict["print_progress"] = IS_PRINT_PROGRESS_OF_HILL_CLIMBING_ALGO
    
    # Configure intermediate frame visualization settings
    # 🎯 Control how often intermediate optimization steps are displayed
    param_dict["intermediate_frame_generation_fps"] = 20  # FPS cap for intermediate display updates (1-60 recommended)
    
    # 🎞️ Control how many frames are recorded to the painting progress GIF
    param_dict["probability_of_writing_intermediate_frame_to_gif"] = 0.2  # Probability of recording frames (0.0 = no frames, 1.0 = all frames)
    

    try:
        # Determine if target is a GIF based on file extension
        is_gif_target = TARGET_FILEPATH.lower().endswith('.gif')

        
        if is_gif_target:
            param_dict["print_progress"] = False
            
            # Handle GIF target - select and paint the specified number of frames
            print(f"🎬 Processing GIF target: {TARGET_FILEPATH}")
            
            # Get the number of frames to paint from UI parameters
            total_available_frames = len(ORIGINAL_GIF_FRAMES_FILE_PATH_LIST) if ORIGINAL_GIF_FRAMES_FILE_PATH_LIST else 0
            num_frames_to_paint = param_dict.get('num_frames_to_paint', total_available_frames)
            
            print(f"📁 Found {total_available_frames} total frames")
            print(f"🎯 Selecting {num_frames_to_paint} frames for painting")
            
            # Select frame indices using the same algorithm as the utility function
            selected_frame_indices = select_frame_indices_for_painting(total_available_frames, num_frames_to_paint)
            
            # Get the actual frame paths for the selected indices
            selected_frame_paths = [ORIGINAL_GIF_FRAMES_FILE_PATH_LIST[i] for i in selected_frame_indices]
            
            print(f"🔍 Selected frame indices: {selected_frame_indices}")
            print(f"📝 Selected {len(selected_frame_paths)} frames to process")
            
            # Calculate FPS for the selected frames (same logic as utility function)
            # Get original FPS from the GIF
            from PIL import Image
            with Image.open(TARGET_FILEPATH) as gif:
                duration = gif.info.get('duration', 100)  # Default to 100ms if not specified
                original_fps = 1000 / duration  # Convert milliseconds to FPS
            
            if len(selected_frame_indices) == total_available_frames:
                # Using all frames, keep original FPS
                fps_for_output = original_fps
                print(f"🎞️ Using original FPS: {fps_for_output:.2f}")
            else:
                # Calculate approximate FPS (original FPS * reduction factor)
                reduction_factor = len(selected_frame_indices) / total_available_frames
                fps_for_output = original_fps * reduction_factor
                print(f"🎞️ Calculated FPS for reduced frames: {fps_for_output:.2f} (reduction factor: {reduction_factor:.3f})")
            
            # Use multiprocessing if enabled in UI
            use_multiprocessing = param_dict.get('enable_multiprocessing', False)
            
            success = PaintingOrchestrator.paint_batch_frames(
                frame_paths=selected_frame_paths,
                texture_paths=TEXTURE_FILEPATH_LIST,
                output_folder=PAINTED_GIF_FRAMES_FULL_FOLDER_PATH,
                ui_dict=param_dict,
                use_multiprocessing=use_multiprocessing
            )
            
            if success:
                # After painting all frames, create the final GIF
                print("🎞️ Creating final GIF from painted frames...")
                try:
                    from utils.utilities import create_gif_from_pngs, get_output_folder_full_filepath
                    
                    output_folder = get_output_folder_full_filepath()
                    gif_name = param_dict.get('painted_gif_name', 'painted_gif_output')
                    
                    # Use the calculated FPS for the selected frames
                    create_gif_from_pngs(
                        PAINTED_GIF_FRAMES_FULL_FOLDER_PATH, 
                        output_folder, 
                        fps_for_output, 
                        file_name=gif_name
                    )
                    print(f"✅ Successfully created GIF: {gif_name}")
                    
                except Exception as e:
                    print(f"⚠️ Warning: Failed to create final GIF: {e}")
                    print("Individual painted frames are still available in the painted_gif_frames folder")
            
        else:
            # Handle single image target
            print(f"🖼️ Processing single image: {TARGET_FILEPATH}")
            
            # Get output details
            from utils.utilities import get_output_folder_full_filepath
            output_folder = get_output_folder_full_filepath()
            filename = param_dict.get('output_image_name', 'painted_image')
            
            success = PaintingOrchestrator.paint_from_ui_params(
                ui_dict=param_dict,
                target_path=TARGET_FILEPATH,
                texture_paths=TEXTURE_FILEPATH_LIST,
                output_folder=output_folder,
                filename=filename,
                is_gif_target=False
            )
        
        # Print final result
        if success:
            print("\n" + "=" * 50)
            print("🎉 Painting Algorithm Completed Successfully!")
            print("✅ All outputs have been saved to the 'output' folder")
            if is_gif_target:
                print(f"📁 Painted frames: {PAINTED_GIF_FRAMES_FULL_FOLDER_PATH}")
        else:
            print("\n" + "=" * 50)
            print("❌ Painting Algorithm Failed")
            print("Please check the console output above for error details")
    
    except Exception as e:
        print(f"\n❌ Critical error in painting algorithm: {e}")
        print("Please check your configuration and try again")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":

    IS_PRINT_PROGRESS_OF_HILL_CLIMBING_ALGO = True
        
    TARGET_FILEPATH, TEXTURE_FILEPATH_LIST, ORIGINAL_GIF_FRAMES_FILE_PATH_LIST, PAINTED_GIF_FRAMES_FULL_FOLDER_PATH = get_target_and_textures()
    print("\n")
    print('TARGET_FILEPATH  ',TARGET_FILEPATH)
    print('TEXTURE_FILEPATH_LIST    ', TEXTURE_FILEPATH_LIST)
    print('ORIGINAL_GIF_FRAMES_FILE_PATH_LIST   ', ORIGINAL_GIF_FRAMES_FILE_PATH_LIST) # original_gif_frames_file_path_list might be None 
    print('PAINTED_GIF_FRAMES_FULL_FOLDER_PATH',PAINTED_GIF_FRAMES_FULL_FOLDER_PATH)

    while True:
        ui_return_value = get_command_from_parameter_ui(TARGET_FILEPATH, target_gif_frames=ORIGINAL_GIF_FRAMES_FILE_PATH_LIST)
        command = ui_return_value["command"]

        # Case 1: User exit parameter UI
        if command == "user_closed_param_ui_window":
            print("User closed param ui window")
            break

        # Case 2: User reselects target and/or texture
        elif command == "reselect_target_texture":
            print("User wants to reselect target and texture")
            TARGET_FILEPATH, TEXTURE_FILEPATH_LIST, ORIGINAL_GIF_FRAMES_FILE_PATH_LIST, PAINTED_GIF_FRAMES_FULL_FOLDER_PATH = get_target_and_textures()

        # Case 3: User runs the hill climbing algorithm
        elif command == "run":
            print("Run hill climb algo with params\n")
            parameters = ui_return_value["parameters"]
            run_painting_algorithm(parameters)

        # Case 4: Error
        else:
            raise ValueError("Unknown command:", command)
