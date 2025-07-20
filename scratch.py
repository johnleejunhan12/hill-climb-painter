import tkinter as tk
from tkinter import ttk, filedialog
from parameter_select_ui import CenteredImageDisplay

if __name__ == "__main__":
    import sys
    root = tk.Tk()
    root.title("Test CenteredImageDisplay - Partitioned")
    # Partition window into left and right frames
    left_frame = tk.Frame(root, bg='red', width=400)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    right_frame = tk.Frame(root, bg='white', width=200)
    right_frame.pack(side=tk.RIGHT, fill=tk.Y)

    # Ask user for an image file
    file_path = filedialog.askopenfilename(title="Select image or gif", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
    if not file_path:
        print("No file selected.")
        sys.exit(0)
    # Initial short side
    short_side = 200
    display = CenteredImageDisplay(left_frame, file_path, short_side)
    display.pack(fill=tk.BOTH, expand=True)
    # Slider to control short side (in right frame)
    def on_slider(val):
        display.update_target_size(int(float(val)))
    slider = ttk.Scale(right_frame, from_=50, to=600, orient=tk.HORIZONTAL, command=on_slider)
    slider.set(short_side)
    slider.pack(fill=tk.X, padx=20, pady=10)
    root.mainloop() 