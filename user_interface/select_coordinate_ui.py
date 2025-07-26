import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
from typing import Union, List, Tuple
from abc import ABC, abstractmethod

def center_window(root, width, height):
    """Center the given window on the screen."""
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate position to center the window
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2) - 10
    
    # Set window geometry
    root.geometry(f"{width}x{height}+{x}+{y}")

class WindowConfig:
    """Centralized configuration for all window sizing and spacing"""
    # Padding and margins
    WINDOW_PADDING_X = 20
    WINDOW_PADDING_Y = 20
    COMPONENT_SPACING = 10
    BUTTON_FRAME_PADDING = 10
    CANVAS_MARGIN = 10
    
    # Component heights
    TITLE_HEIGHT = 25
    SUBTITLE_HEIGHT = 20
    INSTRUCTION_HEIGHT = 15
    COORD_LABEL_HEIGHT = 18
    BUTTON_HEIGHT = 60
    SLIDER_CONTAINER_HEIGHT = 35
    
    # Minimum sizes
    MIN_WINDOW_WIDTH = 590
    MIN_CANVAS_WIDTH = 400
    MIN_CANVAS_HEIGHT = 200
    
    # Button styling
    BUTTON_PADDING_X = 20
    BUTTON_PADDING_Y = 15
    BUTTON_GRID_SPACING = 10
    
    # Font sizes
    TITLE_FONT_SIZE = 15
    SUBTITLE_FONT_SIZE = 11
    COORD_LABEL_FONT_SIZE = 13
    BUTTON_FONT_SIZE = 13
    SLIDER_LABEL_FONT_SIZE = 10

class UIComponent(ABC):
    """Abstract base class for UI components that need to report their space requirements"""
    
    @abstractmethod
    def get_required_height(self) -> int:
        """Return the height this component requires"""
        pass
    
    @abstractmethod
    def get_required_width(self) -> int:
        """Return the width this component requires"""
        pass
    
    def get_spacing_after(self) -> int:
        """Return the spacing needed after this component"""
        return WindowConfig.COMPONENT_SPACING

class TitleComponent(UIComponent):
    def __init__(self, has_subtitle: bool = False, has_instruction: bool = False):
        self.has_subtitle = has_subtitle
        self.has_instruction = has_instruction
    
    def get_required_height(self) -> int:
        height = WindowConfig.TITLE_HEIGHT
        if self.has_subtitle:
            height += WindowConfig.SUBTITLE_HEIGHT + 5  # Small gap between title and subtitle
        if self.has_instruction:
            height += WindowConfig.INSTRUCTION_HEIGHT + 5
        return height
    
    def get_required_width(self) -> int:
        return 400  # Minimum width for title text

class CoordLabelComponent(UIComponent):
    def get_required_height(self) -> int:
        return WindowConfig.COORD_LABEL_HEIGHT
    
    def get_required_width(self) -> int:
        return 300  # Minimum width for coordinate label

class CanvasComponent(UIComponent):
    def __init__(self, canvas_width: int, canvas_height: int):
        self.canvas_width = max(canvas_width, WindowConfig.MIN_CANVAS_WIDTH)
        self.canvas_height = max(canvas_height, WindowConfig.MIN_CANVAS_HEIGHT)
    
    def get_required_height(self) -> int:
        return self.canvas_height
    
    def get_required_width(self) -> int:
        return self.canvas_width

class ButtonFrameComponent(UIComponent):
    def __init__(self, button_count: int = 2):
        self.button_count = button_count
    
    def get_required_height(self) -> int:
        # Add extra padding to ensure buttons are fully visible
        return WindowConfig.BUTTON_HEIGHT + (2 * WindowConfig.BUTTON_FRAME_PADDING) + 10
    
    def get_required_width(self) -> int:
        # Calculate minimum width needed for buttons with equal spacing
        button_width = 150  # Minimum button width
        spacing = WindowConfig.BUTTON_GRID_SPACING
        total_spacing = spacing * (self.button_count + 1)  # Spacing on sides and between buttons
        return (button_width * self.button_count) + total_spacing
    
    def get_spacing_after(self) -> int:
        return 0  # Button frame is typically at the bottom

class SliderComponent(UIComponent):
    def __init__(self, visible: bool = True):
        self.visible = visible
    
    def get_required_height(self) -> int:
        return WindowConfig.SLIDER_CONTAINER_HEIGHT if self.visible else 0
    
    def get_required_width(self) -> int:
        return 350 if self.visible else 0  # Width for slider + labels

class DynamicWindowSizer:
    """Calculates window dimensions based on component requirements"""
    
    def __init__(self):
        self.components = []
    
    def add_component(self, component: UIComponent):
        """Add a component to the layout calculation"""
        self.components.append(component)
    
    def calculate_required_height(self) -> int:
        """Calculate total height needed for all components"""
        total_height = WindowConfig.WINDOW_PADDING_Y * 2  # Top and bottom padding
        
        for i, component in enumerate(self.components):
            total_height += component.get_required_height()
            if i < len(self.components) - 1:  # Don't add spacing after last component
                total_height += component.get_spacing_after()
        
        return total_height
    
    def calculate_required_width(self) -> int:
        """Calculate total width needed for all components"""
        max_component_width = max((comp.get_required_width() for comp in self.components), default=0)
        total_width = max_component_width + (WindowConfig.WINDOW_PADDING_X * 2)
        return max(total_width, WindowConfig.MIN_WINDOW_WIDTH)
    
    def get_window_dimensions(self) -> Tuple[int, int]:
        """Get the calculated window dimensions"""
        return self.calculate_required_width(), self.calculate_required_height()

class SingleSliderModified(tk.Canvas):
    def __init__(self, master, min_val=0, max_val=100, init_val=None, width=300, height=None,
                 command=None, title=None, subtitle=None, title_size=13, subtitle_size=10,
                 bg_color='white', active_color='#007fff', inactive_color='#ccc',
                 active_thumb_color='#007fff', is_set_width_to_parent=False,
                 show_value_labels=False, variable=None, **kwargs):
        self._line_spacing = 4
        if height is None:
            height = self._calculate_height(title, subtitle, title_size, subtitle_size)
        kwargs.setdefault('bg', bg_color)
        kwargs.setdefault('highlightthickness', 0)
        self.is_set_width_to_parent = is_set_width_to_parent
        self._user_height = height
        super().__init__(master, width=width, height=height, **kwargs)
        if is_set_width_to_parent:
            self.bind('<Configure>', self._on_resize)
        self.min_val = min_val
        self.max_val = max_val
        self.command = command
        self.variable = variable
        self.width = width
        self.height = height
        self.pad = 15
        self.thumb_radius = 10
        self.active_thumb = False
        self.slider_line_y = height // 2
        self.slider_line_width = 4
        self.value_range = max_val - min_val
        self.value = init_val if init_val is not None else min_val
        if self.variable:
            self.variable.set(self.value)
        self.title = title
        self.subtitle = subtitle
        self.title_size = title_size
        self.subtitle_size = subtitle_size
        self.show_value_labels = show_value_labels
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.active_thumb_color = active_thumb_color
        self._draw_slider()
        self.bind('<Button-1>', self._on_click)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _calculate_height(self, title, subtitle, title_size, subtitle_size):
        slider_height = 24
        title_lines = title.count('\n') + 1 if title else 0
        subtitle_lines = subtitle.count('\n') + 1 if subtitle else 0
        title_height = title_size * title_lines + self._line_spacing * (title_lines - 1) if title else 0
        subtitle_height = subtitle_size * subtitle_lines + self._line_spacing * (subtitle_lines - 1) if subtitle else 0
        if title and subtitle:
            return title_height + 7 + subtitle_height + 15 + slider_height
        elif title:
            return title_height + 15 + slider_height
        elif subtitle:
            return subtitle_height + 15 + slider_height
        else:
            return slider_height

    def _on_resize(self, event):
        self.config(width=event.width)
        self.width = event.width
        self.height = self._user_height
        self._draw_slider()

    def _draw_slider(self):
        self.delete('all')
        x = self._value_to_pos(self.value)
        y = 0
        if self.title:
            title_str = self.title.replace('<current_value>', str(self.value))
            title_lines = title_str.split('\n')
            for i, line in enumerate(title_lines):
                self.create_text(self.pad, y, text=line, fill='black', font=('Arial', self.title_size, 'bold'), anchor='nw')
                y += self.title_size
                if i < len(title_lines) - 1:
                    y += self._line_spacing
            if self.subtitle:
                y += 7
            else:
                y += 15
        if self.subtitle:
            subtitle_str = self.subtitle.replace('<current_value>', str(self.value))
            subtitle_lines = subtitle_str.split('\n')
            for i, line in enumerate(subtitle_lines):
                self.create_text(self.pad, y, text=line, fill='black', font=('Arial', self.subtitle_size), anchor='nw')
                y += self.subtitle_size
                if i < len(subtitle_lines) - 1:
                    y += self._line_spacing
            y += 15
        slider_y = y + 12
        self.create_line(self.pad, slider_y, self.width - self.pad, slider_y, width=self.slider_line_width, fill=self.inactive_color)
        self.create_line(self.pad, slider_y, x, slider_y, width=self.slider_line_width, fill=self.active_color)
        rect_w, rect_h = 8, 24
        self.thumb = self.create_rectangle(x - rect_w//2, slider_y - rect_h//2,
                                          x + rect_w//2, slider_y + rect_h//2,
                                          fill=self.active_thumb_color if self.active_thumb else self.active_color,
                                          outline='', tags='thumb')
        if self.show_value_labels:
            value_text = str(int(self.value)) if self.min_val.is_integer() else f"{self.value:.1f}"
            self.create_text(x, slider_y + rect_h//2 + 6, text=value_text, fill=self.active_color, font=('Arial', 10))

    def _value_to_pos(self, value):
        usable_width = self.width - 2 * self.pad
        rel = (value - self.min_val) / self.value_range
        return self.pad + rel * usable_width

    def _pos_to_value(self, x):
        usable_width = self.width - 2 * self.pad
        rel = (x - self.pad) / usable_width
        rel = min(max(rel, 0), 1)
        return self.min_val + rel * self.value_range

    def _on_click(self, event):
        x = event.x
        if x < self.pad or x > self.width - self.pad:
            return
        y = 0
        if self.title:
            y += self.title_size
            if self.subtitle:
                y += 7
            else:
                y += 15
        if self.subtitle:
            y += self.subtitle_size + 15
        slider_y = y + 12
        rect_w, rect_h = 8, 24
        thumb_x = self._value_to_pos(self.value)
        thumb_left = thumb_x - rect_w // 2
        thumb_right = thumb_x + rect_w // 2
        thumb_top = slider_y - rect_h // 2
        thumb_bottom = slider_y + rect_h // 2
        if thumb_left <= x <= thumb_right and thumb_top <= event.y <= thumb_bottom:
            self.active_thumb = True
        else:
            value = self._pos_to_value(x)
            self.value = max(self.min_val, min(self.max_val, value))
            self.active_thumb = True
            self._draw_slider()
            if self.variable:
                self.variable.set(self.value)
            if self.command:
                self.command(self.value)

    def _on_drag(self, event):
        if not self.active_thumb:
            return
        x = min(max(event.x, self.pad), self.width - self.pad)
        value = self._pos_to_value(x)
        if value < self.min_val:
            value = self.min_val
        if value > self.max_val:
            value = self.max_val
        self.value = value
        if self.variable:
            self.variable.set(self.value)
        self._draw_slider()
        if self.command:
            self.command(self.value)

    def _on_release(self, event):
        self.active_thumb = False

    def get(self):
        return self.value

    def set(self, value):
        self.value = value
        if self.variable:
            self.variable.set(self.value)
        self._draw_slider()

class CoordinateSelectorUI:
    def __init__(self, image_filepath: Union[str, List[str]], resize_shorter_side_of_image, replay_fps=10, master=None):
        self.image_paths = [image_filepath] if isinstance(image_filepath, str) else image_filepath
        self.is_single_image = len(self.image_paths) == 1
        self.target_size = resize_shorter_side_of_image
        self.replay_fps = replay_fps
        self.selected_coordinates = []
        self.current_image_index = 0
        self.long_hold_selection_delay = 50
        self.right_click_press_time = 0
        self.last_long_hold_selection_time = 0
        self.master = master  # Store master reference
        
        # Initialize window sizer
        self.window_sizer = DynamicWindowSizer()
        
        # Initialize image reference holders to prevent garbage collection
        self.current_image_tk = None
        self._replay_photo_img = None
        
        self._validate_image_paths()
        self._load_and_resize_images()
        self._calculate_component_requirements()
        self._setup_window()
        self._setup_ui()
        self._display_current_image()
        
        self.window_closed_properly = False
        self.replay_window = None
        self.replay_running = False
        self.replay_after_id = None

    def _calculate_component_requirements(self):
        """Calculate space requirements for all components"""
        # Add title component (always present)
        title_comp = TitleComponent(has_subtitle=False, has_instruction=not self.is_single_image)
        self.window_sizer.add_component(title_comp)
        
        # Add coordinate label component
        coord_comp = CoordLabelComponent()
        self.window_sizer.add_component(coord_comp)
        
        # Add canvas component based on image size
        canvas_comp = CanvasComponent(self.max_width, self.max_height)
        self.window_sizer.add_component(canvas_comp)
        
        # Add slider component (only for multiple images)
        slider_comp = SliderComponent(visible=not self.is_single_image)
        self.window_sizer.add_component(slider_comp)
        
        # Add button frame component
        button_comp = ButtonFrameComponent(button_count=2)
        self.window_sizer.add_component(button_comp)
        
        # Get calculated dimensions
        self.window_width, self.window_height = self.window_sizer.get_window_dimensions()

    def _setup_window(self):
        """Setup the main window with calculated dimensions"""
        if self.master is not None:
            self.root = tk.Toplevel(self.master)
            self.root.transient(self.master)
            self.root.grab_set()
        else:
            self.root = tk.Tk()
        
        self.root.title("Select coordinates")
        center_window(self.root, self.window_width, self.window_height)
        self.root.minsize(self.window_width, self.window_height)
        self.root.configure(bg="#f7f7fa")

    def _validate_image_paths(self):
        for path in self.image_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image file not found: {path}")
            if not path.lower().endswith(('.png', '.jpg', '.jpeg')):
                raise ValueError(f"File is not a PNG image: {path}")

    def _load_and_resize_images(self):
        self.images = []
        self.resized_images = []
        for path in self.image_paths:
            try:
                image = Image.open(path)
                self.images.append(image)
                resized = self._resize_image(image, self.target_size)
                self.resized_images.append(resized)
            except Exception as e:
                raise RuntimeError(f"Error loading image {path}: {str(e)}")
        
        # Calculate max dimensions for canvas sizing
        self.max_width = max(img.width for img in self.resized_images)
        self.max_height = max(img.height for img in self.resized_images)

    def _resize_image(self, image: Image.Image, target_shorter_side: int) -> Image.Image:
        width, height = image.size
        if height < width:
            scale_factor = target_shorter_side / height
        else:
            scale_factor = target_shorter_side / width
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _setup_style(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        
        # Button styles with consistent sizing
        button_config = {
            'font': ('Segoe UI', WindowConfig.BUTTON_FONT_SIZE),
            'padding': (WindowConfig.BUTTON_PADDING_X, WindowConfig.BUTTON_PADDING_Y),
            'relief': 'flat',
            'focuscolor': "none"
        }
        
        self.style.configure('TButton', **button_config, background='#4078c0', foreground='#fff')
        self.style.map('TButton', background=[('active', '#305080')])
        
        self.style.configure('TFrame', background='#f5f6fa')
        
        # Specialized button styles
        self.style.configure("Red.TButton", **button_config, background="#d32f2f", foreground="#fff")
        self.style.map("Red.TButton", background=[("active", "#b71c1c")])
        
        self.style.configure("Grey.TButton", **button_config, background="#bdbdbd", foreground="#fff")
        self.style.map("Grey.TButton", background=[("active", "#9e9e9e")])
        
        self.style.configure("Green.TButton", **button_config, background="#388e3c", foreground="#fff")
        self.style.map("Green.TButton", background=[("active", "#1b5e20")])
        
        self.style.configure("DisabledGreen.TButton", **button_config, background="#a5d6a7", foreground="#fff")
        
        self.style.configure("ReplayGreen.TButton", **button_config, background="#388e3c", foreground="#fff")
        self.style.map("ReplayGreen.TButton", background=[("active", "#1b5e20")])
        
        self.style.configure("ReplayRed.TButton", **button_config, background="#d32f2f", foreground="#fff")
        self.style.map("ReplayRed.TButton", background=[("active", "#b71c1c")])

    def _create_equal_spaced_button_frame(self, parent):
        """Create a button frame with equally spaced buttons"""
        button_frame = tk.Frame(parent, bg="#f0f2f5")
        button_frame.pack(fill="x", pady=WindowConfig.BUTTON_FRAME_PADDING)
        
        # Configure grid to have equal column weights for equal spacing
        button_frame.grid_columnconfigure(0, weight=1, uniform="button_group")
        button_frame.grid_columnconfigure(1, weight=1, uniform="button_group")
        
        return button_frame

    def _setup_ui(self):
        self._setup_style()
        
        # Main content frame with proper padding
        self.main_frame = tk.Frame(self.root, bg="#f7f7fa")
        self.main_frame.pack(padx=WindowConfig.WINDOW_PADDING_X, pady=WindowConfig.WINDOW_PADDING_Y, fill="both", expand=True)
        
        # Title label
        self.title_label = ttk.Label(
            self.main_frame,
            text="Shift vector field origin to (?, ?)",
            font=('Arial', WindowConfig.TITLE_FONT_SIZE, 'bold'),
            background="#f7f7fa"
        )
        self.title_label.pack(pady=(0, WindowConfig.COMPONENT_SPACING))
        
        # Instruction label (only for multiple images)
        if not self.is_single_image:
            self.instruction_label = ttk.Label(
                self.main_frame,
                text="Hold right click for faster selection. Press 'Reset all previous selections' to start over.",
                font=('Arial', WindowConfig.SUBTITLE_FONT_SIZE, 'italic'),
                foreground='blue',
                background="#f7f7fa"
            )
            self.instruction_label.pack(pady=(0, WindowConfig.COMPONENT_SPACING))
        
        # Coordinate label
        self.coord_label = ttk.Label(
            self.main_frame,
            text="Select (x,y) coordinate",
            font=('Arial', WindowConfig.COORD_LABEL_FONT_SIZE),
            background="#f7f7fa"
        )
        self.coord_label.pack(pady=(0, WindowConfig.COMPONENT_SPACING))
        
        # Canvas with proper sizing
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.max_width,
            height=self.max_height,
            bg='white'
        )
        self.canvas.pack(pady=(0, WindowConfig.COMPONENT_SPACING))
        
        # Slider frame (only for multiple images)
        if not self.is_single_image:
            self.slider_frame = tk.Frame(self.main_frame, bg="#f7f7fa")
            self.slider_frame.pack(pady=(0, WindowConfig.COMPONENT_SPACING))
            
            ttk.Label(
                self.slider_frame,
                text="Holding selection delay",
                font=('Arial', WindowConfig.SLIDER_LABEL_FONT_SIZE),
                background="#f7f7fa"
            ).pack(side=tk.LEFT, padx=(0, 5))
            
            self.delay_var = tk.DoubleVar(value=50)
            self.delay_slider = SingleSliderModified(
                self.slider_frame,
                min_val=20, max_val=500, init_val=50,
                width=180, title=None, subtitle=None, show_value_labels=False,
                bg_color='#f7f7fa', active_color='#4078c0', inactive_color='#d3d4d9',
                active_thumb_color='#305080', variable=self.delay_var,
                command=self._update_long_hold_delay
            )
            self.delay_slider.pack(side=tk.LEFT, padx=5)
            
            self.delay_value_label = ttk.Label(
                self.slider_frame,
                text="50 ms",
                font=('Arial', WindowConfig.SLIDER_LABEL_FONT_SIZE, 'bold'),
                background="#f7f7fa"
            )
            self.delay_value_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Button frame with equal spacing
        button_frame = self._create_equal_spaced_button_frame(self.root)
        
        # Create buttons with equal spacing
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear" if self.is_single_image else "Reset all previous selections",
            command=self._clear_all_selections,
            style='Red.TButton'
        )
        
        self.confirm_button = ttk.Button(
            button_frame,
            text="Confirm Selection",
            command=self._confirm_selection,
            style='DisabledGreen.TButton',
            state=tk.DISABLED
        )
        
        # Grid buttons with equal spacing
        self.clear_button.grid(row=0, column=0, sticky="ew", padx=(WindowConfig.BUTTON_GRID_SPACING//2, WindowConfig.BUTTON_GRID_SPACING//2))
        self.confirm_button.grid(row=0, column=1, sticky="ew", padx=(WindowConfig.BUTTON_GRID_SPACING//2, WindowConfig.BUTTON_GRID_SPACING//2))
        
        # Bind events
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<B1-Motion>", self._on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)
        if not self.is_single_image:
            self.canvas.bind("<Button-3>", self._on_right_click)
            self.canvas.bind("<B3-Motion>", self._on_right_drag)
            self.canvas.bind("<ButtonRelease-3>", self._on_right_release)
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _update_long_hold_delay(self, value):
        self.long_hold_selection_delay = int(float(value))
        if hasattr(self, 'delay_value_label'):
            self.delay_value_label.config(text=f"{self.long_hold_selection_delay} ms")

    def _display_current_image(self):
        self.canvas.delete("all")
        current_image = self.resized_images[self.current_image_index]
        self.current_image_tk = ImageTk.PhotoImage(current_image)
        x_pos = (self.max_width - current_image.width) // 2
        y_pos = (self.max_height - current_image.height) // 2
        self.image_on_canvas = self.canvas.create_image(
            x_pos, y_pos,
            anchor=tk.NW,
            image=self.current_image_tk
        )
        self.image_x = x_pos
        self.image_y = y_pos
        self.image_width = current_image.width
        self.image_height = current_image.height
        self.selected_x = None
        self.selected_y = None
        self.confirm_button.config(state=tk.DISABLED, style='DisabledGreen.TButton')
        if not self.is_single_image:
            self.coord_label.config(text=f"Image {self.current_image_index + 1}/{len(self.image_paths)}")
        else:
            self.coord_label.config(text="Select (x,y) coordinate")
        if hasattr(self, 'title_label'):
            self.title_label.config(text="Shift vector field origin to (?,?)")

    def _get_image_coordinates(self, event):
        img_x = event.x - self.image_x
        img_y = event.y - self.image_y
        if 0 <= img_x < self.image_width and 0 <= img_y < self.image_height:
            return int(img_x), int(img_y)
        img_x = max(0, min(img_x, self.image_width - 1))
        img_y = max(0, min(img_y, self.image_height - 1))
        return int(img_x), int(img_y)

    def _update_selection(self, x, y):
        self.selected_x = x
        self.selected_y = y
        self.canvas.delete("crosshair")
        canvas_x = self.image_x + x
        canvas_y = self.image_y + y
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
        if hasattr(self, 'title_label'):
            self.title_label.config(text=f"Shift vector field origin to ({x}, {y})")
        self.confirm_button.config(state=tk.NORMAL, style='Green.TButton')

    def _on_left_click(self, event):
        coords = self._get_image_coordinates(event)
        if coords:
            x, y = coords
            self._update_selection(x, y)

    def _on_left_drag(self, event):
        coords = self._get_image_coordinates(event)
        if coords:
            x, y = coords
            self._update_selection(x, y)

    def _on_left_release(self, event):
        pass

    def _on_right_click(self, event):
        if self.is_single_image:
            return
        self.right_click_press_time = time.time()
        self.last_long_hold_selection_time = 0
        self._long_hold_active = True
        self._long_hold_loop_event_x = event.x
        self._long_hold_loop_event_y = event.y
        coords = self._get_image_coordinates(event)
        if coords:
            x, y = coords
            self._update_selection(x, y)
            self._confirm_selection_if_last_image()
        self._start_long_hold_loop()

    def _on_right_drag(self, event):
        if self.is_single_image:
            return
        current_time = time.time()
        press_duration = current_time - self.right_click_press_time
        coords = self._get_image_coordinates(event)
        if not coords:
            return
        x, y = coords
        self._update_selection(x, y)
        self._long_hold_loop_event_x = event.x
        self._long_hold_loop_event_y = event.y

    def _on_right_release(self, event):
        if self.is_single_image:
            return
        self.right_click_press_time = 0
        self._long_hold_active = False

    def _confirm_selection_if_last_image(self):
        if self.selected_x is not None and self.selected_y is not None:
            self.selected_coordinates.append((self.selected_x, self.selected_y))
            if self.current_image_index == len(self.image_paths) - 1:
                if len(self.image_paths) > 1:
                    self._show_replay_window()
                    self.right_click_press_time = 0
                    self._long_hold_active = False
                else:
                    self.window_closed_properly = True
                    self.root.quit()
                    self.root.destroy()
            else:
                self.current_image_index += 1
                self._display_current_image()

    def _confirm_selection(self):
        if self.selected_x is not None and self.selected_y is not None:
            self.selected_coordinates.append((self.selected_x, self.selected_y))
            if self.current_image_index == len(self.image_paths) - 1:
                if len(self.image_paths) > 1:
                    self._show_replay_window()
                    self.right_click_press_time = 0
                    self._long_hold_active = False
                else:
                    self.window_closed_properly = True
                    self.root.quit()
                    self.root.destroy()
            else:
                self.current_image_index += 1
                self._display_current_image()

    def _clear_all_selections(self):
        self.selected_coordinates = []
        self.current_image_index = 0
        self.selected_x = None
        self.selected_y = None
        self._display_current_image()
        if hasattr(self, 'title_label'):
            self.title_label.config(text="Shift vector field origin to (?,?)")

    def _on_window_close(self):
        self.root.quit()

    def _start_long_hold_loop(self):
        if self.is_single_image:
            return
        def loop():
            if not getattr(self, '_long_hold_active', False):
                return
            current_time = time.time()
            press_duration = current_time - self.right_click_press_time
            if press_duration > 0.3:
                time_since_last_selection = current_time - self.last_long_hold_selection_time
                if time_since_last_selection * 1000 >= self.long_hold_selection_delay:
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
        if enabled:
            if self.selected_x is not None and self.selected_y is not None:
                self.confirm_button.config(state=tk.NORMAL, style='Green.TButton')
            else:
                self.confirm_button.config(state=tk.DISABLED, style='DisabledGreen.TButton')
            self.clear_button.config(state=tk.NORMAL, style='Red.TButton')
        else:
            self.confirm_button.config(state=tk.DISABLED, style='Grey.TButton')
            self.clear_button.config(state=tk.DISABLED, style='Grey.TButton')
        if hasattr(self, 'delay_slider'):
            state = tk.NORMAL if enabled else tk.DISABLED
            self.delay_slider.config(state=state)
        if not enabled:
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")
            if not self.is_single_image:
                self.canvas.unbind("<Button-3>")
                self.canvas.unbind("<B3-Motion>")
                self.canvas.unbind("<ButtonRelease-3>")
        else:
            self.canvas.bind("<Button-1>", self._on_left_click)
            self.canvas.bind("<B1-Motion>", self._on_left_drag)
            self.canvas.bind("<ButtonRelease-1>", self._on_left_release)
            if not self.is_single_image:
                self.canvas.bind("<Button-3>", self._on_right_click)
                self.canvas.bind("<B3-Motion>", self._on_right_drag)
                self.canvas.bind("<ButtonRelease-3>", self._on_right_release)

    def _show_replay_window(self):
        if self.replay_window is not None:
            return
        self._set_selection_window_state(False)
        
        # Calculate replay window dimensions using the same system
        replay_sizer = DynamicWindowSizer()
        replay_sizer.add_component(TitleComponent())  # "Replay" title
        replay_sizer.add_component(CanvasComponent(self.max_width, self.max_height))
        replay_sizer.add_component(SliderComponent(visible=True))  # Speed slider
        replay_sizer.add_component(ButtonFrameComponent(button_count=2))
        
        replay_width, replay_height = replay_sizer.get_window_dimensions()
        
        self.replay_window = tk.Toplevel(self.root)
        self.replay_window.title("Replay")
        self.replay_window.protocol("WM_DELETE_WINDOW", self._on_replay_close)
        self.replay_window.minsize(replay_width, replay_height)
        center_window(self.replay_window, replay_width, replay_height)
        self.replay_window.configure(bg="#f7f7fa")
        
        # Main frame with proper padding
        replay_main_frame = tk.Frame(self.replay_window, bg="#f7f7fa")
        replay_main_frame.pack(padx=WindowConfig.WINDOW_PADDING_X, pady=WindowConfig.WINDOW_PADDING_Y, fill="both", expand=True)
        
        title_label = ttk.Label(
            replay_main_frame,
            text="Replay",
            font=('Arial', WindowConfig.TITLE_FONT_SIZE, 'bold'),
            background="#f7f7fa"
        )
        title_label.pack(pady=(0, WindowConfig.COMPONENT_SPACING))
        
        self.replay_canvas = tk.Canvas(
            replay_main_frame,
            width=self.max_width,
            height=self.max_height,
            bg='white'
        )
        self.replay_canvas.pack(pady=(0, WindowConfig.COMPONENT_SPACING))
        
        slider_frame = tk.Frame(replay_main_frame, bg="#f7f7fa")
        slider_frame.pack(pady=(0, WindowConfig.COMPONENT_SPACING))
        
        ttk.Label(
            slider_frame,
            text="Replay speed",
            font=('Arial', WindowConfig.SLIDER_LABEL_FONT_SIZE),
            background="#f7f7fa"
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.replay_fps_var = tk.DoubleVar(value=self.replay_fps)
        self.replay_fps_slider = SingleSliderModified(
            slider_frame,
            min_val=0.5, max_val=100, init_val=self.replay_fps,
            width=180, title=None, subtitle=None, show_value_labels=False,
            bg_color='#f7f7fa', active_color='#4078c0', inactive_color='#d3d4d9',
            active_thumb_color='#305080', variable=self.replay_fps_var,
            command=self._on_replay_fps_change
        )
        self.replay_fps_slider.pack(side=tk.LEFT, padx=5)
        
        self.replay_fps_value_label = ttk.Label(
            slider_frame,
            text=f"{self.replay_fps:.1f} FPS",
            font=('Arial', WindowConfig.SLIDER_LABEL_FONT_SIZE, 'bold'),
            background="#f7f7fa"
        )
        self.replay_fps_value_label.pack(side=tk.LEFT, padx=(5, 0))
        
        self.replay_running = True
        self._replay_index = 0
        self._start_replay_loop()
        
        # Button frame with equal spacing
        button_frame = self._create_equal_spaced_button_frame(self.replay_window)
        
        confirm_all_btn = ttk.Button(
            button_frame,
            text="Confirm all",
            style="ReplayGreen.TButton",
            command=self._on_replay_confirm_all
        )
        reset_all_btn = ttk.Button(
            button_frame,
            text="Reset all",
            style="ReplayRed.TButton",
            command=self._on_replay_reset_all
        )
        
        reset_all_btn.grid(row=0, column=0, sticky="ew", padx=(WindowConfig.BUTTON_GRID_SPACING//2, WindowConfig.BUTTON_GRID_SPACING//2))
        confirm_all_btn.grid(row=0, column=1, sticky="ew", padx=(WindowConfig.BUTTON_GRID_SPACING//2, WindowConfig.BUTTON_GRID_SPACING//2))

    def _start_replay_loop(self):
        if not self.replay_running or self.replay_window is None:
            return
        self._draw_replay_frame(self._replay_index)
        self._replay_index = (self._replay_index + 1) % len(self.resized_images)
        delay = int(1000 / max(self.replay_fps, 0.5))
        if self.replay_window is not None:
            self.replay_after_id = self.replay_window.after(delay, self._start_replay_loop)

    def _draw_replay_frame(self, idx):
        if self.replay_canvas is None:
            return
        self.replay_canvas.delete("all")
        img = self.resized_images[idx]
        photo_img = ImageTk.PhotoImage(img)
        self._replay_photo_img = photo_img
        x_pos = (self.max_width - img.width) // 2
        y_pos = (self.max_height - img.height) // 2
        self.replay_canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=photo_img)
        if idx < len(self.selected_coordinates):
            x, y = self.selected_coordinates[idx]
            rx = x + x_pos
            ry = y + y_pos
            cross_size = 10
            self.replay_canvas.create_line(rx - cross_size, ry, rx + cross_size, ry, fill="red", width=2)
            self.replay_canvas.create_line(rx, ry - cross_size, rx, ry + cross_size, fill="red", width=2)

    def _on_replay_confirm_all(self):
        self.replay_running = False
        if self.replay_after_id and self.replay_window is not None:
            self.replay_window.after_cancel(self.replay_after_id)
        if self.replay_window is not None:
            self.replay_window.destroy()
        self.window_closed_properly = True
        self.root.quit()
        self.root.destroy()
        self.right_click_press_time = 0
        self._long_hold_active = False

    def _on_replay_reset_all(self):
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
        self._set_selection_window_state(True)
        self.right_click_press_time = 0
        self._long_hold_active = False

    def _on_replay_close(self):
        self.replay_running = False
        if self.replay_after_id and self.replay_window is not None:
            self.replay_window.after_cancel(self.replay_after_id)
        if self.replay_window is not None:
            self.replay_window.destroy()
        self.root.quit()

    def _on_replay_fps_change(self, val):
        fps = float(val)
        if fps < 0.5:
            fps = 0.5
        self.replay_fps = fps
        self.replay_fps_value_label.config(text=f"{fps:.1f} FPS")

    def run(self) -> Union[Tuple[int, int], List[Tuple[int, int]]]:
        self.root.mainloop()
        if not self.window_closed_properly:
            print("user closed window, return None")
            self.root.destroy()
            return None
        return self.selected_coordinates

def create_coord_selector_UI(filepaths_of_frames_or_image, resize_shorter_side_of_target, master=None):
    get_coords = CoordinateSelectorUI(filepaths_of_frames_or_image, resize_shorter_side_of_target, master=master)
    coordinates = get_coords.run()
    return coordinates

# Example usage
if __name__ == "__main__":
    filepaths_of_frames_or_image = ["target_image/cat.jpg", "target_image/circles.png", "target_image/dark.png"]

    # filepaths_of_frames_or_image = "target_image/chameleon.png"

    coords = create_coord_selector_UI(filepaths_of_frames_or_image, resize_shorter_side_of_target=265, master=None)
    print(coords)