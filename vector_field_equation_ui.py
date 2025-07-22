import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sympy as sp
from sympy import sympify, lambdify
import warnings
warnings.filterwarnings('ignore')

class VectorFieldVisualizer:
    def __init__(self, master=None, presets=None, sq_grid_size=None, initial_f_string=None, initial_g_string=None):
        if master is None:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(master)
            self.root.transient(master)
            self.root.grab_set()
        self.root.title("Vector Field Visualizer")
        self.root.geometry("800x700")
        self.root.configure(bg='#f0f0f0')
        
        # Default presets if none provided
        self.presets = presets if presets else {
            "preset_1_name": ("x+y", "y+1"),
            "preset_2_name": ("cos(x)", "sin(y)"),
            "preset_3_name": ("-y*x", "y**2")
        }
        
        # Default grid sizes if none provided
        self.sq_grid_size = sq_grid_size if sq_grid_size else [10, 20, 50]
        self.current_grid_size = tk.IntVar(value=self.sq_grid_size[0])
        
        # Variables to store the function
        self.f_expr = None
        self.g_expr = None
        self.f_func = None
        self.g_func = None
        self.result_function = None
        self.confirmed = False
        self.is_valid = False
        
        # Sympy symbols
        self.x, self.y = sp.symbols('x y', real=True)
        
        # Store initial strings
        self.initial_f_string = initial_f_string
        self.initial_g_string = initial_g_string
        
        # Create the UI
        self.setup_styles()
        self.create_widgets()
        self.update_visualization()
        
    def setup_styles(self):
        """Configure modern styling for ttk widgets"""
        style = ttk.Style()
        # style.theme_use('clam')
        
        # Configure button styles
        style.configure('Visualize.TButton',
                       background='#4CAF50',
                       foreground='black',
                       font=('Arial', 11, 'bold'),
                       padding=(20, 10))
        
        style.configure('Confirm.TButton',
                       background='#2196F3',
                       foreground='black',
                       font=('Arial', 11, 'bold'),
                       padding=(20, 10))
        
        # Configure disabled button style
        style.configure('Disabled.TButton',
                       background='#cccccc',
                       foreground='#666666',
                       font=('Arial', 11, 'bold'),
                       padding=(20, 10))
        
        style.map('Visualize.TButton',
                 background=[('active', '#45a049')])
        style.map('Confirm.TButton',
                 background=[('active', '#1976D2')])
        
        # Configure entry style
        style.configure('Modern.TEntry',
                       fieldbackground='white',
                       borderwidth=2,
                       font=('Arial', 12))
        
    def create_widgets(self):
        """Create and layout all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Presets and grid size dropdowns
        preset_frame = ttk.Frame(main_frame)
        preset_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(preset_frame, text="Presets", font=('Arial', 12, 'bold')).grid(row=0, column=0, padx=(0, 10))
        self.preset_var = tk.StringVar()
        self.preset_dropdown = ttk.Combobox(preset_frame, textvariable=self.preset_var, values=list(self.presets.keys()))
        self.preset_dropdown.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.preset_dropdown.bind('<<ComboboxSelected>>', self.on_preset_select)
        self.preset_dropdown.set(list(self.presets.keys())[0])
        
        ttk.Label(preset_frame, text="Grid size", font=('Arial', 12, 'bold')).grid(row=0, column=2, padx=(10, 10))
        self.grid_size_var = tk.StringVar(value=f"{self.sq_grid_size[0]}x{self.sq_grid_size[0]}")
        self.grid_size_dropdown = ttk.Combobox(preset_frame, textvariable=self.grid_size_var, values=[f"{size}x{size}" for size in self.sq_grid_size])
        self.grid_size_dropdown.grid(row=0, column=3, sticky=(tk.W, tk.E))
        self.grid_size_dropdown.bind('<<ComboboxSelected>>', self.on_grid_size_select)
        
        # Vector field plot
        self.create_plot(main_frame)
        
        # Input fields frame
        input_frame = ttk.Frame(main_frame, padding="10")
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        input_frame.columnconfigure(1, weight=1)
        
        # f(x,y) input
        ttk.Label(input_frame, text="f(x,y)", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        
        self.f_entry = ttk.Entry(input_frame, font=('Arial', 12), style='Modern.TEntry')
        self.f_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        # Set initial f string if provided, otherwise use preset
        if self.initial_f_string is not None:
            self.f_entry.insert(0, self.initial_f_string)
        else:
            self.f_entry.insert(0, self.presets[list(self.presets.keys())[0]][0])
        self.f_entry.bind('<KeyRelease>', self.on_entry_change)
        
        # g(x,y) input  
        ttk.Label(input_frame, text="g(x,y)", font=('Arial', 12, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        
        self.g_entry = ttk.Entry(input_frame, font=('Arial', 12), style='Modern.TEntry')
        self.g_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        # Set initial g string if provided, otherwise use preset
        if self.initial_g_string is not None:
            self.g_entry.insert(0, self.initial_g_string)
        else:
            self.g_entry.insert(0, self.presets[list(self.presets.keys())[0]][1])
        self.g_entry.bind('<KeyRelease>', self.on_entry_change)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Valid", 
                                     font=('Arial', 11), 
                                     foreground='green')
        self.status_label.grid(row=3, column=0, pady=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.grid(row=4, column=0, pady=(10, 0))
        
        self.visualize_btn = ttk.Button(button_frame, text="Visualize", 
                                       style='Visualize.TButton',
                                       command=self.update_visualization)
        self.visualize_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.confirm_btn = ttk.Button(button_frame, text="Confirm selection", 
                                     style='Confirm.TButton',
                                     command=self.confirm_selection)
        self.confirm_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Initial validation
        self.validate_expressions()
        
    def create_plot(self, parent):
        """Create the matplotlib plot for vector field visualization"""
        # Create figure and axis
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.fig.patch.set_facecolor('#f0f0f0')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure plot
        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('y', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        
    def validate_expressions(self):
        """Validate the mathematical expressions and update status"""
        try:
            f_text = self.f_entry.get().strip()
            g_text = self.g_entry.get().strip()
            
            if not f_text or not g_text:
                self.update_status("Invalid", "Empty expression", 'red')
                self.is_valid = False
                self.update_button_state()
                return False
            
            # Parse expressions with restricted symbols
            allowed_symbols = {self.x, self.y}
            allowed_functions = ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 
                               'sinh', 'cosh', 'tanh', 'asin', 'acos', 'atan',
                               'abs', 'sign', 'floor', 'ceiling']
            
            # Create safe namespace
            safe_dict = {func: getattr(sp, func) for func in allowed_functions if hasattr(sp, func)}
            safe_dict.update({'x': self.x, 'y': self.y, 'pi': sp.pi, 'e': sp.E})
            
            # Parse expressions
            self.f_expr = sympify(f_text, locals=safe_dict)
            self.g_expr = sympify(g_text, locals=safe_dict)
            
            # Check if expressions contain only allowed symbols
            f_symbols = self.f_expr.free_symbols
            g_symbols = self.g_expr.free_symbols
            
            if not (f_symbols <= allowed_symbols) or not (g_symbols <= allowed_symbols):
                raise ValueError("Only x and y variables are allowed")
            
            # Convert to numerical functions
            self.f_func = lambdify([self.x, self.y], self.f_expr, 'numpy')
            self.g_func = lambdify([self.x, self.y], self.g_expr, 'numpy')
            
            # Test with sample values
            test_result = self.safe_evaluate(0.1, 0.1)
            
            self.update_status("Valid", "", 'green')
            self.is_valid = True
            self.update_button_state()
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "name" in error_msg.lower() and "not defined" in error_msg.lower():
                error_msg = "Unknown function or variable"
            elif "syntax" in error_msg.lower():
                error_msg = "Invalid syntax"
            
            self.update_status("Invalid", error_msg, 'red')
            self.is_valid = False
            self.update_button_state()
            return False
    
    def update_status(self, status, message, color):
        """Update the status label"""
        full_text = status
        if message:
            full_text += f": {message}"
        
        self.status_label.configure(text=full_text, foreground=color)
    
    def update_button_state(self):
        """Update the confirm button state based on validation"""
        if self.is_valid:
            self.confirm_btn.configure(style='Confirm.TButton', state='normal')
        else:
            self.confirm_btn.configure(style='Disabled.TButton', state='disabled')
    
    def safe_evaluate(self, x_val, y_val):
        """Safely evaluate the functions at given points"""
        try:
            if self.f_func is None or self.g_func is None:
                return 0, 0
                
            # Convert inputs to numpy arrays if they aren't already
            x_array = np.asarray(x_val, dtype=float)
            y_array = np.asarray(y_val, dtype=float)
            
            # Evaluate functions
            f_result = self.f_func(x_array, y_array)
            g_result = self.g_func(x_array, y_array)
            
            # Handle scalar results
            if np.isscalar(f_result):
                f_result = np.array([f_result])
            if np.isscalar(g_result):
                g_result = np.array([g_result])
            
            # Replace invalid values with zeros
            f_result = np.where(np.isfinite(f_result), f_result, 0)
            g_result = np.where(np.isfinite(g_result), g_result, 0)
            
            # Return scalars if input was scalar
            if np.isscalar(x_val) and np.isscalar(y_val):
                return float(f_result[0]), float(g_result[0])
            
            return f_result, g_result
            
        except Exception:
            # Return zeros for any evaluation error
            if np.isscalar(x_val) and np.isscalar(y_val):
                return 0.0, 0.0
            else:
                return np.zeros_like(x_val), np.zeros_like(y_val)
    
    def update_visualization(self):
        """Update the vector field plot"""
        if not self.validate_expressions():
            return
        
        # Clear the plot
        self.ax.clear()
        
        # Create coordinate grid based on selected grid size
        grid_size = self.current_grid_size.get()
        density = 1.25
        num_intervals = int(grid_size * density)
        x_range = np.linspace(-grid_size, grid_size, num_intervals)
        y_range = np.linspace(-grid_size, grid_size, num_intervals)
        X, Y = np.meshgrid(x_range, y_range)
        
        # Evaluate vector field
        U, V = self.safe_evaluate(X, Y)
        
        # Normalize vectors
        magnitude = np.sqrt(U**2 + V**2)
        # Avoid division by zero
        magnitude = np.where(magnitude == 0, 1, magnitude)
        length_scale = grid_size/10
        U_norm = U / magnitude * length_scale
        V_norm = V / magnitude * length_scale
        
        # Plot vector field
        quiver_plot = self.ax.quiver(X, Y, U_norm, V_norm, magnitude, 
                                    scale=1, scale_units='xy', angles='xy',
                                    cmap='viridis', alpha=0.8, width=0.003)
        
        # Configure plot
        self.ax.set_xlim(-grid_size, grid_size)
        self.ax.set_ylim(-grid_size, grid_size)
        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('y', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        self.ax.set_title('Vector Field: (f(x,y), g(x,y))', fontsize=14, fontweight='bold')
        
        # Handle colorbar - create once, update afterwards
        if not hasattr(self, 'colorbar') or self.colorbar is None:
            # Create colorbar only on first run
            self.colorbar = self.fig.colorbar(quiver_plot, ax=self.ax, shrink=0.8, label='Magnitude')
        else:
            # Update existing colorbar with new data
            self.colorbar.update_normal(quiver_plot)
        
        self.canvas.draw()
    
    def on_entry_change(self, event=None):
        """Handle changes in entry fields"""
        self.validate_expressions()
    
    def create_result_function(self):
        """Create the final function object to return"""
        if self.f_func is None or self.g_func is None:
            return None
        
        f_func_copy = self.f_func
        g_func_copy = self.g_func
        
        def vector_field_function(x, y):
            """
            Vector field function that returns (f(x,y), g(x,y))
            
            Parameters:
            x, y: float or array-like
                Input coordinates
                
            Returns:
            tuple: (p, q) where p = f(x,y) and q = g(x,y)
                   Returns (0, 0) for undefined values
            """
            try:
                # Convert inputs to numpy arrays
                x_array = np.asarray(x, dtype=float)
                y_array = np.asarray(y, dtype=float)
                
                # Evaluate functions
                p = f_func_copy(x_array, y_array)
                q = g_func_copy(x_array, y_array)
                
                # Handle scalar results
                if np.isscalar(p):
                    p = np.array([p])
                if np.isscalar(q):
                    q = np.array([q])
                
                # Replace invalid values with zeros
                p = np.where(np.isfinite(p), p, 0)
                q = np.where(np.isfinite(q), q, 0)
                
                # Return appropriate format based on input
                if np.isscalar(x) and np.isscalar(y):
                    return float(p[0]), float(q[0])
                else:
                    return p, q
                    
            except Exception:
                # Return zeros for any evaluation error
                if np.isscalar(x) and np.isscalar(y):
                    return 0.0, 0.0
                else:
                    return np.zeros_like(x), np.zeros_like(y)
        
        # Add metadata to the function
        vector_field_function.f_expression = str(self.f_expr)
        vector_field_function.g_expression = str(self.g_expr)
        
        return vector_field_function
    
    def create_result_string(self):
        """Create the formatted string (f(x,y), g(x,y))"""
        if self.f_expr is None or self.g_expr is None:
            return None
        # Convert expressions to strings and remove extra whitespace
        f_str = str(self.f_expr).replace(" ", "")
        g_str = str(self.g_expr).replace(" ", "")
        return f"({f_str}, {g_str})"
    
    def confirm_selection(self):
        """Handle confirm selection button click"""
        # Only proceed if expressions are valid (button should be disabled otherwise)
        if self.is_valid and self.validate_expressions():
            self.result_function = self.create_result_function()
            self.result_string = self.create_result_string()
            self.confirmed = True
            self.root.quit()  # Exit the mainloop
    
    def on_preset_select(self, event):
        """Handle preset selection from dropdown"""
        selected_preset = self.preset_var.get()
        if selected_preset in self.presets:
            f_expr, g_expr = self.presets[selected_preset]
            self.f_entry.delete(0, tk.END)
            self.f_entry.insert(0, f_expr)
            self.g_entry.delete(0, tk.END)
            self.g_entry.insert(0, g_expr)
            self.validate_expressions()
            self.update_visualization()
    
    def on_grid_size_select(self, event):
        """Handle grid size selection from dropdown"""
        selected_size = self.grid_size_var.get()
        grid_size = int(selected_size.split('x')[0])
        self.current_grid_size.set(grid_size)
        self.update_visualization()
    
    def run(self):
        """Run the GUI and return the result string and function"""
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start the GUI
        self.root.mainloop()
        
        # Clean up
        self.root.destroy()
        
        if self.confirmed and self.result_string is not None:
            return self.result_string, self.result_function
        else:
            return None
    
    def on_closing(self):
        """Handle window closing event"""
        self.confirmed = False
        self.root.quit()


def create_vector_field_visualizer(presets=None, sq_grid_size=None, master=None, initial_f_string=None, initial_g_string=None):
    """
    Create and run the vector field visualizer GUI.
    
    Parameters:
    presets: dict, optional
        Dictionary of preset vector fields
    sq_grid_size: list, optional
        List of grid sizes for visualization
    master: Tk or Toplevel, optional
        Parent window
    initial_f_string: str, optional
        Initial expression for f(x,y) to display in input box
    initial_g_string: str, optional
        Initial expression for g(x,y) to display in input box
    
    Returns:
    tuple: (string, function)
        - string: Formatted string "(f(x,y), g(x,y))" with extra whitespace removed except after the comma
        - function: A Python function object f(x, y) that returns (p, q) tuple where p = f(x,y) and q = g(x,y)
        Returns (None, None) if the user cancels or closes the window.
    """
    visualizer = VectorFieldVisualizer(master, presets, sq_grid_size, initial_f_string, initial_g_string)
    return visualizer.run()


# Example usage
if __name__ == "__main__":
    print("Starting Vector Field Visualizer...")
    print("Define your vector field components f(x,y) and g(x,y)")
    print("Available functions: sin, cos, tan, exp, log, sqrt, etc.")
    print("Example: f(x,y) = x*cos(y), g(x,y) = y*sin(x)")
    
    # Run the visualizer with custom presets and grid sizes
    custom_presets = {
        # Radial flows (purely inward or outward)
        "Radial Sink": ("-x", "-y"),                     # Vectors point inward to origin
        "Radial Source": ("x", "y"),                     # Vectors point outward from origin

        # Spiral sinks (inward with rotation)
        "Spiral Sink Clockwise": ("-x + y", "-y - x"),   # Inward spiral, rotating clockwise
        "Spiral Sink Anticlockwise": ("-x - y", "x - y"),# Inward spiral, rotating anticlockwise

        # Spiral sources (outward with rotation)
        "Spiral Source Clockwise": ("x - y", "y + x"),   # Outward spiral, rotating clockwise
        "Spiral Source Anticlockwise": ("x + y", "-x + y"), # Outward spiral, rotating anticlockwise

        # Pure rotation (no in/out, just circular flow)
        "Rotation Clockwise": ("y", "-x"),               # Clockwise rotation (solid-body)
        "Rotation Anticlockwise": ("-y", "x")            # Anticlockwise rotation (solid-body)
    }

    custom_grid_sizes = [10, 20, 30]
    initial_f_string = "x+y+1"
    initial_g_string = "x-y-2"
    result = create_vector_field_visualizer(custom_presets, custom_grid_sizes, initial_f_string=initial_f_string, initial_g_string=initial_g_string)

    if result is None:
        print("User closed window")
    else:
        vector_string, vector_function = result
        print("\nVector field created successfully!")
        print(f"Vector field: {vector_string}")
        
        # Test the function
        print("\nTesting the function:")
        print(f"At (1, 1): {vector_function(1, 1)}")
        print(f"At (0, 0): {vector_function(0, 0)}")
        print(f"At (-1, 2): {vector_function(-1, 2)}")
        
        # Test with arrays
        import numpy as np
        x_test = np.array([0, 1, -1])
        y_test = np.array([0, 1, 2])
        result = vector_function(x_test, y_test)
        print(f"Array input test: {result}")