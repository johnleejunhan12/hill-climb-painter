import numpy as np
import numba as nb
import matplotlib.pyplot as plt
from utilities import clamp_int


def create_random_rectangle(canvas_height, canvas_width, texture_height, texture_width):
    """
    Creates a random rectangle with its center located at a random integer pixel index within the canvas.
    The rectangle maintains the same aspect ratio as the given texture, with its width fixed at 20 pixels.
    The rectangle is also randomly rotated by an angle theta in radians, uniformly sampled from [-π, π).

    Parameters:
        canvas_height (int): Height of the canvas in pixels.
        canvas_width (int): Width of the canvas in pixels.
        texture_height (int): Height of the reference texture in pixels.
        texture_width (int): Width of the reference texture in pixels.

    Returns:
        rectangle (list): A list containing:
            - x (int): Horizontal pixel index of the rectangle center (0 ≤ x < canvas_width).
            - y (int): Vertical pixel index of the rectangle center (0 ≤ y < canvas_height).
            - rect_height (float): Height of the rectangle, scaled to preserve texture aspect ratio.
            - rect_width (float): Fixed width of the rectangle (50.0).
            - theta (float): Rotation angle in radians, uniformly sampled from [-π, π).
    """
    # Fixed rectangle width
    rect_width = 100.0
    # Maintain aspect ratio from texture
    aspect_ratio = texture_height / texture_width
    rect_height = rect_width * aspect_ratio

    # Random integer center positions (0 to size-1)
    x = np.random.randint(0, canvas_width)
    y = np.random.randint(0, canvas_height)

    # Random angle in radians between -π and π
    theta = np.random.uniform(-np.pi, np.pi)

    return [x, y, rect_height, rect_width, theta]

def get_mutated_rectangle_copy(rectangle, canvas_height, canvas_width):
    """
    Takes in a rectangle and returns a mutated copy of it.
    One of three mutation cases is randomly applied with equal probability:

    Case 1: Mutate center x and y by a small integer amount in [-15, 15], clamped to canvas bounds.
    Case 2: Scale both rect_height and rect_width by the same factor in [0.8, 1.2].
    Case 3: Adjust theta by a small radian in [-0.8, 0.8], clamped to [-pi, pi].

    Parameters:
        rectangle (list): [x(int), y(int), rect_height(float), rect_width(float), theta(float)]
        canvas_height (int): Height of the canvas in pixels.
        canvas_width (int): Width of the canvas in pixels.

    Returns:
        mutated_rectangle (list): A mutated copy of the input rectangle.
    """
    x, y, rect_height, rect_width, theta = rectangle
    mutated = [x, y, rect_height, rect_width, theta]  # copy

    case = np.random.choice([1, 2, 3])

    if case == 1:
        # Case 1: Mutate x and y
        dx = np.random.randint(-15, 16)
        dy = np.random.randint(-15, 16)
        mutated[0] = clamp_int(x + dx, 0, canvas_width - 1)
        mutated[1] = clamp_int(y + dy, 0, canvas_height - 1)

    elif case == 2:
        # Case 2: Scale height and width
        scale = np.random.uniform(0.8, 1.2)
        mutated[2] = rect_height * scale
        mutated[3] = rect_width * scale

    else:
        # Case 3: Adjust theta
        dtheta = np.random.uniform(-0.8, 0.8)
        new_theta = theta + dtheta
        # Wrap angle to [-π, π]
        new_theta = (new_theta + np.pi) % (2 * np.pi) - np.pi
        mutated[4] = new_theta

    return mutated

def rectangle_to_polygon(rectangle):
    """
    Converts a rectangle specified as [x, y, rect_height, rect_width, theta] into a 4x2 array of (x, y)
    polygon vertices, accounting for rotation. Vertices are returned as np.int32.

    Parameters:
        rectangle (list): [x, y, rect_height, rect_width, theta]

    Returns:
        vertices (np.ndarray): A 4x2 array of integer (x, y) coordinates (dtype=np.int32)
                               representing the corners of the rotated rectangle.
    """
    x, y, h, w, theta = rectangle

    # Half-dimensions
    dx = w / 2
    dy = h / 2

    # Define rectangle corners centered at origin (before rotation)
    corners = np.array([
        [-dx, -dy],
        [ dx, -dy],
        [ dx,  dy],
        [-dx,  dy]
    ])

    # Rotation matrix
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    rotation_matrix = np.array([
        [cos_theta, -sin_theta],
        [sin_theta,  cos_theta]
    ])

    # Rotate and translate corners
    rotated = corners @ rotation_matrix.T
    translated = rotated + np.array([x, y])

    return np.round(translated).astype(np.int32)

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

@nb.njit(cache=True)
def get_average_rgb_value(target_rgba, texture_greyscale_alpha, scanline_x_intersects_array, poly_y_min, rect_x_center, rect_y_center, rect_height, rect_width, rect_theta):
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

    # Find scale factor when rectangle is scaled back to texture
    rect_reverse_scale_x = texture_width / rect_width
    rect_reverse_scale_y = texture_height / rect_height

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
            # 1) Translate by (-rect_x_center, -rect_y_center) to align rectangle center with origin
            translated_x = x - rect_x_center
            translated_y = y - rect_y_center

            # 2) Rotate about origin by -rect_theta radians
            rotated_x = translated_x * np.cos(-rect_theta) + translated_y * np.sin(-rect_theta)
            rotated_y = -translated_x * np.sin(-rect_theta) + translated_y * np.cos(-rect_theta)

            # 3) Scale by 1/sh, scale by 1/sw
            scaled_x = rotated_x * rect_reverse_scale_x
            scaled_y = rotated_y * rect_reverse_scale_y

            # 4) Translation in the direction (texture_x_center, texture_y_center) from origin
            new_x = scaled_x + (texture_width / 2)
            new_y = scaled_y + (texture_height / 2)

            # 5) Skip pixel if its corresponding transformed pixel is out of bounds
            if new_x < 0 or new_y < 0 or new_x > texture_width - 1 or new_y > texture_height - 1:
                continue

            # 6) Perform bi linear interpolation to find interpolated alpha in texture:
            # 6a) Find the (x,y) coordinates of the 4 pixels surrounding the floating point coordinate (new_x, new_y)
            top_left_x, top_left_y = np.int32(np.floor(new_x)), np.int32(np.floor(new_y))
            bottom_left_x, bottom_left_y = top_left_x, top_left_y + 1
            top_right_x, top_right_y = top_left_x + 1, top_left_y
            bottom_right_x, bottom_right_y = top_left_x + 1, top_left_y + 1

            # i) get alpha intensity of 4 corners
            top_left_intensity, top_right_intensity = (texture_greyscale_alpha[top_left_y, top_left_x, 1],
                                                       texture_greyscale_alpha[top_right_y, top_right_x, 1])
            bottom_left_intensity, bottom_right_intensity = (texture_greyscale_alpha[bottom_left_y, bottom_left_x, 1],
                                                             texture_greyscale_alpha[bottom_right_y, bottom_right_x, 1])

            # ii) Get weighted intensity for top and bottom pixels along x-axis
            weight_left, weight_right = new_x - top_left_x, top_right_x - new_x
            weighted_avg_top = top_left_intensity * weight_left + top_right_intensity * weight_right
            weighted_avg_bottom = bottom_left_intensity * weight_left + bottom_right_intensity * weight_right

            # iii) Get weighted intensity along y-axis
            weight_top, weight_bottom = new_y - top_left_y, bottom_left_y - new_y
            weighted_alpha_intensity = weighted_avg_top * weight_top + weighted_avg_bottom * weight_bottom

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

    # Find scale factor when rectangle is scaled back to texture
    rect_reverse_scale_x = texture_width / rect_width
    rect_reverse_scale_y = texture_height / rect_height


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
            # 1) Translate by (-rect_x_center, -rect_y_center) to align rectangle center with origin
            translated_x = x - rect_x_center
            translated_y = y - rect_y_center

            # 2) Rotate about origin by -rect_theta radians
            rotated_x = translated_x * np.cos(-rect_theta) + translated_y * np.sin(-rect_theta)
            rotated_y = -translated_x * np.sin(-rect_theta) + translated_y * np.cos(-rect_theta)

            # 3) Scale by 1/sh, scale by 1/sw
            scaled_x = rotated_x * rect_reverse_scale_x
            scaled_y = rotated_y * rect_reverse_scale_y

            # 4) Translation in the direction (texture_x_center, texture_y_center) from origin
            new_x = scaled_x + (texture_width / 2)
            new_y = scaled_y + (texture_height / 2)

            # 5) Skip pixel if its corresponding transformed pixel is out of bounds
            if new_x < 0 or new_y < 0 or new_x > texture_width - 1 or new_y > texture_height - 1:
                continue

            # 5a) Increment the count of pixels
            count_pixels += 1

            # 6) Perform bi linear interpolation to find rgba of pixel:
            # 6a) Find the (x,y) coordinates of the 4 pixels surrounding the floating point coordinate (new_x, new_y)
            top_left_x, top_left_y = np.int32(np.floor(new_x)), np.int32(np.floor(new_y))
            bottom_left_x, bottom_left_y = top_left_x, top_left_y + 1
            top_right_x, top_right_y = top_left_x + 1, top_left_y
            bottom_right_x, bottom_right_y = top_left_x + 1, top_left_y + 1

            # Find the interpolated alpha and greyscale value
            interpolated_greyscale = np.float32(0)
            interpolated_alpha = np.float32(0)
            for c in range(0,2): # 0:greyscale, 1:alpha
                # 6b) Find the weighted intensity of the channel
                # i) get intensity of 4 corners
                top_left_intensity, top_right_intensity = texture_greyscale_alpha[top_left_y, top_left_x, c], texture_greyscale_alpha[
                    top_right_y, top_right_x, c]
                bottom_left_intensity, bottom_right_intensity = texture_greyscale_alpha[bottom_left_y, bottom_left_x, c], texture_greyscale_alpha[
                    bottom_right_y, bottom_right_x, c]

                # ii) Get weighted intensity for top and bottom pixels along x-axis
                weight_left, weight_right = new_x - top_left_x, top_right_x - new_x
                weighted_avg_top = top_left_intensity * weight_left + top_right_intensity * weight_right
                weighted_avg_bottom = bottom_left_intensity * weight_left + bottom_right_intensity * weight_right

                # iii) Get weighted intensity along y-axis
                weight_top, weight_bottom = new_y - top_left_y, bottom_left_y - new_y
                weighted_avg_intensity = np.float32(weighted_avg_top * weight_top + weighted_avg_bottom * weight_bottom)

                if c == 0: # greyscale channel
                    interpolated_greyscale = weighted_avg_intensity
                elif c == 1: # alpha channel
                    interpolated_alpha = weighted_avg_intensity

            # Scoring logic: pixel score = original pixel difference - new pixel difference
            # original pixel difference is sum of squared difference between current and target
            # new pixel difference is sum of squared differences between blended and target
            # score is higher when new pixel difference is lower than original pixel difference
            # score is lower when new pixel difference is higher than original pixel difference

            # 1) Find original sum of squared differences between current and target rgb
            original_pixel_difference = np.sum((current_rgba[y,x,0:3] - target_rgba[y,x,0:3]) ** 2)
            # 2) Find foreground and background rgb pixel color
            foreground_rgb = rgb * interpolated_greyscale
            background_rgb = current_rgba[y,x,0:3]

            # Perform alpha blending:
            # 3)  Find alphas for foreground, background and resultant alpha
            foreground_alpha = interpolated_alpha
            background_alpha = target_rgba[y,x,3]
            resultant_alpha = foreground_alpha + background_alpha * (1 - foreground_alpha)

            # 4) Find blended rgb values, handle case where front and back alpha is both 0 where the resulting alpha is zero
            blended_rgb = np.zeros(3, dtype = np.float32)

            if resultant_alpha == 0:    # Let resulting rgb be same as original rgb from background
                blended_rgb = current_rgba[y,x,0:3]

            else:   # find the resulting alpha value and color using straight alpha blending
                blended_rgb = ((foreground_rgb*foreground_alpha + background_rgb*background_alpha*(1-foreground_alpha)) / resultant_alpha).astype(np.float32)

            # 5) Find the new sum of squared pixel difference between blended and target
            new_pixel_difference = np.sum((blended_rgb - target_rgba[y, x, 0:3]) ** 2)

            pixel_score = original_pixel_difference - new_pixel_difference
            total_score += pixel_score

    # penalize degenerate rectangles
    if count_pixels < 4:
        return -1

    return total_score

def draw_texture_on_canvas(texture_greyscale_alpha, current_rgba, scanline_x_intersects_array, poly_y_min, rgb,
                           rect_x_center, rect_y_center, rect_height, rect_width, rect_theta):
    """
    Mutates current_rgba by drawing the texture withing specified rectangle. Does not return anything

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
    """



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