import tkinter as tk
from tkinter import ttk
import os
import json


class ParameterSelectUI:
    def __init__(self, filepath, config_file="config.json"):
        """
        Initialize the ParameterSelectUI with a filepath.
        
        Args:
            filepath (str): Full path to the target file
            config_file (str): Path to the configuration file
        """
        self.filepath = filepath
        self.file_extension = self._get_file_extension()
        self.config_file = config_file
        self.config_data = self._load_config()
        
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Parameter Selection")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configure modern flat style
        self._configure_modern_style()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs based on file extension
        self._create_tabs()
        
        # Set minimum window size
        self.root.update_idletasks()
        min_width = int(self.root.winfo_reqwidth() * 1.25)
        min_height = self.root.winfo_reqheight()
        self.root.minsize(min_width, min_height)
    
    def _configure_modern_style(self):
        """Configure modern flat styling for the UI."""
        style = ttk.Style()
        
        # Configure the notebook style for flat appearance
        style.configure('TNotebook', background='#f0f0f0', borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#e0e0e0', 
                       foreground='#333333',
                       borderwidth=0,
                       padding=[20, 10],
                       focuscolor='none')
        
        # Configure selected tab
        style.map('TNotebook.Tab',
                 background=[('selected', '#ffffff')],
                 foreground=[('selected', '#000000')])
        
        # Configure frame style
        style.configure('TFrame', background='#ffffff')
        
        # Configure button style (for future use)
        style.configure('TButton',
                       background='#0078d4',
                       foreground='white',
                       borderwidth=0,
                       padding=[15, 8],
                       focuscolor='none')
        
        style.map('TButton',
                 background=[('active', '#106ebe'), ('pressed', '#005a9e')])
        
        # Configure entry style (for future use)
        style.configure('TEntry',
                       borderwidth=1,
                       relief='flat',
                       fieldbackground='#ffffff',
                       focuscolor='#0078d4')
        
        # Configure label style (for future use)
        style.configure('TLabel',
                       background='#ffffff',
                       foreground='#333333')
        
        # Configure checkbutton style (for future use)
        style.configure('TCheckbutton',
                       background='#ffffff',
                       foreground='#333333',
                       focuscolor='none')
        
                # Configure scale style (for future use)
        style.configure('Horizontal.TScale',
                       background='#ffffff',
                       troughcolor='#e0e0e0',
                       sliderwidth=20,
                       sliderlength=20,
                       borderwidth=0,
                       focuscolor='none')
    
    def _load_config(self):
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found")
            return {}
        except json.JSONDecodeError:
            print(f"Invalid JSON in config file {self.config_file}")
            return {}
    
    def _get_file_extension(self):
        """Extract file extension from filepath."""
        _, ext = os.path.splitext(self.filepath)
        return ext.lower()
    
    def _create_tabs(self):
        """Create tabs based on file extension."""
        # Always show general parameters tab
        self.general_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.general_tab, text="General Parameters")
        self._populate_general_tab()
        
        # Show image parameters tab only for image files
        if self.file_extension in ['.jpg', '.jpeg', '.png']:
            self.image_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.image_tab, text="Image Parameters")
        
        # Show gif parameters tab only for gif files
        if self.file_extension == '.gif':
            self.gif_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.gif_tab, text="GIF Parameters")
        
        # Always show advanced settings tab (rightmost)
        self.advanced_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.advanced_tab, text="Advanced Settings")
        self._populate_advanced_tab()
    
    def run(self):
        """Start the UI main loop."""
        self.root.mainloop()
    
    def _populate_general_tab(self):
        """Populate the general parameters tab with widgets."""
        # Create main container frame
        main_container = ttk.Frame(self.general_tab)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Configure grid weights - left side expands, right side fixed
        main_container.grid_columnconfigure(0, weight=1)  # Left side expands
        main_container.grid_columnconfigure(1, weight=0)  # Right side fixed width
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left side - Red container (expands with window)
        left_frame = ttk.Frame(main_container)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Create red container
        self.left_canvas = tk.Canvas(left_frame, bg='red', highlightthickness=0)
        self.left_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Blue container (fixed width)
        right_frame = ttk.Frame(main_container, width=380)  # Fixed width of 380px
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_frame.grid_propagate(False)  # Prevent frame from shrinking
        
        # Create blue container with scrollable content
        self.right_canvas = tk.Canvas(right_frame, bg='blue', highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.right_canvas.yview)
        content_frame = tk.Frame(self.right_canvas, bg='white')
        
        content_frame.bind(
            "<Configure>",
            lambda e: self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
        )
        
        self.right_canvas.create_window((0, 0), window=content_frame, anchor="nw")
        self.right_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.right_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create sections
        self._create_target_section(content_frame)
        self._create_texture_section(content_frame)
        self._create_pygame_section(content_frame)
        self._create_vector_field_section(content_frame)
    

    
    def _create_section_container(self, parent, title):
        """Create a section container with title and border."""
        # Main container frame
        container_frame = ttk.Frame(parent)
        container_frame.pack(fill=tk.X, pady=(15, 10), padx=15)
        
        # Title label
        title_label = ttk.Label(container_frame, text=title, font=('Segoe UI', 11, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Content frame with border
        content_frame = ttk.Frame(container_frame, relief="solid", borderwidth=1)
        content_frame.pack(fill=tk.X)
        
        # Inner padding frame
        inner_frame = ttk.Frame(content_frame)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        return inner_frame
    
    def _create_target_section(self, parent):
        """Create Target Settings section."""
        frame = self._create_section_container(parent, "Target Settings")
        
        # Resize shorter side of target slider
        self.target_var = tk.IntVar(value=493)
        
        # Label with current value
        target_label = ttk.Label(frame, text="Resize shorter side of target: 493px")
        target_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Slider
        target_slider = ttk.Scale(
            frame,
            from_=100,
            to=500,
            variable=self.target_var,
            orient="horizontal",
            length=300
        )
        target_slider.pack(fill=tk.X, pady=(0, 5))
        
        # Update label function
        def update_target_label():
            target_label.config(text=f"Resize shorter side of target: {self.target_var.get()}px")
        
        self.target_var.trace_add("write", lambda *args: update_target_label())
        
        # Min/Max labels
        bounds_frame = ttk.Frame(frame)
        bounds_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(bounds_frame, text="100").pack(side=tk.LEFT)
        ttk.Label(bounds_frame, text="500").pack(side=tk.RIGHT)
    
    def _create_texture_section(self, parent):
        """Create Texture Settings section."""
        frame = self._create_section_container(parent, "Texture Settings")
        
        # Texture opacity slider
        self.opacity_var = tk.DoubleVar(value=1.00)
        
        # Label with current value
        opacity_label = ttk.Label(frame, text="Texture opacity: 1.00")
        opacity_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Slider
        opacity_slider = ttk.Scale(
            frame,
            from_=0.0,
            to=1.0,
            variable=self.opacity_var,
            orient="horizontal",
            length=300
        )
        opacity_slider.pack(fill=tk.X, pady=(0, 5))
        
        # Update label function
        def update_opacity_label():
            opacity_label.config(text=f"Texture opacity: {self.opacity_var.get():.2f}")
        
        self.opacity_var.trace_add("write", lambda *args: update_opacity_label())
        
        # Min/Max labels
        bounds_frame = ttk.Frame(frame)
        bounds_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(bounds_frame, text="0.0").pack(side=tk.LEFT)
        ttk.Label(bounds_frame, text="1.0").pack(side=tk.RIGHT)
        
        # Initial random rectangle pixel width slider
        self.rect_width_var = tk.IntVar(value=193)
        
        # Label with current value
        rect_label = ttk.Label(frame, text="Initial random rectangle pixel width: 193px")
        rect_label.pack(anchor=tk.W, pady=(10, 5))
        
        # Slider
        rect_slider = ttk.Scale(
            frame,
            from_=10,
            to=200,
            variable=self.rect_width_var,
            orient="horizontal",
            length=300
        )
        rect_slider.pack(fill=tk.X, pady=(0, 5))
        
        # Update label function
        def update_rect_label():
            rect_label.config(text=f"Initial random rectangle pixel width: {self.rect_width_var.get()}px")
        
        self.rect_width_var.trace_add("write", lambda *args: update_rect_label())
        
        # Min/Max labels
        bounds_frame2 = ttk.Frame(frame)
        bounds_frame2.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(bounds_frame2, text="10px").pack(side=tk.LEFT)
        ttk.Label(bounds_frame2, text="200px").pack(side=tk.RIGHT)
        
        # Allow scaling during mutation checkbox
        self.scaling_var = tk.BooleanVar(value=True)
        scaling_checkbox = ttk.Checkbutton(
            frame,
            text="Allow scaling during mutation",
            variable=self.scaling_var
        )
        scaling_checkbox.pack(anchor=tk.W, pady=(10, 0))
    
    def _create_pygame_section(self, parent):
        """Create Pygame Display Settings section."""
        frame = self._create_section_container(parent, "Pygame Display Settings")
        
        # Show progress checkbox
        self.show_progress_var = tk.BooleanVar(value=True)
        show_progress_checkbox = ttk.Checkbutton(
            frame,
            text="Show progress",
            variable=self.show_progress_var
        )
        show_progress_checkbox.pack(anchor=tk.W, pady=(0, 5))
        
        # Display rectangle improvement checkbox
        self.display_improvement_var = tk.BooleanVar(value=True)
        display_improvement_checkbox = ttk.Checkbutton(
            frame,
            text="Display rectangle improvement in progress",
            variable=self.display_improvement_var
        )
        display_improvement_checkbox.pack(anchor=tk.W, pady=(0, 0))
    
    def _create_vector_field_section(self, parent):
        """Create Vector Field Settings section."""
        frame = self._create_section_container(parent, "Vector Field Settings")
        
        # Enable vector field checkbox
        self.enable_vector_field_var = tk.BooleanVar(value=True)
        enable_checkbox = ttk.Checkbutton(
            frame,
            text="Enable vector field",
            variable=self.enable_vector_field_var
        )
        enable_checkbox.pack(anchor=tk.W, pady=(0, 10))
        
        # Edit vector field origin button
        self.edit_button = tk.Button(
            frame,
            text="Edit vector field origin",
            bg="#4078c0",
            fg="#000000",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            font=('Segoe UI', 9),
            state="normal"
        )
        self.edit_button.pack(anchor=tk.W, pady=(0, 0))
        
        # Button click handler
        def button_click():
            print("Edit vector field origin button clicked")
        
        self.edit_button.config(command=button_click)
        
        # Update button appearance when checkbox changes
        def update_button():
            if self.enable_vector_field_var.get():
                self.edit_button.config(bg="#4078c0", fg="#000000", state="normal")
            else:
                self.edit_button.config(bg="#cfcfcf", fg="#737373", state="disabled")
        
        self.enable_vector_field_var.trace_add("write", lambda *args: update_button())
    
    def _populate_advanced_tab(self):
        """Populate the advanced settings tab with widgets."""
        # Create main frame
        main_frame = ttk.Frame(self.advanced_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Get advanced parameters from config
        advanced_params = self.config_data.get("advanced_parameters", {})
        
        # Create debug section
        self._create_debug_section(main_frame, advanced_params.get("debug_settings", {}))
    
    def _create_debug_section(self, parent, debug_settings):
        """Create Debug Settings section."""
        frame = self._create_section_container(parent, "Debug Settings")
        
        # Create checkboxes for each debug setting
        for key, config in debug_settings.items():
            if config.get("widget_type") == "checkbox":
                var = tk.BooleanVar(value=config.get("current_value", False))
                checkbox = ttk.Checkbutton(
                    frame, 
                    text=config.get("description", key),
                    variable=var
                )
                checkbox.pack(anchor=tk.W, pady=5)
    
    def destroy(self):
        """Destroy the UI window."""
        self.root.destroy()


if __name__ == "__main__":
    # Example usage
    test_filepath = "example.png"
    ui = ParameterSelectUI(test_filepath)
    ui.run()
