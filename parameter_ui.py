import tkinter.ttk as ttk
import tkinter as tk
from select_coordinate_ui import *
from tkinter_components import *

from utilities import count_frames_in_gif
from vector_field_equation_ui import create_vector_field_visualizer



class ParameterUI:
    def __init__(self, target_filepath, gif_frames_full_filepath_list = None):
        """
        Initialize the Parameter UI with an optional target file path.
        
        Args:
            target_filepath (str, optional): Path to target file to get its extention
        """
        self.target_filepath = target_filepath
        self.gif_frames_full_filepath_list = gif_frames_full_filepath_list # will be provided if the target is gif

        self.list_of_coord_for_shifting_vector_field_origin = None
        self.file_ext = os.path.splitext(self.target_filepath)[1].lower() if self.target_filepath else None # Gets the file extention
        if self.file_ext == ".gif":
            self.num_frames_in_original_gif = count_frames_in_gif(self.target_filepath)
            if gif_frames_full_filepath_list is None:
                raise AssertionError("Extention is gif but no gif frames are provided for ParameterUI")
        # Abstracted dimensions for first tab components
        self.PARAM_COMPONENT_WIDTH = 500
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
        

        self.initial_choose_vector_eqn_btn_label = "*Shift origin to (?, ?)" if self.file_ext != ".gif" else "*Shift origin to (?, ?), (?, ?), ..."

        # Vector field function attribute
        self.vector_field_function = lambda x, y: (-x,-y)
        self.f_string = None
        self.g_string = None

        # Shift vector field origin attribute
        self.is_selected_vector_field_origin = False

        # Initialize the param dict to be returned
        self.result = None

        # Initialize the UI
        self._create_ui()
    
    def on_dummy(self, *args, **kwargs):
        pass
    
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
        print("Setting up button style...")
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
            foreground='red',     # red text
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
        window_width = 540
        window_height = 800
        center_window(self.root, window_width, window_height)
        self.root.minsize(window_width, 540)   # Set minimum window size (width, height)
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
        self.button2 = ttk.Button(self.dual_button_frame, text="Submit", command=self.on_submit_button_press)
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
        self.result = {"command": "user_closed_param_ui_window"}
        dialog.destroy()
        self.root.quit()  # Exit mainloop
        self.root.destroy()  # Destroy window

    def on_select_target_texture(self):
        """Handle 'Select target and texture' button press"""
        self.result = {"command": "reselect_target_texture"}
        self.root.quit()  # Exit mainloop
        self.root.destroy()  # Destroy window
    def on_submit_button_press(self):
        """Handle 'Submit' button press"""
        self.result = {"command": "run", "parameters": self.get_parameters()}
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
        self.computation_size_slider = SingleSlider(self.param_frame, min_val=100, max_val=500, init_val=500, width=self.PARAM_COMPONENT_WIDTH, 
            title="1) Computation size: <current_value> pixels", 
            subtitle="- Increase to capture more image detail, decrease for speed\n- Slider will reset existing selection of vector field origin translation coordinates", 
            is_set_width_to_parent=True, bg_color=color, command=self.on_computation_size_slider_change)
        self.computation_size_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.computation_size_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)
        self.resize_shorter_side_of_target = self.computation_size_slider.get()


        # 2) Add how many textures
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.num_shapes_slider = SingleSlider(self.param_frame, min_val=100, max_val=1000, init_val=500, width=self.PARAM_COMPONENT_WIDTH, 
            title="2) Add <current_value> textures", subtitle="- Increase to paint finer details, decrease for speed", is_set_width_to_parent=True, bg_color=color)
        self.num_shapes_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.num_shapes_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 3) Number of personally climb iterations
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.hill_climb_range = RangeSlider(self.param_frame, min_val=1, max_val=500, init_min=20, init_max=100, width=self.PARAM_COMPONENT_WIDTH,
            title="3) Number of hill climb iterations: Min = <current_min_value>, Max = <current_max_value>", 
            subtitle="- Number of iterations grows linearly as more textures are painted. \
                \n- Higher iteraton improves texture placement but requires more computation", is_set_width_to_parent=True, bg_color=color)
        self.hill_climb_range.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.hill_climb_range, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 4) Texture opacity settings
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.texture_opacity_slider = SingleSlider(self.param_frame, min_val=0, max_val=100, init_val=100, width=self.PARAM_COMPONENT_WIDTH,
            title="4) Texture opacity: <current_value>%", 
            subtitle="- Give the texture a translucent effect by decreasing its opacity", is_set_width_to_parent=True, bg_color=color)
        self.texture_opacity_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.texture_opacity_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 5) Initial texture width
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.rect_width_slider = SingleSlider(self.param_frame, min_val=10, max_val=200, init_val=20, width=self.PARAM_COMPONENT_WIDTH, 
            title="5) Initial texture size: <current_value> pixels", 
            subtitle="- Influences size of texture when it is initially created", is_set_width_to_parent=True, bg_color=color)
        self.rect_width_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.rect_width_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 6) Allow size of texture to vary
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.scaling_chk = CustomCheckbox(self.param_frame, text="6) Constrain texture dimensions to initial size", checked=True, width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT, 
            is_set_width_to_parent=True, bg_color=color)
        self.scaling_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.scaling_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        if file_ext in ['.png', '.jpg', '.jpeg']:
            # 7) Show painting progress as new textures are added
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.show_pygame_chk = CustomToggleVisibilityCheckbox(self.param_frame, text="7) Display painting progress", checked=False, visibility_manager=self.param_vis_manager, width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT, is_set_width_to_parent=True, bg_color=color)
            self.show_pygame_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.param_vis_manager.register_widget(self.show_pygame_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            # 7a) Show improvement of individual textures
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.rect_improve_chk = CustomCheckbox(self.param_frame, text="7a) Display placement progress", checked=False, width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT, is_set_width_to_parent=True, bg_color=color)
            self.rect_improve_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.param_vis_manager.register_widget(self.rect_improve_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            # 7b) Display final image after painting (conditional)
            display_final_chk = None
            if file_ext in ['.png', '.jpg', '.jpeg']:
                color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
                self.prev_color_idx = self.widget_color_idx
                self.display_final_chk = CustomCheckbox(self.param_frame, text="7b) Display final image after painting", checked=False, width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT, is_set_width_to_parent=True, bg_color=color)
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
        self.premature_chk = CustomToggleVisibilityCheckbox(self.param_frame, text="8) Allow early termination of hill climbing", checked=False, 
            visibility_manager=self.param_vis_manager, width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT, is_set_width_to_parent=True, bg_color=color)
        self.premature_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.premature_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        # 8a) Terminate after n iterations
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.fail_threshold_slider = SingleSlider(self.param_frame, min_val=20, max_val=100, init_val=100, width=self.PARAM_COMPONENT_WIDTH, height=50, 
            subtitle="- Terminate after <current_value> failed iterations where there is no improvement", is_set_width_to_parent=True, bg_color=color)
        self.fail_threshold_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.fail_threshold_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)
        # Set up conditional logic: fail_threshold_slider only shows when premature_chk is checked
        self.premature_chk.set_controlled_widgets([self.fail_threshold_slider])


        # 9) Enable vector field
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.vector_field_chk = CustomToggleVisibilityCheckbox(self.param_frame, text="9) Enable vector field", checked=False, visibility_manager=self.param_vis_manager, width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT, is_set_width_to_parent=True, bg_color=color)
        self.vector_field_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.vector_field_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})

        # 9.i) Edit vector field
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.edit_vector_btn = ttk.Button(self.param_frame, text="(f(x,y), g(x,y)) = (-x, -y)", 
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
                self.output_frame, min_val=800, max_val=4000, init_val=1200,
                width=self.PARAM_COMPONENT_WIDTH,
                title="1) Output image size: <current_value> px", subtitle="- Render the output in a higher resolution", 
                is_set_width_to_parent=True, bg_color=color
            )
            self.output_size_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.output_size_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)


            # 2) Name of output image
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.image_name_input = CustomTextInput(
                self.output_frame, width=self.PARAM_COMPONENT_WIDTH,
                title="2) Name of output image", subtitle="- Image will be saved to output folder when algorithm terminates", is_set_width_to_parent=True, bg_color=color
            )
            self.image_name_input.set("image_output")
            self.image_name_input.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.image_name_input, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)

            # 3) Create GIF progress Checkbox
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.create_gif_chk = CustomToggleVisibilityCheckbox(
                self.output_frame, text="3) Create GIF of painting progress", checked=False,
                width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT,
                is_set_width_to_parent=True, bg_color=color,
                visibility_manager=self.output_vis_manager
            )
            self.create_gif_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.create_gif_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            # 3i) GIF Filename Input
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.gif_name_input = CustomTextInput(
                self.output_frame, width=self.PARAM_COMPONENT_WIDTH, 
                title="3a) Enter GIF filename", subtitle="- Gif will be saved to output folder when algorithm terminates", is_set_width_to_parent=True, bg_color=color
            )
            self.gif_name_input.set("gif_output")
            self.gif_name_input.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.gif_name_input, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS}, controller=self.create_gif_chk)
            # Set controlled widgets for the checkbox
            self.create_gif_chk.set_controlled_widgets([self.gif_name_input])
            self.add_between_padding(self.output_frame, self.output_vis_manager)




        # Sections 8: GIF Settings (for .gif)
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

            # Painted GIF Filename Input
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.painted_gif_name_input = CustomTextInput(
                self.output_frame, width=self.PARAM_COMPONENT_WIDTH,
                title="2) Painted GIF filename", subtitle=None, is_set_width_to_parent=True, bg_color=color
            )
            self.painted_gif_name_input.set("painted_gif_output")
            self.painted_gif_name_input.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.painted_gif_name_input, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)

            # Multiprocessing Checkbox
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.multiprocessing_chk = CustomCheckbox(
                self.output_frame, text="3) Enable multiprocessing for batch frame processing", checked=False,
                width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT,
                is_set_width_to_parent=True, bg_color=color
            )
            self.multiprocessing_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.multiprocessing_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)
    
    ############### Vector field buttons #################
    def on_shift_vector_origin(self):
        print("Opens the window to get list of (x,y) coordinates")
        # prereq: either gif frames Or target image
        self.resize_shorter_side_of_target = self.computation_size_slider.get()

        # Non GIF case
        if self.file_ext != ".gif":
            user_choosen_coords_list = create_coord_selector_UI(self.target_filepath, self.resize_shorter_side_of_target, master=self.root)
            if user_choosen_coords_list is not None:
                self.list_of_coord_for_shifting_vector_field_origin = user_choosen_coords_list
                self.is_selected_vector_field_origin = True
                label = "Shift origin to: " + str(user_choosen_coords_list[0])
                self.shift_vector_origin_btn.config(text=label)
                self.style.configure("button_shift_vector_field.TButton", foreground="black")

        # GIF case
        else:
            user_choosen_coords_list = create_coord_selector_UI(self.gif_frames_full_filepath_list, self.resize_shorter_side_of_target, master=self.root)
            if user_choosen_coords_list is not None:
                self.list_of_coord_for_shifting_vector_field_origin = user_choosen_coords_list
                label = "Shift origin to: " + str(user_choosen_coords_list[0])+", "+str(user_choosen_coords_list[1])+"..."
                self.shift_vector_origin_btn.config(text=label)
                self.style.configure("button_shift_vector_field.TButton", foreground="black")


    # Adjusting computation size slider will reset the selected vector field
    def on_computation_size_slider_change(self, sliderval=None):
        self.is_selected_vector_field_origin = False
        self.list_of_coord_for_shifting_vector_field_origin = None
        self.shift_vector_origin_btn.config(text=self.initial_choose_vector_eqn_btn_label)
        self.style.configure("button_shift_vector_field.TButton", foreground="red")

        
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
        if self.f_string is None or self.g_string is None:
            result = create_vector_field_visualizer(custom_presets, custom_grid_sizes, master=self.root)
        else:
            result = create_vector_field_visualizer(custom_presets, custom_grid_sizes, master=self.root, initial_f_string=self.f_string, initial_g_string=self.g_string)

        if result is not None:
            function_string = result[0]
            # Update button text with the returned string
            self.edit_vector_btn.configure(text=f"(f(x,y), g(x,y)) = {function_string}")
            # Update the vector field function
            self.vector_field_function = result[1]
            # update the f_string and g_string
            expr = function_string.strip("()")  # Remove the parentheses
            self.f_string, self.g_string = [part.strip() for part in expr.split(",")]  # Split by comma and strip whitespace

    def on_debug_vector_field(self):
        print(f"[DEBUG] vector_field_function id: {id(self.vector_field_function)}")
        try:
            print("[DEBUG] self.list_of_coord_for_shifting_vector_field_origin=", self.list_of_coord_for_shifting_vector_field_origin)
            print(f"[DEBUG] vector_field_function(1, 1): {self.vector_field_function(1, 1)}")
            print(self.f_string, self.g_string)
            # print(self.list_of_coord_for_shifting_vector_field_origin)
        except Exception as e:
            print(f"[DEBUG] Error calling vector_field_function: {e}")
    ######################################################

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
            parameters['create_gif'] = self.create_gif_chk.get()
            parameters['gif_output_name'] = self.gif_name_input.get() if self.create_gif_chk.get() else None
        elif self.file_ext == '.gif':
            parameters['num_frames_to_paint'] = self.frames_in_gif_slider.get()
            parameters['painted_gif_name'] = self.painted_gif_name_input.get()
            parameters['enable_multiprocessing'] = self.multiprocessing_chk.get()

        return parameters

    def run(self):
        """Start the UI main loop and return the result based on user action"""
        self.result = None  # Reset result
        self.root.mainloop()  # Run the Tkinter main loop
        return self.result  # Return the result set by button actions or closing

        # modify the run method and the methods inside param ui to return values in 3 cases:
        # Case 1: User closed the "X" button
        # return {"command":"user_closed_param_ui_window"}

        # Case 2: User pressed button1 (Select target and texture button)
        # return {"command":"reselect_target_texture"}

        # Case 3: User pressed button2 (Submit button)
        # return {"command":"run", "parameters":<parameter dictionary obtained>}

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

# def get_command_from_parameter_ui(target, texture):
#     # Initialises the GUI and returns its output
#     # init gui
#     # call its run method to get output
#     # return output


# Inside another file:
# import get_command_from_parameter_ui from parameter_ui

# get_command_from_parameter_ui("C:\\Git Repos\\hill-climb-painter\\readme_stuff\\shrek_original.gif", 
#                               ['C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0000.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0001.png'])


# Take a look at the run method and clarify requirements before coding



# in other file...
if __name__ == "__main__":

    path_of_target = "C:\\Git Repos\\hill-climb-painter\\readme_stuff\\shrek_original.gif"
    gif_frames_full_filepaths = ['C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0000.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0001.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0002.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0003.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0004.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0005.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0006.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0007.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0008.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0009.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0010.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0011.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0012.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0013.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0014.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0015.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0016.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0017.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0018.png', 'C:\\Git Repos\\hill-climb-painter\\original_gif_frames\\shrek_painted_frame_0019.png']

    command = get_command_from_parameter_ui(path_of_target, target_gif_frames=gif_frames_full_filepaths)
    print(command)

    
#     path_of_target = "C:\\Git Repos\\hill-climb-painter\\target_image\\cat.jpg"

#     ui = ParameterUI(target_filepath=path_of_target, gif_frames_full_filepath_list=None)
#     ui.run()
    

    # quit()
    # path_of_target = "C:\\Git Repos\\hill-climb-painter\\readme_stuff\\shrek_original.gif"
    # gif_frames_full_filepaths = ['C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0000.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0001.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0002.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0003.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0004.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0005.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0006.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0007.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0008.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0009.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0010.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0011.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0012.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0013.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0014.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0015.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0016.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0017.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0018.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0019.png']
    
    # ui = ParameterUI(target_filepath=path_of_target, gif_frames_full_filepath_list=gif_frames_full_filepaths)
    # ui.run()