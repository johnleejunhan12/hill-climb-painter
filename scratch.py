
        # # 1) Computation size (done)
        # self.i_computation_size = get_value("computation_size", assert_type=int)
        # self.i_computation_size_min_value = get_value("computation_size", "min_value", assert_type=int)
        # self.i_computation_size_max_value = get_value("computation_size", "max_value", assert_type=int)

        # # 2) Add how many textures (done)
        # self.i_num_textures = get_value("num_textures", assert_type=int)
        # self.i_num_textures_min_value = get_value("num_textures", "min_value", assert_type=int)
        # self.i_num_textures_max_value = get_value("num_textures", "max_value", assert_type=int)

        # # 3) Number of hill climb iterations (done)
        # self.i_num_hill_climb_iterations_current_lower_value = get_value("num_hill_climb_iterations", "current_lower_value", assert_type=int)
        # self.i_num_hill_climb_iterations_current_upper_value = get_value("num_hill_climb_iterations", "current_upper_value", assert_type=int)
        # self.i_num_hill_climb_iterations_min_value = get_value("num_hill_climb_iterations", "min_value", assert_type=int)
        # self.i_num_hill_climb_iterations_max_value = get_value("num_hill_climb_iterations", "max_value", assert_type=int)

        # # 4) Texture opacity settings (done)
        # self.i_texture_opacity = get_value("texture_opacity", assert_type=int)
        # self.i_texture_opacity_min_value = get_value("texture_opacity", "min_value", assert_type=int)
        # self.i_texture_opacity_max_value = get_value("texture_opacity", "max_value", assert_type=int)

        # # 5) Initial texture width (done)
        # self.i_initial_texture_width = get_value("initial_texture_width", assert_type=int)
        # self.i_initial_texture_width_min_value = get_value("initial_texture_width", "min_value", assert_type=int)
        # self.i_initial_texture_width_max_value = get_value("initial_texture_width", "max_value", assert_type=int)

        # # 6) Fix size of texture (done)
        # self.i_uniform_texture_size_bool = get_value("uniform_texture_size", assert_type=bool)

        # # 8) allow early termination of hill climb (done)
        # self.i_allow_early_termination_bool = get_value("allow_early_termination", assert_type=bool)
        # # 8a) Terminate after n iterations (done)
        # self.i_failed_iterations_threshold = get_value("failed_iterations_threshold", assert_type=int)
        # self.i_failed_iterations_threshold_min_value = get_value("failed_iterations_threshold", "min_value", assert_type=int)
        # self.i_failed_iterations_threshold_max_value = get_value("failed_iterations_threshold", "max_value", assert_type=int)

        # # 9) Enable vector field (done)
        # self.i_enable_vector_field_bool = get_value("enable_vector_field", assert_type=bool)

        # 9.i) Edit vector field and # 9.ii) Shift vector field origin buttons
        self.i_vector_field_f_string = get_value("vector_field_f", assert_type=str)
        self.i_vector_field_g_string = get_value("vector_field_g", assert_type=str)
        

        # (done)
        # self.i_vector_field_origin_shift_list_of_tuples = get_value("vector_field_origin_shift", assert_type=list)


        # # (done)
        # # 7) Show painting progress as new textures are added
        # self.i_display_painting_progress_bool = get_value("display_painting_progress", assert_type=bool)
        # # 7a) Show improvement of individual textures
        # self.i_display_placement_progress_bool = get_value("display_placement_progress", assert_type=bool)
        # # 7b) Display final image after painting (conditional)
        # self.i_display_final_image_bool = get_value("display_final_image", assert_type=bool)




        # Output tab initial parameters

        # # 1) Output image size (done)
        # self.i_output_image_size = get_value("output_image_size", assert_type=int)
        # self.i_output_image_size_min_value = get_value("output_image_size", "min_value", assert_type=int)
        # self.i_output_image_size_max_value = get_value("output_image_size", "max_value", assert_type=int)

        # # 2) Output image name (done)
        # self.i_output_image_name_string = get_value("output_image_name", assert_type=str)

        # # 3) Create gif of painting progress checkbox (done)
        # self.i_create_gif_of_painting_progress_bool = get_value("create_gif_of_painting_progress", assert_type=bool)
        # # 3i) Name of painting progress gif (done)
        # self.i_name_of_painting_progress_gif_string = get_value("gif_output_name", assert_type=str)

        # tab2 GIF Settings (for target with .gif)

        # # (Done)
        # # A) Name of painted gif (a new gif where we paint all frames of target gif)
        # self.i_painted_gif_name_string = get_value("painted_gif_name", assert_type=str)
        # # B) Multiprocessing checkbox
        # self.i_enable_multiprocessing_bool = get_value("enable_multiprocessing", assert_type=bool)





















# from tkinter import *
# from tkinter import font

# root = Tk()
# root.title('Font Families')
# fonts=list(font.families())
# fonts.sort()

# def populate(frame):
#     '''Put in the fonts'''
#     listnumber = 1
#     for i, item in enumerate(fonts):
#         label = "listlabel" + str(listnumber)
#         label = Label(frame,text=item,font=(item, 16))
#         label.grid(row=i)
#         label.bind("<Button-1>",lambda e,item=item:copy_to_clipboard(item))
#         listnumber += 1

# def copy_to_clipboard(item):
#     root.clipboard_clear()
#     root.clipboard_append("font=('" + item.lstrip('@') + "', 12)")

# def onFrameConfigure(canvas):
#     '''Reset the scroll region to encompass the inner frame'''
#     canvas.configure(scrollregion=canvas.bbox("all"))

# canvas = Canvas(root, borderwidth=0, background="#ffffff")
# frame = Frame(canvas, background="#ffffff")
# vsb = Scrollbar(root, orient="vertical", command=canvas.yview)
# canvas.configure(yscrollcommand=vsb.set)

# vsb.pack(side="right", fill="y")
# canvas.pack(side="left", fill="both", expand=True)
# canvas.create_window((4,4), window=frame, anchor="nw")

# frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

# populate(frame)

# root.mainloop()