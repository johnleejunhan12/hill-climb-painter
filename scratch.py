# import tkinter as tk

# root = tk.Tk()
# root.title("Tkinter Button Relief Styles")

# reliefs = ["flat", "raised", "sunken", "groove", "ridge", "solid"]

# for i, style in enumerate(reliefs):
#     btn = tk.Button(
#         root,
#         text=style.capitalize(),
#         relief=style,
#         width=12,
#         height=2,
#         bd=4  # Border width (matters for most styles)
#     )
#     btn.grid(row=0, column=i, padx=5, pady=10)

# root.mainloop()


import tkinter as tk
from tkinter import messagebox

def on_exit_click():
    # Create popup
    popup = tk.Toplevel(root)
    popup.title("Confirm Exit")
    popup.geometry("300x120")
    popup.resizable(False, False)

    # Keep popup on top and modal
    popup.transient(root)    # Attach popup to root
    popup.grab_set()         # Make popup modal
    popup.attributes('-topmost', True)  # Always on top

    # Center message
    tk.Label(popup, text="Are you sure you want to exit?", pady=10).pack()

    # Button frame
    button_frame = tk.Frame(popup)
    button_frame.pack(pady=10)

    def on_yes():
        root.destroy()

    def on_no():
        popup.destroy()

    tk.Button(button_frame, text="Yes", width=10, command=on_yes).pack(side="left", padx=5)
    tk.Button(button_frame, text="No", width=10, command=on_no).pack(side="right", padx=5)

# Main window
root = tk.Tk()
root.title("Main Window")
root.geometry("400x300")
root.protocol("WM_DELETE_WINDOW", on_exit_click)  # Intercept close button

tk.Button(root, text="Exit", command=on_exit_click).pack(pady=120)

root.mainloop()
