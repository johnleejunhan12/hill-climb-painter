import tkinter as tk
from tkinter import ttk
import json
from PIL import Image, ImageTk, ImageSequence
import os


def center_window(root, width=1000, height=700):
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

class ParameterSelectUI:
    def __init__(self, root=None, target_full_file_path=None):
        """Initialize the ParameterSelectUI with main window and layout."""
        if root is None:
            self.root = tk.Tk()
            self.root.title("Parameter Select UI")
        else:
            self.root = root
        # Center the window
        center_window(self.root, width=1000, height=700)
        # Set minimum window size
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        self.target_full_file_path = target_full_file_path
        self.display_component = None
        # Setup styling
        self.setup_styling()
        # Create the main layout
        self.create_layout()
        
    def setup_styling(self):
        """Configure modern ttk styles with zero padding and all-white backgrounds."""
        style = ttk.Style()
        style.configure('Modern.TNotebook', background='white', borderwidth=0)
        style.configure('Modern.TNotebook.Tab', 
                       padding=[0, 0],
                       background='white',
                       foreground='black',
                       borderwidth=0,
                       relief='flat')
        style.map('Modern.TNotebook.Tab',
                  background=[('selected', 'white'), ('!selected', 'white')],
                  relief=[('selected', 'flat'), ('!selected', 'flat')])
        
    def create_layout(self):
        """Create the main layout with left and right containers."""
        # Create left and right containers
        self.left_container = tk.Frame(self.root, bg='red')
        self.left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_container = tk.Frame(self.root, bg='white', width=450)
        self.right_container.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_container.pack_propagate(False)
        # If a target image is provided, display it
        if self.target_full_file_path:
            # Use a default short side for now; will be updated by slider
            short_side = 200
            self.display_component = CenteredImageDisplay(self.left_container, self.target_full_file_path, short_side)
            self.display_component.pack(fill=tk.BOTH, expand=True)
        # Create the tab system
        self.create_tabs(self.right_container)
        
    def create_tabs(self, parent):
        """Create the tab system with three tabs inside the given parent."""
        self.notebook = ttk.Notebook(parent, style='Modern.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        tab_names = [
            "general_parameters",
            "target_is_image_parameters",
            "target_is_gif_parameters"
        ]
        for i, name in enumerate(tab_names, 1):
            self.create_tab(i, tab_name=name)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
    def create_tab(self, tab_number, tab_name=None):
        """Create a tab with the given number and name. Tab 1 is built dynamically from config.json."""
        tab_frame = ttk.Frame(self.notebook)
        display_name = tab_name if tab_name else f"Tab {tab_number}"
        self.notebook.add(tab_frame, text=display_name)

        if tab_number == 1:
            # Load config.json
            with open('config.json', 'r') as f:
                config = json.load(f)
            general = config.get('general_parameters', {})
            # Outer vertical container for all sections
            outer = tk.Frame(tab_frame, bg='white')
            outer.pack(fill=tk.BOTH, expand=True)
            for section_name, section in general.items():
                section_frame = SectionFrame(outer, section_name)
                section_frame.pack(fill=tk.X, pady=10, padx=8)
                for key, widget in section.items():
                    wtype = widget.get('widget_type')
                    label = widget.get('label', key)
                    if wtype == 'slider':
                        decimal_places = widget.get('decimal_place')
                        comp = SliderComponent(
                            section_frame,
                            label=label,
                            minval=widget['min_value'],
                            maxval=widget['max_value'],
                            initial=widget['current_value'],
                            decimal_places=decimal_places,
                            units=widget.get('unit', '')
                        )
                        comp.pack(fill=tk.X, pady=3)
                        # Connect the resize shorter side of target slider to the display component
                        if key == 'resize_target_shorter_side_of_target' and hasattr(self, 'display_component') and self.display_component:
                            def on_slider_change(val, comp=comp):
                                self.display_component.update_target_size(float(val))
                            comp.value.trace_add('write', lambda *args, comp=comp: on_slider_change(comp.get()))
                    elif wtype == 'checkbox':
                        comp = CheckboxComponent(section_frame, label, widget['current_value'])
                        comp.pack(fill=tk.X, pady=3)
                    elif wtype == 'textbox':
                        comp = TextboxComponent(section_frame, label, widget['current_value'])
                        comp.pack(fill=tk.X, pady=3)
        else:
            content_label = tk.Label(tab_frame, 
                                   text=display_name, 
                                   font=('Arial', 12),
                                   bg='white',
                                   fg='black',
                                   borderwidth=0,
                                   highlightthickness=0)
            content_label.pack(expand=True)
        
    def create_buttons(self, parent):
        """Create two equal-width buttons in a horizontal container at the bottom, filling the region with no extra space between or at the edges, and not influenced by text length."""
        # Create a horizontal container (frame) for the buttons
        button_container = tk.Frame(parent, bg='white')
        button_container.pack(fill=tk.BOTH, expand=True)
        button_container.pack_propagate(False)
        container_width = parent.winfo_reqwidth() or 450  # fallback to 450 if not yet realized
        button_container.grid_columnconfigure(0, weight=1, minsize=container_width//2)
        button_container.grid_columnconfigure(1, weight=1, minsize=container_width//2)
        button_container.grid_rowconfigure(0, weight=1)

        btn1 = tk.Button(button_container, text="Reselect target\nand texture", bg='#aee3fa', fg='black', font=('Arial', 11), borderwidth=1, relief='solid', highlightthickness=0)
        btn2 = tk.Button(button_container, text="Confirm", bg='#4caf50', fg='black', font=('Arial', 11), borderwidth=1, relief='solid', highlightthickness=0)
        btn1.grid(row=0, column=0, sticky='nsew')
        btn2.grid(row=0, column=1, sticky='nsew')
        
    def on_tab_changed(self, event):
        current_tab = self.notebook.select()
        tab_id = self.notebook.index(current_tab)
        tab_name = self.notebook.tab(tab_id, "text")
        print(f"Switched to {tab_name}")
        
    def run(self):
        if hasattr(self.root, 'mainloop'):
            self.root.mainloop()
        
    def get_root(self):
        return self.root


class SliderComponent(tk.Frame):
    def __init__(self, parent, label, minval=100, maxval=500, initial=493, on_change=None, decimal_places=None, units=None, **kwargs):
        super().__init__(parent, bg='white', **kwargs)
        self.on_change = on_change
        self.minval = minval
        self.maxval = maxval
        self.decimal_places = decimal_places
        self.is_float = decimal_places is not None
        self.units = units
        self.value = tk.DoubleVar(value=initial) if self.is_float else tk.IntVar(value=initial)
        self._last_valid = str(initial)

        slider_font = ('Segoe UI', 10)

        # Bordered box (modern, flat border)
        self.bordered = tk.Frame(self, bg='white', highlightbackground='#bbb', highlightthickness=0, bd=0, relief='flat')
        self.bordered.pack(fill=tk.X, expand=False)

        # Row 1: Label and numeric-only entry (no padding)
        row1 = tk.Frame(self.bordered, bg='white', borderwidth=0, highlightthickness=0)
        row1.pack(fill=tk.X, pady=(0, 3))
        label_widget = tk.Label(row1, text=label, bg='white', anchor='w', font=slider_font, borderwidth=0, highlightthickness=0)
        label_widget.pack(side=tk.LEFT)

        vcmd = (self.register(self._validate_entry), '%P')
        self.entry = tk.Entry(row1, width=6, font=slider_font, justify='center', validate='key', validatecommand=vcmd,
                             borderwidth=1, relief='solid', highlightthickness=1)
        self.entry.insert(0, self._format_val(initial))
        self.entry.pack(side=tk.LEFT, padx=(3, 0))
        self.entry.bind('<FocusOut>', self._on_entry_focus_out)
        self.entry.bind('<Return>', self._on_entry_return)

        # Units label (if specified)
        if self.units:
            self.units_label = tk.Label(row1, text=self.units, bg='white', font=slider_font, borderwidth=0, highlightthickness=0)
            self.units_label.pack(side=tk.LEFT, padx=(3, 0))
        else:
            self.units_label = None

        # Row 2: Min label, slider, max label (no padding)
        row2 = tk.Frame(self.bordered, bg='white', borderwidth=0, highlightthickness=0)
        row2.pack(fill=tk.X)
        min_label = tk.Label(row2, text=self._format_val(minval), bg='white', font=slider_font, borderwidth=0, highlightthickness=0)
        min_label.pack(side=tk.LEFT, padx=(0, 3))
        self.slider = ttk.Scale(row2, from_=minval, to=maxval, orient=tk.HORIZONTAL, variable=self.value, command=self._on_slider)
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        max_label = tk.Label(row2, text=self._format_val(maxval), bg='white', font=slider_font, borderwidth=0, highlightthickness=0)
        max_label.pack(side=tk.LEFT)

        # Custom step logic for track click
        self.slider.bind('<Button-1>', self._on_slider_track_click)

        # Keep everything in sync
        self.value.trace_add('write', self._on_value_change)

    def _format_val(self, val):
        if self.is_float:
            return f"{float(val):.{self.decimal_places}f}"
        else:
            return str(int(val))

    def _validate_entry(self, P):
        if P == '':
            return True
        if self.is_float:
            # Only allow digits and at most one dot
            if P.count('.') > 1:
                return False
            allowed = set('0123456789.')
            return all(c in allowed for c in P)
        else:
            return P.isdigit()

    def _on_entry_focus_out(self, event=None):
        self._commit_entry()

    def _on_entry_return(self, event=None):
        self._commit_entry()

    def _commit_entry(self):
        val = self.entry.get()
        if val == '':
            val = self._format_val(self.minval)
        try:
            num = float(val) if self.is_float else int(val)
        except ValueError:
            num = float(self._last_valid) if self.is_float else int(self._last_valid)
        if num < self.minval:
            num = self.minval
        elif num > self.maxval:
            num = self.maxval
        if self.is_float:
            num = round(num, self.decimal_places)
        self.value.set(num)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self._format_val(num))
        self._last_valid = self._format_val(num)
        if self.units_label:
            self.units_label.config(text=self.units)

    def _on_slider(self, value):
        val = float(value) if self.is_float else int(float(value))
        if self.is_float:
            val = round(val, self.decimal_places)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self._format_val(val))
        self._last_valid = self._format_val(val)
        if self.units_label:
            self.units_label.config(text=self.units)
        if self.on_change:
            self.on_change(val)

    def _on_value_change(self, *args):
        val = self.value.get()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self._format_val(val))
        self._last_valid = self._format_val(val)
        if self.units_label:
            self.units_label.config(text=self.units)

    def get(self):
        return self.value.get()

    def set(self, val):
        self.value.set(val)

    def _get_step(self):
        if self.is_float:
            return 10 ** (-self.decimal_places)
        else:
            return 1

    def _on_slider_track_click(self, event):
        slider = self.slider
        smin = float(slider['from'])
        smax = float(slider['to'])
        sval = self.value.get()
        step = self._get_step()
        slider_length = slider.winfo_width()
        rel_x = event.x / slider_length
        # Calculate the value at the click position
        click_val = smin + (smax - smin) * rel_x
        # Estimate thumb position and size
        thumb_size = 20  # px, approximate size of the thumb
        thumb_center_x = int((sval - smin) / (smax - smin) * slider_length)
        # If click is within the thumb region, allow default behavior
        if abs(event.x - thumb_center_x) <= thumb_size // 2:
            return  # allow default drag
        # Otherwise, custom step logic
        if click_val > sval:
            new_val = min(sval + step, smax)
        else:
            new_val = max(sval - step, smin)
        if self.is_float:
            new_val = round(new_val, self.decimal_places)
        self.value.set(new_val)
        return "break"


class SectionFrame(tk.Frame):
    def __init__(self, parent, section_name, **kwargs):
        super().__init__(parent, bg='white', **kwargs)
        label = tk.Label(self, text=section_name.replace('_', ' ').title(), font=('Segoe UI', 11, 'bold'), bg='white')
        label.pack(anchor='w', pady=(0, 4))

class CheckboxComponent(tk.Frame):
    def __init__(self, parent, label, initial, **kwargs):
        super().__init__(parent, bg='white', **kwargs)
        self.var = tk.BooleanVar(value=initial)
        self.checkbox = tk.Checkbutton(self, text=label, variable=self.var, bg='white', anchor='w')
        self.checkbox.pack(anchor='w')
    def get(self):
        return self.var.get()
    def set(self, val):
        self.var.set(val)

class TextboxComponent(tk.Frame):
    def __init__(self, parent, label, initial, **kwargs):
        super().__init__(parent, bg='white', **kwargs)
        tk.Label(self, text=label, bg='white').pack(side=tk.LEFT)
        self.entry = tk.Entry(self, bg='white')
        self.entry.insert(0, str(initial))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    def get(self):
        return self.entry.get()
    def set(self, val):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, str(val))

class CenteredImageDisplay(tk.Frame):
    def __init__(self, parent, file_path, target_short_side, **kwargs):
        super().__init__(parent, bg='white', **kwargs)
        self.file_path = file_path
        self.target_short_side = target_short_side
        self.label = tk.Label(self, bg='white')
        self.label.pack(expand=True)
        self.frames = []
        self.original_frames = []
        self.frame_durations = []
        self.frame_index = 0
        self.animating = False
        self._photo_ref = None  # Prevent GC
        self._after_id = None  # Track scheduled after callback
        self._load_image()
        self.update_target_size(self.target_short_side)

    def _load_image(self):
        self.animating = False
        self.frames = []
        self.original_frames = []
        self.frame_durations = []
        self.frame_index = 0
        if not os.path.exists(self.file_path):
            self.label.config(image='', text='Image not found', fg='white', font=('Segoe UI', 12, 'bold'))
            return
        try:
            img = Image.open(self.file_path)
            self.is_gif = getattr(img, "is_animated", False) or self.file_path.lower().endswith('.gif')
            if self.is_gif:
                self.original_frames = []
                self.frame_durations = []
                for frame in ImageSequence.Iterator(img):
                    self.original_frames.append(frame.copy())
                    self.frame_durations.append(frame.info.get('duration', 100))
                self._resize_frames()
                self._show_gif_frame()
            else:
                self.img = img
                self._show_image()
        except Exception as e:
            self.label.config(image='', text=f'Error: {e}', fg='white', font=('Segoe UI', 12, 'bold'))

    def _resize_frames(self):
        self.frames = [self._resize_to_short_side(frame, self.target_short_side) for frame in self.original_frames]

    def _resize_to_short_side(self, img, short_side):
        w, h = img.size
        if w <= 0 or h <= 0:
            return img
        if w < h:
            new_w = int(round(short_side))
            new_h = int(round(h * (short_side / w)))
        else:
            new_h = int(round(short_side))
            new_w = int(round(w * (short_side / h)))
        # Ensure minimum size of 1x1
        new_w = max(1, new_w)
        new_h = max(1, new_h)
        return img.resize((new_w, new_h), Image.LANCZOS)

    def _show_image(self):
        img = self._resize_to_short_side(self.img, self.target_short_side)
        photo = ImageTk.PhotoImage(img)
        self._photo_ref = photo
        self.label.config(image=photo, text='')
        self.label.image = photo
        self._center_label(img.size)

    def _show_gif_frame(self):
        if not self.frames:
            return
        # Cancel any previous scheduled callback
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        frame = self.frames[self.frame_index]
        photo = ImageTk.PhotoImage(frame)
        self._photo_ref = photo
        self.label.config(image=photo, text='')
        self.label.image = photo
        self._center_label(frame.size)
        delay = 100
        if self.frame_durations and self.frame_index < len(self.frame_durations):
            delay = self.frame_durations[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.animating = True
        self._after_id = self.after(delay, self._show_gif_frame)

    def _center_label(self, img_size):
        # Center the image in the available space
        self.label.pack_forget()
        self.label.pack(expand=True)
        self.label.config(anchor='center')

    def update_target_size(self, new_short_side):
        self.target_short_side = new_short_side
        # Cancel any previous scheduled callback
        if hasattr(self, '_after_id') and self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        if hasattr(self, 'img') and not getattr(self, 'is_gif', False):
            self._show_image()
        elif self.frames:
            self._resize_frames()
            self.frame_index = 0  # Restart animation from the first frame
            self._show_gif_frame()

    def set_file(self, new_file_path):
        self.file_path = new_file_path
        self._load_image()

# --- Test case for main UI ---
if __name__ == "__main__":
    import sys
    from tkinter import filedialog
    root = tk.Tk()
    root.title("ParameterSelectUI with CenteredImageDisplay")
    # Ask user for an image file
    file_path = filedialog.askopenfilename(title="Select image or gif", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
    if not file_path:
        print("No file selected.")
        sys.exit(0)
    app = ParameterSelectUI(root, target_full_file_path=file_path)
    app.run()
