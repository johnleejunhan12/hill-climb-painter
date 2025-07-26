import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
from typing import Union, List, Tuple

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
        self._validate_image_paths()
        self._load_and_resize_images()
        self._calculate_window_dimensions()
        if master is None:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(master)
            self.root.transient(master)
            self.root.grab_set()
        self.root.title("Select coordinates")
        center_window(self.root, max(self.window_width, 590), max(self.window_height+20, 250))
        self.root.minsize(max(self.window_width, 590), max(self.window_height+20, 250))
        self._setup_ui()
        self._display_current_image()
        self.window_closed_properly = False
        self.replay_window = None
        self.replay_running = False
        self.replay_after_id = None

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

    def _resize_image(self, image: Image.Image, target_shorter_side: int) -> Image.Image:
        width, height = image.size
        if height < width:
            scale_factor = target_shorter_side / height
        else:
            scale_factor = target_shorter_side / width
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def _calculate_window_dimensions(self):
        self.max_width = max(img.width for img in self.resized_images)
        self.max_height = max(img.height for img in self.resized_images)
        self.window_width = self.max_width + 40
        self.window_height = self.max_height + 220

    def _setup_style(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Segoe UI', 12), padding=0, relief='flat',
                           background='#4078c0', foreground='#fff', focuscolor="none")
        self.style.map('TButton', background=[('active', '#305080')])
        self.style.configure('TFrame', background='#f5f6fa')
        self.style.configure("Red.TButton", background="#d32f2f", foreground="#fff",
                           font=('Arial', 12, 'bold'), padding=(20, 10))
        self.style.map("Red.TButton", background=[("active", "#b71c1c")])
        self.style.configure("Grey.TButton", background="#bdbdbd", foreground="#fff",
                           font=('Arial', 12, 'bold'), padding=(20, 10))
        self.style.map("Grey.TButton", background=[("active", "#9e9e9e")])
        self.style.configure("Green.TButton", background="#388e3c", foreground="#fff",
                           font=('Arial', 12, 'bold'), padding=(20, 10))
        self.style.map("Green.TButton", background=[("active", "#1b5e20")])
        self.style.configure("DisabledGreen.TButton", background="#a5d6a7", foreground="#fff",
                           font=('Arial', 12, 'bold'), padding=(20, 10))
        self.style.configure("ReplayGreen.TButton", background="#388e3c", foreground="#fff",
                           font=('Arial', 12, 'bold'), padding=(20, 10))
        self.style.map("ReplayGreen.TButton", background=[("active", "#1b5e20")])
        self.style.configure("ReplayRed.TButton", background="#d32f2f", foreground="#fff",
                           font=('Arial', 12, 'bold'), padding=(20, 10))
        self.style.map("ReplayRed.TButton", background=[("active", "#b71c1c")])

    def _setup_ui(self):
        self._setup_style()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)
        self.root.configure(bg="#f7f7fa")
        self.main_frame.configure(bg="#f7f7fa")
        self.title_label = ttk.Label(
            self.main_frame,
            text="Shift vector field origin to (?, ?)",
            font=('Arial', 15, 'bold'),
            background="#f7f7fa"
        )
        self.title_label.pack(pady=(0, 6))
        if not self.is_single_image:
            self.instruction_label = ttk.Label(
                self.main_frame,
                text="Hold right click for faster selection. Press 'Reset all previous selections' to start over.",
                font=('Arial', 11, 'italic'),
                foreground='blue',
                background="#f7f7fa"
            )
            self.instruction_label.pack(pady=(0, 10))
        self.coord_label = ttk.Label(
            self.main_frame,
            text="Select (x,y) coordinate",
            font=('Arial', 13),
            background="#f7f7fa"
        )
        self.coord_label.pack(pady=(0, 8))
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.max_width,
            height=self.max_height,
            bg='white'
        )
        self.canvas.pack(pady=(0, 10))
        button_frame = tk.Frame(self.root, bg="#f0f2f5")
        button_frame.pack(fill="x")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        self.confirm_button = ttk.Button(
            button_frame,
            text="Confirm Selection",
            command=self._confirm_selection,
            style='DisabledGreen.TButton',
            state=tk.DISABLED,
            padding=(20, 15)
        )
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear" if self.is_single_image else "Reset all previous selections",
            command=self._clear_all_selections,
            style='Red.TButton',
            padding=(20, 15)
        )
        self.clear_button.grid(row=0, column=0, sticky="nsew", padx=5)
        self.confirm_button.grid(row=0, column=1, sticky="nsew", padx=5)
        button_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        button_frame.grid_columnconfigure(1, weight=1, uniform="group1")
        if not self.is_single_image:
            self.slider_frame = tk.Frame(self.main_frame, bg="#f7f7fa")
            self.slider_frame.pack(pady=(0, 10))
            ttk.Label(
                self.slider_frame,
                text="Holding selection delay",
                font=('Arial', 10),
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
                font=('Arial', 10, 'bold'),
                background="#f7f7fa"
            )
            self.delay_value_label.pack(side=tk.LEFT, padx=(5, 0))
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
        self.replay_window = tk.Toplevel(self.root)
        self.replay_window.title("Replay")
        self.replay_window.protocol("WM_DELETE_WINDOW", self._on_replay_close)
        self.replay_window.minsize(max(self.window_width, 590), max(self.window_height-20, 200))
        center_window(self.replay_window, max(self.window_width, 590), max(self.window_height+20, 200))
        self.replay_window.configure(bg="#f7f7fa")
        title_label = ttk.Label(
            self.replay_window,
            text="Replay",
            font=('Arial', 15, 'bold'),
            background="#f7f7fa"
        )
        title_label.pack(pady=(10, 6))
        self.replay_canvas = tk.Canvas(
            self.replay_window,
            width=self.max_width,
            height=self.max_height,
            bg='white'
        )
        self.replay_canvas.pack(padx=10, pady=10)
        slider_frame = tk.Frame(self.replay_window, bg="#f7f7fa")
        slider_frame.pack(pady=(0, 10))
        ttk.Label(
            slider_frame,
            text="Replay speed",
            font=('Arial', 10),
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
            font=('Arial', 10, 'bold'),
            background="#f7f7fa"
        )
        self.replay_fps_value_label.pack(side=tk.LEFT, padx=(5, 0))
        self.replay_running = True
        self._replay_index = 0
        self._start_replay_loop()
        button_frame = tk.Frame(self.replay_window, bg="#f0f2f5")
        button_frame.pack(fill="x")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.pack(pady=10)
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
        reset_all_btn.grid(row=0, column=0, padx=(5, 5), pady=5, ipadx=20, ipady=5, sticky="ew")
        confirm_all_btn.grid(row=0, column=1, padx=(5, 5), pady=5, ipadx=20, ipady=5, sticky="ew")

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
    # filepaths_of_frames_or_image = ['C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0000.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0001.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0002.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0003.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0004.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0005.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0006.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0007.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0008.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0009.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0010.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0011.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0012.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0013.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0014.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0015.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0016.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0017.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0018.png', 'C:\\Git Repos\\hill-climb-painter\\texture\\shrek_original_frame_0019.png']

    # filepaths_of_frames_or_image = "target_image/chameleon.png"

    coords = create_coord_selector_UI(filepaths_of_frames_or_image, resize_shorter_side_of_target=200, master=None)
    print(coords)