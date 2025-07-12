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
    rect_width = 50.0

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
                x_intersects[y_scanline_index, intersect_count] = clamp_int(x_intersect, 0, canvas_width - 1)
                # Increment count of intersections
                intersect_count += 1

            # Exit loop after finding 2 intersections
            if intersect_count == 2:
                break

        # If both intersections are out of bounds, denote left and right intersection as (-1,-1)
        if count_negative_x_intersection == 2 or count_exceed_boundary_x_intersection == 2:
            x_intersects[y_scanline_index, 0] = -1
            x_intersects[y_scanline_index, 1] = -1
            continue

        # sort the x intersection from left to right
        if x_intersects[y_scanline_index, 0] > x_intersects[y_scanline_index, 1]:
            temp = x_intersects[y_scanline_index, 0]
            x_intersects[y_scanline_index, 0] = x_intersects[y_scanline_index, 1]
            x_intersects[y_scanline_index, 1] = temp

    return y_min_clamped, y_max_clamped, x_intersects



@nb.njit(cache=True)
def draw_x_intersects_on_bg_debug(background, scanline_x_intersects, poly_y_min, polygon_color, polygon_alpha):
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


