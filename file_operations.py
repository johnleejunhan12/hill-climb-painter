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




