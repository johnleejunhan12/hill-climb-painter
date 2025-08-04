import os
from PIL import Image
import glob

def convert_pngs_to_jpg(folder_path, quality=95, delete_original=False):
    """
    Convert all PNG files in a folder to JPG format with specified quality.
    
    Args:
        folder_path (str): Path to the folder containing PNG files
        quality (int): JPG quality (1-100, default 95)
        delete_original (bool): Whether to delete original PNG files (default False)
    
    Returns:
        list: List of successfully converted files
    """
    
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder path '{folder_path}' does not exist")
    
    # Find all PNG files in the folder
    png_pattern = os.path.join(folder_path, "*.png")
    png_files = glob.glob(png_pattern, recursive=False)
    
    # Also check for uppercase extension
    png_pattern_upper = os.path.join(folder_path, "*.PNG")
    png_files.extend(glob.glob(png_pattern_upper, recursive=False))
    
    converted_files = []
    failed_files = []
    
    for png_file in png_files:
        try:
            # Open the PNG image
            with Image.open(png_file) as img:
                # Convert RGBA to RGB if necessary (JPG doesn't support transparency)
                if img.mode in ('RGBA', 'LA'):
                    # Create a white background
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    # Paste the image onto the white background
                    if img.mode == 'RGBA':
                        rgb_img.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                    else:  # LA mode
                        rgb_img.paste(img, mask=img.split()[-1])
                    img = rgb_img
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Generate output filename
                base_name = os.path.splitext(png_file)[0]
                jpg_file = f"{base_name}.jpg"
                
                # Save as JPG with specified quality
                img.save(jpg_file, 'JPEG', quality=quality, optimize=True)
                
                converted_files.append(jpg_file)
                print(f"Converted: {os.path.basename(png_file)} -> {os.path.basename(jpg_file)}")
                
                # Delete original PNG if requested
                if delete_original:
                    os.remove(png_file)
                    print(f"Deleted original: {os.path.basename(png_file)}")
                    
        except Exception as e:
            failed_files.append((png_file, str(e)))
            print(f"Failed to convert {os.path.basename(png_file)}: {e}")
    
    # Print summary
    print(f"\nConversion complete!")
    print(f"Successfully converted: {len(converted_files)} files")
    if failed_files:
        print(f"Failed to convert: {len(failed_files)} files")
        for failed_file, error in failed_files:
            print(f"  - {os.path.basename(failed_file)}: {error}")
    
    return converted_files

# Example usage
if __name__ == "__main__":
    # Convert all PNGs in current directory
    folder = "."  # Current directory
    
    # Or specify a different folder:
    # folder = "/path/to/your/image/folder"
    
    try:
        converted = convert_pngs_to_jpg(folder, quality=95, delete_original=False)
        print(f"Converted {len(converted)} files successfully!")
    except Exception as e:
        print(f"Error: {e}")