import os
import shutil


def create_folder(folder_name: str) -> str:
    """
    Create a folder in the current working directory. If the folder already exists, 
    does nothing and returns the existing folder path.
    
    Args:
        folder_name (str): Name of the folder to create
    
    Returns:
        str: Full path to the created or existing folder
    
    Raises:
        OSError: If there's an error creating the folder
        NotADirectoryError: If the path exists but is not a directory
    """
    # Define folder path in current working directory
    folder_path = os.path.join(os.getcwd(), folder_name)
    
    if os.path.exists(folder_path):
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"'{folder_name}' exists but is not a directory")
        print(f"Folder '{folder_name}' already exists")
        return folder_path
    
    try:
        os.makedirs(folder_path)
        print(f"Created folder: {folder_name}")
        return folder_path
    except OSError as e:
        raise OSError(f"Failed to create folder '{folder_name}'. Reason: {e}")


def clear_folder_contents(folder_path: str) -> str:
    """
    Clear all contents of an existing folder at the specified path.
    
    Args:
        folder_path (str): Full path to the folder to clear
    
    Returns:
        str: Full path to the cleared folder
    
    Raises:
        FileNotFoundError: If the folder doesn't exist
        NotADirectoryError: If the path exists but is not a directory
        Exception: If there's an error clearing the folder contents
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder does not exist at {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Path exists but is not a directory: {folder_path}")
    
    # Clear existing files and subdirectories
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
            raise Exception(f"Failed to clear folder at {folder_path}. Error deleting {file_path}: {e}")
    
    print(f"Cleared folder: {folder_path}")
    return folder_path


def copy_and_paste_file(source_file_path: str, destination_folder_full_path: str, overwrite_existing: bool = True) -> str:
    """
    Copy a file to a destination folder with configurable overwrite behavior.
    
    Args:
        source_file_path (str): Full path to the source file to copy
        destination_folder_full_path (str): Full path to the destination folder
        overwrite_existing (bool, optional): Whether to overwrite existing files. 
                                           Defaults to True. If False, appends "copy1", "copy2", etc.
    
    Returns:
        str: Full path to the copied file
    
    Raises:
        FileNotFoundError: If the source file doesn't exist
        NotADirectoryError: If the destination path exists but is not a directory
        OSError: If there's an error during the copy operation
    """
    # Check if source file exists
    if not os.path.exists(source_file_path):
        raise FileNotFoundError(f"Source file does not exist: {source_file_path}")
    
    # Check if source is a file (not a directory)
    if not os.path.isfile(source_file_path):
        raise OSError(f"Source path is not a file: {source_file_path}")
    
    # Check if destination folder exists
    if not os.path.exists(destination_folder_full_path):
        raise FileNotFoundError(f"Destination folder does not exist: {destination_folder_full_path}")
    
    # Check if destination is a directory
    if not os.path.isdir(destination_folder_full_path):
        raise NotADirectoryError(f"Destination path is not a directory: {destination_folder_full_path}")
    
    # Get the filename from the source path
    filename = os.path.basename(source_file_path)
    name, extension = os.path.splitext(filename)
    
    # Determine the destination file path
    if overwrite_existing:
        destination_file_path = os.path.join(destination_folder_full_path, filename)
    else:
        # Find the next available copy number
        copy_number = 1
        while True:
            if copy_number == 1:
                new_filename = f"{name}_copy1{extension}"
            else:
                new_filename = f"{name}_copy{copy_number}{extension}"
            
            test_path = os.path.join(destination_folder_full_path, new_filename)
            if not os.path.exists(test_path):
                destination_file_path = test_path
                break
            copy_number += 1
    
    try:
        shutil.copy2(source_file_path, destination_file_path)
        print(f"Copied file to: {destination_file_path}")
        return destination_file_path
    except OSError as e:
        raise OSError(f"Failed to copy file from {source_file_path} to {destination_file_path}. Reason: {e}")




