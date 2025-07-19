import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageSequence
import os
from select_target_ui import FileSelectorUI


class TargetTextureSelectorUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # Initialize all attributes before UI setup
        self.selected_image_path = None
        self.selected_image = None
        self.selected_gif_frames = None
        self.gif_frame_index = 0
        self.gif_animation_id = None
        self.selected_texture_paths = []
        self.selected_texture_images = []
        self.texture_grid_labels = []
        self.title("Target & Texture Selector")
        self.configure(bg="#f5f6fa")
        self.minsize(800, 600)
        self.resizable(True, True)
        self._center_window(1000, 700)
        self._setup_style()
        self._build_ui()
        self.bind('<Configure>', self._on_resize)

    def _center_window(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 12), padding=0, relief='flat', background='#4078c0', foreground='#fff', focuscolor=style.lookup('TButton', 'background'))
        style.map('TButton', background=[('active', '#305080')])
        style.configure('TFrame', background='#f5f6fa')

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1, minsize=1)
        self.grid_columnconfigure(1, weight=1, minsize=1)

        # Left container
        self.left_container = ttk.Frame(self)
        self.left_container.grid(row=0, column=0, sticky="nsew")
        self.left_container.grid_rowconfigure(0, weight=1, minsize=300)
        self.left_container.grid_columnconfigure(0, weight=1)
        self.left_container.grid_propagate(False)
        # Remove debug blue box from left container
        # for widget in self.left_container.winfo_children():
        #     widget.destroy()
        # self.left_debug_box = tk.Frame(self.left_container, bg="blue")
        # self.left_debug_box.grid(row=0, column=0, sticky="nsew")

        # Right container
        self.right_container = ttk.Frame(self)
        self.right_container.grid(row=0, column=1, sticky="nsew")
        self.right_container.grid_rowconfigure(0, weight=1, minsize=300)
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_propagate(False)
        # Right container: debugging red box
        for widget in self.right_container.winfo_children():
            widget.destroy()
        self.right_debug_box = tk.Frame(self.right_container, bg="red")
        self.right_debug_box.grid(row=0, column=0, sticky="nsew")

        # --- Left: Image/GIF display ---
        self.image_display = tk.Label(self.left_container, bg="#eaeaea", bd=0, relief='flat', font=("Segoe UI", 16), anchor='center', justify='center')
        self.image_display.grid(row=0, column=0, sticky="nsew")
        self.image_display.configure(image='', text='No target selected')

        # --- Left: Select Target Button ---
        self.select_target_btn = ttk.Button(
            self.left_container, text="Select target", command=self._on_select_target, takefocus=0
        )
        self.select_target_btn.grid(row=1, column=0, sticky="ew", ipady=10)
        self.left_container.update_idletasks()
        self.select_target_btn.configure(width=1)
        self.left_container.grid_propagate(False)

        # Add display to right (red) debug box
        self.right_debug_display = tk.Label(self.right_container, text="No textures selected", font=("Segoe UI", 16), bg="#eaeaea", bd=0, relief='flat', anchor='center', justify='center')
        self.right_debug_display.grid(row=0, column=0, sticky="nsew")

        # Add button to right (red) debug box
        self.right_debug_btn = ttk.Button(self.right_container, text="Select texture(s)")
        self.right_debug_btn.grid(row=1, column=0, sticky="ew", ipady=10)

        # --- Right: Texture display and button ---
        self.texture_display_frame = tk.Frame(self.right_container, bg="#eaeaea", bd=0, relief='flat')
        self.texture_display_frame.grid(row=0, column=0, sticky="nsew")
        self.right_container.grid_rowconfigure(0, weight=1)
        self.right_container.grid_columnconfigure(0, weight=1)

        def on_select_textures():
            selector_single = FileSelectorUI(
                '.png',
                is_select_multiple_files=True,
                window_title="Select texture",
            )
            paths = selector_single.select_file()
            if isinstance(paths, str):
                paths = [paths]
            if not paths:
                self.selected_texture_paths = []
                self.selected_texture_images = []
                self._update_texture_display()
                update_right_clear_btn()
                return
            self.selected_texture_paths = paths
            self.selected_texture_images = [Image.open(p) for p in paths]
            self._update_texture_display()
            update_right_clear_btn()

        self.select_texture_btn = ttk.Button(self.right_container, text="Select texture(s)", command=on_select_textures, takefocus=0)
        self.select_texture_btn.grid(row=1, column=0, sticky="ew", ipady=10)
        self.right_container.update_idletasks()
        self.select_texture_btn.configure(width=1)
        self.right_container.grid_propagate(False)

        def _update_texture_display():
            # Remove old grid
            for label in getattr(self, 'texture_grid_labels', []):
                label.destroy()
            self.texture_grid_labels = []
            frame = self.texture_display_frame
            for widget in frame.winfo_children():
                widget.destroy()
            n = len(self.selected_texture_images)
            if n == 0:
                label = tk.Label(frame, text="No textures selected", font=("Segoe UI", 16), bg="#eaeaea", bd=0, relief='flat', anchor='center', justify='center')
                label.place(relx=0.5, rely=0.5, anchor='center')
                self.texture_grid_labels = [label]
                return
            # Determine grid size
            import math
            grid_size = math.ceil(n ** 0.5)
            # Get frame size
            frame.update_idletasks()
            w = frame.winfo_width() or frame.winfo_reqwidth()
            h = frame.winfo_height() or frame.winfo_reqheight()
            if w < 10 or h < 10:
                w = 300
                h = 300
            cell_w = w // grid_size
            cell_h = h // grid_size
            # Place images
            for idx, img in enumerate(self.selected_texture_images):
                row = idx // grid_size
                col = idx % grid_size
                img_copy = img.copy()
                img_copy.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img_copy)
                label = tk.Label(frame, image=tk_img, bg="#eaeaea")
                setattr(label, 'image', tk_img)  # Prevent GC
                label.grid(row=row, column=col, sticky="nsew")
                self.texture_grid_labels.append(label)
            for i in range(grid_size):
                frame.grid_rowconfigure(i, weight=1)
                frame.grid_columnconfigure(i, weight=1)
        self._update_texture_display = _update_texture_display

        # Ensure the texture placeholder is visible on startup
        self._update_texture_display()

        # --- Left: Clear Selection Button ---
        def update_left_clear_btn():
            if self.selected_image_path is None:
                self.clear_target_btn.state(["disabled"])
                self.clear_target_btn.configure(style="Grey.TButton")
            else:
                self.clear_target_btn.state(["!disabled"])
                self.clear_target_btn.configure(style="Red.TButton")

        def on_clear_left():
            if self.selected_image_path is not None:
                self.selected_image_path = None
                self.selected_image = None
                self.selected_gif_frames = None
                self._update_image_display()
            update_left_clear_btn()

        self.clear_target_btn = ttk.Button(
            self.left_container, text="Clear selection", command=on_clear_left
        )
        self.clear_target_btn.grid(row=2, column=0, sticky="ew", ipady=10, pady=0)

        # Attach update_left_clear_btn to self so it can be called as a method
        self.update_left_clear_btn = update_left_clear_btn

        # --- Right: Clear Selection Button ---
        def on_clear_right():
            if self.selected_texture_paths:
                self.selected_texture_paths = []
                self.selected_texture_images = []
                self._update_texture_display()
            update_right_clear_btn()

        self.clear_texture_btn = ttk.Button(
            self.right_container, text="Clear selection", command=on_clear_right
        )
        self.clear_texture_btn.grid(row=2, column=0, sticky="ew", ipady=10, pady=0)

        def update_right_clear_btn():
            if not self.selected_texture_paths:
                self.clear_texture_btn.state(["disabled"])
                self.clear_texture_btn.configure(style="Grey.TButton")
            else:
                self.clear_texture_btn.state(["!disabled"])
                self.clear_texture_btn.configure(style="Red.TButton")

        # Add custom styles for red and grey buttons
        style = ttk.Style(self)
        style.configure("Red.TButton", background="#d32f2f", foreground="#fff")
        style.map("Red.TButton", background=[("active", "#b71c1c")])
        style.configure("Grey.TButton", background="#bdbdbd", foreground="#fff")
        style.map("Grey.TButton", background=[("active", "#9e9e9e")])

        # Update clear buttons on selection changes
        update_left_clear_btn()
        update_right_clear_btn()

        # --- Confirm Button at the bottom ---
        def update_confirm_btn():
            if self.selected_image_path and self.selected_texture_paths:
                self.confirm_btn.configure(style="Green.TButton")
                self.confirm_btn.state(["!disabled"])
            else:
                self.confirm_btn.configure(style="Grey.TButton")
                self.confirm_btn.state(["disabled"])

        self.confirm_btn = ttk.Button(self, text="Confirm")
        self.confirm_btn.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=10, pady=0)
        self.confirm_btn.configure(command=self._on_confirm)

        # Add custom style for green button
        style.configure("Green.TButton", background="#388e3c", foreground="#fff")
        style.map("Green.TButton", background=[("active", "#1b5e20")])

        # Update confirm button state after any selection/clear
        def update_all_btns():
            update_left_clear_btn()
            update_right_clear_btn()
            update_confirm_btn()
        self.update_all_btns = update_all_btns
        # Patch all update points to call update_all_btns
        # Left
        old_update_image_display = self._update_image_display
        def new_update_image_display(*args, **kwargs):
            old_update_image_display(*args, **kwargs)
            self.update_all_btns()
        self._update_image_display = new_update_image_display
        # Right
        old_update_texture_display = self._update_texture_display
        def new_update_texture_display(*args, **kwargs):
            old_update_texture_display(*args, **kwargs)
            self.update_all_btns()
        self._update_texture_display = new_update_texture_display
        # Initial state
        update_confirm_btn()

        # Remove patching logic for select_texture_btn's command
        # orig_on_select_textures = self.select_texture_btn['command']
        # def patched_on_select_textures(*args, **kwargs):
        #     orig_on_select_textures()
        #     update_right_clear_btn()
        # self.select_texture_btn.configure(command=patched_on_select_textures)

    def _on_resize(self, event):
        pass  # No-op for debug red box state

    # def _resize_buttons(self):
    #     # Set button width to match container width (minus padding)
    #     left_width = self.left_container.winfo_width()
    #     btn_width = max(1, left_width - 40)  # 20px padding each side
    #     self.select_target_btn.configure(width=btn_width // 10)  # ttk width is in chars, approx

    def _on_select_target(self):
        selector_single = FileSelectorUI(
            ['.png', '.jpg', '.jpeg', '.gif'],
            is_select_multiple_files=False,
            window_title="Select target",
        )
        path = selector_single.select_file()
        # Ensure path is a string (handle list case for robustness)
        if isinstance(path, list):
            path = path[0] if path else None
        if path:
            self.selected_image_path = path
            ext = os.path.splitext(path)[1].lower()
            if ext == '.gif':
                self._load_gif(path)
            else:
                self._load_image(path)
            self._update_image_display()


    def _load_image(self, path):
        if self.gif_animation_id:
            self.after_cancel(self.gif_animation_id)
            self.gif_animation_id = None
        img = Image.open(path)
        self.selected_image = img.copy()
        self.selected_gif_frames = None

    def _load_gif(self, path):
        if self.gif_animation_id:
            self.after_cancel(self.gif_animation_id)
            self.gif_animation_id = None
        img = Image.open(path)
        # Downscale if too large
        max_dim = 500
        if img.width > max_dim or img.height > max_dim:
            scale = min(max_dim / img.width, max_dim / img.height)
            new_size = (int(img.width * scale), int(img.height * scale))
            frames = [frame.copy().resize(new_size, Image.Resampling.LANCZOS) for frame in ImageSequence.Iterator(img)]
        else:
            frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
        self.selected_gif_frames = [ImageTk.PhotoImage(frame.convert('RGBA')) for frame in frames]
        self.selected_image = None
        self.gif_frame_index = 0
        self._animate_gif()

    def _animate_gif(self):
        if not self.selected_gif_frames:
            return
        frame = self.selected_gif_frames[self.gif_frame_index]
        self.image_display.configure(image=frame)
        self.gif_frame_index = (self.gif_frame_index + 1) % len(self.selected_gif_frames)
        self.gif_animation_id = self.after(80, self._animate_gif)

    def _update_image_display(self):
        if self.selected_image_path is None:
            self.image_display.configure(image='', text='No target selected')
            self.update_left_clear_btn()
            return
        ext = os.path.splitext(self.selected_image_path)[1].lower()
        if ext == '.gif' and self.selected_gif_frames:
            # Already handled by animation
            self.update_left_clear_btn()
            return
        if self.selected_image:
            # Resize to fit display area, keep aspect ratio
            container_width = self.left_container.winfo_width()
            container_height = self.left_container.winfo_height() - 50  # button height
            if container_width < 10 or container_height < 10:
                self.update_left_clear_btn()
                return
            img = self.selected_image.copy()
            img.thumbnail((container_width, container_height), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.image_display.configure(image=tk_img, text='')
            setattr(self.image_display, 'image', tk_img)  # Prevent garbage collection
        self.update_left_clear_btn()

    def run_and_get_selection(self):
        self.result = None
        self.mainloop()
        return self.result

    def _on_confirm(self):
        # Called when confirm button is pressed
        self.result = (self.selected_image_path, list(self.selected_texture_paths))
        self.destroy()

if __name__ == "__main__":
    app = TargetTextureSelectorUI()
    result = app.run_and_get_selection()
    print(result)
