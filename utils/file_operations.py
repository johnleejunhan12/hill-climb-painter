import os
import shutil
from typing import Union, List

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
        # print(f"Folder '{folder_name}' already exists")
        return folder_path
    
    try:
        os.makedirs(folder_path)
        print(f"Created folder: {folder_name}")
        return folder_path
    except OSError as e:
        raise OSError(f"Failed to create folder '{folder_name}'. Reason: {e}")
    
def clear_folder_contents(folder_path: str, exclude_files: Union[str, List[str]] = None) -> str:
    """
    Clear all contents of an existing folder at the specified path, except for specified excluded files or directories.
    
    Args:
        folder_path (str): Full path to the folder to clear
        exclude_files (Union[str, List[str]], optional): A single file/directory path or a list of file/directory paths to exclude from deletion
    
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
    
    # Normalize exclude_files to a list
    if exclude_files is None:
        exclude_files = []
    elif isinstance(exclude_files, str):
        exclude_files = [exclude_files]
    elif not isinstance(exclude_files, list):
        raise ValueError("exclude_files must be a string or a list of strings")
    
    # Convert exclude_files to absolute paths to avoid path comparison issues
    exclude_paths = [os.path.abspath(path) for path in exclude_files]
    
    # Clear existing files and subdirectories, skipping excluded paths
    for filename in os.listdir(folder_path):
        file_path = os.path.abspath(os.path.join(folder_path, filename))
        if file_path in exclude_paths:
            continue
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
            raise Exception(f"Failed to clear folder at {folder_path}. Error deleting {file_path}: {e}")
    
    # Print cleared folder and excluded files
    if exclude_paths:
        excluded_files_str = ", ".join(os.path.basename(path) for path in exclude_paths)
        # print(f"Cleared folder: {folder_path}. Excluded files: {excluded_files_str}")
    else:
        #print(f"Cleared folder: {folder_path}")
        pass
    
    return folder_path


def copy_and_paste_file(source_file_path: str, destination_folder_full_path: str, overwrite_existing: bool = True) -> str:
    """
    Copy a file to a destination folder with configurable overwrite behavior.
    Does nothing if the source file is already in the destination folder.
    
    Args:
        source_file_path (str): Full path to the source file to copy
        destination_folder_full_path (str): Full path to the destination folder
        overwrite_existing (bool, optional): Whether to overwrite existing files. 
                                           Defaults to True. If False, appends "copy1", "copy2", etc.
    
    Returns:
        str: Full path to the copied file, or the source file path if it is already in the destination folder
    
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
    
    # Check if source file is already in the destination folder
    source_dir = os.path.dirname(os.path.abspath(source_file_path))
    destination_dir = os.path.abspath(destination_folder_full_path)
    if source_dir == destination_dir:
        # print(f"Source file is already in destination folder: {source_file_path}")
        return source_file_path
    
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
        # print(f"Copied file to: {destination_file_path}")
        return destination_file_path
    except OSError as e:
        raise OSError(f"Failed to copy file from {source_file_path} to {destination_file_path}. Reason: {e}")


def count_image_files(filepath):
    """Counts the number of image files with specific extensions in a directory.

    Args:
        filepath (str): The path to the directory to check.

    Returns:
        int: The number of files with .png, .jpg, .jpeg, or .gif extensions (case-insensitive).
        str: "Invalid directory path" if the provided filepath is not a valid directory.

    Note:
        Only files in the specified directory are counted (non-recursive).
        Subdirectories are ignored.
    """
    # Define the extensions to look for
    extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # Initialize counter
    count = 0
    # Check if the filepath is a valid directory
    if os.path.isdir(filepath):
        # Iterate through files in the directory
        for file in os.listdir(filepath):
            # Check if the file ends with one of the specified extensions
            if file.lower().endswith(extensions):
                count += 1
        return count
    else:
        return "Invalid directory path"

def get_first_image_file(filepath):
    """Returns the full path of the first image file in a directory, sorted alphabetically.

    Args:
        filepath (str): The path to the directory to check.

    Returns:
        str: The full path of the first file with .png, .jpg, .jpeg, or .gif extension.
        None: If no matching files are found.
        str: "Invalid directory path" if the provided filepath is not a valid directory.

    Note:
        Only files in the specified directory are considered (non-recursive).
        Files are sorted alphabetically to ensure consistent ordering.
    """
    # Define the extensions to look for
    extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # Check if the filepath is a valid directory
    if os.path.isdir(filepath):
        # Get list of files in the directory
        files = [f for f in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, f)) and f.lower().endswith(extensions)]
        # Sort files to ensure consistent order (alphabetical)
        files.sort()
        # Return the full path of the first file or None if no matching files
        return os.path.join(filepath, files[0]) if files else None
    else:
        return "Invalid directory path"

def all_files_are_png(filepath):
    """Checks if all files in a directory have the .png extension.

    Args:
        filepath (str): The path to the directory to check.

    Returns:
        bool: True if all files have the .png extension (case-insensitive), False otherwise.
              Also returns False if the directory is empty or invalid.

    Note:
        Only files in the specified directory are checked (non-recursive).
        Subdirectories are ignored.
    """
    # Check if the filepath is a valid directory
    if not os.path.isdir(filepath):
        return False
    
    # Get list of files (excluding directories)
    files = [f for f in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, f))]
    
    # If no files, return False
    if not files:
        return False
    
    # Check if all files end with .png (case-insensitive)
    return all(f.lower().endswith('.png') for f in files)

def get_image_file_paths(filepath):
    """Returns a list of full file paths for image files in a directory.

    Args:
        filepath (str): The path to the directory to check.

    Returns:
        list: A list of full file paths for files with .png, .jpg, .jpeg, or .gif extensions.
        list: ["Invalid directory path"] if the provided filepath is not a valid directory.

    Note:
        Only files in the specified directory are included (non-recursive).
        Subdirectories are ignored.
    """
    # Define the extensions to look for
    extensions = ('.png', '.jpg', '.jpeg', '.gif')
    # Initialize list for full file paths
    file_paths = []
    # Check if the filepath is a valid directory
    if os.path.isdir(filepath):
        # Iterate through items in the directory
        for item in os.listdir(filepath):
            # Get the full path
            full_path = os.path.join(filepath, item)
            # Check if it's a file and has the correct extension
            if os.path.isfile(full_path) and item.lower().endswith(extensions):
                file_paths.append(full_path)
        return file_paths
    else:
        return ["Invalid directory path"]