import numpy as np
from matplotlib import pyplot as plt

from utilities import *

















shortest_side_px = 200

if __name__ == "__main__":

    target_image_filepath = "target_image/die.png"
    target_rgba = import_image_as_rgba(target_image_filepath)
    # print_image_array(target_rgba)

    texture_greyscale_alpha = import_image_as_greyscale_alpha(target_image_filepath)
    # print_image_array(texture_image)

    target_height, target_width = get_height_width_of_array(target_rgba)
    #print(target_height, target_width)

    # current is blank white opaque canvas
    current = create_white_canvas(target_height, target_width, shortest_side_px)
    # print_image_array(canvas)
