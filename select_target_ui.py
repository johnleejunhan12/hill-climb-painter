import tkinter as tk
from tkinter import filedialog, messagebox
import os


class FileSelectorUI:
    """
    A class for selecting files through a GUI dialog with configurable file type filters.
    
    This class allows users to select files with specific extensions. It supports
    both single extension (e.g., '.png') and multiple extensions (e.g., ['.png', '.jpg', '.gif']).
    The file dialog will filter files based on the provided extensions and validate
    the selected file against the allowed extensions.
    
    Supports both single file selection and multiple file selection modes.
    """
    
    def __init__(self, allowed_extensions, is_select_multiple_files=False, window_title=None, window_position=None, custom_filepath=None):
        """
        Initialize the FileSelectorUI.
        
        Args:
            allowed_extensions (str or list): Single extension (e.g., '.png') or 
                                            list of extensions (e.g., ['.png', '.jpg', '.gif'])
            is_select_multiple_files (bool): If True, allows selecting multiple files.
                                           If False, allows selecting only one file.
                                           Defaults to False.
            window_title (str, optional): Custom title for the file dialog window.
                                        If None, uses default title with extensions.
                                        Defaults to None.
            window_position (tuple, optional): Position for the file dialog window as (x, y) coordinates.
                                            If None, uses system default position.
                                            Defaults to None.
            custom_filepath (str, optional): If provided, the file dialog will open at this path. If the path is invalid or inaccessible, a warning is printed and the default Downloads folder is used. If None, the dialog opens in the Downloads folder. Defaults to None.
        """
        self.root = None
        self.is_select_multiple_files = is_select_multiple_files
        self.window_title = window_title
        self.window_position = window_position
        self.custom_filepath = custom_filepath
        
        # Convert single extension to list for consistent handling
        if isinstance(allowed_extensions, str):
            self.allowed_extensions = [allowed_extensions.lower()]
        else:
            self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
    
    def get_downloads_folder(self):
        """
        Get the Downloads folder path for the current user.
        Returns the Downloads folder path if found, otherwise returns current working directory.
        """
        # Get the user's home directory
        home_dir = os.path.expanduser("~")
        
        # Common Downloads folder paths across different operating systems
        downloads_paths = [
            os.path.join(home_dir, "Downloads"),  # Windows, macOS, Linux
            os.path.join(home_dir, "downloads"),  # Some Linux distributions
            os.path.join(home_dir, "Desktop", "Downloads"),  # Some macOS setups
        ]
        
        # Check if any of the Downloads paths exist
        for path in downloads_paths:
            if os.path.exists(path) and os.path.isdir(path):
                return path
        
        # Fallback to current working directory
        return os.getcwd()
    
    def is_valid_file(self, file_path):
        """
        Check if the selected file has an allowed extension.
        
        Args:
            file_path (str): Path to the file to check
            
        Returns:
            bool: True if file has an allowed extension, False otherwise
        """
        if not file_path:
            return False
        
        # Get file extension and convert to lowercase
        file_extension = os.path.splitext(file_path)[1].lower()
        
        return file_extension in self.allowed_extensions
    
    def validate_files(self, file_paths):
        """
        Validate a list of file paths against allowed extensions.
        
        Args:
            file_paths (list): List of file paths to validate
            
        Returns:
            tuple: (bool, list) - (all_valid, invalid_files)
        """
        if not file_paths:
            return True, []
        
        invalid_files = []
        for file_path in file_paths:
            if not self.is_valid_file(file_path):
                invalid_files.append(os.path.basename(file_path))
        
        return len(invalid_files) == 0, invalid_files
    
    def _cleanup(self):
        """Internal method to clean up the Tkinter root window."""
        if self.root:
            try:
                self.root.destroy()
                self.root = None
            except:
                pass
    
    def select_file(self):
        """
        Open a file dialog to select file(s) with allowed extensions.
        Keeps prompting until valid file(s) are selected or user cancels.
        If custom_filepath is provided and valid, the dialog opens there. Otherwise, it opens in the Downloads folder. If neither is accessible, prints a warning and uses the current working directory.
        
        Returns:
            str or list: Single file path (str) if is_select_multiple_files=False,
                        List of file paths (list) if is_select_multiple_files=True,
                        None if cancelled
        """
        # Create the main window (hidden)
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        
        # Position the window if coordinates are provided
        if self.window_position:
            x, y = self.window_position
            self.root.geometry(f"+{x}+{y}")
        
        # Determine the initial directory
        initial_dir = None
        if self.custom_filepath is not None:
            try:
                if os.path.exists(self.custom_filepath) and os.path.isdir(self.custom_filepath):
                    initial_dir = self.custom_filepath
                else:
                    print(f"[Warning] Provided custom_filepath '{self.custom_filepath}' is not a valid directory. Falling back to Downloads folder.")
            except Exception as e:
                print(f"[Warning] Error accessing custom_filepath '{self.custom_filepath}': {e}. Falling back to Downloads folder.")
        if initial_dir is None:
            try:
                initial_dir = self.get_downloads_folder()
            except Exception as e:
                print(f"[Warning] Error accessing Downloads folder: {e}. Using current working directory.")
                initial_dir = os.getcwd()
        
        # Create file type filters for the dialog
        file_types = []
        
        # Add combined filter for all extensions
        if len(self.allowed_extensions) > 1:
            # Create a combined filter string like "*.png;*.jpg;*.gif"
            combined_filter = ";".join([f"*{ext}" for ext in self.allowed_extensions])
            file_types.append(("Supported files", combined_filter))
        
        # Add individual filters for each extension
        for ext in self.allowed_extensions:
            file_types.append((f"{ext.upper()[1:]} files", f"*{ext}"))
        
        # Add "All files" filter
        file_types.append(("All files", "*.*"))
        
        # Create title with allowed extensions
        extensions_str = ", ".join(self.allowed_extensions)
        selection_mode = "files" if self.is_select_multiple_files else "file"
        
        # Use custom title if provided, otherwise use default title
        if self.window_title:
            title = self.window_title
        else:
            title = f"Select {selection_mode} ({extensions_str})"
        
        while True:
            # Set up the file dialog based on selection mode
            if self.is_select_multiple_files:
                file_paths = filedialog.askopenfilenames(
                    title=title,
                    filetypes=file_types,
                    initialdir=initial_dir
                )
            else:
                file_path = filedialog.askopenfilename(
                    title=title,
                    filetypes=file_types,
                    initialdir=initial_dir
                )
                file_paths = [file_path] if file_path else []
            
            # If user cancels, cleanup and return None
            if not file_paths:
                self._cleanup()
                return None
            
            # Validate selected files
            all_valid, invalid_files = self.validate_files(file_paths)
            
            if all_valid:
                self._cleanup()
                # Return appropriate type based on selection mode
                if self.is_select_multiple_files:
                    return list(file_paths)
                else:
                    return file_paths[0]  # Return single file path as string
            else:
                # Show error message and ask user to reselect
                extensions_list = ", ".join(self.allowed_extensions)
                invalid_files_str = ", ".join(invalid_files)
                messagebox.showerror(
                    "Invalid File Type",
                    f"Please select files with one of these extensions: {extensions_list}\n\nInvalid files: {invalid_files_str}"
                )
                # Continue the loop to ask for another selection


if __name__ == "__main__":
    # Example usage with single file selection and custom title
    print("=== Single File Selection Example ===")
    selector_single = FileSelectorUI(
        ['.png', '.jpg', '.jpeg', '.gif'], 
        is_select_multiple_files=False,
        window_title="Choose target image or gif",
        window_position=(100, 100)  # Position at coordinates (100, 100)
    )
    selected_file = selector_single.select_file()
    
    if selected_file:
        print(f"✅ Successfully selected file: {selected_file}")
    else:
        print("❌ No file selected.")
    
    print("\n=== Multiple File Selection Example ===")
    # Example usage with multiple file selection and default title
    selector_multiple = FileSelectorUI(
        ['.png', '.jpg', '.jpeg', '.gif'],
        is_select_multiple_files=True,        
        window_title="Choose texture images (can choose multiple)",
        window_position=(500, 500)  # Position at coordinates (200, 200)
    )
    selected_files = selector_multiple.select_file()
    
    if selected_files:
        print(f"✅ Successfully selected {len(selected_files)} files:")
        for i, file_path in enumerate(selected_files, 1):
            print(f"  {i}. {file_path}")
    else:
        print("❌ No files selected.")

    print("\n=== Custom Filepath Test Case ===")
    # Test case using custom_filepath
    selector_custom = FileSelectorUI(
        ['.png', '.jpg', '.jpeg', '.gif'],
        is_select_multiple_files=True,
        window_title="Choose from custom filepath (texture_presets)",
        window_position=(300, 300),
        custom_filepath="C:/Git Repos/hill-climb-painter/texture_presets"
    )
    selected_custom_files = selector_custom.select_file()
    if selected_custom_files:
        print(f"✅ Successfully selected {len(selected_custom_files)} files from custom filepath:")
        for i, file_path in enumerate(selected_custom_files, 1):
            print(f"  {i}. {file_path}")
    else:
        print("❌ No files selected from custom filepath.")

