import tkinter.ttk as ttk
import tkinter as tk
from select_coordinate_ui import *
from tkinter_components import *
import random
import os
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
        self.PARAM_COMPONENT_WIDTH = 600
        self.PARAM_SLIDER_HEIGHT = 100
        self.PARAM_DUAL_SLIDER_HEIGHT = 115
        self.PARAM_CHECKBOX_HEIGHT = 25
        self.PARAM_TEXT_INPUT_HEIGHT = 100
        self.PAD_BETWEEN_ALL_COMPONENTS = 0
        self.CUSTOM_PADDING_HEIGHT = 15
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
        

        self.initial_choose_vector_eqn_btn_label = "Shift vector field origin to (?, ?)" if self.file_ext != ".gif" else "Shift vector field origin to (?, ?), (?,?), ..."

        # Vector field function attribute
        self.vector_field_function = lambda x, y: (-x,-y)
        self.f_string = None
        self.g_string = None

        # Shift vector field origin attribute
        self.is_selected_vector_field_origin = False



        # Initialize the UI
        self._create_ui()
    
    def on_dummy(self, *args, **kwargs):
        pass
    def apply_modern_notebook_style(self):
        """Apply modern styling to the ttk.Notebook and remove dotted focus line from tabs"""
        style = ttk.Style()
        
        # Configure modern tab appearance
        style.configure("Modern.TNotebook", 
                    background="#f8f9fa",
                    borderwidth=0)
        
        style.configure("Modern.TNotebook.Tab",
                    padding=[10, 10],  # More spacious padding
                    background="#e9ecef",
                    foreground="black",  # Always black text
                    font=("Segoe UI", 11, "normal"),
                    borderwidth=0,
                    focuscolor="",      # Disable focus highlight
                    lightcolor="",      # Remove light border effect
                    darkcolor="")       # Remove dark border effect (optional)
        
        # Active tab styling (background only, text remains black)
        style.map("Modern.TNotebook.Tab",
                background=[("selected", "#007bff"),
                            ("active", "#6c757d")],
                focuscolor=[("!focus", "#e9ecef"), ("focus", "#e9ecef")])

        # Remove the focus element from the tab layout to fully eliminate the dotted line
        style.layout("Modern.TNotebook.Tab",
            [('Notebook.tab', {'sticky': 'nswe', 'children':
                [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
                    [('Notebook.label', {'side': 'top', 'sticky': ''})]
                })]
            })]
        )
        
        # Apply the style to your notebook
        self.notebook.configure(style="Modern.TNotebook")
    # Helper for scrollable frame
    class ScrollableFrame(tk.Frame):
        def __init__(self, master, **kwargs):
            super().__init__(master, **kwargs)
            canvas = tk.Canvas(self, borderwidth=0, background="white", highlightthickness=0)
            self.frame = tk.Frame(canvas, background="white")
            vsb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=vsb.set)
            canvas.pack(side="left", fill="both", expand=True)
            vsb.pack(side="right", fill="y")
            canvas.create_window((0, 0), window=self.frame, anchor="nw")
            self.frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            self.canvas = canvas
    
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

    def _create_ui(self):
        """Create the main UI elements"""
        self.root = tk.Tk()
        self.root.title("Hill Climb Painter UI")
        self.root.geometry('1000x1000')
        self.root.configure(bg='white')
        self.root.resizable(True, True)

        self.notebook = ttk.Notebook(self.root)
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
    

    def _create_parameter_widgets_tab_1(self):
        # Check file extension
        if not self.target_filepath:
            return
        file_ext = self.file_ext

        """Create all parameter widgets for the first tab"""
        # 1) Computation size
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
            subtitle="- Number of iterations grows from min to max linearly as more textures are painted. \
                \n- Higher iteraton improves texture placement but requires more computation", is_set_width_to_parent=True, bg_color=color)
        self.hill_climb_range.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.hill_climb_range, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 4) Texture opacity settings
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.texture_opacity_slider = SingleSlider(self.param_frame, min_val=0, max_val=100, init_val=50, width=self.PARAM_COMPONENT_WIDTH,
            title="4) Texture opacity percentage: <current_value>%", 
            subtitle="- Gives the texture a translucent effect by decreasing its opacity", is_set_width_to_parent=True, bg_color=color)
        self.texture_opacity_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.texture_opacity_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 5) Initial texture width
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.rect_width_slider = SingleSlider(self.param_frame, min_val=10, max_val=200, init_val=20, width=self.PARAM_COMPONENT_WIDTH, 
            title="5) Initial texture width to <current_value> pixels", 
            subtitle="- Influences size of texture when it is initially created", is_set_width_to_parent=True, bg_color=color)
        self.rect_width_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.rect_width_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 6) Allow size of texture to vary
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.scaling_chk = CustomCheckbox(self.param_frame, text="6) Allow size of texture to vary during optimization", checked=True, width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT, 
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
            # 7.i) Show improvement of individual textures
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.rect_improve_chk = CustomCheckbox(self.param_frame, text="7.i)Show improvement of individual textures", checked=False, width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT, is_set_width_to_parent=True, bg_color=color)
            self.rect_improve_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.param_vis_manager.register_widget(self.rect_improve_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            # 7.ii) Display final image after painting (conditional)
            display_final_chk = None
            if file_ext in ['.png', '.jpg', '.jpeg']:
                color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
                self.prev_color_idx = self.widget_color_idx
                self.display_final_chk = CustomCheckbox(self.param_frame, text="7.ii) Display final image after painting", checked=False, width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT, is_set_width_to_parent=True, bg_color=color)
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
        # 8i) Terminate after n iterations
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.fail_threshold_slider = SingleSlider(self.param_frame, min_val=20, max_val=100, init_val=100, width=self.PARAM_COMPONENT_WIDTH, height=50, 
            subtitle="- 8i) Terminate after <current_value> failed iterations where there is no improvement", is_set_width_to_parent=True, bg_color=color)
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
        self.edit_vector_btn = tk.Button(self.param_frame, text="9.i) Edit vector field: (f(x,y), g(x,y)) = (-x, -y)", font=("Arial", 11), bg='#007fff', fg='white', relief='flat', command=self.on_edit_vector_field)
        self.edit_vector_btn.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.edit_vector_btn, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})

        # 9.iii) Debug vector field function
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.debug_vector_btn = tk.Button(self.param_frame, text="9.iii) Debug vector field function", font=("Arial", 11), bg='#007fff', fg='white', relief='flat', command=self.on_debug_vector_field)
        self.debug_vector_btn.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.debug_vector_btn, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})

        # 9.ii) Shift vector field origin
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx

        self.shift_vector_origin_btn = tk.Button(self.param_frame, text=self.initial_choose_vector_eqn_btn_label, font=("Arial", 11), bg='#007fff', fg='white', relief='flat', command=self.on_shift_vector_origin)
        self.shift_vector_origin_btn.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.shift_vector_origin_btn, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        

        # Set up dependency: 9.i, 9.ii only show if vector_field_chk is checked
        self.vector_field_chk.set_controlled_widgets([self.edit_vector_btn, self.shift_vector_origin_btn, self.debug_vector_btn])

    def _create_parameter_widgets_tab_2(self):
        """Create parameter widgets for the second tab (Output Settings) based on file extension"""
        # Check file extension
        if not self.target_filepath:
            return
        file_ext = self.file_ext

        # Section 6: Image Output Settings (for .png, .jpg, .jpeg)
        if file_ext in ['.png', '.jpg', '.jpeg']:
            # 1) Output image size
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
                title="3.i) GIF filename", is_set_width_to_parent=True, bg_color=color
            )
            self.gif_name_input.set("gif_output")
            self.gif_name_input.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.gif_name_input, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS}, controller=self.create_gif_chk)
            # Set controlled widgets for the checkbox
            self.create_gif_chk.set_controlled_widgets([self.gif_name_input])
            self.add_between_padding(self.output_frame, self.output_vis_manager)




        # Sections 8: GIF Settings (for .gif)
        elif file_ext == '.gif':
            # 1) Limit number of frames painted in original GIF.
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
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
    
    # Vector field buttons
    def on_shift_vector_origin(self):
        print("Opens the window to get list of (x,y) coordinates")
        # prereq: either gif frames Or target image
        self.resize_shorter_side_of_target = self.computation_size_slider.get()
        if self.file_ext != ".gif":
            # print(self.target_filepath, self.resize_shorter_side_of_target)
            print("self.list_of_coord_for_shifting_vector_field_origin before", self.list_of_coord_for_shifting_vector_field_origin)
            user_choosen_coords_list = create_coord_selector_UI(self.target_filepath, self.resize_shorter_side_of_target, master=self.root)
            if user_choosen_coords_list is not None:
                self.list_of_coord_for_shifting_vector_field_origin = user_choosen_coords_list
                self.is_selected_vector_field_origin = True
                if len(user_choosen_coords_list) == 1:
                    label = "Shift field center to: " + str(user_choosen_coords_list[0])
                else:
                    label = str(user_choosen_coords_list[0])+str(user_choosen_coords_list[1])+"..."
                self.shift_vector_origin_btn.config(text=label)
            print("self.list_of_coord_for_shifting_vector_field_origin after", self.list_of_coord_for_shifting_vector_field_origin)

        else:
            # need the gif frames somehow...
            print("Gif frames required")

    # Adjusting computation size slider will reset the selected vector field
    def on_computation_size_slider_change(self, sliderval=None):
        self.is_selected_vector_field_origin = False
        self.list_of_coord_for_shifting_vector_field_origin = None
        self.shift_vector_origin_btn.config(text=self.initial_choose_vector_eqn_btn_label)

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
            self.edit_vector_btn.configure(text=f"9.i) Edit vector field: {function_string}")
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

    def run(self):
        """Start the UI main loop"""
        self.root.mainloop()
# Example usage:
if __name__ == "__main__":
    # path_of_target = "asd.png"
    path_of_target = "C:\\Git Repos\\hill-climb-painter\\target_gif\\galaxy.gif"
    path_of_target = "C:\\Git Repos\\hill-climb-painter\\target_image\\cat.jpg"
    # path_of_target = "C:\\Git Repos\\hill-climb-painter\\target_image\\rainbow.png"

    # Create an instance of ParameterUI with a target file path
    ui = ParameterUI(target_filepath=path_of_target, gif_frames_full_filepath_list=None)
    
    # Start the UI
    ui.run()