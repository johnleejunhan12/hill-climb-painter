import tkinter as tk
from tkinter import ttk

class SelectTargetButtonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.title("Select Target Button Demo")
        self.configure(bg="#f5f6fa")
        self.minsize(300, 200)
        self._center_window(300, 200)
        
        # Setup style for the button
        self._setup_style()
        
        # Create the select target button
        self.select_target_btn = ttk.Button(
            self,
            text="Select target",
            command=self._on_select_target,
            takefocus=0
        )
        self.select_target_btn.pack(pady=20, padx=20, ipady=10, fill="x")
        
        # Configure button width to stretch
        self.update_idletasks()
        self.select_target_btn.configure(width=1)
    
    def _center_window(self, width, height):
        """Center the window on the screen."""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_style(self):
        """Apply the exact style from TargetTextureSelectorUI for TButton."""
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure(
            'TButton',
            font=('Segoe UI', 12),
            padding=0,
            relief='flat',
            background='#4078c0',  # Blue background
            foreground='#fff',     # White text
            focuscolor=style.lookup('TButton', 'background')
        )
        style.map(
            'TButton',
            background=[('active', '#305080')]  # Darker blue when active
        )
    
    def _on_select_target(self):
        """Placeholder for select target action."""
        print("Select target button clicked")

if __name__ == "__main__":
    app = SelectTargetButtonApp()
    app.mainloop()