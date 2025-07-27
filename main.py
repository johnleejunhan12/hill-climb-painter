from user_interface.target_texture_select_ui import TargetTextureSelectorUI
from file_operations import *
from user_interface.parameter_ui import *
from utilities import extract_gif_frames_to_output_folder_and_get_approx_fps 


def get_target_and_textures(is_prompt_user_before_quit=False):
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

    select_target_and_texture_ui = TargetTextureSelectorUI(is_prompt_user_before_quit = is_prompt_user_before_quit,
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

    # Extract gif frames
    def is_gif_file(filepath):
        # Get the file extension (lowercase to handle .GIF, .gif, etc.)
        file_ext = os.path.splitext(filepath)[1].lower()
        return file_ext == '.gif'

    original_gif_frames = None

    if is_gif_file(target):
        # Create two folders to store original gif frames and painted frames. Folders are created if they do not already exist.
        original_gif_frames_full_folder_path = create_folder("original_gif_frames")
        painted_gif_frames_full_folder_path = create_folder("painted_gif_frames")
        # Clear the contents of these two folders accumulated from previous run
        clear_folder_contents(original_gif_frames_full_folder_path)
        clear_folder_contents(painted_gif_frames_full_folder_path)

        # Export gif frames as png file into the original_gif_frames folder and find the approximate fps of the gif.
        # If max_number_of_extracted_frames is lesser than number of frames in the gif, approx_fps will be smaller than the number of frames in gif to keep total duration roughly the same
        approx_fps = extract_gif_frames_to_output_folder_and_get_approx_fps(
            full_path_to_gif=target,
            max_number_of_extracted_frames=10000000000,
            output_folder=original_gif_frames_full_folder_path
        )

        # Create a list of full filepath to pngs inside the original_gif_frames
        original_gif_frames = []

        for item in sorted(os.listdir(original_gif_frames_full_folder_path), key=lambda x: x.lower()):
            if item.lower().endswith('.png'):
                full_path = os.path.join(original_gif_frames_full_folder_path, item)
                original_gif_frames.append(full_path) 

    return target, textures, original_gif_frames


if __name__ == "__main__":

    print(f"My __name__ is: {__name__}")
        
    target_filepath, texture_filepath_list, original_gif_frames_file_path_list = get_target_and_textures(is_prompt_user_before_quit=True)
    print("\n")
    print('target_filepath  ',target_filepath)
    print('texture_filepath_list    ', texture_filepath_list)
    print('original_gif_frames_file_path_list   ', original_gif_frames_file_path_list) # original_gif_frames_file_path_list might be None 

    while True:
        ui_return_value = get_command_from_parameter_ui(target_filepath, target_gif_frames=original_gif_frames_file_path_list)
        command = ui_return_value["command"]

        # Case 1: User exit parameter UI
        if command == "user_closed_param_ui_window":
            print("User closed param ui window")
            break

        # Case 2: User reselects target and/or texture
        elif command == "reselect_target_texture":
            print("User wants to reselect target and texture")
            new_target_filepath, texture_filepath_list, original_gif_frames_file_path_list = get_target_and_textures(is_prompt_user_before_quit=True)

        # Case 3: User runs the hill climbing algorithm
        elif command == "run":
            print("Run hill climb algo with params")
            parameters = ui_return_value["parameters"]
            for k,v in parameters.items():
                print(k,v)

        # Case 4: Error
        else:
            raise ValueError("Unknown command:", command)
