import numpy as np
import numba as nb
from numba import prange
import matplotlib.pyplot as plt
from utilities import clamp_int


def create_random_rectangle(canvas_height, canvas_width, texture_height, texture_width, vector_field, custom_rectangle_width=200):
    """
    Creates a random rectangle with its center located at a random integer pixel index within the canvas.
    The rectangle maintains the same aspect ratio as the given texture, with its width fixed at 20 pixels.
    The rectangle is also randomly rotated by an angle theta in radians, uniformly sampled from [-π, π).

    Parameters:
        canvas_height (int): Height of the canvas in pixels.
        canvas_width (int): Width of the canvas in pixels.
        texture_height (int): Height of the reference texture in pixels.
        texture_width (int): Width of the reference texture in pixels.
        vector_field (VectorField): A vector field that maps (x,y) coordinate to theta radians in range [-pi,pi]
        custom_rectangle_width (int): Optional parameter to specify the width of randomly generated rectangle

    Returns:
        rectangle (list): A list containing:
            - x (int): Horizontal pixel index of the rectangle center (0 ≤ x < canvas_width).
            - y (int): Vertical pixel index of the rectangle center (0 ≤ y < canvas_height).
            - rect_height (float): Height of the rectangle, scaled to preserve texture aspect ratio.
            - rect_width (float): Fixed width of the rectangle (50.0).
            - theta (float): Rotation angle in radians, uniformly sampled from [-π, π).
    """

    rect_width = custom_rectangle_width
    # Maintain aspect ratio from texture
    aspect_ratio = texture_height / texture_width
    rect_height = rect_width * aspect_ratio

    # Random integer center positions (0 to size-1)
    x = np.random.randint(0, canvas_width)
    y = np.random.randint(0, canvas_height)

    if vector_field.is_enabled:
        # Get theta from vector field
        theta = vector_field.get_vector_field_theta(x, y)
    else:
        # Random angle in radians between -π and π
        theta = np.random.uniform(-np.pi, np.pi)

    return [x, y, rect_height, rect_width, theta]

def get_mutated_rectangle_copy(rectangle, canvas_height, canvas_width, vector_field, is_scaling_allowed):
    """
    Takes in a rectangle and returns a mutated copy of it.
    One of three mutation cases is randomly applied with equal probability:

    Case 1: Mutate center x and y by a small integer amount, clamped to canvas bounds.
    Case 2: Scale both rect_height and rect_width by the same factor.
    Case 3: Adjust theta by a random radian between -pi and pi, clamped to [-pi, pi].

    Parameters:
        rectangle (list): [x(int), y(int), rect_height(float), rect_width(float), theta(float)]
        canvas_height (int): Height of the canvas in pixels.
        canvas_width (int): Width of the canvas in pixels.
        vector_field (VectorField): A vector field that maps (x,y) coordinate to theta radians in range [-pi,pi]
        is_scaling_allowed (Boolean): Flag to determine if the height and width should be mutated

    Returns:
        mutated_rectangle (list): A mutated copy of the input rectangle.
    """
    x, y, rect_height, rect_width, theta = rectangle
    mutated = [x, y, rect_height, rect_width, theta]  # copy

    is_vector_field_enabled = vector_field.is_enabled

    if is_vector_field_enabled: # Dont need to rotate randomly as the vector field outputs theta given (x,y)
        mutation_operation_case = [1]
    else:
        mutation_operation_case = [1,3]

    if is_scaling_allowed:
        mutation_operation_case.append(2)

    case = np.random.choice(mutation_operation_case)
        
    if case == 1:
        # Case 1: Mutate x and y
        dx = np.random.randint(-100, 100)
        dy = np.random.randint(-100, 100)
        mutated[0] = clamp_int(x + dx, 0, canvas_width - 1)
        mutated[1] = clamp_int(y + dy, 0, canvas_height - 1)

        # if vector field is enabled, need to find the new theta after doing the random translation
        if is_vector_field_enabled:
            mutated[4] = vector_field.get_vector_field_theta(mutated[0], mutated[1])

    elif case == 2:
        # Case 2: Scale height and width
        scale = np.random.uniform(0.5, 1.5)
        mutated[2] = rect_height * scale
        mutated[3] = rect_width * scale

    elif case == 3: # Case 3: Do rotation
        dtheta = np.random.uniform(-np.pi, np.pi)
        new_theta = theta + dtheta
        # Wrap angle to [-π, π]
        new_theta = (new_theta + np.pi) % (2 * np.pi) - np.pi
        mutated[4] = new_theta

    return mutated


@nb.njit(fastmath=True, cache=True)
def rectangle_to_polygon(x, y, h, w, theta):
    """
    Converts a rectangle specified by x, y, rect_height, rect_width, theta into a 4x2 array of (x, y)
    polygon vertices, accounting for rotation. Vertices are returned as np.int32.

    Parameters:
        x (int): x center coordinate of rectangle
        y (int): y center coordinate of rectangle
        h (np.float32): height of rectangle
        w (np.float32): width of rectangle
        theta (np.float32): Angle of rotation between -pi and pi radians inclusive

    Returns:
        vertices (np.ndarray): A 4x2 array of integer (x, y) coordinates (dtype=np.int32)
                               representing the corners of the rotated rectangle.
    """

    dx = w / 2.0
    dy = h / 2.0

    # Define corners (counter-clockwise from bottom-left)
    corners = np.empty((4, 2), dtype=np.float32)
    corners[0, :] = (-dx, -dy)
    corners[1, :] = ( dx, -dy)
    corners[2, :] = ( dx,  dy)
    corners[3, :] = (-dx,  dy)

    # Precompute sin and cos
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    # Rotate and translate
    result = np.empty((4, 2), dtype=np.int32)
    for i in range(4):
        cx, cy = corners[i]
        rx = cos_theta * cx - sin_theta * cy
        ry = sin_theta * cx + cos_theta * cy
        result[i, 0] = int(np.round(rx + x))
        result[i, 1] = int(np.round(ry + y))

    return result


def display_rectangle_vertices_debug(vertices, title="Rectangle"):
    """
    Displays a rectangle given its 4x2 array of (x, y) vertices.

    Parameters:
        vertices (np.ndarray): A 4x2 NumPy array of vertex coordinates.
        title (str): Title of the plot.
    """
    if not isinstance(vertices, np.ndarray) or vertices.shape != (4, 2):
        raise ValueError("vertices must be a 4x2 NumPy array")

    # Close the loop for the polygon by appending the first point again
    closed_vertices = np.vstack([vertices, vertices[0]])

    # Separate x and y coordinates
    xs, ys = closed_vertices[:, 0], closed_vertices[:, 1]

    # Plotting
    plt.figure(figsize=(5, 5))
    plt.plot(xs, ys, marker='o', linestyle='-', color='blue')
    plt.fill(xs, ys, alpha=0.2, color='blue')  # optional: filled polygon
    plt.scatter(xs[:-1], ys[:-1], color='red')  # highlight original 4 vertices
    for i, (x, y) in enumerate(vertices):
        plt.text(x + 1, y + 1, f'P{i}', fontsize=9)

    plt.title(title)
    plt.axis('equal')
    plt.gca().invert_yaxis()  # Flip the y-axis downward
    plt.grid(True)
    plt.xlabel("x")
    plt.ylabel("y")
    plt.show()




@nb.njit(cache=True)
def get_y_index_bounds_and_scanline_x_intersects(vertices, canvas_height, canvas_width):
    """
    Finds pairs of (left, right) x intersects for each scanline passing through 2 edges

    Parameters:
        vertices (np.ndarray): A 4x2 NumPy array of vertex coordinates of type np.int32
        canvas_height (int): Pixel height of canvas
        canvas_width (int): Pixel width of canvas
    Returns:
        y_min (int): Minimum y integer coordinate of the polygon, bounded by canvas index
        y_max (int): Maximum y integer coordinate of the polygon, bounded by canvas index
        x_intersects (np.ndarray): np.int32 NumPy array of size (y_max_clamped - y_min_clamped + 1, 2)
    """
    num_vertices = vertices.shape[0]

    # find y_min and y_max
    y_min = vertices[0, 1]
    y_max = vertices[0, 1]
    for i in range(1, num_vertices):
        y = vertices[i, 1]
        y_min = min(y_min, y)
        y_max = max(y_max, y)


    # clamp y_min and y_max
    y_min_clamped = clamp_int(y_min, 0, canvas_height - 1)
    y_max_clamped = clamp_int(y_max, 0, canvas_height - 1)


    # Find the number of scanlines required (same as the number of possible pairs of x_intersects)
    num_scanlines = y_max_clamped - y_min_clamped + 1


    # Initialize numpy array to hold x intersects pairs for all possible scanlines
    # Note that the scanline algorithm may not detect any intersects in corner cases, so denote missing or out of bounds x intersect left and right as (-1,-1)
    x_intersects = np.full((num_scanlines, 2), -1, dtype=np.int32)
    array_index = 0
    # For each scanline...
    for y_scanline_index in range(y_min_clamped, y_max_clamped + 1):
        # Initialize counter for number of intersections as well as index from 0 to 1
        intersect_count = 0
        # Initialize counters for number of intersections that are out of canvas boundary
        count_negative_x_intersection = 0
        count_exceed_boundary_x_intersection = 0

        # For all edges of polygon...
        for source_index in range(num_vertices):
            # Find y coordinate of source vertex and dest vertex
            dest_index = (source_index + 1) % num_vertices
            y_source = vertices[source_index, 1]
            y_dest = vertices[dest_index, 1]
            # Check if the edge intersects scanline
            if (y_source < y_scanline_index <= y_dest) or (y_dest < y_scanline_index <= y_source):
                if y_source == y_dest:
                    # Corner case where edge is horizontal, scanline and edge are collinear
                    # Let the intersection happen at the source vertex
                    x_intersect = vertices[source_index, 0]
                else:
                    # Calculate the approximate integer x-coordinate of the intersection
                    x_intersect = vertices[source_index, 0] + (vertices[dest_index, 0] - vertices[source_index, 0]) * (y_scanline_index - y_source) // (y_dest - y_source)

                # Increment counters if any type of out of bounds intersection are found
                if x_intersect < 0:
                    count_negative_x_intersection += 1
                elif x_intersect >= canvas_width:
                    count_exceed_boundary_x_intersection += 1

                # Store the clamped intersection
                x_intersects[array_index, intersect_count] = clamp_int(x_intersect, 0, canvas_width - 1)
                # Increment count of intersections
                intersect_count += 1

            # Exit loop after finding 2 intersections
            if intersect_count == 2:
                break

        # If both intersections are out of bounds, denote left and right intersection as (-1,-1)
        if count_negative_x_intersection == 2 or count_exceed_boundary_x_intersection == 2:
            x_intersects[array_index, 0] = -1
            x_intersects[array_index, 1] = -1
            continue

        # sort the x intersection from left to right
        if x_intersects[array_index, 0] > x_intersects[array_index, 1]:
            temp = x_intersects[array_index, 0]
            x_intersects[array_index, 0] = x_intersects[array_index, 1]
            x_intersects[array_index, 1] = temp

        array_index += 1

    return y_min_clamped, y_max_clamped, x_intersects



# Helper functions for larger get_average_rgb_value, get_score_of_rectangle and draw_texture_on_canvas functions
@nb.njit(cache=True, fastmath=True)
def transform_rect_texture_coordinate(x, y, rect_x_center, rect_y_center, rect_height, rect_width, rect_theta, 
                                      texture_width, texture_height):
    """
    Transforms canvas coordinates to texture coordinates for a rotated, scaled rectangle.

    This function performs an inverse geometric transformation to map a point from the canvas
    coordinate system to the corresponding point in the texture coordinate system. The
    transformation accounts for the rectangle's position, rotation, and scaling relative
    to the texture.

    The transformation process:
    1. Translate canvas point to align rectangle center with origin
    2. Rotate by negative theta (inverse rotation) to undo rectangle rotation
    3. Scale by inverse scaling factors to map from rectangle size to texture size
    4. Translate to texture center coordinates

    This allows sampling the texture at the correct location that corresponds to each
    pixel position within the transformed rectangle on the canvas.

    Parameters:
        x (int):
            Canvas x coordinate to transform
        y (int):
            Canvas y coordinate to transform
        rect_x_center (int):
            x coordinate/index of rectangle center
        rect_y_center (int):
            y coordinate/index of rectangle center
        rect_height (np.float32):
            height of rectangle in pixels
        rect_width (np.float32):
            width of rectangle in pixels
        rect_theta (np.float32):
            radian rotation of rectangle in range [-pi, pi]
        texture_width (int):
            width of the texture in pixels
        texture_height (int):
            height of the texture in pixels

    Returns:
        tuple[np.float32, np.float32]:
            new_x, new_y - Transformed coordinates in texture space
    """
    # Calculate inverse scale factors to map from rectangle size back to texture size
    rect_reverse_scale_x = texture_width / rect_width
    rect_reverse_scale_y = texture_height / rect_height

    # 1) Translate by (-rect_x_center, -rect_y_center) to align rectangle center with origin
    translated_x = x - rect_x_center
    translated_y = y - rect_y_center

    # 2) Rotate about origin by -rect_theta radians (inverse rotation matrix)
    rotated_x = translated_x * np.cos(rect_theta) + translated_y * np.sin(rect_theta)
    rotated_y = -translated_x * np.sin(rect_theta) + translated_y * np.cos(rect_theta)

    # 3) Scale by inverse scale factors to map from rectangle dimensions to texture dimensions
    scaled_x = rotated_x * rect_reverse_scale_x
    scaled_y = rotated_y * rect_reverse_scale_y

    # 4) Translate to texture center coordinates
    new_x = np.float32(scaled_x + (texture_width / 2))
    new_y = np.float32(scaled_y + (texture_height / 2))

    return new_x, new_y

@nb.njit(cache=True)
def bi_linear_interpolation_in_texture_space(x_floating, y_floating, texture_greyscale_alpha, channel):
    """
    Performs bilinear interpolation to sample a texture at floating-point coordinates.

    This function calculates the interpolated intensity value for a specific channel at
    non-integer coordinates by computing a weighted average of the four surrounding pixel
    values. This is essential for smooth texture sampling when geometric transformations
    result in floating-point texture coordinates.

    The bilinear interpolation process:
    1. Identifies the four integer pixel coordinates that surround the floating-point location
    2. Extracts intensity values for the specified channel from these four pixels
    3. Performs linear interpolation along the x-axis for both top and bottom pixel pairs
    4. Performs linear interpolation along the y-axis between the two x-interpolated values

    Parameters:
        x_floating (np.float32):
            Floating x coordinate in texture space
        y_floating (np.float32):
            Floating y coordinate in texture space
        texture_greyscale_alpha (np.ndarray):
            Array of shape (H, W, 2) representing normalised grayscale and alpha, dtype np.float32.
        channel (int):
            index of channel, 0 is greyscale, 1 is alpha

    Returns:
        weighted_avg_intensity (np.float32):
            Interpolated intensity of 4 surrounding pixels for the specified channel.
    """
    
    # 1) Find the (x,y) coordinates of the 4 pixels surrounding the floating point coordinate (x_floating, y_floating)
    top_left_x, top_left_y = np.int32(np.floor(x_floating)), np.int32(np.floor(y_floating))
    bottom_left_x, bottom_left_y = top_left_x, top_left_y + 1
    top_right_x, top_right_y = top_left_x + 1, top_left_y
    bottom_right_x, bottom_right_y = top_left_x + 1, top_left_y + 1

    # 2) Find the weighted intensity of the channel
    # i) get intensity of 4 corners
    top_left_intensity, top_right_intensity = texture_greyscale_alpha[top_left_y, top_left_x, channel], \
        texture_greyscale_alpha[top_right_y, top_right_x, channel]
    bottom_left_intensity, bottom_right_intensity = texture_greyscale_alpha[bottom_left_y, bottom_left_x, channel], \
        texture_greyscale_alpha[bottom_right_y, bottom_right_x, channel]

    # ii) Get weighted intensity for top and bottom pixels along x-axis
    weight_left, weight_right = x_floating - top_left_x, top_right_x - x_floating
    weighted_avg_top = top_left_intensity * weight_left + top_right_intensity * weight_right
    weighted_avg_bottom = bottom_left_intensity * weight_left + bottom_right_intensity * weight_right

    # iii) Get weighted intensity along y-axis
    weight_top, weight_bottom = y_floating - top_left_y, bottom_left_y - y_floating
    weighted_avg_intensity = np.float32(weighted_avg_top * weight_top + weighted_avg_bottom * weight_bottom)

    return weighted_avg_intensity

@nb.njit(cache=True)
def alpha_blend(foreground_rgb, foreground_alpha, background_rgb, background_alpha):
    """
    Blends foreground pixel over background pixel using straight alpha blending

    Parameters:
        foreground_rgb (np.ndarray):
            length 3 numpy array containing normalized rgb values, dtype np.float32.
        foreground_alpha (np.float32):
            alpha of foreground
        background_rgb (np.ndarray):
            length 3 numpy array containing normalized rgb values, dtype np.float32.
        background_alpha (np.float32):
            alpha of background
    Returns
        resultant_rgb (np.ndarray):
            length 3 numpy array containing normalized rgb values, dtype np.float32.
        resultant_alpha (np.float32):
            alpha of blended pixel
    """
    resultant_alpha = foreground_alpha + background_alpha * (1 - foreground_alpha)
    if resultant_alpha == 0:
        resultant_rgb = background_rgb
    else:
        resultant_rgb = ((foreground_rgb * foreground_alpha + background_rgb * background_alpha * (
                    1 - foreground_alpha)) / resultant_alpha).astype(np.float32)

    return resultant_rgb, resultant_alpha


@nb.njit(cache=True)
def get_average_rgb_value(target_rgba, texture_greyscale_alpha, scanline_x_intersects_array, poly_y_min,
                          rect_x_center, rect_y_center, rect_height, rect_width, rect_theta):
    """
    Projects a grayscale-alpha texture onto a specified rotated rectangle region of a target image
    and computes the average RGB color of target pixels where the texture's projected alpha exceeds a threshold.

    The function transforms each pixel within the scanline-filled rectangular region of the target image
    back into texture space using inverse geometric transformations (translation, rotation, scaling),
    then samples the alpha value of the corresponding texture pixel via bi-linear interpolation.
    If the interpolated alpha exceeds 0.2, the corresponding RGB value in the target image is considered
    significant and accumulated. The function returns the normalized average RGB color over all such pixels.

    Parameters:
        target_rgba (np.ndarray):
            Normalized RGBA image of shape (H, W, 4), dtype np.float32.

        texture_greyscale_alpha (np.ndarray):
            Array of shape (H, W, 2) representing grayscale and alpha, dtype np.float32.

        scanline_x_intersects_array (np.ndarray):
            np.int32 NumPy array of size (y_max_clamped - y_min_clamped + 1, 2)

        poly_y_min (int):
            index of clamped y index of polygon within boundary of canvas

        rect_x_center (int):
            x coordinate/index of rectangle center

        rect_y_center (int):
            y coordinate/index of rectangle center

        rect_height (np.float32):
            height of rectangle in pixels

        rect_width (np.float32):
            width of rectangle in pixels

        rect_theta (np.float32)
            radian rotation of rectangle in range [-pi, pi]

    Returns:
        average_rgb (np.array):
            Length 3 dtype np.float32 array containing normalized rgb values
    """

    # Get height and width of texture
    texture_height, texture_width = texture_greyscale_alpha.shape[0], texture_greyscale_alpha.shape[1]

    # Define total rgb intensity
    total_rgb_intensity = np.zeros(3, dtype = np.float32)
    # Define count of pixels that influence the rgb intensity
    count_influential_pixels = 0

    for i in range(scanline_x_intersects_array.shape[0]):
        # Get scanline x intersects
        x_left = scanline_x_intersects_array[i, 0]
        x_right = scanline_x_intersects_array[i, 1]
        # skip out of bounds x intersects
        if x_left == -1 or x_right == -1:
            continue

        # Get y index of scanline
        y = i + poly_y_min

        for x in range(x_left, x_right + 1):
            # Get transformed coordinates in texture space (might be floating point)
            new_x, new_y = transform_rect_texture_coordinate(x, y, rect_x_center, rect_y_center, rect_height,
                                                             rect_width, rect_theta, texture_width, texture_height)

            # 5) Skip pixel if its corresponding transformed pixel is out of bounds
            if new_x < 0 or new_y < 0 or new_x > texture_width - 2 or new_y > texture_height - 2:
                continue

            # 6) Perform bi linear interpolation to find interpolated alpha in texture
            weighted_alpha_intensity = bi_linear_interpolation_in_texture_space(new_x, new_y, texture_greyscale_alpha, channel=1)

            # 7) If the interpolated alpha intensity is greater than 0.2, find the rgb value in target_rgba at (x,y)
            if weighted_alpha_intensity > 0.2:
                total_rgb_intensity += target_rgba[y, x, 0:3]
                count_influential_pixels += 1

    # Find average rgb values
    average_rgb = total_rgb_intensity / count_influential_pixels
    return average_rgb

@nb.njit(cache=True)
def get_score_of_rectangle(target_rgba, texture_greyscale_alpha, current_rgba, scanline_x_intersects_array, poly_y_min, rgb,
                          rect_x_center, rect_y_center, rect_height, rect_width, rect_theta):
    """
    Calculates a fitness score for placing a textured rectangle onto a canvas by comparing
    the resulting blended image against a target image.

    This function performs geometric transformation, bilinear interpolation, and alpha blending
    to simulate placing a textured rectangle at a specific position, size, and rotation on the
    current canvas. It then computes a score based on how much the blended result improves
    the match with the target image compared to the original canvas.

    Scoring logic:
    1. For each pixel in the rectangle's scanline intersection area:
       - Transform canvas coordinates to texture coordinates using inverse geometric transformation
       - Sample texture values using bilinear interpolation
       - Perform alpha blending between texture and current canvas
       - Calculate pixel-wise improvement score (original_error - new_error)
    2. Sum all pixel scores to get the total rectangle score
    3. Penalize degenerate rectangles (< 4 pixels) with a score of -1

    Higher scores indicate better fit, where the textured rectangle would improve the canvas
    to better match the target image.

    Parameters:
        target_rgba (np.ndarray):
            Normalized RGBA image of shape (H, W, 4), dtype np.float32.

        texture_greyscale_alpha (np.ndarray):
            Array of shape (H, W, 2) representing grayscale and alpha, dtype np.float32.

        current_rgba (np.ndarray):
            Normalized RGBA image of shape (H, W, 4), dtype np.float32.

        scanline_x_intersects_array (np.ndarray):
            np.int32 NumPy array of size (y_max_clamped - y_min_clamped + 1, 2)

        poly_y_min (int):
            index of clamped y index of polygon within boundary of canvas

        rgb (np.ndarray):
            np.float32 NumPy array denoting average rgb values for multiplying with greyscale channel

        rect_x_center (int):
            x coordinate/index of rectangle center

        rect_y_center (int):
            y coordinate/index of rectangle center

        rect_height (np.float32):
            height of rectangle in pixels

        rect_width (np.float32):
            width of rectangle in pixels

        rect_theta (np.float32)
            radian rotation of rectangle in range [-pi, pi]

    Returns:
        score (int):
            Total fitness score for the rectangle placement. Higher values indicate better fit.
            Returns -1 for degenerate rectangles with fewer than 4 pixels.
    """

    total_score = 0
    count_pixels = 0

    # Get height and width of texture
    texture_height, texture_width = texture_greyscale_alpha.shape[0], texture_greyscale_alpha.shape[1]

    for i in range(scanline_x_intersects_array.shape[0]):
        # Get scanline x intersects
        x_left = scanline_x_intersects_array[i, 0]
        x_right = scanline_x_intersects_array[i, 1]
        # skip out of bounds x intersects
        if x_left == -1 or x_right == -1:
            continue

        # Get y index of scanline
        y = i + poly_y_min

        for x in range(x_left, x_right + 1):
            # Get transformed coordinates in texture space (might be floating point)
            new_x, new_y = transform_rect_texture_coordinate(x, y, rect_x_center, rect_y_center, rect_height,
                                                             rect_width, rect_theta, texture_width, texture_height)

            # 5) Skip pixel if its corresponding transformed pixel is out of bounds, else increment the count of pixels
            if new_x < 0 or new_y < 0 or new_x > texture_width - 2 or new_y > texture_height - 2:
                continue
            else:
                count_pixels += 1

            # 6) Perform bi linear interpolation to find interpolated greyscale and alpha intensity, simulate mapping 4 nearest pixels to a single (x,y) pixel in the target_rgba space
            interpolated_greyscale = bi_linear_interpolation_in_texture_space(new_x, new_y, texture_greyscale_alpha, channel=0)
            interpolated_alpha = bi_linear_interpolation_in_texture_space(new_x, new_y, texture_greyscale_alpha, channel=1)

            # 7) Find the score of pixel
            # Scoring logic: pixel score = original pixel difference - new pixel difference
            # original pixel difference is sum of squared difference between current and target
            # new pixel difference is sum of squared differences between blended and target
            # score is higher when new pixel difference is lower than original pixel difference
            # score is lower when new pixel difference is higher than original pixel difference

            # i) Find original sum of squared differences between current and target rgb
            original_pixel_difference = np.sum((current_rgba[y,x,0:3] - target_rgba[y,x,0:3]) ** 2)

            # ii) Alpha blend rgba of interpolated pixel onto rgba of current_rgba
            foreground_rgb = rgb * interpolated_greyscale
            foreground_alpha = interpolated_alpha
            background_rgb = current_rgba[y,x,0:3]
            background_alpha = current_rgba[y,x,3]
            blended_rgb, resultant_alpha = alpha_blend(foreground_rgb, foreground_alpha, background_rgb, background_alpha)

            # iii) Find the new sum of squared pixel difference between blended and target
            new_pixel_difference = np.sum((blended_rgb - target_rgba[y, x, 0:3]) ** 2)

            pixel_score = original_pixel_difference - new_pixel_difference
            total_score += pixel_score

    # penalize degenerate rectangles
    if count_pixels < 4:
        return -1

    return total_score

@nb.njit(cache=True)
def draw_texture_on_canvas(texture_greyscale_alpha, current_rgba, scanline_x_intersects_array, poly_y_min, rgb,
                           rect_x_center, rect_y_center, rect_height, rect_width, rect_theta):
    """
    Mutates current_rgba by drawing the texture within specified rectangle.

    Parameters:
        texture_greyscale_alpha (np.ndarray):
            Array of shape (H, W, 2) representing grayscale and alpha, dtype np.float32.

        current_rgba (np.ndarray):
            Normalized RGBA image of shape (H, W, 4), dtype np.float32.

        scanline_x_intersects_array (np.ndarray):
            np.int32 NumPy array of size (y_max_clamped - y_min_clamped + 1, 2)

        poly_y_min (int):
            index of clamped y index of polygon within boundary of canvas

        rgb (np.ndarray):
            np.float32 NumPy array denoting average rgb values for multiplying with greyscale channel

        rect_x_center (int):
            x coordinate/index of rectangle center

        rect_y_center (int):
            y coordinate/index of rectangle center

        rect_height (np.float32):
            height of rectangle in pixels

        rect_width (np.float32):
            width of rectangle in pixels

        rect_theta (np.float32)
            radian rotation of rectangle in range [-pi, pi]

    Returns:
        current_rgba (np.ndarray):
            Normalized RGBA image of shape (H, W, 4), dtype np.float32. this array has been mutated and also returned
    """

    # Get height and width of texture
    texture_height, texture_width = texture_greyscale_alpha.shape[0], texture_greyscale_alpha.shape[1]

    for i in range(scanline_x_intersects_array.shape[0]):
        # Get scanline x intersects
        x_left = scanline_x_intersects_array[i, 0]
        x_right = scanline_x_intersects_array[i, 1]
        # skip out of bounds x intersects
        if x_left == -1 or x_right == -1:
            continue

        # Get y index of scanline
        y = i + poly_y_min

        for x in range(x_left, x_right + 1):
            # Get transformed coordinates in texture space (might be floating point)
            new_x, new_y = transform_rect_texture_coordinate(x, y, rect_x_center, rect_y_center, rect_height,
                                                             rect_width, rect_theta, texture_width, texture_height)

            # 5) Skip pixel if its corresponding transformed pixel is out of bounds
            if new_x < 0 or new_y < 0 or new_x > texture_width - 2 or new_y > texture_height - 2:
                continue

            # 6) Perform bi linear interpolation to find interpolated greyscale and alpha intensity, simulate mapping 4 nearest pixels to a single (x,y) pixel in the target_rgba space
            interpolated_greyscale = bi_linear_interpolation_in_texture_space(new_x, new_y, texture_greyscale_alpha, channel=0)
            interpolated_alpha = bi_linear_interpolation_in_texture_space(new_x, new_y, texture_greyscale_alpha, channel=1)


            # Find alpha blended rgba of interpolated pixel onto rgba of current_rgba
            foreground_rgb = rgb * interpolated_greyscale
            foreground_alpha = interpolated_alpha
            background_rgb = current_rgba[y,x,0:3]
            background_alpha = current_rgba[y,x,3]
            blended_rgb, resultant_alpha = alpha_blend(foreground_rgb, foreground_alpha, background_rgb, background_alpha)

            # Mutate current_rgba pixel to new alpha blended pixel value
            current_rgba[y,x,0:3] = blended_rgb
            current_rgba[y, x, 3] = resultant_alpha
    
    # current_rgba is mutated but returned also
    return current_rgba



def get_score_avg_rgb_ymin_and_scanline_xintersect(rect_list, target_rgba, texture_greyscale_alpha, current_rgba):
    """
    (Description here)

    Returns score, average_rgb and scanline_x_intersects of a [x, y, h, w, theta] rect list 
    """
    # 1) Find vertices of rectangle
    x, y, h, w, theta = rect_list
    h, w, theta = np.float32(h), np.float32(w), np.float32(theta)
    rect_vertices = rectangle_to_polygon(x, y, h, w, theta)
    # 2) Find x-intersects for every scanline and the miny of rectangle
    canvas_height, canvas_width = current_rgba.shape[0], current_rgba.shape[1]
    y_min, y_max, scanline_x_intersects_array = get_y_index_bounds_and_scanline_x_intersects(rect_vertices, canvas_height, canvas_width)
    # 3) Find the average rgb value
    average_rgb = get_average_rgb_value(target_rgba, texture_greyscale_alpha, scanline_x_intersects_array, y_min, *rect_list)
    # 4) Score the rectangle
    score = get_score_of_rectangle(target_rgba, texture_greyscale_alpha, current_rgba, scanline_x_intersects_array, y_min, average_rgb, *rect_list)
    return score, average_rgb, y_min, scanline_x_intersects_array

# Draws the best rect list onto canvas
def update_canvas_with_best_rect(rect_list, target_rgba, texture_greyscale_alpha, current_rgba):
    # 1) Find vertices of rectangle
    x, y, h, w, theta = rect_list
    h, w, theta = np.float32(h), np.float32(w), np.float32(theta)
    rect_vertices = rectangle_to_polygon(x, y, h, w, theta)
    # 2) Find x-intersects for every scanline and the miny of rectangle
    canvas_height, canvas_width = current_rgba.shape[0], current_rgba.shape[1]
    y_min, y_max, scanline_x_intersects_array = get_y_index_bounds_and_scanline_x_intersects(rect_vertices, canvas_height, canvas_width)
    # 3) Find the average rgb value
    average_rgb = get_average_rgb_value(target_rgba, texture_greyscale_alpha, scanline_x_intersects_array, y_min, *rect_list)
    # 4) Draw the texture onto canvas
    draw_texture_on_canvas(texture_greyscale_alpha, current_rgba, scanline_x_intersects_array, y_min, average_rgb, *rect_list)

# debugging
def draw_x_intersects_on_bg_debug(background, scanline_x_intersects, poly_y_min, polygon_color, polygon_alpha):
    background = background.copy()
    for i in range(scanline_x_intersects.shape[0]):
        # Get scanline x intersects
        line_start = scanline_x_intersects[i,0]
        line_end = scanline_x_intersects[i,1]
        # case where there is no intersect
        if line_start == -1 or line_end == -1:
            continue

        # Get y value of scanline
        y =  i + poly_y_min

        for x in range(line_start, line_end+1):
            # Get rgba of front pixel
            rf, gf, bf = polygon_color[0], polygon_color[1], polygon_color[2]
            af = polygon_alpha
            # Get rgba of back pixel
            rb, gb, bb, ab =  background[y, x ,0], background[y, x ,1], background[y, x ,2], background[y, x ,3]
            # If front and back alpha is both 0, the resulting alpha is zero, ignore this pixel and continue
            if af == 0 and ab == 0:
                continue
            # Find the resulting alpha value and color
            alpha = af + ab * (1 - af)
            r = (rf * af + rb*ab*(1-af)) / alpha
            g = (gf * af + gb*ab*(1-af)) / alpha
            b = (bf * af + bb*ab*(1-af)) / alpha
            # Set the background color to the new r,g,b and alpha value
            background[y, x ,0] = r
            background[y, x ,1] = g
            background[y, x ,2] = b
            background[y, x ,3] = alpha
    plt.imshow(background)
    plt.show()