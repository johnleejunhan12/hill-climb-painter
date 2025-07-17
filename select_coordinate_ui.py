import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

def choose_coordinate_from_image_user_interface(image_filepaths, resize_shorter_side_of_image):
    """
    Display a list of PNG images sequentially and allow user to select coordinates with mouse click.
    
    Args:
        image_filepaths (list): List of full paths to PNG image files
        resize_shorter_side_of_image (int): Target size in pixels for the shorter side of each image
        
    Returns:
        list: List of (x, y) coordinate tuples as integers for each image
        
    Raises:
        FileNotFoundError: If any image file doesn't exist
        Exception: If any image cannot be loaded or displayed
        ValueError: If image_filepaths is empty or resize_shorter_side_of_image is not positive
    """
    
    # Validate inputs
    if not image_filepaths:
        raise ValueError("image_filepaths cannot be empty")
    
    if not isinstance(resize_shorter_side_of_image, int) or resize_shorter_side_of_image <= 0:
        raise ValueError("resize_shorter_side_of_image must be a positive integer")
    
    # Validate all files exist
    for filepath in image_filepaths:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Image file not found: {filepath}")
    
    # Variables to store results
    selected_coordinates = []
    current_image_index = 0
    
    # Variables for current selection
    selected_x = None
    selected_y = None
    coordinate_selected = False
    
    # Create main window
    root = tk.Tk()
    root.title("Select Coordinates on Images")
    root.resizable(False, False)
    
    # Variables for UI components
    canvas = None
    photo = None
    selection_marker = None
    coord_label = None
    confirm_button = None
    progress_label = None
    
    def resize_image(image, target_shorter_side):
        """Resize image so shorter side equals target_shorter_side while maintaining aspect ratio"""
        width, height = image.size
        
        # Calculate the scale factor based on the shortest side
        if height < width:
            scale_factor = target_shorter_side / height
        else:
            scale_factor = target_shorter_side / width
        
        # Calculate new dimensions
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def load_current_image():
        """Load and display the current image"""
        nonlocal canvas, photo, selection_marker, current_image_index
        
        try:
            # Load and resize image
            image = Image.open(image_filepaths[current_image_index])
            resized_image = resize_image(image, resize_shorter_side_of_image)
            photo = ImageTk.PhotoImage(resized_image)
            
            # Update or create canvas
            if canvas:
                canvas.destroy()
            
            canvas = tk.Canvas(root, width=resized_image.width, height=resized_image.height)
            canvas.pack(pady=10)
            
            # Display image on canvas
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            
            # Reset selection state
            selection_marker = None
            reset_selection_state()
            
            # Bind click events to canvas
            canvas.bind("<Button-1>", on_canvas_click)        # Left click
            canvas.bind("<Button-3>", on_canvas_right_click)   # Right click
            
            # Update progress
            progress_label.config(text=f"Image {current_image_index + 1} of {len(image_filepaths)}")
            
            # Update window size
            root.update_idletasks()
            width = root.winfo_reqwidth()
            height = root.winfo_reqheight()
            x = (root.winfo_screenwidth() // 2) - (width // 2)
            y = (root.winfo_screenheight() // 2) - (height // 2)
            root.geometry(f"{width}x{height}+{x}+{y}")
            
            return resized_image
            
        except Exception as e:
            raise Exception(f"Error loading image {image_filepaths[current_image_index]}: {str(e)}")
    
    def reset_selection_state():
        """Reset selection state for new image"""
        nonlocal selected_x, selected_y, coordinate_selected
        
        selected_x = None
        selected_y = None
        coordinate_selected = False
        
        # Reset UI
        coord_label.config(text="Click on image to select coordinates")
        confirm_button.config(state=tk.DISABLED)
    
    def on_canvas_click(event):
        nonlocal selected_x, selected_y, selection_marker
        
        # Store coordinates
        selected_x = event.x
        selected_y = event.y
        
        # Remove previous marker if exists
        if selection_marker:
            canvas.delete(selection_marker)
        
        # Create visual marker at selected point
        marker_size = 10
        selection_marker = canvas.create_oval(
            event.x - marker_size//2, event.y - marker_size//2,
            event.x + marker_size//2, event.y + marker_size//2,
            fill="red", outline="white", width=2
        )
        
        # Update coordinate display
        coord_label.config(text=f"Translate vector field origin to ({event.x}, {event.y})")
        confirm_button.config(state=tk.NORMAL)
    
    def on_canvas_right_click(event):
        nonlocal selected_x, selected_y, selection_marker, coordinate_selected
        
        # Store coordinates
        selected_x = event.x
        selected_y = event.y
        
        # Remove previous marker if exists
        if selection_marker:
            canvas.delete(selection_marker)
        
        # Create visual marker at selected point
        marker_size = 10
        selection_marker = canvas.create_oval(
            event.x - marker_size//2, event.y - marker_size//2,
            event.x + marker_size//2, event.y + marker_size//2,
            fill="red", outline="white", width=2
        )
        
        # Update coordinate display
        coord_label.config(text=f"Translate vector field origin to ({event.x}, {event.y})")
        
        # Instant select - automatically confirm
        on_confirm()
    
    def on_select_center():
        nonlocal selected_x, selected_y, selection_marker
        
        # Get current image dimensions
        current_width = canvas.winfo_width()
        current_height = canvas.winfo_height()
        
        # Calculate center coordinates
        center_x = current_width // 2
        center_y = current_height // 2
        
        # Store coordinates
        selected_x = center_x
        selected_y = center_y
        
        # Remove previous marker if exists
        if selection_marker:
            canvas.delete(selection_marker)
        
        # Create visual marker at center point
        marker_size = 10
        selection_marker = canvas.create_oval(
            center_x - marker_size//2, center_y - marker_size//2,
            center_x + marker_size//2, center_y + marker_size//2,
            fill="red", outline="white", width=2
        )
        
        # Update coordinate display
        coord_label.config(text=f"Translate vector field origin to ({center_x}, {center_y})")
        confirm_button.config(state=tk.NORMAL)
    
    def on_reset():
        nonlocal selected_x, selected_y, selection_marker
        
        # Clear coordinates
        selected_x = None
        selected_y = None
        
        # Remove marker if exists
        if selection_marker:
            canvas.delete(selection_marker)
            selection_marker = None
        
        # Reset UI to original state
        coord_label.config(text="Click on image to select coordinates")
        confirm_button.config(state=tk.DISABLED)
    
    def on_confirm():
        nonlocal current_image_index, coordinate_selected
        
        if selected_x is not None and selected_y is not None:
            # Store the coordinates for this image
            selected_coordinates.append((int(selected_x), int(selected_y)))
            
            # Move to next image
            current_image_index += 1
            
            # Check if we've processed all images
            if current_image_index >= len(image_filepaths):
                # All images processed, exit
                coordinate_selected = True
                root.quit()
            else:
                # Load next image
                load_current_image()
    
    try:
        # Create control frame first
        control_frame = tk.Frame(root)
        control_frame.pack(pady=10)
        
        # Progress label
        progress_label = tk.Label(control_frame, text="", font=("Arial", 12), fg="blue")
        progress_label.pack(pady=5)
        
        # Coordinate display label
        coord_label = tk.Label(control_frame, text="Click on image to select coordinates", 
                              font=("Arial", 12))
        coord_label.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(control_frame)
        button_frame.pack(pady=10)
        
        # Confirm button (initially disabled)
        confirm_button = tk.Button(button_frame, text="Confirm", command=on_confirm,
                                  bg="green", fg="white", font=("Arial", 12),
                                  state=tk.DISABLED, padx=20)
        confirm_button.pack(side=tk.LEFT, padx=5)
        
        # Select center button
        center_button = tk.Button(button_frame, text="Select Center", command=on_select_center,
                                 bg="blue", fg="white", font=("Arial", 12), padx=20)
        center_button.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        reset_button = tk.Button(button_frame, text="Reset", command=on_reset,
                               bg="orange", fg="white", font=("Arial", 12), padx=20)
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = tk.Label(control_frame, 
                               text="Left click to select coordinates, right click for instant select, use Select Center for center point",
                               font=("Arial", 10), fg="gray")
        instructions.pack(pady=5)
        
        # Load first image
        load_current_image()
        
        # Start GUI event loop
        root.mainloop()
        
    except Exception as e:
        root.destroy()
        raise Exception(f"Error in user interface: {str(e)}")
    
    finally:
        # Clean up
        root.destroy()
    
    # Return coordinates if all images were processed
    if coordinate_selected and len(selected_coordinates) == len(image_filepaths):
        return selected_coordinates
    else:
        raise Exception("Coordinate selection was cancelled or incomplete")

# Example usage:
if __name__ == "__main__":
    try:
        # Example usage - replace with your actual image paths
        image_paths = ["target_image/chameleon.png", "target_image/circles.png", "target_image/dark.png"]
        target_size = 400  # Resize shorter side to 400 pixels
        
        coordinates = choose_coordinate_from_image_user_interface(image_paths, target_size)
        
        for i, (x, y) in enumerate(coordinates):
            print(f"Image {i+1}: Selected coordinates ({x}, {y})")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")