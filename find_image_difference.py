import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def visualize_image_difference(image_path1, image_path2, title="Image Difference", save_path=None):
    """
    Compare two PNG images and visualize their pixel-wise differences.
    
    Parameters:
    -----------
    image_path1 : str
        Path to the first PNG image
    image_path2 : str
        Path to the second PNG image
    title : str, optional
        Title for the plot (default: "Image Difference")
    save_path : str, optional
        Path to save the difference visualization (default: None)
    
    Returns:
    --------
    numpy.ndarray
        2D array containing RMS differences between pixels
    """
    
    # Load the images
    try:
        img1 = Image.open(image_path1).convert('RGB')
        img2 = Image.open(image_path2).convert('RGB')
    except Exception as e:
        raise ValueError(f"Error loading images: {e}")
    
    # Check if images have the same size
    if img1.size != img2.size:
        raise ValueError(f"Images must have the same size. Got {img1.size} and {img2.size}")
    
    # Convert to numpy arrays
    arr1 = np.array(img1, dtype=np.float32)
    arr2 = np.array(img2, dtype=np.float32)
    
    # Calculate RMS difference for each pixel
    # SQRT((r1-r2)^2 + (g1-g2)^2 + (b1-b2)^2)
    diff_squared = (arr1 - arr2) ** 2
    rms_diff = np.sqrt(np.sum(diff_squared, axis=2))
    
    # Create the visualization
    plt.figure(figsize=(10, 8))

    # Plot the difference using viridis colormap
    im = plt.imshow(rms_diff, cmap='viridis', interpolation='nearest')
    
    # Add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('RMS Pixel Difference', rotation=270, labelpad=20)
    
    # Set title and labels
    plt.title(title, fontsize=14, pad=20)
    plt.xlabel('Width (pixels)')
    plt.ylabel('Height (pixels)')
    
    # # Add statistics as text
    # min_diff = np.min(rms_diff)
    # max_diff = np.max(rms_diff)
    # mean_diff = np.mean(rms_diff)

    
    plt.tight_layout()
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Difference visualization saved to: {save_path}")
    
    plt.show()
    
    print(np.sum(rms_diff))
    return rms_diff




# With custom title and save path
rmse_before = visualize_image_difference(
    'empty_canvas.png', 
    'mona_lisa.jpg',
    title='Before adding texture',
    save_path='empty_canvas_mona_lisa.png'
)

rmse_after = visualize_image_difference(
    'good.png', 
    'mona_lisa.jpg',
    title='After adding texture',
    save_path='good_mona_lisa.png'
)





score_array = rmse_before - rmse_after


def plot_dark_mode_simple(score_array):
    """
    Simple dark mode using plt.style.use('dark_background')
    """
    plt.style.use('dark_background')
    
    plt.figure(figsize=(10, 8))
    plt.imshow(score_array, cmap='RdYlGn')
    plt.colorbar()
    plt.title('Pixel wise score of texture placement', fontsize=14, pad=20)
    plt.show()
plot_dark_mode_simple(score_array)
