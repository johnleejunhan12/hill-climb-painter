
from target_texture_select_ui import TargetTextureSelectorUI
from file_operations import *

if __name__ == "__main__":
    select_target_and_texture_ui = TargetTextureSelectorUI()
    target_image_full_filepath, list_of_texture_images_full_path = select_target_and_texture_ui.run_and_get_selection()

    target_folder_fullpath = create_folder("target")
    clear_folder_contents(target_folder_fullpath)
    target = copy_and_paste_file(target_image_full_filepath, target_folder_fullpath)

    texture_folder_fullpath = create_folder("texture")
    textures = []
    clear_folder_contents(texture_folder_fullpath)
    for texture_path in list_of_texture_images_full_path:
        textures.append(copy_and_paste_file(texture_path, texture_folder_fullpath))


    # get full filepath of target
    print(target, textures)