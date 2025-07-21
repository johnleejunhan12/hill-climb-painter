import tkinter as tk
from tkinter_components import RangeSlider, SingleSlider, CustomTextInput

root = tk.Tk()
root.title('Slider Height Test')
root.geometry('400x1000')

# RangeSlider with specified height=200, blue background
slider_blue = RangeSlider(root, min_val=0, max_val=100, init_min=20, init_max=80, height=200, bg_color='blue', title='Blue: height=200', show_value_labels=True)
slider_blue.pack(fill='x', padx=20, pady=(10,0))

# RangeSlider without specified height, red background
slider_red = RangeSlider(root, min_val=0, max_val=100, init_min=30, init_max=70, bg_color='red', title='Red: auto height', show_value_labels=True)
slider_red.pack(fill='x', padx=20, pady=(10,30))

# SingleSlider with specified height=150, green background
single_green = SingleSlider(root, min_val=0, max_val=100, init_val=50, height=150, bg_color='green', title='Green: height=150', show_value_labels=True)
single_green.pack(fill='x', padx=20, pady=(10,0))

# SingleSlider without specified height, orange background
single_orange = SingleSlider(root, min_val=0, max_val=100, init_val=75, bg_color='orange', title='Orange: auto height', show_value_labels=True)
single_orange.pack(fill='x', padx=20, pady=(10,30))

# CustomTextInput with multi-line title and subtitle (auto height)
text_input_multiline = CustomTextInput(
    root,
    title='Multi-line Title\nSecond Line',
    subtitle='Multi-line Subtitle\nAnother line',
    width=350,
    bg_color='grey'
)
text_input_multiline.pack(fill='x', padx=20, pady=(10,0))

# CustomTextInput with single-line title, no subtitle (auto height)
text_input_single = CustomTextInput(
    root,
    title='Single-line Title',
    width=350,
    bg_color='yellow'
)
text_input_single.pack(fill='x', padx=20, pady=(10,0))

root.mainloop()
