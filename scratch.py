
#         # # 1) Computation size (done)
#         # self.i_computation_size = get_value("computation_size", assert_type=int)
#         # self.i_computation_size_min_value = get_value("computation_size", "min_value", assert_type=int)
#         # self.i_computation_size_max_value = get_value("computation_size", "max_value", assert_type=int)

#         # # 2) Add how many textures (done)
#         # self.i_num_textures = get_value("num_textures", assert_type=int)
#         # self.i_num_textures_min_value = get_value("num_textures", "min_value", assert_type=int)
#         # self.i_num_textures_max_value = get_value("num_textures", "max_value", assert_type=int)

#         # # 3) Number of hill climb iterations (done)
#         # self.i_num_hill_climb_iterations_current_lower_value = get_value("num_hill_climb_iterations", "current_lower_value", assert_type=int)
#         # self.i_num_hill_climb_iterations_current_upper_value = get_value("num_hill_climb_iterations", "current_upper_value", assert_type=int)
#         # self.i_num_hill_climb_iterations_min_value = get_value("num_hill_climb_iterations", "min_value", assert_type=int)
#         # self.i_num_hill_climb_iterations_max_value = get_value("num_hill_climb_iterations", "max_value", assert_type=int)

#         # # 4) Texture opacity settings (done)
#         # self.i_texture_opacity = get_value("texture_opacity", assert_type=int)
#         # self.i_texture_opacity_min_value = get_value("texture_opacity", "min_value", assert_type=int)
#         # self.i_texture_opacity_max_value = get_value("texture_opacity", "max_value", assert_type=int)

#         # # 5) Initial texture width (done)
#         # self.i_initial_texture_width = get_value("initial_texture_width", assert_type=int)
#         # self.i_initial_texture_width_min_value = get_value("initial_texture_width", "min_value", assert_type=int)
#         # self.i_initial_texture_width_max_value = get_value("initial_texture_width", "max_value", assert_type=int)

#         # # 6) Fix size of texture (done)
#         # self.i_uniform_texture_size_bool = get_value("uniform_texture_size", assert_type=bool)

#         # # 8) allow early termination of hill climb (done)
#         # self.i_allow_early_termination_bool = get_value("allow_early_termination", assert_type=bool)
#         # # 8a) Terminate after n iterations (done)
#         # self.i_failed_iterations_threshold = get_value("failed_iterations_threshold", assert_type=int)
#         # self.i_failed_iterations_threshold_min_value = get_value("failed_iterations_threshold", "min_value", assert_type=int)
#         # self.i_failed_iterations_threshold_max_value = get_value("failed_iterations_threshold", "max_value", assert_type=int)

#         # # 9) Enable vector field (done)
#         # self.i_enable_vector_field_bool = get_value("enable_vector_field", assert_type=bool)

#         # 9.i) Edit vector field and # 9.ii) Shift vector field origin buttons
#         # self.i_vector_field_f_string = get_value("vector_field_f", assert_type=str)
#         # self.i_vector_field_g_string = get_value("vector_field_g", assert_type=str)
        

#         # (done)
#         # self.i_vector_field_origin_shift_list_of_tuples = get_value("vector_field_origin_shift", assert_type=list)


#         # # (done)
#         # # 7) Show painting progress as new textures are added
#         # self.i_display_painting_progress_bool = get_value("display_painting_progress", assert_type=bool)
#         # # 7a) Show improvement of individual textures
#         # self.i_display_placement_progress_bool = get_value("display_placement_progress", assert_type=bool)
#         # # 7b) Display final image after painting (conditional)
#         # self.i_display_final_image_bool = get_value("display_final_image", assert_type=bool)




#         # Output tab initial parameters

#         # # 1) Output image size (done)
#         # self.i_output_image_size = get_value("output_image_size", assert_type=int)
#         # self.i_output_image_size_min_value = get_value("output_image_size", "min_value", assert_type=int)
#         # self.i_output_image_size_max_value = get_value("output_image_size", "max_value", assert_type=int)

#         # # 2) Output image name (done)
#         # self.i_output_image_name_string = get_value("output_image_name", assert_type=str)

#         # # 3) Create gif of painting progress checkbox (done)
#         # self.i_create_gif_of_painting_progress_bool = get_value("create_gif_of_painting_progress", assert_type=bool)
#         # # 3i) Name of painting progress gif (done)
#         # self.i_name_of_painting_progress_gif_string = get_value("gif_output_name", assert_type=str)

#         # tab2 GIF Settings (for target with .gif)

#         # # (Done)
#         # # A) Name of painted gif (a new gif where we paint all frames of target gif)
#         # self.i_painted_gif_name_string = get_value("painted_gif_name", assert_type=str)
#         # # B) Multiprocessing checkbox
#         # self.i_enable_multiprocessing_bool = get_value("enable_multiprocessing", assert_type=bool)





















# # from tkinter import *
# # from tkinter import font

# # root = Tk()
# # root.title('Font Families')
# # fonts=list(font.families())
# # fonts.sort()

# # def populate(frame):
# #     '''Put in the fonts'''
# #     listnumber = 1
# #     for i, item in enumerate(fonts):
# #         label = "listlabel" + str(listnumber)
# #         label = Label(frame,text=item,font=(item, 16))
# #         label.grid(row=i)
# #         label.bind("<Button-1>",lambda e,item=item:copy_to_clipboard(item))
# #         listnumber += 1

# # def copy_to_clipboard(item):
# #     root.clipboard_clear()
# #     root.clipboard_append("font=('" + item.lstrip('@') + "', 12)")

# # def onFrameConfigure(canvas):
# #     '''Reset the scroll region to encompass the inner frame'''
# #     canvas.configure(scrollregion=canvas.bbox("all"))

# # canvas = Canvas(root, borderwidth=0, background="#ffffff")
# # frame = Frame(canvas, background="#ffffff")
# # vsb = Scrollbar(root, orient="vertical", command=canvas.yview)
# # canvas.configure(yscrollcommand=vsb.set)

# # vsb.pack(side="right", fill="y")
# # canvas.pack(side="left", fill="both", expand=True)
# # canvas.create_window((4,4), window=frame, anchor="nw")

# # frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

# # populate(frame)

# # root.mainloop()


















# import tkinter as tk
# from tkinter import ttk
# import math

# class ModernProgressBar(tk.Canvas):
#     """Modern progress bar with smooth animations and contemporary styling"""
    
#     def __init__(self, master, width=300, height=8, bg_color='#e8eaed', 
#                  progress_color='#4285f4', text_color='#5f6368', 
#                  show_text=True, show_percentage=False, corner_radius=None,
#                  animate_duration=300, **kwargs):
        
#         # Set default corner radius to half height for pill shape
#         if corner_radius is None:
#             corner_radius = height // 2
            
#         self.width = width
#         self.height = height
#         self.bg_color = bg_color
#         self.progress_color = progress_color
#         self.text_color = text_color
#         self.show_text = show_text
#         self.show_percentage = show_percentage
#         self.corner_radius = min(corner_radius, height // 2)  # Ensure valid radius
#         self.animate_duration = animate_duration
        
#         # Progress state
#         self.current_value = 0
#         self.max_value = 100
#         self.target_value = 0
#         self.animation_steps = 20
#         self.animation_step_delay = max(1, animate_duration // self.animation_steps)
        
#         # Animation state
#         self.animating = False
#         self.animation_id = None
        
#         super().__init__(master, width=width, height=height + (25 if show_text else 0), 
#                         highlightthickness=0, **kwargs)
        
#         self._draw_progress_bar()
    
#     def _create_rounded_rectangle(self, x1, y1, x2, y2, radius, **kwargs):
#         """Create a rounded rectangle on the canvas"""
#         points = []
        
#         # Ensure radius doesn't exceed half the width or height
#         radius = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
        
#         if radius <= 0:
#             # Fall back to regular rectangle
#             return self.create_rectangle(x1, y1, x2, y2, **kwargs)
        
#         # Create rounded rectangle using polygon
#         # Top edge
#         points.extend([x1 + radius, y1])
#         points.extend([x2 - radius, y1])
        
#         # Top-right corner
#         for i in range(5):
#             angle = i * math.pi / (2 * 4)  # 0 to π/2 in 5 steps
#             px = x2 - radius + radius * math.cos(angle)
#             py = y1 + radius - radius * math.sin(angle)
#             points.extend([px, py])
        
#         # Right edge
#         points.extend([x2, y1 + radius])
#         points.extend([x2, y2 - radius])
        
#         # Bottom-right corner
#         for i in range(5):
#             angle = i * math.pi / (2 * 4)  # 0 to π/2 in 5 steps
#             px = x2 - radius + radius * math.sin(angle)
#             py = y2 - radius + radius * math.cos(angle)
#             points.extend([px, py])
        
#         # Bottom edge
#         points.extend([x2 - radius, y2])
#         points.extend([x1 + radius, y2])
        
#         # Bottom-left corner
#         for i in range(5):
#             angle = i * math.pi / (2 * 4)  # 0 to π/2 in 5 steps
#             px = x1 + radius - radius * math.cos(angle)
#             py = y2 - radius + radius * math.sin(angle)
#             points.extend([px, py])
        
#         # Left edge
#         points.extend([x1, y2 - radius])
#         points.extend([x1, y1 + radius])
        
#         # Top-left corner
#         for i in range(5):
#             angle = i * math.pi / (2 * 4)  # 0 to π/2 in 5 steps
#             px = x1 + radius - radius * math.sin(angle)
#             py = y1 + radius - radius * math.cos(angle)
#             points.extend([px, py])
        
#         return self.create_polygon(points, smooth=True, **kwargs)
    
#     def _draw_progress_bar(self):
#         """Draw the progress bar"""
#         self.delete("all")
        
#         bar_y = 5 if self.show_text else 0
        
#         # Background bar
#         self._create_rounded_rectangle(
#             0, bar_y, self.width, bar_y + self.height,
#             self.corner_radius, fill=self.bg_color, outline=""
#         )
        
#         # Progress bar
#         if self.current_value > 0:
#             progress_width = max(1, (self.current_value / self.max_value) * self.width)
#             self._create_rounded_rectangle(
#                 0, bar_y, progress_width, bar_y + self.height,
#                 self.corner_radius, fill=self.progress_color, outline=""
#             )
        
#         # Text display
#         if self.show_text:
#             if self.show_percentage:
#                 percentage = (self.current_value / self.max_value) * 100
#                 text = f"{percentage:.0f}%"
#             else:
#                 text = f"{int(self.current_value)}/{int(self.max_value)}"
            
#             self.create_text(
#                 self.width // 2, bar_y + self.height + 12,
#                 text=text, fill=self.text_color,
#                 font=('Segoe UI', 9), anchor='center'
#             )
    
#     def _animate_step(self, step):
#         """Single animation step"""
#         if not self.animating or step >= self.animation_steps:
#             self.current_value = self.target_value
#             self.animating = False
#             self._draw_progress_bar()
#             return
        
#         # Smooth easing function (ease-out)
#         progress = step / self.animation_steps
#         eased_progress = 1 - (1 - progress) ** 3  # Cubic ease-out
        
#         start_value = self.current_value
#         value_diff = self.target_value - start_value
#         self.current_value = start_value + (value_diff * eased_progress)
        
#         self._draw_progress_bar()
        
#         # Schedule next step
#         self.animation_id = self.after(self.animation_step_delay, 
#                                      lambda: self._animate_step(step + 1))
    
#     def set_progress(self, value, animate=True):
#         """Set progress value (0 to max_value)"""
#         value = max(0, min(value, self.max_value))
        
#         if self.animation_id:
#             self.after_cancel(self.animation_id)
#             self.animation_id = None
        
#         if animate and abs(value - self.current_value) > 0.1:
#             self.target_value = value
#             self.animating = True
#             self._animate_step(0)
#         else:
#             self.current_value = value
#             self.target_value = value
#             self.animating = False
#             self._draw_progress_bar()
    
#     def set_max_value(self, max_value):
#         """Set maximum value"""
#         self.max_value = max(1, max_value)
#         self._draw_progress_bar()
    
#     def get_progress(self):
#         """Get current progress value"""
#         return self.current_value


# # Demo application
# class ProgressBarDemo:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.root.title("Modern Progress Bar Demo")
#         self.root.geometry("500x400")
#         self.root.configure(bg='#f8f9fa')
        
#         # Main frame
#         main_frame = tk.Frame(self.root, bg='#f8f9fa')
#         main_frame.pack(expand=True, fill='both', padx=30, pady=30)
        
#         # Title
#         title = tk.Label(main_frame, text="Modern Progress Bar Components", 
#                         font=('Segoe UI', 16, 'bold'), bg='#f8f9fa', fg='#202124')
#         title.pack(pady=(0, 30))
        
#         # Style 1: Default pill-shaped progress bar
#         self._create_demo_section(main_frame, "Default Style", 
#                                 show_text=True, show_percentage=False)
        
#         # Style 2: Percentage display
#         self._create_demo_section(main_frame, "With Percentage", 
#                                 show_text=True, show_percentage=True,
#                                 progress_color='#34a853')
        
#         # Style 3: Compact without text
#         self._create_demo_section(main_frame, "Compact Style", 
#                                 show_text=False, height=6,
#                                 progress_color='#ea4335')
        
#         # Style 4: Larger with custom colors
#         self._create_demo_section(main_frame, "Custom Theme", 
#                                 show_text=True, show_percentage=False,
#                                 height=12, progress_color='#9c27b0',
#                                 bg_color='#f3e5f5')
        
#         # Control buttons
#         self._create_controls(main_frame)
        
#     def _create_demo_section(self, parent, title, **progress_kwargs):
#         section_frame = tk.Frame(parent, bg='#f8f9fa')
#         section_frame.pack(fill='x', pady=10)
        
#         # Section title
#         label = tk.Label(section_frame, text=title, 
#                         font=('Segoe UI', 11, 'bold'), 
#                         bg='#f8f9fa', fg='#5f6368')
#         label.pack(anchor='w', pady=(0, 8))
        
#         # Progress bar
#         progress_bar = ModernProgressBar(section_frame, width=350, **progress_kwargs)
#         progress_bar.pack(anchor='w')
#         progress_bar.set_max_value(10)  # Simulate 10 images
#         progress_bar.set_progress(3)    # Currently on image 3
        
#         # Store reference for controls
#         if not hasattr(self, 'progress_bars'):
#             self.progress_bars = []
#         self.progress_bars.append(progress_bar)
    
#     def _create_controls(self, parent):
#         control_frame = tk.Frame(parent, bg='#f8f9fa')
#         control_frame.pack(fill='x', pady=(30, 0))
        
#         tk.Label(control_frame, text="Demo Controls:", 
#                 font=('Segoe UI', 11, 'bold'), 
#                 bg='#f8f9fa', fg='#202124').pack(anchor='w', pady=(0, 10))
        
#         button_frame = tk.Frame(control_frame, bg='#f8f9fa')
#         button_frame.pack(fill='x')
        
#         # Simulate different progress states
#         for i, (text, value) in enumerate([("Start", 1), ("Progress", 5), ("Almost Done", 8), ("Complete", 10)]):
#             btn = tk.Button(button_frame, text=f"{text} ({value}/10)",
#                            command=lambda v=value: self._update_all_progress(v),
#                            font=('Segoe UI', 10), relief='flat',
#                            bg='#4285f4', fg='white', padx=15, pady=8)
#             btn.pack(side='left', padx=(0, 10))
    
#     def _update_all_progress(self, value):
#         """Update all progress bars to simulate image navigation"""
#         for bar in self.progress_bars:
#             bar.set_progress(value, animate=True)
    
#     def run(self):
#         self.root.mainloop()


# if __name__ == "__main__":
# #     demo = ProgressBarDemo()
# #     demo.run()

#         import tkinter as tk
#         from tkinter import ttk
#         import time

#         def start_progress():
#                 progress['value'] = 0  # Reset progress
#                 root.update()
#                 for i in range(101):
#                         progress['value'] = i  # Update progress
#                         root.update()  # Refresh the GUI
#                         time.sleep(0.05)  # Simulate work
#                 start_button['state'] = 'normal'  # Re-enable button

#         root = tk.Tk()
#         root.title("Determinate Progress Bar")
#         root.geometry("300x100")

#         # Create progress bar
#         progress = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
#         progress.grid(row=0, column=0, padx=10, pady=20)

#         # Create start button
#         start_button = ttk.Button(root, text="Start", command=start_progress)
#         start_button.grid(row=1, column=0, padx=10, pady=10)

#         root.mainloop()
import os
print(__file__)

# print(os.path.abspath(__file__))


print(os.path.dirname(__file__))

print(os.path.dirname(os.path.dirname(__file__)))

print(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

print(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))


