import time
from utils.rectangle import *
from utils.utilities import *

def warmup_numba():
    print("Warming up numba functions")
    start = time.time()
    clamp_int(1, 1, 1)
    rectangle = [1,1,2,2,0]
    vertices, canvas_height, canvas_width= rectangle_to_polygon(1,1, np.float32(2), np.float32(2), np.float32(0)),10,10
    target_rgba, texture_greyscale_alpha = np.ones((10,10,4), dtype = np.float32), np.ones((10,10,4), dtype = np.float32)
    current_rgba = np.ones(target_rgba.shape, dtype=np.float32)
    poly_y_min, y_max_clamped, scanline_x_intersects_array = get_y_index_bounds_and_scanline_x_intersects(vertices, canvas_height, canvas_width)
    rgb_avg = get_average_rgb_value(target_rgba, texture_greyscale_alpha, scanline_x_intersects_array, poly_y_min, *rectangle)
    get_score_of_rectangle(target_rgba, texture_greyscale_alpha, current_rgba, scanline_x_intersects_array, poly_y_min,
                           rgb_avg, *rectangle)

    draw_texture_on_canvas(texture_greyscale_alpha, current_rgba, scanline_x_intersects_array, poly_y_min, rgb_avg,
                           *rectangle)
    end = time.time()
    print(f"Time taken for numba warmup: {end - start:.4f} seconds")