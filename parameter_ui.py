import tkinter.ttk as ttk
import tkinter as tk
from tkinter_components import *
import random
import os


class ParameterUI:
    def __init__(self, target_filepath=None):
        """
        Initialize the Parameter UI with an optional target file path.
        
        Args:
            target_filepath (str, optional): Path to target file for processing
        """
        self.target_filepath = target_filepath
        
        # Abstracted dimensions for first tab components
        self.PARAM_COMPONENT_WIDTH = 500
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
        
        self.widget_color_idx = 0
        self.prev_color_idx = None
        
        # Initialize the UI
        self._create_ui()
    
    def on_dummy(self, *args, **kwargs):
        pass
    
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
        file_ext = os.path.splitext(self.target_filepath)[1].lower()

        """Create all parameter widgets for the first tab"""
        # 1) Computation size
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.resize_slider = SingleSlider(self.param_frame, min_val=100, max_val=500, init_val=500, width=self.PARAM_COMPONENT_WIDTH, 
            title="1) Computation size: <current_value> pixels", subtitle="- Increase to capture more image detail, decrease for speed", is_set_width_to_parent=True, bg_color=color)
        self.resize_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.resize_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 2) Add how many textures
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.num_shapes_slider = SingleSlider(self.param_frame, min_val=100, max_val=1000, init_val=500, width=self.PARAM_COMPONENT_WIDTH, 
            title="2) Add <current_value> textures", subtitle="- Increase to paint finer details, decrease for speed", is_set_width_to_parent=True, bg_color=color)
        self.num_shapes_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.num_shapes_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        self.add_between_padding(self.param_frame, self.param_vis_manager)


        # 3) Number of hill climb iterations
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
        # 9.i) Enable vector field
        color, self.widget_color_idx = self.get_next_color(self.widget_color_idx+1, self.prev_color_idx)
        self.prev_color_idx = self.widget_color_idx
        self.edit_vector_btn = tk.Button(self.param_frame, text="9.i) Edit vector field", font=("Arial", 11), bg='#007fff', fg='white', relief='flat')
        self.edit_vector_btn.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
        self.param_vis_manager.register_widget(self.edit_vector_btn, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
        # Set up dependency: edit_vector_btn only shows if vector_field_chk is checked
        self.vector_field_chk.set_controlled_widgets([self.edit_vector_btn])


        # 10) Display final image checkbox
        if file_ext in ['.png', '.jpg', '.jpeg']:
            # (Removed: now handled as 7.ii)
            pass # This block is now redundant as the checkbox is moved


        
    def _create_parameter_widgets_tab_2(self):
        """Create parameter widgets for the second tab (Output Settings) based on file extension"""
        # Check file extension
        if not self.target_filepath:
            return
        file_ext = os.path.splitext(self.target_filepath)[1].lower()

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
            # Section 8: Make GIF from GIF Settings
            # Frames in GIF Slider
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.frames_in_gif_slider = SingleSlider(
                self.output_frame, min_val=2, max_val=200, init_val=200,
                width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_SLIDER_HEIGHT,
                title="Frames in original GIF", subtitle=None, is_set_width_to_parent=True, bg_color=color
            )
            self.frames_in_gif_slider.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.frames_in_gif_slider, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)

            # Painted GIF Filename Input
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.painted_gif_name_input = CustomTextInput(
                self.output_frame, width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_TEXT_INPUT_HEIGHT,
                title="Painted GIF filename", subtitle=None, is_set_width_to_parent=True, bg_color=color
            )
            self.painted_gif_name_input.set("painted_gif_output")
            self.painted_gif_name_input.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.painted_gif_name_input, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)

            # Multiprocessing Checkbox
            color, self.widget_color_idx = self.get_next_color(self.widget_color_idx + 1, self.prev_color_idx)
            self.prev_color_idx = self.widget_color_idx
            self.multiprocessing_chk = CustomCheckbox(
                self.output_frame, text="Enable multiprocessing for batch frame processing", checked=False,
                width=self.PARAM_COMPONENT_WIDTH, height=self.PARAM_CHECKBOX_HEIGHT,
                is_set_width_to_parent=True, bg_color=color
            )
            self.multiprocessing_chk.pack(fill='x', pady=self.PAD_BETWEEN_ALL_COMPONENTS)
            self.output_vis_manager.register_widget(self.multiprocessing_chk, {'fill': 'x', 'pady': self.PAD_BETWEEN_ALL_COMPONENTS})
            self.add_between_padding(self.output_frame, self.output_vis_manager)

    # def get_parameters(self):
    #     """Get all current parameter values as a dictionary"""
    #     params = {
    #         'resize_size': self.resize_slider.get(),
    #         'num_textures': self.num_shapes_slider.get(),
    #         'hill_climb_min': self.hill_climb_range.get_min(),
    #         'hill_climb_max': self.hill_climb_range.get_max(),
    #         'texture_opacity': self.texture_opacity_slider.get(),
    #         'initial_width': self.rect_width_slider.get(),
    #         'allow_scaling': self.scaling_chk.get(),
    #         'show_progress': self.show_pygame_chk.get(),
    #         'show_improvement': self.rect_improve_chk.get(),
    #         'early_termination': self.premature_chk.get(),
    #         'fail_threshold': self.fail_threshold_slider.get(),
    #         'vector_field_enabled': self.vector_field_chk.get(),
    #         'target_filepath': self.target_filepath
    #     }

    #     # Add Section 6 parameters if they exist (for .png, .jpg, .jpeg)
    #     if hasattr(self, 'output_size_slider'):
    #         params.update({
    #             'output_image_size': self.output_size_slider.get(),
    #             'image_name': self.image_name_input.get(),
    #             'append_datetime': self.append_datetime_chk.get(),
    #             'display_final_image': self.display_final_chk.get()
    #         })

    #     # Add Sections 7 and 8 parameters if they exist (for .gif)
    #     if hasattr(self, 'create_gif_chk'):
    #         params.update({
    #             'create_gif': self.create_gif_chk.get(),
    #             'gif_fps': self.gif_fps_slider.get(),
    #             'gif_filename': self.gif_name_input.get(),
    #             'frames_in_gif': self.frames_in_gif_slider.get(),
    #             'painted_gif_filename': self.painted_gif_name_input.get(),
    #             'enable_multiprocessing': self.multiprocessing_chk.get()
    #         })

    #     return params

    def run(self):
        """Start the UI main loop"""
        self.root.mainloop()

# Example usage:
if __name__ == "__main__":
    # Create an instance of ParameterUI with a target file path
    ui = ParameterUI(target_filepath="path/to/target/image.gif")
    
    # Start the UI
    ui.run()
    
    # # After the UI is closed, you can get the parameter values
    # parameters = ui.get_parameters()
    # print("Selected parameters:", parameters)