import tkinter as tk
from tkinter import ttk

def center_window(root, width, height):
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate position to center the window
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    # Set window geometry
    root.geometry(f"{width}x{height}+{x}+{y}")

# Create the main window
root = tk.Tk()
root.title("Notebook Layout")

# Set window size and center it
window_width = 400
window_height = 300
center_window(root, window_width, window_height)

# Set minimum window size
root.minsize(300, 200)

# Create a frame to center the notebook
notebook_frame = tk.Frame(root)
notebook_frame.pack(pady=20)

# Create the notebook widget
notebook = ttk.Notebook(notebook_frame)
notebook.pack()

# Create and add two tabs to the notebook
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
notebook.add(tab1, text="Tab 1")
notebook.add(tab2, text="Tab 2")

# Create a frame for buttons to center them
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Create two buttons of equal size
button1 = tk.Button(button_frame, text="Button 1", width=10)
button2 = tk.Button(button_frame, text="Button 2", width=10)

# Place buttons side by side with padding
button1.pack(side=tk.LEFT, padx=5)
button2.pack(side=tk.LEFT, padx=5)

# Run the main loop
root.mainloop()