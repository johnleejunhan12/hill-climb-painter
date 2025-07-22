import tkinter as tk

root = tk.Tk()
root.title("Multiple Frames")

# Top frame
top_frame = tk.Frame(root, bg="lightblue", height=100)
top_frame.pack(fill="x")  # Fill horizontally

# Bottom frame
bottom_frame = tk.Frame(root, bg="lightgreen")
bottom_frame.pack(fill="both", expand=True)  # Fill all available space

# Add widgets to top frame
tk.Label(top_frame, text="Top Section").pack(pady=20)

# Add widgets to bottom frame
tk.Button(bottom_frame, text="Button 1").pack(side="left", padx=10)
tk.Button(bottom_frame, text="Button 2").pack(side="left")

root.mainloop()