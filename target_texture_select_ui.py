import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageSequence
import os
from select_target_ui import FileSelectorUI
from file_operations import *

class TargetTextureSelectorUI(tk.Tk):
    def __init__(self, is_prompt_user_before_quit=False, initial_selected_image_path=None, initial_selected_texture_paths=None):
        super().__init__()
        
        # Validate initial parameters
        if initial_selected_image_path is not None:
            assert isinstance(initial_selected_image_path, str), "initial_selected_image_path must be a string"
            assert os.path.exists(initial_selected_image_path), f"Initial image path does not exist: {initial_selected_image_path}"
            ext = os.path.splitext(initial_selected_image_path)[1].lower()
            assert ext in ['.png', '.jpg', '.jpeg', '.gif'], f"Invalid image extension: {ext}. Must be png, jpg, jpeg, or gif"
        
        if initial_selected_texture_paths is not None:
            assert isinstance(initial_selected_texture_paths, list), "initial_selected_texture_paths must be a list"
            for path in initial_selected_texture_paths:
                assert isinstance(path, str), "Each texture path must be a string"
                assert os.path.exists(path), f"Initial texture path does not exist: {path}"
                ext = os.path.splitext(path)[1].lower()
                assert ext == '.png', f"Invalid texture extension: {ext}. Must be png"
        
        # Validate is_prompt_user_before_quit
        assert isinstance(is_prompt_user_before_quit, bool), "is_prompt_user_before_quit must be a boolean"
        
        # Initialize all attributes before UI setup
        self.is_prompt_user_before_quit = is_prompt_user_before_quit
        self.selected_image_or_gif_path = initial_selected_image_path
        self.selected_image = None
        self.selected_gif_frames = None
        self.gif_frame_index = 0
        self.gif_animation_id = None
        self.selected_texture_paths = initial_selected_texture_paths or []
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
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load initial selections after UI is built
        self._load_initial_selections()

    def _load_initial_selections(self):
        print(f"Loading initial image: {self.selected_image_or_gif_path}")
        if self.selected_image_or_gif_path is not None:
            ext = os.path.splitext(self.selected_image_or_gif_path)[1].lower()
            print(f"Extension: {ext}")
            if ext == '.gif':
                self._load_gif(self.selected_image_or_gif_path)
            else:
                self._load_image(self.selected_image_or_gif_path)
            self.update_idletasks()
            self._update_image_display()
            print("Image display updated")

        # Load initial textures
        if self.selected_texture_paths:
            def greyscale_with_alpha(p):
                img = Image.open(p)
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and 'transparency' in img.info):
                    img = img.convert("RGBA")
                    r, g, b, a = img.split()
                    grey = Image.merge("RGB", (r, g, b)).convert("L")
                    img = Image.merge("RGBA", (grey, grey, grey, a))
                else:
                    img = img.convert("L").convert("RGB")
                return img
            
            self.selected_texture_images = [greyscale_with_alpha(p) for p in self.selected_texture_paths]
            self._update_texture_display()

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
        style.configure("Red.TButton", background="#d32f2f", foreground="#fff")
        style.map("Red.TButton", background=[("active", "#b71c1c")])
        style.configure("Grey.TButton", background="#bdbdbd", foreground="#fff")
        style.map("Grey.TButton", background=[("active", "#9e9e9e")])
        style.configure("Green.TButton", background="#388e3c", foreground="#fff")
        style.map("Green.TButton", background=[("active", "#1b5e20")])

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

        # Right container
        self.right_container = ttk.Frame(self)
        self.right_container.grid(row=0, column=1, sticky="nsew")
        self.right_container.grid_rowconfigure(0, weight=1, minsize=300)
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_propagate(False)

        # Left: Image/GIF display
        self.image_display = tk.Label(self.left_container, bg="#eaeaea", bd=0, relief='flat', font=("Segoe UI", 16), anchor='center', justify='center')
        self.image_display.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.image_display.configure(image='', text='No target selected\nAllowed: png, jpeg, jpg, gif')

        # Left: Select Target Button
        self.select_target_btn = ttk.Button(
            self.left_container, text="Select target", command=self._on_select_target, takefocus=0
        )
        self.select_target_btn.grid(row=1, column=0, sticky="ew", ipady=10, padx=5, pady=5)
        self.left_container.update_idletasks()
        self.select_target_btn.configure(width=1)
        self.left_container.grid_propagate(False)

        # Right: Texture display
        self.texture_display_frame = tk.Frame(self.right_container, bg="#eaeaea", bd=0, relief='flat')
        self.texture_display_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.right_container.grid_rowconfigure(0, weight=1)
        self.right_container.grid_columnconfigure(0, weight=1)

        # Right: Select Texture Button
        def on_select_textures():
            selector_single = FileSelectorUI(
                '.png',
                is_select_multiple_files=True,
                window_title="Select texture(s)",
                custom_filepath=os.path.join(os.path.dirname(__file__), 'texture_presets')
            )
            paths = selector_single.select_file()
            if isinstance(paths, str):
                paths = [paths]
            if not paths:
                self.selected_texture_paths = []
                self.selected_texture_images = []
                self._update_texture_display()
                self.update_all_btns()
                return
            self.selected_texture_paths = paths
            def greyscale_with_alpha(p):
                img = Image.open(p)
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and 'transparency' in img.info):
                    img = img.convert("RGBA")
                    r, g, b, a = img.split()
                    grey = Image.merge("RGB", (r, g, b)).convert("L")
                    img = Image.merge("RGBA", (grey, grey, grey, a))
                else:
                    img = img.convert("L").convert("RGB")
                return img
            self.selected_texture_images = [greyscale_with_alpha(p) for p in paths]
            self._update_texture_display()
            self.update_all_btns()

        self.select_texture_btn = ttk.Button(self.right_container, text="Select texture(s)", command=on_select_textures, takefocus=0)
        self.select_texture_btn.grid(row=1, column=0, sticky="ew", ipady=10, padx=5, pady=5)
        self.right_container.update_idletasks()
        self.select_texture_btn.configure(width=1)
        self.right_container.grid_propagate(False)

        # Right: Texture display update
        def _update_texture_display():
            for label in getattr(self, 'texture_grid_labels', []):
                label.destroy()
            self.texture_grid_labels = []
            frame = self.texture_display_frame
            for widget in frame.winfo_children():
                widget.destroy()
            n = len(self.selected_texture_images)
            if n == 0:
                label = tk.Label(frame, text="No textures selected\nAllowed: png", font=("Segoe UI", 16), bg="#eaeaea", bd=0, relief='flat', anchor='center', justify='center')
                label.place(relx=0.5, rely=0.5, anchor='center')
                self.texture_grid_labels = [label]
                return
            import math
            grid_size = math.ceil(n ** 0.5)
            frame.update_idletasks()
            w = frame.winfo_width() or frame.winfo_reqwidth()
            h = frame.winfo_height() or frame.winfo_reqheight()
            if w < 10 or h < 10:
                w = 300
                h = 300
            cell_w = w // grid_size
            cell_h = h // grid_size
            for idx, img in enumerate(self.selected_texture_images):
                row = idx // grid_size
                col = idx % grid_size
                img_copy = img.copy()
                img_copy.thumbnail((cell_w, cell_h), Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img_copy)
                label = tk.Label(frame, image=tk_img, bg="#eaeaea")
                setattr(label, 'image', tk_img)
                label.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
                self.texture_grid_labels.append(label)
            for i in range(grid_size):
                frame.grid_rowconfigure(i, weight=1)
                frame.grid_columnconfigure(i, weight=1)
        self._update_texture_display = _update_texture_display
        self._update_texture_display()

        # Left: Clear Selection Button
        def update_left_clear_btn():
            if self.selected_image_or_gif_path is None:
                self.clear_target_btn.state(["disabled"])
                self.clear_target_btn.configure(style="Grey.TButton")
            else:
                self.clear_target_btn.state(["!disabled"])
                self.clear_target_btn.configure(style="Red.TButton")

        def on_clear_left():
            if self.selected_image_or_gif_path is not None:
                self.selected_image_or_gif_path = None
                self.selected_image = None
                self.selected_gif_frames = None
                if self.gif_animation_id:
                    self.after_cancel(self.gif_animation_id)
                    self.gif_animation_id = None
                self._update_image_display()
            self.update_all_btns()

        self.clear_target_btn = ttk.Button(
            self.left_container, text="Clear selected target", command=on_clear_left
        )
        self.clear_target_btn.grid(row=2, column=0, sticky="ew", ipady=10, padx=5, pady=0)
        self.update_left_clear_btn = update_left_clear_btn

        # Right: Clear Selection Button
        def on_clear_right():
            if self.selected_texture_paths:
                self.selected_texture_paths = []
                self.selected_texture_images = []
                self._update_texture_display()
            self.update_all_btns()

        self.clear_texture_btn = ttk.Button(
            self.right_container, text="Clear selected texture(s)", command=on_clear_right
        )
        self.clear_texture_btn.grid(row=2, column=0, sticky="ew", ipady=10, padx=5, pady=0)

        def update_right_clear_btn():
            if not self.selected_texture_paths:
                self.clear_texture_btn.state(["disabled"])
                self.clear_texture_btn.configure(style="Grey.TButton")
            else:
                self.clear_texture_btn.state(["!disabled"])
                self.clear_texture_btn.configure(style="Red.TButton")

        # Confirm Button
        def update_confirm_btn():
            if self.selected_image_or_gif_path and self.selected_texture_paths:
                self.confirm_btn.configure(style="Green.TButton")
                self.confirm_btn.state(["!disabled"])
            else:
                self.confirm_btn.configure(style="Grey.TButton")
                self.confirm_btn.state(["disabled"])

        self.confirm_btn = ttk.Button(self, text="Confirm", command=self._on_confirm)
        self.confirm_btn.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=10, padx=5, pady=5)

        # Update all buttons
        def update_all_btns():
            update_left_clear_btn()
            update_right_clear_btn()
            update_confirm_btn()
        self.update_all_btns = update_all_btns

        # Patch update methods
        old_update_image_display = self._update_image_display
        def new_update_image_display(*args, **kwargs):
            old_update_image_display(*args, **kwargs)
            self.update_all_btns()
        self._update_image_display = new_update_image_display

        old_update_texture_display = self._update_texture_display
        def new_update_texture_display(*args, **kwargs):
            old_update_texture_display(*args, **kwargs)
            self.update_all_btns()
        self._update_texture_display = new_update_texture_display

        update_confirm_btn()
    def on_closing(self):
        """Handle the window close event with a modern confirmation dialog"""
        if self.is_prompt_user_before_quit:
            dialog = tk.Toplevel(self)
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
                font=("Segoe UI", 13, "bold"),
                bg="#f0f2f5",
                fg="#333333"
            )
            message.pack(pady=(20, 30))
            
            # Button frame
            button_frame = tk.Frame(container, bg="#f0f2f5")
            button_frame.pack(fill="x")
            
            # Modern button style
            style = ttk.Style()
            style.configure(
                "Modern.TButton",
                font=("Segoe UI", 11),
                padding=10,
                background="#ffffff",
                foreground="#333333",
                borderwidth=0
            )
            style.map(
                "Modern.TButton",
                background=[("active", "#e0e0e0"), ("pressed", "#d0d0d0")],
                foreground=[("active", "#333333")]
            )
            
            # Yes button
            yes_button = ttk.Button(
                button_frame,
                text="Yes",
                style="Modern.TButton",
                command=lambda: self.confirm_exit(dialog)
            )
            yes_button.pack(side="left", padx=(0, 10), ipady=5, ipadx=20)
            
            # No button
            no_button = ttk.Button(
                button_frame,
                text="No",
                style="Modern.TButton",
                command=dialog.destroy
            )
            no_button.pack(side="right", padx=(10, 0), ipady=5, ipadx=20)
            
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
            dialog.transient(self)
        else:
            self.confirm_exit(None)

    def confirm_exit(self, dialog):
        if dialog:
            dialog.destroy()
        if self.gif_animation_id:
            self.after_cancel(self.gif_animation_id)
            self.gif_animation_id = None
        self.result = None
        self.destroy()

    def _on_resize(self, event):
        pass

    def _on_select_target(self):
        selector_single = FileSelectorUI(
            ['.png', '.jpg', '.jpeg', '.gif'],
            is_select_multiple_files=False,
            window_title="Select target",
        )
        path = selector_single.select_file()
        if isinstance(path, list):
            path = path[0] if path else None
        if path:
            self.selected_image_or_gif_path = path
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
        if self.selected_image_or_gif_path is None:
            self.image_display.configure(image='', text='No target selected\nAllowed: png, jpeg, jpg, gif')
            return
        ext = os.path.splitext(self.selected_image_or_gif_path)[1].lower()
        if ext == '.gif' and self.selected_gif_frames:
            return
        if self.selected_image:
            container_width = self.left_container.winfo_width()
            container_height = self.left_container.winfo_height() - 50
            if container_width < 10 or container_height < 10:
                return
            img = self.selected_image.copy()
            img.thumbnail((container_width, container_height), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            self.image_display.configure(image=tk_img, text='')
            setattr(self.image_display, 'image', tk_img)

    def run_and_get_selection(self):
        self.result = None
        self.mainloop()
        return self.result

    def _on_confirm(self):
        if self.gif_animation_id:
            self.after_cancel(self.gif_animation_id)
            self.gif_animation_id = None
        self.result = (self.selected_image_or_gif_path, list(self.selected_texture_paths))
        self.destroy()

if __name__ == "__main__":
    # app = TargetTextureSelectorUI(
    #     initial_selected_image_path="C:\Git Repos\hill-climb-painter\\readme_stuff\sunset_painted.gif",
    #     initial_selected_texture_paths=['C:/Git Repos/hill-climb-painter/texture_presets/Paintstrokes/stroke4.png', 
    #                                     'C:/Git Repos/hill-climb-painter/texture_presets/Paintstrokes/stroke6.png']
    # )
    # app = TargetTextureSelectorUI(
    #     initial_selected_image_path="C:\\Git Repos\\hill-climb-painter\\target\\image_output_20250717_202223.png",
    #     initial_selected_texture_paths=['C:/Git Repos/hill-climb-painter/texture_presets/Paintstrokes/stroke4.png', 
    #                                     'C:/Git Repos/hill-climb-painter/texture_presets/Paintstrokes/stroke6.png']
    # )
    app = TargetTextureSelectorUI(
        is_prompt_user_before_quit = True,
        initial_selected_image_path="C:\\Git Repos\\hill-climb-painter\\target_image\\cat2.jpg",
        initial_selected_texture_paths=['C:/Git Repos/hill-climb-painter/texture_presets/Paintstrokes/stroke4.png', 
                                        'C:/Git Repos/hill-climb-painter/texture_presets/Paintstrokes/stroke6.png']
    )

# "C:\Git Repos\hill-climb-painter\target_image\cat2.jpg"

    # app = TargetTextureSelectorUI()
    result = app.run_and_get_selection()
    print(result)