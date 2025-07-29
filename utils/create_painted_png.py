import numpy as np
import os
import time
from PIL import Image
from utils.utilities import *
from utils.rectangle import *
import multiprocessing as mp
from multiprocessing import shared_memory

def find_output_height_width_scale(height, width, desired_length_of_longer_side):
    """
    Returns the new height and width of a resized image, preserving aspect ratio.
    Scale the longest side of original image to desired_length_of_longer_side pixels and scale the shorter side by the same scale factor to keep the same aspect ratio.

    Parameters:
        height (int): height of original image
        width (int): width of original image
        desired_length_of_longer_side (int): desired size of longer side of output image
    Returns:
        output_height (int): height of output
        output_width (int): width of output
        scale_factor (np.float32): scale factor from original image to output image
    """
    # case 1: Portrait
    if height > width:
        # scale height to desired_length_of_longer_side pixels
        output_height = desired_length_of_longer_side
        # find scaling factor from original to output
        scale_factor = desired_length_of_longer_side / height
        # scale width by same scale factor
        output_width = width * scale_factor
    # case 2: Landscape
    elif height <= width:
        # scale width to desired_length_of_longer_side pixels
        output_width = desired_length_of_longer_side
        # find scaling factor from original to output
        scale_factor = desired_length_of_longer_side / width
        # scale height by same scale factor
        output_height = height * scale_factor

    return int(output_height), int(output_width), np.float32(scale_factor)

def polygon_to_rect(vertices):
    """
    Converts a 4x2 array of polygon vertices back to rectangle parameters.
    
    Parameters:
        vertices (np.ndarray): A 4x2 array of (x, y) coordinates representing
                              the corners of a rotated rectangle in counter-clockwise
                              order starting from bottom-left.
    
    Returns:
        tuple: (x, y, h, w, theta) where:
            x (float): x center coordinate of rectangle
            y (float): y center coordinate of rectangle  
            h (float): height of rectangle
            w (float): width of rectangle
            theta (float): Angle of rotation in radians between -pi and pi
    """
    # Convert to float for calculations
    vertices = vertices.astype(np.float32)
    
    # Center is the average of all vertices
    x = np.mean(vertices[:, 0])
    y = np.mean(vertices[:, 1])
    
    # Get two adjacent edges to determine width, height, and rotation
    # Edge from vertex 0 to vertex 1 (bottom edge)
    edge1 = vertices[1] - vertices[0]
    # Edge from vertex 0 to vertex 3 (left edge)  
    edge2 = vertices[3] - vertices[0]
    
    # Width is length of bottom edge, height is length of left edge
    w = np.linalg.norm(edge1)
    h = np.linalg.norm(edge2)
    
    # Rotation angle is the angle of the bottom edge
    theta = np.arctan2(edge1[1], edge1[0])
    
    # Ensure theta is in [-pi, pi] range
    theta = np.arctan2(np.sin(theta), np.cos(theta))
    
    return x, y, h, w, theta


# Old function logic before multiprocessing version was implemented
# def create_output_rgba(texture_dict, best_rect_list_of_dict, original_height, original_width, desired_length_of_longer_side, target_rgba):
#     """
#     Using the optimal rectangle and their corresponding texture and rgb, recreate the canvas in a better quality than the scoring canvas
    

#     Parameters:
#         vertices (np.ndarray): 
    
#     Returns:
#         tuple: (x, y, h, w, theta) 
#     """
#     print("Creating output image...")
#     start_time = time.time()
#     # 1) Find the height and width of output canvas and corresponding scale factor from original to output image
#     output_height, output_width, scale_factor = find_output_height_width_scale(original_height, original_width, desired_length_of_longer_side)

#     # 2) Create normalized rgba blank canvas that is fully opaque of size (output_height, output_width, 4). All rgb values of blank canvas is the average rgb color of the target image
#     output_rgba = np.ones((output_height, output_width, 4), dtype=np.float32)
#     average_rgb = get_average_rgb_of_rgba_image(target_rgba)
#     output_rgba[:,:,0:3] *= average_rgb

#     # 3) Loop through each rect and texture in best_rect_with_texture
#     for rect_texture_rgb_dict in best_rect_list_of_dict:
#         # 3) Get the [x,y,h,w,theta] representation of the best rectangle and its rgb color
#         best_rect_list = rect_texture_rgb_dict["best_rect_list"] # [x,y,h,w,theta]
#         rgb = rect_texture_rgb_dict["rgb"] # length 3 np.float32 np array

#         # 4) Get texture greyscale_alpha
#         texture_key = rect_texture_rgb_dict["texture_key"] # 0,1,2...
#         texture_greyscale_alpha = texture_dict[texture_key]["texture_greyscale_alpha"] # (h,w,2) np array

#         # 5) Find rectangle vertices in the output space using linear transformation (scaling at origin)
#         original_vertices = rectangle_to_polygon(*best_rect_list)
#         output_rect_vertices = (original_vertices * scale_factor).astype(np.int32)

#         # 6) Find the [x,y,h,w,theta] representation of output_rect_vertices
#         output_rect_list = polygon_to_rect(output_rect_vertices)

#         # 7) Find the ymin and scanline xintersects of rectangle constrained to output image height and width
#         y_min, y_max, scanline_x_intersects_array = get_y_index_bounds_and_scanline_x_intersects(output_rect_vertices, output_height, output_width)

#         # 8) Draw the rectangle onto output_rgba
#         draw_texture_on_canvas(texture_greyscale_alpha, output_rgba, scanline_x_intersects_array, y_min, rgb, *output_rect_list)
#     end_time = time.time()
#     elapsed_time = end_time - start_time
#     print(f"Time taken to create output image: {elapsed_time:.6f} seconds")
#     return output_rgba

class CreateOutputImage:
    def __init__(self, texture_dict, original_height, original_width, desired_length_of_longer_side, target_rgba, use_worker_process=True):
        self.texture_dict = texture_dict
        self.target_rgba = target_rgba
        self.output_height, self.output_width, self.scale_factor = find_output_height_width_scale(
            original_height, original_width, desired_length_of_longer_side)
        self.average_rgb = get_average_rgb_of_rgba_image(target_rgba)
        self.use_worker_process = use_worker_process
        if use_worker_process:
            self.queue = mp.Queue()
            self.sentinel = "__DONE__"
            # Shared memory for output_rgba
            self.shm = shared_memory.SharedMemory(create=True, size=self.output_height * self.output_width * 4 * np.float32().nbytes)
            self.output_rgba = np.ndarray((self.output_height, self.output_width, 4), dtype=np.float32, buffer=self.shm.buf)
            self.output_rgba[:] = 1.0
            self.output_rgba[:, :, 0:3] *= self.average_rgb
            self.output_rgba[:, :, 3] = 1.0
            self.worker_process = mp.Process(target=self.worker, args=(self.queue, self.shm.name, self.output_rgba.shape, self.output_rgba.dtype, self.texture_dict, self.scale_factor, self.sentinel))
            self.worker_process.start()
        else:
            # Synchronous mode: accumulate jobs in a list
            self.jobs = []
            self.output_rgba = np.ones((self.output_height, self.output_width, 4), dtype=np.float32)
            self.output_rgba[:, :, 0:3] *= self.average_rgb
            self.output_rgba[:, :, 3] = 1.0

    def enqueue(self, rect_texture_rgb_dict):
        if self.use_worker_process:
            self.queue.put(rect_texture_rgb_dict)
        else:
            self.jobs.append(rect_texture_rgb_dict)

    def finish(self):
        if self.use_worker_process:
            self.queue.put(self.sentinel)
            self.worker_process.join()
            # Copy the result out of shared memory before closing
            result = np.copy(self.output_rgba)
            self.shm.close()
            self.shm.unlink()
            return result
        else:
            # Synchronous: process all jobs in this process
            for job in self.jobs:
                best_rect_list = job["best_rect_list"]
                rgb = job["rgb"]
                texture_key = job["texture_key"]
                texture_greyscale_alpha = self.texture_dict[texture_key]["texture_greyscale_alpha"]
                original_vertices = rectangle_to_polygon(*best_rect_list)
                output_rect_vertices = (original_vertices * self.scale_factor).astype(np.int32)
                output_rect_list = polygon_to_rect(output_rect_vertices)
                y_min, y_max, scanline_x_intersects_array = get_y_index_bounds_and_scanline_x_intersects(
                    output_rect_vertices, self.output_height, self.output_width)
                draw_texture_on_canvas(texture_greyscale_alpha, self.output_rgba, scanline_x_intersects_array, y_min, rgb, *output_rect_list)
            return self.output_rgba

    @staticmethod
    def worker(queue, shm_name, shape, dtype, texture_dict, scale_factor, sentinel):
        # Attach to shared memory
        shm = shared_memory.SharedMemory(name=shm_name)
        output_rgba = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
        while True:
            # example job: {"best_rect_list":best_rect_list, "texture_key": texture_key, "rgb": rgb_of_best_rect}
            job = queue.get()
            if job == sentinel:
                break
            # Unpack job
            best_rect_list = job["best_rect_list"]
            rgb = job["rgb"]
            texture_key = job["texture_key"]
            texture_greyscale_alpha = texture_dict[texture_key]["texture_greyscale_alpha"]
            # Find rectangle vertices in the output space using linear transformation (scaling at origin)
            original_vertices = rectangle_to_polygon(*best_rect_list)
            output_rect_vertices = (original_vertices * scale_factor).astype(np.int32)
            # Find the [x,y,h,w,theta] representation of output_rect_vertices
            output_rect_list = polygon_to_rect(output_rect_vertices)
            # Find the ymin and scanline xintersects of rectangle constrained to output image height and width
            y_min, y_max, scanline_x_intersects_array = get_y_index_bounds_and_scanline_x_intersects(
                output_rect_vertices, shape[0], shape[1])
            # Draw onto shared output_rgba
            draw_texture_on_canvas(texture_greyscale_alpha, output_rgba, scanline_x_intersects_array, y_min, rgb, *output_rect_list)
        shm.close()


