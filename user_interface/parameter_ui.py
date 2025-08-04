import tkinter.ttk as ttk
import tkinter as tk

import os
import warnings

try:
    from utils.file_operations import clear_folder_contents
except ImportError:
    import sys
    sys.path.append('..')
    from utils.file_operations import clear_folder_contents



try:
    from .select_coordinate_ui import *
except ImportError:
    from select_coordinate_ui import *

try:
    from .tkinter_components import *
except ImportError:
    from tkinter_components import *

try:
    from .vector_field_equation_ui import *
except ImportError:
    from vector_field_equation_ui import *


try:
    from .read_write_parameter_json import *
except ImportError:
    from read_write_parameter_json import *

def count_frames_in_gif(filepath):
    """
    Returns the number of frames in a GIF file.
    Args:
        filepath (str): Full path to the GIF file.
    Returns:
        int: Number of frames in the GIF.
    """
    from PIL import Image
    with Image.open(filepath) as img:
        count = 0
        try:
            while True:
                img.seek(count)
                count += 1
        except EOFError:
            pass
    return count

def get_image_dimensions(image_path):
    """
    Get the width and height of an image file in pixels.
    
    Args:
        image_path (str): Path to the image file (jpg, jpeg, png, or gif)
    
    Returns:
        tuple: (width, height) in pixels
        
    Raises:
        FileNotFoundError: If the image file doesn't exist
        ValueError: If the file is not a supported image format
        Exception: For other image processing errors
    """
    
    # Check if file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Get file extension
    _, ext = os.path.splitext(image_path.lower())
    supported_formats = ['.jpg', '.jpeg', '.png', '.gif']
    
    if ext not in supported_formats:
        raise ValueError(f"Unsupported format: {ext}. Supported formats: {supported_formats}")
    
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            return width, height
            
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

class ParameterUI:
    def __init__(self, target_filepath, gif_frames_full_filepath_list = None):
        """
        Initialize the Parameter UI with an optional target file path.
        
        Args:
            target_filepath (str, optional): Path to target file to get its extention
        """
        self.target_filepath = target_filepath
        self.gif_frames_full_filepath_list = gif_frames_full_filepath_list # will be provided if the target is gif

        self.file_ext = os.path.splitext(self.target_filepath)[1].lower() if self.target_filepath else None # Gets the file extention
        if self.file_ext == ".gif":
            self.num_frames_in_original_gif = count_frames_in_gif(self.target_filepath)
            if gif_frames_full_filepath_list is None:
                raise AssertionError("Extention is gif but no gif frames are provided for ParameterUI")
        # Abstracted dimensions for first tab components
        self.PARAM_COMPONENT_WIDTH = 530
        self.PARAM_SLIDER_HEIGHT = 100
        self.PARAM_DUAL_SLIDER_HEIGHT = 115
        self.PARAM_CHECKBOX_HEIGHT = 25
        self.PARAM_TEXT_INPUT_HEIGHT = 100
        self.PAD_BETWEEN_ALL_COMPONENTS = 1
        self.CUSTOM_PADDING_HEIGHT = 20
        self.CUSTOM_PADDING_BG = "white"
        
        # Define a palette of visually distinct pastel colors
        self.PASTEL_COLORS = [
            '#FFB3BA',  # light red
            '#BAE1FF',  # light blue
            '#BAFFC9',  # light green
            '#FFFFBA',  # light yellow
            '#FFDFBA',  # light orange
            '#E2BAFF',  # light purple
        ]
        self.PASTEL_COLORS = [
            '#FFFFFF'  # light red

        ]
        self.widget_color_idx = 0
        self.prev_color_idx = None
        

        # Initialize the param dict to be returned
        self.returned_dict_command = None


        # Initialize the parameters from the param_dict
        self.create_initial_params()

        # Initialize the UI
        self._create_ui()

    def create_initial_params(self):
        """
        Create initial parameters from the param_dict.
        """
        self.param_dict_from_json_file = read_parameter_json()
        if self.param_dict_from_json_file is None:
            raise ValueError("Failed to read parameters.json or it is empty.")
        def get_value(key, value_key='value', assert_type=None):
            """
            Helper function to get value from param_dict with a default.
            Issues a warning only if the key or 'value' field is missing.
            """
            if key not in self.param_dict_from_json_file:
                raise KeyError(f"Key '{key}' is missing in parameters.json.")
            parameter = self.param_dict_from_json_file[key]
            if value_key not in parameter:
                raise KeyError(f"'{value_key}' field is missing in parameters.json for key '{key}'.")
            result = parameter[value_key]

            if assert_type is not None:
                if not isinstance(result, assert_type):
                    raise TypeError(f"Expected type {assert_type} for key '{key}', but got {type(result)}.") 
            return result

        # i_ stand for "initial" and is used to indicate that this is the initial value of the parameter

        # 1) Computation size
        self.i_computation_size = get_value("computation_size", assert_type=int)
        self.i_computation_size_min_value = get_value("computation_size", "min_value", assert_type=int)
        self.i_computation_size_max_value = get_value("computation_size", "max_value", assert_type=int)

        # 2) Add how many textures
        self.i_num_textures = get_value("num_textures", assert_type=int)
        self.i_num_textures_min_value = get_value("num_textures", "min_value", assert_type=int)
        self.i_num_textures_max_value = get_value("num_textures", "max_value", assert_type=int)

        # 3) Number of hill climb iterations
        self.i_num_hill_climb_iterations_current_lower_value = get_value("num_hill_climb_iterations", "current_lower_value", assert_type=int)
        self.i_num_hill_climb_iterations_current_upper_value = get_value("num_hill_climb_iterations", "current_upper_value", assert_type=int)
        self.i_num_hill_climb_iterations_min_value = get_value("num_hill_climb_iterations", "min_value", assert_type=int)
        self.i_num_hill_climb_iterations_max_value = get_value("num_hill_climb_iterations", "max_value", assert_type=int)

        # 4) Texture opacity settings
        self.i_texture_opacity = get_value("texture_opacity", assert_type=int)
        self.i_texture_opacity_min_value = get_value("texture_opacity", "min_value", assert_type=int)
        self.i_texture_opacity_max_value = get_value("texture_opacity", "max_value", assert_type=int)

        # 5) Initial texture width
        self.i_initial_texture_width = get_value("initial_texture_width", assert_type=int)
        self.i_initial_texture_width_min_value = get_value("initial_texture_width", "min_value", assert_type=int)
        self.i_initial_texture_width_max_value = get_value("initial_texture_width", "max_value", assert_type=int)

        # 6) Fix size of texture
        self.i_uniform_texture_size_bool = get_value("uniform_texture_size", assert_type=bool)

        # 7) Show painting progress as new textures are added
        self.i_display_painting_progress_bool = get_value("display_painting_progress", assert_type=bool)
        # 7a) Show improvement of individual textures
        self.i_display_placement_progress_bool = get_value("display_placement_progress", assert_type=bool)
        # 7b) Display final image after painting (conditional)
        self.i_display_final_image_bool = get_value("display_final_image", assert_type=bool)


        # 8) allow early termination of hill climb
        self.i_allow_early_termination_bool = get_value("allow_early_termination", assert_type=bool)
        # 8a) Terminate after n iterations
        self.i_failed_iterations_threshold = get_value("failed_iterations_threshold", assert_type=int)
        self.i_failed_iterations_threshold_min_value = get_value("failed_iterations_threshold", "min_value", assert_type=int)
        self.i_failed_iterations_threshold_max_value = get_value("failed_iterations_threshold", "max_value", assert_type=int)

        # 9) Enable vector field
        self.i_enable_vector_field_bool = get_value("enable_vector_field", assert_type=bool)

        # 9.i) Edit vector field button
        self.i_vector_field_f_string = get_value("vector_field_f", assert_type=str)
        self.i_vector_field_g_string = get_value("vector_field_g", assert_type=str)
        self.f_string = self.i_vector_field_f_string
        self.g_string = self.i_vector_field_g_string
        # Vector field function attribute
        self.vector_field_function = VectorFieldVisualizer.get_function_from_string_equations(self.i_vector_field_f_string, self.i_vector_field_g_string)
        if self.vector_field_function is None:
            raise ValueError("Invalid vector field equations provided in parameters.json. \n" \
            "- Please check 'vector_field_f' and 'vector_field_g' values. \n" \
            "- Do use 'x' and 'y' as variables in the equations and use * to multiply, e.g. 'x*y' instead of 'xy'. \n" \
            "- Ensure that the equations do not contain division by zero or other invalid operations. (x/y is fine but not x/0 or x/(y-y))\n" \
            "- list of valid operations: +, -, *, /, **, sin, cos, tan, exp, log, sqrt, abs.\n" \
            "- For example, valid equations are: 'x + y', 'sin(x) + cos(y)', 'x**2 + y**2', 'sqrt(abs(x + y))'.")

        # 9.ii) Shift vector field origin buttons
        self.i_vector_field_origin_shift_list_of_coords = get_value("vector_field_origin_shift", assert_type=list)
        self.target_previous_height = get_value("vector_field_origin_shift", "target_previous_height", assert_type=int)
        self.target_previous_width = get_value("vector_field_origin_shift", "target_previous_width", assert_type=int)
        self.target_prev_extention = get_value("vector_field_origin_shift", "target_previous_extention", assert_type=str)

        # Check if the target image dimensions match the previous dimensions and has the same extention.
        self.target_width, self.target_height = get_image_dimensions(self.target_filepath)
        self.is_same_target_ext_and_dimension = self.file_ext == self.target_prev_extention and self.target_previous_height == self.target_height and self.target_previous_width == self.target_width
        
        
        self.is_shift_origin_coord_selected = True

        # If the target image dimensions match the previous dimensions and has the same extention
        if self.is_same_target_ext_and_dimension:
            # Check if the list of coordinates is still valid
            if self.file_ext == ".gif" and len(self.i_vector_field_origin_shift_list_of_coords) != self.num_frames_in_original_gif:
                print("Number of coordinates do not match number of frames in the original gif, resetting the list of coordinates for shifting vector field origin")
                self.list_of_coord_for_shifting_vector_field_origin = [[]]  # Reset to empty list
                self.is_shift_origin_coord_selected = False
            elif self.file_ext != ".gif" and len(self.i_vector_field_origin_shift_list_of_coords) != 1:
                print("Target is not gif but the list of coordinates for shifting vector field origin has more than one coordinate, resetting the list of coordinates for shifting vector field origin")
                self.list_of_coord_for_shifting_vector_field_origin = [[]]  # Reset to empty list
                self.is_shift_origin_coord_selected = False
            else:
                # Use the list of coordinates from the parameters.json
                self.list_of_coord_for_shifting_vector_field_origin = self.i_vector_field_origin_shift_list_of_coords
        else:
            print("Target image dimensions have changed or extention has changed, resetting the list of coordinates for shifting vector field origin")
            self.list_of_coord_for_shifting_vector_field_origin = [[]]  # Reset to empty list
            self.is_shift_origin_coord_selected = False
        
        if self.list_of_coord_for_shifting_vector_field_origin == [[]]: # Case where parameter json contains [[]]
            self.is_shift_origin_coord_selected = False

        if self.is_shift_origin_coord_selected:
            self.initial_choose_vector_eqn_btn_label = \
                f"Shift origin to {str(tuple(self.list_of_coord_for_shifting_vector_field_origin[0]))}" if self.file_ext != ".gif" else f"Shift origin to {str(tuple(self.list_of_coord_for_shifting_vector_field_origin[0]))}, {str(tuple(self.list_of_coord_for_shifting_vector_field_origin[1]))}, ..."
        else:
            self.initial_choose_vector_eqn_btn_label = "Shift origin to (?, ?)" if self.file_ext != ".gif" else "Shift origin to (?, ?), (?, ?), ..."

        # Output tab initial parameters
        # 1) Output image size
        self.i_output_image_size = get_value("output_image_size", assert_type=int)
        self.i_output_image_size_min_value = get_value("output_image_size", "min_value", assert_type=int)
        self.i_output_image_size_max_value = get_value("output_image_size", "max_value", assert_type=int)

        # 2) Output image name
        self.i_output_image_name_string = get_value("output_image_name", assert_type=str)

        # 3) Create gif of painting progress checkbox
        self.i_create_gif_of_painting_progress_bool = get_value("create_gif_of_painting_progress", assert_type=bool)
        # 3i) Name of painting progress gif
        self.i_name_of_painting_progress_gif_string = get_value("painting_progress_gif_name", assert_type=str)

        # tab2 GIF Settings (for target with .gif)
        # A) Name of painted gif (a new gif where we paint all frames of target gif)
        self.i_painted_gif_name_string = get_value("painted_gif_name", assert_type=str)
        # B) Multiprocessing checkbox
        self.i_enable_multiprocessing_bool = get_value("enable_multiprocessing", assert_type=bool)

    def apply_modern_notebook_style(self):
        """Apply modern styling to the ttk.Notebook and remove dotted focus line from tabs"""
        # Set the clam theme
        style = ttk.Style()
        style.theme_use('clam')

        # Configure notebook style
        style.configure('TNotebook', 
                       background='#f8f9fa',
                       borderwidth=0)

        # Configure notebook tabs
        style.configure('TNotebook.Tab', 
                        padding=(20,8),
                       background='#e9ecef',
                       foreground='#495057',
                       borderwidth=0,
                       focuscolor='none',   ################### important
                       relief='flat',
                       font = ('Segoe UI', 12))
        
        # Configure selected tab
        style.map('TNotebook.Tab',
                    padding=[('selected', [20, 8]), ('active', [20, 8])],
                  background=[('selected', 'white'), ('active', "#4792d3")],
                  foreground=[('selected', 'black'), ('active', 'white')],
                  relief=[('selected', 'flat'), ('active', 'flat')])
        

        # Apply the custom style to the notebook
        self.notebook.configure(style="TNotebook")

    class ScrollableFrame(tk.Frame):
        def __init__(self, master, **kwargs):
            super().__init__(master, **kwargs)
            canvas = tk.Canvas(self, borderwidth=0, background="white", highlightthickness=0)
            self.frame = tk.Frame(canvas, background="white")
            vsb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=vsb.set)
            canvas.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")
            canvas.create_window((5, 0), window=self.frame, anchor="nw")
            
            self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            self.canvas = canvas
            self.cursor_inside = False
            
            # Store the after ID for cursor tracking
            self.cursor_check_id = None
            
            self._setup_cursor_tracking()
            self._setup_global_scrolling()
        
        def _setup_cursor_tracking(self):
            """Set up cursor tracking using continuous position monitoring"""
            def check_cursor_position():
                try:
                    x, y = self.winfo_pointerxy()
                    widget_x = self.winfo_rootx()
                    widget_y = self.winfo_rooty()
                    widget_width = self.winfo_width()
                    widget_height = self.winfo_height()
                    was_inside = self.cursor_inside
                    self.cursor_inside = (widget_x <= x <= widget_x + widget_width and 
                                        widget_y <= y <= widget_y + widget_height)
                    # Schedule next check and store the after ID
                    self.cursor_check_id = self.after(50, check_cursor_position)
                except tk.TclError:
                    # Widget might be destroyed
                    return
            
            # Start cursor position monitoring
            self.after_idle(check_cursor_position)
        
        def _setup_global_scrolling(self):
            """Set up global mouse wheel event handling"""
            def on_mousewheel(event):
                if not self.cursor_inside:
                    return
                if not self.canvas.winfo_exists():
                    return
                scroll_region = self.canvas.cget("scrollregion")
                if not scroll_region:
                    return
                region_coords = scroll_region.split()
                if len(region_coords) != 4:
                    return
                content_height = float(region_coords[3])
                canvas_height = self.canvas.winfo_height()
                if content_height <= canvas_height:
                    return
                if hasattr(event, 'delta') and event.delta:
                    delta = -1 * (event.delta / 120)
                else:
                    if hasattr(event, 'num'):
                        delta = -1 if event.num == 4 else 1
                    else:
                        return
                self.canvas.yview_scroll(int(delta), "units")
            
            def setup_global_binding():
                root = self.winfo_toplevel()
                root.bind_all("<MouseWheel>", on_mousewheel, add=True)
                root.bind_all("<Button-4>", on_mousewheel, add=True)
                root.bind_all("<Button-5>", on_mousewheel, add=True)
            
            self.after_idle(setup_global_binding)
        
        def destroy(self):
            """Clean up global bindings and cancel after callbacks when widget is destroyed"""
            # Cancel the cursor tracking after callback
            if self.cursor_check_id is not None:
                try:
                    self.after_cancel(self.cursor_check_id)
                except tk.TclError as e:
                    print(e)
                    pass  # Ignore if the callback is already invalid
                self.cursor_check_id = None
            
            # Optionally unbind global mouse wheel events
            try:
                root = self.winfo_toplevel()
                root.unbind_all("<MouseWheel>")
                root.unbind_all("<Button-4>")
                root.unbind_all("<Button-5>")
            except tk.TclError as e:
                print(e)
                pass  # Ignore if the root window is already destroyed
            
            super().destroy()

    def add_section_pad(self, frame):
        tk.Frame(frame, height=20, bg='white').pack(fill='x')
    
    def get_next_color(self, idx, prev_idx=None):
        # Ensure no two adjacent widgets have the same color
        color_idx = idx % len(self.PASTEL_COLORS)
        if prev_idx is not None and color_idx == prev_idx:
            color_idx = (color_idx + 1) % len(self.PASTEL_COLORS)
        return self.PASTEL_COLORS[color_idx], color_idx
    
    def add_between_padding(self, frame, vis_manager):
        between_padding = Padding(frame, height=self.CUSTOM_PADDING_HEIGHT, bg_color=self.CUSTOM_PADDING_BG)
        between_padding.pack(fill='x')
        vis_manager.register_widget(between_padding, {'fill': 'x'})

    def setup_button_style(self):
        """Apply the exact style from TargetTextureSelectorUI for TButton."""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Button 1
        self.style.configure(
            'button1.TButton',
            font=('Segoe UI', 13),
            padding=(0, 10),  # (horizontal_padding, vertical_padding)
            relief='flat',
            background='#4078c0',  # Blue background
            foreground='#fff',     # White text
            focuscolor='none'
        )
        self.style.map('button1.TButton', background=[('active', '#305080')])  # Darker blue when active

        # Button 2
        self.style.configure(
            'button2.TButton',
            font=('Segoe UI', 13),
            padding=(0, 10),  # (horizontal_padding, vertical_padding)
            relief='flat',
            background='#388e3c',  # Green background
            foreground='#fff',     # White text
            focuscolor='none'
        )
        self.style.map("button2.TButton", background=[("active", "#1b5e20")]) # Darker green when active
        self.button1.configure(style="button1.TButton")
        self.button2.configure(style="button2.TButton")

        self.style.configure(
            'button_edit_vector_field.TButton',
            font=('Segoe UI', 14), # times new roman alternative
            padding=(0, 8),  # (horizontal_padding, vertical_padding)
            relief='default',
            background='#ffffff',  # white background
            foreground='black',     # black text
            focuscolor='none',
            borderwidth=2
        )
        self.style.map(
            "button_edit_vector_field.TButton",
            background=[('selected', 'white'), ('active', "#dcefff")],
            foreground=[('selected', 'black'), ('active', 'black')],
        )

        self.style.configure(
            'button_shift_vector_field.TButton',
            font=('Segoe UI', 14), # times new roman alternative
            padding=(0, 8),  # (horizontal_padding, vertical_padding)
            relief='default',
            background='#ffffff',  # white background
            foreground='black' if self.is_shift_origin_coord_selected else 'red',     # red text
            focuscolor='none',
            borderwidth=2
        )
        self.style.map(
            "button_shift_vector_field.TButton",
            background=[('selected', 'white'), ('active', "#dcefff")],
            foreground=[('selected', 'black'), ('active', 'black')],
        )

    def _create_ui(self):
        """Create the main UI elements"""
        self.root = tk.Tk()
        self.root.title("Select parameters")


        def center_window(root, width, height):
            # Get screen dimensions
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            
            # Calculate position to center the window
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            
            # Set window geometry
            root.geometry(f"{width}x{height}+{x}+{y}")

        # Set window size and center it
        window_width = 570
        
        # Get screen dimensions to calculate appropriate window height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate window height based on screen size, leaving margin for taskbar/dock
        # Use 90% of screen height, but cap at 850 (original size) for very large screens
        max_height = min(850, int(screen_height * 0.9))
        window_height = max_height
        
        center_window(self.root, window_width, window_height)
        self.root.minsize(window_width, 570)   # Set minimum window size (width, height)
        self.root.configure(bg='white')
        self.root.resizable(True, True) ################# Make window resizable? resize this?

        
        # Bind the close button (X) to show the confirmation dialog
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.parent_frame = tk.Frame(self.root, bg="white", relief="flat")
        self.parent_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.notebook = ttk.Notebook(self.parent_frame)
        self.apply_modern_notebook_style()
        self.notebook.pack(fill='both', expand=True)

        # Tab 1: Parameters
        self.param_scroll = self.ScrollableFrame(self.notebook)
        self.param_frame = self.param_scroll.frame
        self.param_vis_manager = VisibilityManager()  # Separate VisibilityManager for Tab 1
        self._create_parameter_widgets_tab_1()

        # Tab 2: Output Settings
        self.output_scroll = self.ScrollableFrame(self.notebook)
        self.output_frame = self.output_scroll.frame
        self.output_vis_manager = VisibilityManager()  # Separate VisibilityManager for Tab 2
        self._create_parameter_widgets_tab_2()

        self.notebook.add(self.param_scroll, text="Parameters")
        self.notebook.add(self.output_scroll, text="Output Settings")

        self.dual_button_frame = tk.Frame(self.parent_frame, bg="white", height = 50)
        self.dual_button_frame.pack(fill="x")

        # Bind button1 to on_select_target_texture
        padx,pady=1,0
        self.button1 = ttk.Button(self.dual_button_frame, text="Select target and texture", command=self.on_select_target_texture) 
        self.button1.grid(row=0, column=0, sticky="nsew", padx=padx, pady=pady)
        self.button2 = ttk.Button(self.dual_button_frame, text="Submit", command=self.on_submit_button_press, 
                                  state="normal" if self.is_shift_origin_coord_selected else "disabled")
        if not self.i_enable_vector_field_bool:
            self.button2.configure(state="normal")
        self.button2.grid(row=0, column=1, sticky="nsew", padx=padx, pady=pady)

        self.setup_button_style()

        self.dual_button_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        self.dual_button_frame.grid_columnconfigure(1, weight=1, uniform="group1")

    def on_closing(self):
        """Handle the window close event with a modern confirmation dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Confirm Exit")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', True)
        
        # Modern styling
        dialog.configure(bg="#f0f2f5")
        
        # Center the dialog
        dialog_width = 350
        dialog_height = 180
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # Container frame for better padding
        container = tk.Frame(dialog, bg="#f0f2f5")
        container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Message with modern font and spacing
        message = tk.Label(
            container,
            text="Exit application?",
            font=("Segoe UI", 13),
            bg="#f0f2f5",
            fg="#333333"
        )
        message.pack(pady=(20, 30))
        
        # Button frame with grid configuration
        button_frame = tk.Frame(container, bg="#f0f2f5")
        button_frame.pack(fill="x")
        
        # Configure grid columns to expand equally
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Modern button style
        style = ttk.Style()
        style.configure(
            "Modern.TButton",
            font=("Segoe UI", 12),
            padding=10,
            background="#ffffff",
            foreground="#333333",
            borderwidth=0,
            focuscolor="none"
        )
        style.map(
            "Modern.TButton",
            background=[('selected', 'white'), ('active', "#4792d3")],
            foreground=[('selected', 'black'), ('active', 'white')],
        )

        # Yes button
        yes_button = ttk.Button(
            button_frame,
            text="Yes",
            style="Modern.TButton",
            command=lambda: self.confirm_exit(dialog)
        )
        yes_button.grid(row=0, column=0, padx=(0, 5), pady=5, ipadx=20, ipady=5, sticky="ew")
        
        # No button
        no_button = ttk.Button(
            button_frame,
            text="No",
            style="Modern.TButton",
            command=dialog.destroy
        )
        no_button.grid(row=0, column=1, padx=(5, 0), pady=5, ipadx=20, ipady=5, sticky="ew")
        
        # Add subtle shadow effect to dialog
        dialog.update_idletasks()
        dialog.configure(
            borderwidth=1,
            relief="flat",
            highlightbackground="#d0d0d0",
            highlightcolor="#d0d0d0",
            highlightthickness=1
        )
        
        # Ensure dialog stays on top and grabs focus
        dialog.grab_set()
        dialog.transient(self.root)

    def confirm_exit(self, dialog):
        """Set result for window close and destroy the dialog and root"""
        self.returned_dict_command = {"command": "user_closed_param_ui_window"}
        # write the new parameters to parameters.json
        self.save_parameters()
        dialog.destroy()
        self.root.quit()  # Exit mainloop
        self.root.destroy()  # Destroy window

    def on_select_target_texture(self):
        """Handle 'Select target and texture' button press"""
        self.returned_dict_command = {"command": "reselect_target_texture"}
        # write the new parameters to parameters.json
        self.save_parameters()
        self.root.quit()  # Exit mainloop
        self.root.destroy()  # Destroy window
    def on_submit_button_press(self):
        """Handle 'Submit' button press"""
        # Clear painted_gif_frames folder if input is a GIF
        if self.file_ext == ".gif":
            try:
                clear_folder_contents("painted_gif_frames")
                print("Cleared painted_gif_frames folder")
            except Exception as e:
                print(f"Warning: Failed to clear painted_gif_frames folder: {e}")
        
        self.returned_dict_command = {"command": "run", "parameters": self.get_parameters()}
        # write the new parameters to parameters.json
        self.save_parameters()
        self.root.quit()  # Exit mainloop
        self.root.destroy()  # Destroy window
    # Tab 1
    def _create_parameter_widgets_tab_1(self):
        # Check file extension
        if not self.target_filepath:
            return
        file_ext = self.file_ext

        """Create all parameter widgets for the first tab"""
        # 1) Computation size
        self.add_between_padding(self.param_frame, self.param_vis_manager)
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.computation_size_slider = SingleSlider(self.param_frame, 
            min_val=self.i_computation_size_min_value, 
            max_val=self.i_computation_size_max_value, 
            init_val=self.i_computation_size, 
            width=self.PARAM_COMPONENT_WIDTH, 
            title="1) Computation size: <current_value> pixels", 
            subtitle="- Increase to capture more image detail, decrease for speed\n- Slider movement resets existing selection of vector field origin translation coordinates", 
            is_set_width_to_parent=True, 
            bg_color=color, 
            command=self.on_computation_size_slider_change
        )
        self.computation_size_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.computation_size_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)
        self.resize_shorter_side_of_target = self.computation_size_slider.get()


        # 2) Add how many textures
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.num_shapes_slider = SingleSlider(self.param_frame, 
            min_val=self.i_num_textures_min_value, 
            max_val=self.i_num_textures_max_value, 
            init_val=self.i_num_textures, 
            width=self.PARAM_COMPONENT_WIDTH, 
            title="2) Add <current_value> textures", 
            subtitle="- Increase to paint finer details, decrease for speed", 
            is_set_width_to_parent=True, 
            bg_color=color
        )
        self.num_shapes_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.num_shapes_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 3) Number of hill climb iterations
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.hill_climb_range = RangeSlider(self.param_frame, 
            min_val=self.i_num_hill_climb_iterations_min_value, 
            max_val=self.i_num_hill_climb_iterations_max_value, 
            init_min=self.i_num_hill_climb_iterations_current_lower_value, 
            init_max=self.i_num_hill_climb_iterations_current_upper_value,
            width=self.PARAM_COMPONENT_WIDTH,
            title="3) Number of hill climb iterations: Min = <current_min_value>, Max = <current_max_value>", 
            subtitle="- Number of iterations grows linearly as more textures are painted. \n- Higher iteraton improves texture placement but requires more computation", 
            is_set_width_to_parent=True, 
            bg_color=color
        )
        self.hill_climb_range.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.hill_climb_range, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 4) Texture opacity settings
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.texture_opacity_slider = SingleSlider(self.param_frame, 
            min_val=self.i_texture_opacity_min_value, 
            max_val=self.i_texture_opacity_max_value, 
            init_val=self.i_texture_opacity, 
            width=self.PARAM_COMPONENT_WIDTH,
            title="4) Texture opacity: <current_value>%", 
            subtitle="- Give the texture a translucent effect by decreasing its opacity", 
            is_set_width_to_parent=True, 
            bg_color=color
        )
        self.texture_opacity_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.texture_opacity_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 5) Initial texture width
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.rect_width_slider = SingleSlider(self.param_frame, 
            min_val=self.i_initial_texture_width_min_value, 
            max_val=self.i_initial_texture_width_max_value, 
            init_val=self.i_initial_texture_width, 
            width=self.PARAM_COMPONENT_WIDTH, 
            title="5) Initial texture size: <current_value> pixels", 
            subtitle="- Influences size of texture when it is initially created", 
            is_set_width_to_parent=True, 
            bg_color=color)
        self.rect_width_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.rect_width_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 6) Fix size of texture
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.scaling_chk = CustomCheckbox(self.param_frame, 
            text="6) Constrain texture size to initial size", 
            checked=self.i_uniform_texture_size_bool, 
            width=self.PARAM_COMPONENT_WIDTH, 
            height=self.PARAM_CHECKBOX_HEIGHT, 
            is_set_width_to_parent=True, 
            bg_color=color)
        self.scaling_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.scaling_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        if file_ext in ['.png', '.jpg', '.jpeg']:
            # 7) Show painting progress as new textures are added
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.show_pygame_chk = CustomToggleVisibilityCheckbox(self.param_frame, 
                text="7) Display painting progress", 
                checked=self.i_display_painting_progress_bool, 
                visibility_manager=self.param_vis_manager, 
                width=self.PARAM_COMPONENT_WIDTH, 
                height=self.PARAM_CHECKBOX_HEIGHT, 
                is_set_width_to_parent=True, 
                bg_color=color
            )
            self.show_pygame_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.param_vis_manager.register_widget(self.show_pygame_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            # 7a) Show improvement of individual textures
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.rect_improve_chk = CustomCheckbox(self.param_frame,
                text="7a) Show improvement of individual textures", 
                checked=self.i_display_placement_progress_bool, 
                width=self.PARAM_COMPONENT_WIDTH, 
                height=self.PARAM_CHECKBOX_HEIGHT, 
                is_set_width_to_parent=True, 
                bg_color=color
            )
            self.rect_improve_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.param_vis_manager.register_widget(self.rect_improve_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            # 7b) Display final image after painting (conditional)
            display_final_chk = None
            if file_ext in ['.png', '.jpg', '.jpeg']:
                color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
                self.prev_color_idx = self.widget_color_idx
                self.display_final_chk = CustomCheckbox(self.param_frame, 
                    text="7b) Display final image after painting", 
                    checked=self.i_display_final_image_bool, 
                    width=self.PARAM_COMPONENT_WIDTH, 
                    height=self.PARAM_CHECKBOX_HEIGHT, 
                    is_set_width_to_parent=True, 
                    bg_color=color
                )
                self.display_final_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
                self.param_vis_manager.register_widget(self.display_final_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
                display_final_chk = self.display_final_chk
            # Set up dependency: both 7.i and 7.ii only show if show_pygame_chk is checked
            controlled_widgets = [self.rect_improve_chk]
            if display_final_chk is not None:
                controlled_widgets.append(display_final_chk)
            self.show_pygame_chk.set_controlled_widgets(controlled_widgets)
            self.add_between_padding(self.param_frame, self.param_vis_manager)
            

        # 8) allow early termination of hill climb
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.premature_chk = CustomToggleVisibilityCheckbox(self.param_frame,
            text="8) Allow early termination of hill climbing", 
            checked=self.i_allow_early_termination_bool, 
            visibility_manager=self.param_vis_manager, 
            width=self.PARAM_COMPONENT_WIDTH, 
            height=self.PARAM_CHECKBOX_HEIGHT, 
            is_set_width_to_parent=True, 
            bg_color=color
        )
        self.premature_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.premature_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        # 8a) Terminate after n iterations
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.fail_threshold_slider = SingleSlider(self.param_frame, 
            min_val=self.i_failed_iterations_threshold_min_value, 
            max_val=self.i_failed_iterations_threshold_max_value, 
            init_val=self.i_failed_iterations_threshold, 
            width=self.PARAM_COMPONENT_WIDTH, 
            height=50, 
            subtitle="- Terminate after <current_value> failed iterations where there is no improvement", 
            is_set_width_to_parent=True, 
            bg_color=color
        )
        self.fail_threshold_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.fail_threshold_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)
        # Set up conditional logic: fail_threshold_slider only shows when premature_chk is checked
        self.premature_chk.set_controlled_widgets([self.fail_threshold_slider])


        # 9) Enable vector field
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.vector_field_chk = CustomToggleVisibilityCheckbox(self.param_frame, 
            text="9) Enable vector field", 
            checked=self.i_enable_vector_field_bool, 
            visibility_manager=self.param_vis_manager, 
            width=self.PARAM_COMPONENT_WIDTH, 
            height=self.PARAM_CHECKBOX_HEIGHT, 
            is_set_width_to_parent=True, 
            bg_color=color,
            command = self.on_vector_field_checkbox_change
        )
        self.vector_field_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.vector_field_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})

        # 9.i) Edit vector field
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.edit_vector_btn = ttk.Button(self.param_frame, text=f"(f(x,y), g(x,y)) = ({self.i_vector_field_f_string}, {self.i_vector_field_g_string})", 
                                         style="button_edit_vector_field.TButton",
                                         command=self.on_edit_vector_field)
        self.edit_vector_btn.pack(fill='x', padx=(20, 0), pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.edit_vector_btn, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})

        # 9.ii) Shift vector field origin
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.shift_vector_origin_btn = ttk.Button(self.param_frame, text=self.initial_choose_vector_eqn_btn_label, 
                                                 style="button_shift_vector_field.TButton",
                                                 command=self.on_shift_vector_origin)
        self.shift_vector_origin_btn.pack(fill='x', padx=(20,0), pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.shift_vector_origin_btn, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})

        # Set up dependency: 9.i, 9.ii only show if vector_field_chk is checked
        self.vector_field_chk.set_controlled_widgets([self.edit_vector_btn, self.shift_vector_origin_btn])
        self.add_between_padding(self.param_frame, self.param_vis_manager)

    # Tab 2
    def _create_parameter_widgets_tab_2(self):
        """Create parameter widgets for the second tab (Output Settings) based on file extension"""
        # Check file extension
        if not self.target_filepath:
            return
        file_ext = self.file_ext

        # Section 6: Image Output Settings (for .png, .jpg, .jpeg)
        if file_ext in ['.png', '.jpg', '.jpeg']:
            # 1) Output image size
            self.add_between_padding(self.output_frame, self.output_vis_manager)
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.output_size_slider = SingleSlider(
                self.output_frame, 
                min_val=self.i_output_image_size_min_value, 
                max_val=self.i_output_image_size_max_value, 
                init_val=self.i_output_image_size,
                width=self.PARAM_COMPONENT_WIDTH,
                title="1) Output image size: <current_value> px", subtitle="- Render the output in a higher resolution", 
                is_set_width_to_parent=True,
                bg_color=color
            )
            self.output_size_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.output_size_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)


            # 2) Output image name
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.image_name_input = CustomTextInput(self.output_frame, 
                width=self.PARAM_COMPONENT_WIDTH,
                title="2) Name of output image", 
                subtitle="- Image will be saved to output folder when algorithm terminates", 
                is_set_width_to_parent=True, 
                bg_color=color
            )
            self.image_name_input.set(self.i_output_image_name_string)
            self.image_name_input.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.image_name_input, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)

            # 3) Create GIF progress Checkbox
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.create_gif_chk = CustomToggleVisibilityCheckbox(self.output_frame, 
                text="3) Create GIF of painting progress", 
                checked=self.i_create_gif_of_painting_progress_bool,
                width=self.PARAM_COMPONENT_WIDTH, 
                height=self.PARAM_CHECKBOX_HEIGHT,
                is_set_width_to_parent=True, 
                bg_color=color,
                visibility_manager=self.output_vis_manager
            )
            self.create_gif_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.create_gif_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            # 3i) Name of painting progress GIF
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.gif_name_input = CustomTextInput(
                self.output_frame, 
                width=self.PARAM_COMPONENT_WIDTH, 
                title="3a) Enter GIF filename", 
                subtitle="- Gif will be saved to output folder when algorithm terminates", is_set_width_to_parent=True, bg_color=color
            )
            self.gif_name_input.set(self.i_name_of_painting_progress_gif_string)
            self.gif_name_input.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.gif_name_input, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS}, controller=self.create_gif_chk)
            # Set controlled widgets for the checkbox
            self.create_gif_chk.set_controlled_widgets([self.gif_name_input])
            self.add_between_padding(self.output_frame, self.output_vis_manager)




        # tab2 GIF Settings (for target with .gif)
        elif file_ext == '.gif':
            self.add_between_padding(self.output_frame, self.output_vis_manager)
            # 1) Limit number of frames painted in original GIF.
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.add_between_padding(self.param_frame, self.param_vis_manager)
            self.frames_in_gif_slider = SingleSlider(
                self.output_frame, min_val=2, max_val=self.num_frames_in_original_gif, init_val=self.num_frames_in_original_gif,
                width=self.PARAM_COMPONENT_WIDTH,
                title=f"1) Paint <current_value> out of {self.num_frames_in_original_gif} frames from target GIF", 
                subtitle=f"- Optionally reduce number of frames painted to speed up computation. \
                \n- FPS of frames will be adjusted accordingly to keep total duration unchanged", is_set_width_to_parent=True, bg_color=color
            )
            self.frames_in_gif_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.frames_in_gif_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)

            # A) Name of painted gif (a new gif where we paint all frames of target gif)
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.painted_gif_name_input = CustomTextInput(
                self.output_frame, 
                width=self.PARAM_COMPONENT_WIDTH,
                title="2) Painted GIF filename", 
                subtitle=None, 
                is_set_width_to_parent=True, 
                bg_color=color
            )
            self.painted_gif_name_input.set(self.i_painted_gif_name_string)
            self.painted_gif_name_input.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.painted_gif_name_input, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)

            # B) Multiprocessing Checkbox
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.multiprocessing_chk = CustomCheckbox(
                self.output_frame, 
                text="3) Enable multiprocessing for batch frame processing", 
                checked=self.i_enable_multiprocessing_bool,
                width=self.PARAM_COMPONENT_WIDTH, 
                height=self.PARAM_CHECKBOX_HEIGHT,
                is_set_width_to_parent=True, 
                bg_color=color
            )
            self.multiprocessing_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.multiprocessing_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)
    
    ################ Enable vector field checkbox #################
    def on_vector_field_checkbox_change(self, state=None):
        """Handle changes to the vector field checkbox"""
        if state == False: # Vector field is not enabled
            self.button2.config(state="normal")

        else: # Vector field is enabled
            # Check if shift origin coordinates are selected
            if not self.is_shift_origin_coord_selected:
                self.button2.config(state="disabled")  # Disable the submit button if vector field is enabled and origin(s) not selected
                self.style.configure("button_shift_vector_field.TButton", foreground="red")
            
    ############### Vector field buttons #################
    def on_shift_vector_origin(self):
        print("Opens the window to get list of (x,y) coordinates")
        # prereq: either gif frames Or target image
        self.resize_shorter_side_of_target = self.computation_size_slider.get()

        for _ in range(1):
            if self.file_ext != ".gif":  # Non GIF case
                user_choosen_coords_list = create_coord_selector_UI(self.target_filepath, self.resize_shorter_side_of_target, master=self.root)
                if user_choosen_coords_list is None:
                    break
                label = "Shift origin to: " + str(tuple(user_choosen_coords_list[0]))
            
            else: # GIF case
                user_choosen_coords_list = create_coord_selector_UI(self.gif_frames_full_filepath_list, self.resize_shorter_side_of_target, master=self.root)
                if user_choosen_coords_list is None:
                    break
                label = "Shift origin to: " + str(tuple(user_choosen_coords_list[0]))+", "+str(tuple(user_choosen_coords_list[1]))+"..."
            
        # If UI returns coordinates
        if user_choosen_coords_list is not None:
            # Update the current state of UI
            self.list_of_coord_for_shifting_vector_field_origin = user_choosen_coords_list
            self.is_shift_origin_coord_selected = True
            # Update select vector shift origin button text and text color
            self.shift_vector_origin_btn.config(text=label)
            self.style.configure("button_shift_vector_field.TButton", foreground="black")
            # Enable submit button
            self.button2.config(state="normal")
            

    # Adjusting computation size slider will reset the selected vector field
    def on_computation_size_slider_change(self, sliderval=None):
        # reset selected coordinates
        self.is_shift_origin_coord_selected = False
        self.list_of_coord_for_shifting_vector_field_origin = [[]]
        # Make the shift vector origin button state that there are no selected coordinates
        self.shift_vector_origin_btn.config(text="Shift origin to (?, ?)" if self.file_ext != ".gif" else "Shift origin to (?, ?), (?, ?), ...")
        self.style.configure("button_shift_vector_field.TButton", foreground="red")
        # If Enable vector field checkbox is True and there are no coordinates selected, disable submit button
        if self.vector_field_chk.get() == True and not self.is_shift_origin_coord_selected:
            self.button2.config(state="disabled")

    # Opens the window for user to define vector field
    def on_edit_vector_field(self):
        custom_presets = {
            "Radial Sink": ("-x", "-y"),
            "Radial Source": ("x", "y"),
            "Spiral Sink Clockwise": ("-x + y", "-y - x"),
            "Spiral Sink Anticlockwise": ("-x - y", "x - y"),
            "Spiral Source Clockwise": ("x - y", "y + x"),
            "Spiral Source Anticlockwise": ("x + y", "-x + y"),
            "Rotation Clockwise": ("y", "-x"),
            "Rotation Anticlockwise": ("-y", "x")
        }
        custom_grid_sizes = [10, 20, 30]
        self.root.update()
        print("f_string, g_string from param UI",self.f_string, self.g_string)
        result = create_vector_field_visualizer(custom_presets, custom_grid_sizes, master=self.root, initial_f_string=self.f_string, initial_g_string=self.g_string)

        if result is not None:
            function_string = result[0]
            print("Function string returned from vector field visualizer:", function_string)
            # Update button text with the returned string
            self.edit_vector_btn.configure(text=f"(f(x,y), g(x,y)) = {function_string}")
            # Update the vector field function
            self.vector_field_function = result[1]
            # update the f_string and g_string
            expr = function_string.strip("()")  # Remove the parentheses
            self.f_string, self.g_string = [part.strip() for part in expr.split(",")]  # Split by comma and strip whitespace
            print(self.f_string, self.g_string)

    def get_parameters(self):
        """
        Returns a dictionary containing all parameters from the UI widgets.
        
        Returns:
            dict: A dictionary with parameter names as keys and their values.
        """
        parameters = {}

        # Tab 1: Parameters
        parameters['computation_size'] = self.computation_size_slider.get()
        parameters['num_textures'] = self.num_shapes_slider.get()
        min_iter, max_iter = self.hill_climb_range.get()
        parameters['hill_climb_min_iterations'] = min_iter
        parameters['hill_climb_max_iterations'] = max_iter
        parameters['texture_opacity'] = self.texture_opacity_slider.get()
        parameters['initial_texture_width'] = self.rect_width_slider.get()
        parameters['uniform_texture_size'] = self.scaling_chk.get()
        parameters['allow_early_termination'] = self.premature_chk.get()
        parameters['failed_iterations_threshold'] = self.fail_threshold_slider.get()
        parameters['enable_vector_field'] = self.vector_field_chk.get()
        parameters['vector_field_f'] = self.f_string
        parameters['vector_field_g'] = self.g_string
        parameters['vector_field_function'] = self.vector_field_function
        parameters['vector_field_origin_shift'] = self.list_of_coord_for_shifting_vector_field_origin

        # Conditional parameters for image files (.png, .jpg, .jpeg)
        if self.file_ext in ['.png', '.jpg', '.jpeg']:
            parameters['display_painting_progress'] = self.show_pygame_chk.get()
            parameters['display_placement_progress'] = self.rect_improve_chk.get()
            parameters['display_final_image'] = self.display_final_chk.get()

        # Tab 2: Output Settings
        if self.file_ext in ['.png', '.jpg', '.jpeg']:
            parameters['output_image_size'] = self.output_size_slider.get()
            parameters['output_image_name'] = self.image_name_input.get()
            parameters['create_gif_of_painting_progress'] = self.create_gif_chk.get()
            parameters['painting_progress_gif_name'] = self.gif_name_input.get() if self.create_gif_chk.get() else ""
        elif self.file_ext == '.gif':
            parameters['num_frames_to_paint'] = self.frames_in_gif_slider.get()
            parameters['painted_gif_name'] = self.painted_gif_name_input.get()
            parameters['enable_multiprocessing'] = self.multiprocessing_chk.get()
        
        # Handle conditional logic:
        if self.file_ext != ".gif":
            parameters['enable_multiprocessing'] = False

        return parameters

    def save_parameters(self):
        """
        Save the current parameters to a JSON file.
        """
        user_selected_parameters = self.get_parameters()

        json_parameters = self.param_dict_from_json_file

        parameter_keys = [
            "computation_size",
            "num_textures",
            # "hill_climb_min_iterations",
            # "hill_climb_max_iterations",
            "texture_opacity",
            "initial_texture_width",
            "uniform_texture_size",
            "allow_early_termination",
            "failed_iterations_threshold",
            "enable_vector_field",
            "vector_field_f",
            "vector_field_g",
            # "vector_field_function",
            "vector_field_origin_shift",
            "display_painting_progress",
            "display_placement_progress",
            "display_final_image",
            "output_image_size",
            "output_image_name",
            "create_gif_of_painting_progress",
            "painting_progress_gif_name",
            # "num_frames_to_paint",
            "painted_gif_name",
            "enable_multiprocessing"
        ]

        # Save user selected parameters
        for param_key in parameter_keys:
            param_value = user_selected_parameters.get(param_key, "Key not present")
            if param_value == "Key not present":
                continue
            else:
                json_parameters[param_key]["value"] = param_value
        # Handle case of num_hill_climb_iteration dual slider parameters
        json_parameters["num_hill_climb_iterations"]["current_lower_value"] = user_selected_parameters['hill_climb_min_iterations']
        json_parameters["num_hill_climb_iterations"]["current_upper_value"] = user_selected_parameters['hill_climb_max_iterations']


        # Save image dimensions and name of file extention
        json_parameters["vector_field_origin_shift"]["target_previous_height"] = self.target_height
        json_parameters["vector_field_origin_shift"]["target_previous_width"] = self.target_width
        json_parameters["vector_field_origin_shift"]["target_previous_extention"] = self.file_ext


        # print("Saving parameters to JSON file:", json_parameters)
        # dump to json 
        write_parameter_json(json_parameters)



    def run(self):
        """Start the UI main loop and return the result based on user action"""
        self.returned_dict_command = None  # Reset result
        self.root.mainloop()  # Run the Tkinter main loop
        return self.returned_dict_command  # Return the result set by button actions or closing


def get_command_from_parameter_ui(target, target_gif_frames=None):
    """
    Initialize the ParameterUI and return the command based on user interaction.
    
    Args:
        target (str): Path to the target file (image or GIF).
        target_gif_frames (list or None): List of file paths for GIF frames or None for non-GIF targets.
    
    Returns:
        dict: Dictionary containing the command and optional parameters based on user action.
    """
    # Initialize ParameterUI
    ui = ParameterUI(target_filepath=target, gif_frames_full_filepath_list=target_gif_frames)
    # Run the UI and get the result
    result = ui.run()
    return result



if __name__ == "__main__":

    # path_of_target = "C:\\Git Repos\\hill-climb-painter\\readme_stuff\\shrek_original.gif"
    # gif_frames_full_filepaths = ['C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0000.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0001.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0002.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0003.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0004.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0005.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0006.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0007.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0008.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0009.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0010.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0011.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0012.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0013.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0014.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0015.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0016.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0017.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0018.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0019.png']

    # command = get_command_from_parameter_ui(path_of_target, target_gif_frames=gif_frames_full_filepaths)
    # print(command)

    
    # path_of_target = "C:\\Git Repos\\hill-climb-painter\\target_image\\cat.jpg"
    # result = get_command_from_parameter_ui(path_of_target, target_gif_frames=None)
    # print(result)


    path_of_target = "C:\\Git Repos\\hill-climb-painter\\readme_stuff\\shrek_original.gif"
    gif_frames_full_filepaths = [
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0000.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0001.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0002.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0003.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0004.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0005.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0006.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0007.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0008.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0009.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0010.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0011.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0012.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0013.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0014.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0015.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0016.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0017.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0018.png",
        "C:\\Git Repos\\hill-climb-painter\\testing_gif_frames\\shrek-somebody-ezgif.com-crop (1)_frame_0019.png"
    ]

    result = get_command_from_parameter_ui(path_of_target, target_gif_frames=gif_frames_full_filepaths)

    for k,v in result["parameters"].items():
        print(f"{k}: {v}\n")

    # print(result["parameters"]["vector_field_function"])

    # path_of_target = "C:\\Git Repos\\hill-climb-painter\\readme_stuff\\shrek_original.gif"
    # gif_frames_full_filepaths = ['C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0000.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0001.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0002.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0003.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0004.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0005.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0006.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0007.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0008.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0009.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0010.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0011.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0012.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0013.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0014.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0015.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0016.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0017.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0018.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0019.png']
    
    # ui = ParameterUI(target_filepath=path_of_target, gif_frames_full_filepath_list=gif_frames_full_filepaths)
    # ui.run()