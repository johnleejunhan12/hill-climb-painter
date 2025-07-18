import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
from typing import Union, List, Tuple

class UserClosedGUIWindow(Exception):
    """Custom exception for when user closes the GUI window prematurely"""
    pass

class CoordinateSelectorUI:
    def __init__(self, image_filepath: Union[str, List[str]], resize_shorter_side_of_image: int, replay_fps: int = 10):
        """
        Initialize the CoordinateSelectorUI class.
    
    Args:
            image_filepath: Path to a single image or list of paths to multiple images
            resize_shorter_side_of_image: Target size in pixels for the shorter side of each image
            replay_fps: Frames per second for the replay slideshow (if multiple images)
        """
        # Convert single filepath to list for uniform handling
        self.image_paths = [image_filepath] if isinstance(image_filepath, str) else image_filepath
        self.target_size = resize_shorter_side_of_image
        self.replay_fps = replay_fps
        self.selected_coordinates = []
        self.current_image_index = 0
        self.long_hold_selection_delay = 50  # Default value before slider sets it
        self.right_click_press_time = 0
        self.last_long_hold_selection_time = 0
        
        # Validate image paths exist
        self._validate_image_paths()
        
        # Load and resize all images upfront
        self._load_and_resize_images()
        
        # Calculate maximum window dimensions needed to display all images
        self._calculate_window_dimensions()
        
        # Initialize Tkinter root window
        self.root = tk.Tk()
        self.root.title("Select coordinates")
                    
        # Setup the UI components
        self._setup_ui()
        
        # Display the first image
        self._display_current_image()
        
        # Track if window was closed properly
        self.window_closed_properly = False

        # For replay window
        self.replay_window = None
        self.replay_running = False
        self.replay_after_id = None
    
    def _validate_image_paths(self):
        """Check that all image paths exist and are valid PNG files"""
        for path in self.image_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image file not found: {path}")
            if not path.lower().endswith('.png'):
                raise ValueError(f"File is not a PNG image: {path}")
    
    def _load_and_resize_images(self):
        """Load and resize all images according to target shorter side length"""
        self.images = []
        self.resized_images = []
        
        for path in self.image_paths:
            try:
                image = Image.open(path)
                self.images.append(image)
                
                # Resize the image
                resized = self._resize_image(image, self.target_size)
                self.resized_images.append(resized)
            except Exception as e:
                raise RuntimeError(f"Error loading image {path}: {str(e)}")
    
    def _resize_image(self, image: Image.Image, target_shorter_side: int) -> Image.Image:
        """
        Resize image so shorter side equals target_shorter_side while maintaining aspect ratio.
        
        Args:
            image: PIL Image object to resize
            target_shorter_side: Target size for the shorter side of the image
            
        Returns:
            Resized PIL Image object
        """
        width, height = image.size  # Get original image dimensions
        if height < width:
            scale_factor = target_shorter_side / height  # Scale based on height if it's the shorter side
        else:
            scale_factor = target_shorter_side / width   # Scale based on width if it's the shorter side
        new_width = int(width * scale_factor)           # Calculate new width
        new_height = int(height * scale_factor)         # Calculate new height
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)  # Resize with high-quality filter
    
    def _calculate_window_dimensions(self):
        """Calculate the maximum window dimensions needed to display all images"""
        self.max_width = max(img.width for img in self.resized_images)
        self.max_height = max(img.height for img in self.resized_images)
        
        # Add some padding for UI elements
        self.window_width = self.max_width + 40
        self.window_height = self.max_height + 150  # Extra space for buttons and labels
    
    def _setup_ui(self):
        """Set up all the UI components"""
        # Create main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)

        # Set background color for main frame
        self.root.configure(bg="#f7f7fa")
        self.main_frame.configure(bg="#f7f7fa")

        # Title label
        self.title_label = ttk.Label(
            self.main_frame,
            text="Shift vector field origin to (?, ?)",
            font=('Arial', 15, 'bold'),
            background="#f7f7fa"
        )
        self.title_label.pack(pady=(0, 6))

        # Instruction label above the image
        self.instruction_label = ttk.Label(
            self.main_frame,
            text="Hold right click for faster selection. Press 'Clear all previous selections' to start over.",
            font=('Arial', 11, 'italic'),
            foreground='blue',
            background="#f7f7fa"
        )
        self.instruction_label.pack(pady=(0, 10))
        
        # Create canvas for image display
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.max_width,
            height=self.max_height,
            bg='white',
            highlightthickness=2,
            highlightbackground="#b0b0b0",
            relief=tk.RIDGE,
            bd=2
        )
        self.canvas.pack(pady=(0, 10))
        
        # Label for instructions and coordinate display
        self.coord_label = ttk.Label(
            self.main_frame,
            text="Select (x,y) coordinate",
            font=('Arial', 12),
            background="#f7f7fa"
        )
        self.coord_label.pack(pady=(0, 8))
        
        button_frame = tk.Frame(self.main_frame, bg="#f7f7fa")
        button_frame.pack(pady=(0, 12))
        self.confirm_button = tk.Button(
            button_frame,
            text="Confirm Selection",
            command=self._confirm_selection,
            state=tk.DISABLED,
            bg='green',
            fg='white',
            font=('Arial', 12, 'bold'),
            activebackground='#2ecc40',
            activeforeground='white',
            width=16,
            height=2,
            bd=0,
            relief=tk.FLAT
        )
        self.confirm_button.pack(side=tk.LEFT, padx=(0, 12))
        self.clear_button = tk.Button(
            button_frame,
            text="Clear all previous selections",
            command=self._clear_all_selections,
            bg='red',
            fg='white',
            font=('Arial', 12, 'bold'),
            activebackground='#e74c3c',
            activeforeground='white',
            width=22,
            height=2,
            bd=0,
            relief=tk.FLAT
        )
        self.clear_button.pack(side=tk.LEFT)
        
        # Slider for long hold selection delay
        self.slider_frame = tk.Frame(self.main_frame, bg="#f7f7fa")
        self.slider_frame.pack(pady=(0, 10))
        ttk.Label(
            self.slider_frame,
            text="Long hold selection delay (ms):",
            font=('Arial', 10),
            background="#f7f7fa"
        ).pack(side=tk.LEFT)
        self.delay_slider = ttk.Scale(
            self.slider_frame,
            from_=20,
            to=500,
            value=50,
            command=self._update_long_hold_delay,
            length=180
        )
        self.delay_slider.pack(side=tk.LEFT, padx=5)
        self.delay_value_label = ttk.Label(
            self.slider_frame,
            text="50",
            font=('Arial', 10, 'bold'),
            background="#f7f7fa"
        )
        self.delay_value_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self._on_left_click)  # Left click press
        self.canvas.bind("<B1-Motion>", self._on_left_drag)  # Left click drag
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)  # Left click release
        
        self.canvas.bind("<Button-3>", self._on_right_click)  # Right click press
        self.canvas.bind("<B3-Motion>", self._on_right_drag)  # Right click drag
        self.canvas.bind("<ButtonRelease-3>", self._on_right_release)  # Right click release
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
    
    def _update_long_hold_delay(self, value):
        """Update the long hold selection delay based on slider value"""
        self.long_hold_selection_delay = int(float(value))
        self.delay_value_label.config(text=str(self.long_hold_selection_delay))
    
    def _display_current_image(self):
        """Display the current image on the canvas"""
        # Clear previous drawings
        self.canvas.delete("all")
        
        # Get current image
        current_image = self.resized_images[self.current_image_index]
        self.current_image_tk = ImageTk.PhotoImage(current_image)
        
        # Calculate position to center the image
        x_pos = (self.max_width - current_image.width) // 2
        y_pos = (self.max_height - current_image.height) // 2
        
        # Display the image
        self.image_on_canvas = self.canvas.create_image(
            x_pos, y_pos, 
            anchor=tk.NW, 
            image=self.current_image_tk
        )
        
        # Store image position and dimensions for coordinate calculation
        self.image_x = x_pos
        self.image_y = y_pos
        self.image_width = current_image.width
        self.image_height = current_image.height
        
        # Reset selection state
        self.selected_x = None
        self.selected_y = None
        self.confirm_button.config(state=tk.DISABLED, bg='green')
        
        # Update status label
        self.coord_label.config(text=f"Image {self.current_image_index + 1}/{len(self.image_paths)}")
        # Reset title label
        if hasattr(self, 'title_label'):
            self.title_label.config(text="Shift vector field origin to (?,?)")
    
    def _get_image_coordinates(self, event):
        """
        Convert canvas coordinates to image coordinates with boundary checking.
        
        Args:
            event: Mouse event containing x,y coordinates
            
        Returns:
            Tuple of (x, y) coordinates within image bounds, or None if outside image
        """
        # Calculate coordinates relative to image
        img_x = event.x - self.image_x
        img_y = event.y - self.image_y
        
        # Check if coordinates are within image bounds
        if 0 <= img_x < self.image_width and 0 <= img_y < self.image_height:
            return int(img_x), int(img_y)
        
        # If outside bounds, clamp to nearest valid coordinate
        img_x = max(0, min(img_x, self.image_width - 1))
        img_y = max(0, min(img_y, self.image_height - 1))
        return int(img_x), int(img_y)
    
    def _update_selection(self, x, y):
        """
        Update the selected coordinate and display it on the canvas.
        
        Args:
            x: x-coordinate within image
            y: y-coordinate within image
        """
        # Store the selected coordinates
        self.selected_x = x
        self.selected_y = y
        
        # Clear previous crosshair
        self.canvas.delete("crosshair")
        
        # Calculate canvas coordinates
        canvas_x = self.image_x + x
        canvas_y = self.image_y + y
        
        # Draw red crosshair
        cross_size = 10
        self.canvas.create_line(
            canvas_x - cross_size, canvas_y, 
            canvas_x + cross_size, canvas_y,
            fill="red", tags="crosshair", width=2
        )
        self.canvas.create_line(
            canvas_x, canvas_y - cross_size, 
            canvas_x, canvas_y + cross_size,
            fill="red", tags="crosshair", width=2
        )
        

        # Update title label
        if hasattr(self, 'title_label'):
            self.title_label.config(text=f"Shift vector field origin to ({x}, {y})")
        
        # Enable confirm button and change color to green
        self.confirm_button.config(state=tk.NORMAL, bg='green')
    
    def _on_left_click(self, event):
        """Handle left mouse button click (initial press)"""
        coords = self._get_image_coordinates(event)
        if coords:
            x, y = coords
            self._update_selection(x, y)
    
    def _on_left_drag(self, event):
        """Handle left mouse button drag (moving while pressed)"""
        coords = self._get_image_coordinates(event)
        if coords:
            x, y = coords
            self._update_selection(x, y)
    
    def _on_left_release(self, event):
        """Handle left mouse button release"""
        pass  # No special action needed on release
    
    def _on_right_click(self, event):
        """Handle right mouse button click (initial press)"""
        self.right_click_press_time = time.time()
        self.last_long_hold_selection_time = 0
        self._long_hold_active = True  # Track if long hold is active
        self._long_hold_loop_event_x = event.x
        self._long_hold_loop_event_y = event.y
        
        # Immediately select point on right click
        coords = self._get_image_coordinates(event)
        if coords:
            x, y = coords
            self._update_selection(x, y)
            self._confirm_selection_if_last_image()
        # Start long hold loop
        self._start_long_hold_loop()
    
    def _on_right_drag(self, event):
        """Handle right mouse button drag (moving while pressed)"""
        current_time = time.time()
        press_duration = current_time - self.right_click_press_time
        coords = self._get_image_coordinates(event)
        if not coords:
            return
        x, y = coords
        self._update_selection(x, y)
        # Update stored event position for long hold loop
        self._long_hold_loop_event_x = event.x
        self._long_hold_loop_event_y = event.y
    
    def _on_right_release(self, event):
        """Handle right mouse button release"""
        self.right_click_press_time = 0
        self._long_hold_active = False  # Stop long hold loop
    
    def _confirm_selection_if_last_image(self):
        """
        Confirm selection if this is the last image, otherwise just confirm and move to next.
        This is used for right-click rapid selection.
        """
        if self.selected_x is not None and self.selected_y is not None:
            self.selected_coordinates.append((self.selected_x, self.selected_y))
            
            if self.current_image_index == len(self.image_paths) - 1:
                # Last image - show replay window if multiple images
                if len(self.image_paths) > 1:
                    self._show_replay_window()
                    # Reset right click state
                    self.right_click_press_time = 0
                    self._long_hold_active = False
                else:
                    self.window_closed_properly = True
                    self.root.quit()
                    self.root.destroy()
            else:
                # Move to next image
                self.current_image_index += 1
                self._display_current_image()
    
    def _confirm_selection(self):
        """Handle confirm button click - store selection and move to next image or close"""
        if self.selected_x is not None and self.selected_y is not None:
            self.selected_coordinates.append((self.selected_x, self.selected_y))
            
            if self.current_image_index == len(self.image_paths) - 1:
                # Last image - show replay window if multiple images
                if len(self.image_paths) > 1:
                    self._show_replay_window()
                    # Reset right click state
                    self.right_click_press_time = 0
                    self._long_hold_active = False
                else:
                    self.window_closed_properly = True
                    self.root.quit()
                    self.root.destroy()
            else:
                # Move to next image
                self.current_image_index += 1
                self._display_current_image()
    
    def _clear_all_selections(self):
        """Clear all previous selections and restart from the first image."""
        self.selected_coordinates = []
        self.current_image_index = 0
        self.selected_x = None
        self.selected_y = None
        self._display_current_image()
        # Reset title label
        if hasattr(self, 'title_label'):
            self.title_label.config(text="Shift vector field origin to (?,?)")
    
    def _on_window_close(self):
        """Handle window close event before all selections are made"""
        self.root.quit()
    
    def _start_long_hold_loop(self):
        """Start the long hold loop for repeated selection confirmation."""
        def loop():
            if not getattr(self, '_long_hold_active', False):
                return
            current_time = time.time()
            press_duration = current_time - self.right_click_press_time
            # Only start rapid selection after 300ms
            if press_duration > 0.3:
                time_since_last_selection = current_time - self.last_long_hold_selection_time
                if time_since_last_selection * 1000 >= self.long_hold_selection_delay:
                    # Use the last known event position
                    coords = self._get_image_coordinates(
                        type('Event', (object,), {'x': self._long_hold_loop_event_x, 'y': self._long_hold_loop_event_y})()
                    )
                    if coords:
                        x, y = coords
                        self._update_selection(x, y)
                        self._confirm_selection_if_last_image()
                    self.last_long_hold_selection_time = current_time
            self.root.after(10, loop)
        self.root.after(10, loop)
    
    def _set_selection_window_state(self, enabled: bool):
        """Enable or disable all controls in the selection window."""
        state = tk.NORMAL if enabled else tk.DISABLED
        # Disable/enable buttons
        self.confirm_button.config(state=state)
        self.clear_button.config(state=state)
        # Disable/enable slider
        self.delay_slider.config(state=state)
        # Disable/enable canvas events
        if not enabled:
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            self.canvas.unbind("<Button-3>")
            self.canvas.unbind("<B3-Motion>")
            self.canvas.unbind("<ButtonRelease-3>")
        else:
            self.canvas.bind("<Button-1>", self._on_left_click)
            self.canvas.bind("<B1-Motion>", self._on_left_drag)
            self.canvas.bind("<ButtonRelease-1>", self._on_left_release)
            self.canvas.bind("<Button-3>", self._on_right_click)
            self.canvas.bind("<B3-Motion>", self._on_right_drag)
            self.canvas.bind("<ButtonRelease-3>", self._on_right_release)
    
    def _show_replay_window(self):
        """Show a replay window with a slideshow of images and overlays of selected coordinates."""
        if self.replay_window is not None:
            return
        # Disable selection window controls
        self._set_selection_window_state(False)
        self.replay_window = tk.Toplevel(self.root)
        self.replay_window.title("Replay")
        self.replay_window.protocol("WM_DELETE_WINDOW", self._on_replay_close)

        # --- Replay window UI polish ---
        if self.replay_window is not None:
            self.replay_window.configure(bg="#f7f7fa")
        # Title label
        title_label = ttk.Label(
            self.replay_window,
            text="Replay",
            font=('Arial', 15, 'bold'),
            background="#f7f7fa"
        )
        title_label.pack(pady=(10, 6))

        # Canvas for replay
        self.replay_canvas = tk.Canvas(
            self.replay_window,
            width=self.max_width,
            height=self.max_height,
            bg='white',
            highlightthickness=2,
            highlightbackground="#b0b0b0",
            relief=tk.RIDGE,
            bd=2
        )
        self.replay_canvas.pack(padx=10, pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.replay_window, bg="#f7f7fa")
        button_frame.pack(pady=10)
        
        # Confirm all button (green)
        confirm_all_btn = tk.Button(
            button_frame,
            text="Confirm all",
            bg="green",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self._on_replay_confirm_all
        )
        confirm_all_btn.pack(side=tk.LEFT, padx=10)

        # Reset all button (red)
        reset_all_btn = tk.Button(
            button_frame,
            text="Reset all",
            bg="red",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self._on_replay_reset_all
        )
        reset_all_btn.pack(side=tk.LEFT, padx=10)

        # Slider for adjusting replay FPS
        slider_frame = tk.Frame(self.replay_window, bg="#f7f7fa")
        slider_frame.pack(pady=(0, 10))
        ttk.Label(slider_frame, text="Replay FPS:").pack(side=tk.LEFT)
        self.replay_fps_var = tk.DoubleVar(value=self.replay_fps)
        self.replay_fps_slider = tk.Scale(
            slider_frame,
            from_=0.5,
            to=100,
            orient=tk.HORIZONTAL,
            resolution=0.5,
            variable=self.replay_fps_var,
            command=self._on_replay_fps_change,
            length=200
        )
        self.replay_fps_slider.pack(side=tk.LEFT, padx=5)
        self.replay_fps_value_label = tk.Label(slider_frame, text=f"{self.replay_fps:.1f} FPS")
        self.replay_fps_value_label.pack(side=tk.LEFT)

        self.replay_running = True
        self._replay_index = 0
        self._start_replay_loop()

    def _start_replay_loop(self):
        """Start the replay slideshow loop."""
        if not self.replay_running or self.replay_window is None:
            return
        self._draw_replay_frame(self._replay_index)
        self._replay_index = (self._replay_index + 1) % len(self.resized_images)
        delay = int(1000 / max(self.replay_fps, 0.5))
        if self.replay_window is not None:
            self.replay_after_id = self.replay_window.after(delay, self._start_replay_loop)

    def _draw_replay_frame(self, idx):
        """Draw a single frame in the replay window with overlayed coordinate."""
        if self.replay_canvas is None:
            return
        self.replay_canvas.delete("all")
        img = self.resized_images[idx]
        photo_img = ImageTk.PhotoImage(img)
        # Store PhotoImage in an instance variable to prevent GC
        self._replay_photo_img = photo_img
        x_pos = (self.max_width - img.width) // 2
        y_pos = (self.max_height - img.height) // 2
        self.replay_canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=photo_img)
        # Draw overlayed coordinate if available
        if idx < len(self.selected_coordinates):
            x, y = self.selected_coordinates[idx]
            # The coordinates were selected on the resized image, so use them directly
            rx = x + x_pos
            ry = y + y_pos
            cross_size = 10
            self.replay_canvas.create_line(rx - cross_size, ry, rx + cross_size, ry, fill="red", width=2)
            self.replay_canvas.create_line(rx, ry - cross_size, rx, ry + cross_size, fill="red", width=2)

    def _on_replay_confirm_all(self):
        """User confirms all selections in replay window."""
        self.replay_running = False
        if self.replay_after_id and self.replay_window is not None:
            self.replay_window.after_cancel(self.replay_after_id)
        if self.replay_window is not None:
            self.replay_window.destroy()
        self.window_closed_properly = True
        self.root.quit()
        self.root.destroy()
        # Reset right click state
        self.right_click_press_time = 0
        self._long_hold_active = False

    def _on_replay_reset_all(self):
        """User resets all selections in replay window."""
        self.replay_running = False
        if self.replay_after_id and self.replay_window is not None:
            self.replay_window.after_cancel(self.replay_after_id)
        if self.replay_window is not None:
            self.replay_window.destroy()
        self.selected_coordinates = []
        self.current_image_index = 0
        self.selected_x = None
        self.selected_y = None
        self.window_closed_properly = False
        self.replay_window = None
        self.replay_after_id = None
        self._replay_index = 0
        self._display_current_image()
        # Re-enable selection window controls
        self._set_selection_window_state(True)
        # Reset right click state
        self.right_click_press_time = 0
        self._long_hold_active = False

    def _on_replay_close(self):
        """Handle close event for the replay window."""
        self.replay_running = False
        if self.replay_after_id and self.replay_window is not None:
            self.replay_window.after_cancel(self.replay_after_id)
        if self.replay_window is not None:
            self.replay_window.destroy()
        self.root.quit()
        self.root.destroy()
    
    def _on_replay_fps_change(self, val):
        """Update the replay FPS from the slider."""
        try:
            fps = float(val)
            if fps < 0.5:
                fps = 0.5
            self.replay_fps = fps
            self.replay_fps_value_label.config(text=f"{fps:.1f} FPS")
        except Exception:
            pass

    def run(self) -> Union[Tuple[int, int], List[Tuple[int, int]]]:
        """
        Run the GUI and return the selected coordinates.
        
        Returns:
            If single image was provided: tuple of (x, y)
            If multiple images were provided: list of (x, y) tuples
            
        Raises:
            UserClosedGUIWindow: If user closed the window before completing all selections
        """
        self.root.mainloop()
        if not self.window_closed_properly:
            raise UserClosedGUIWindow("User closed GUI window before completing all selections")
        # Return appropriate format based on input
        if len(self.image_paths) == 1:
            return self.selected_coordinates[0]
        return self.selected_coordinates


# Example usage
if __name__ == "__main__":
    try:
        image_paths = ["target_image/chameleon.png", "target_image/circles.png", "target_image/dark.png"]
        target_size = 400  # Resize shorter side to 400 pixels
        get_coords = CoordinateSelectorUI(image_paths, target_size)
        coordinates = get_coords.run()
        if type(coordinates) == tuple:
            print(coordinates)
        elif isinstance(coordinates, list):
            for i, (x, y) in enumerate(coordinates):
                print(f"Image {i+1}: Selected coordinates ({x}, {y})")
        else:
            print(coordinates)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")