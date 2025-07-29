import os
import time
import numpy as np
import imageio
import multiprocessing as mp
from typing import Optional

# Try to import faster libraries
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


class CreateOutputGIF:
    def __init__(self, fps: int, is_create_gif: bool, gif_file_name: str, use_fast_writer: bool = True):
        """
        Initialize the GIF creator with specified parameters.
        
        Args:
            fps (int): Frames per second for the output GIF
            is_create_gif (bool): Whether to create GIF or not
            gif_file_name (str): Name of the output GIF file (without extension)
            use_fast_writer (bool): Use optimized PIL writer for better performance
        """
        self.fps = fps
        self.is_create_gif = is_create_gif
        self.gif_file_name = gif_file_name
        self.use_fast_writer = use_fast_writer and PIL_AVAILABLE
        
        # Initialize process and queue attributes
        self.process: Optional[mp.Process] = None
        self.queue: Optional[mp.Queue] = None
        
        if self.is_create_gif:
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            # Create queue and process
            self.queue = mp.Queue(maxsize=100)  # Limit queue size to prevent memory buildup
            self.process = mp.Process(target=self._gif_writer_process)
            self.process.start()
    
    def _gif_writer_process(self):
        """
        Process function that runs in separate process to write GIF frames.
        Uses streaming approach to avoid memory accumulation.
        """
        # Create output directory if it doesn't exist
        os.makedirs("output", exist_ok=True)
        
        # Generate base filename without extension
        base_name = self.gif_file_name
        if base_name.lower().endswith('.gif'):
            base_name = base_name[:-4]
        
        # Determine the final filename with copy numbering if needed
        gif_filename = f"{base_name}.gif"
        counter = 0
        gif_path = os.path.join("output", gif_filename)
        
        while os.path.exists(gif_path):
            counter += 1
            if counter == 1:
                gif_filename = f"{base_name} - Copy.gif"
            else:
                gif_filename = f"{base_name} - Copy ({counter}).gif"
            gif_path = os.path.join("output", gif_filename)
        
        # Choose writer based on availability and preference
        if self.use_fast_writer:
            self._write_gif_with_pil(gif_path)
        else:
            self._write_gif_with_imageio(gif_path)
    
    def _write_gif_with_pil(self, gif_path: str):
        """Fast GIF writing using PIL with optimization."""
        frames = []
        frame_count = 0
        
        try:
            while True:
                try:
                    frame_data = self.queue.get(timeout=1.0)
                    if frame_data is None:
                        break
                    
                    # Decompress frame data
                    frame = self._decompress_frame(frame_data)
                    if frame is None:
                        continue
                    
                    # Convert and optimize frame
                    frame_uint8 = self._ensure_uint8(frame)
                    
                    # Convert to PIL Image with optimization
                    if frame_uint8.shape[2] == 4:  # RGBA
                        # Convert to RGB for smaller GIF size
                        rgb_frame = frame_uint8[:, :, :3]
                        pil_frame = Image.fromarray(rgb_frame, 'RGB')
                    else:
                        pil_frame = Image.fromarray(frame_uint8)
                    
                    # Optimize: reduce colors for smaller file size
                    pil_frame = pil_frame.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
                    frames.append(pil_frame)
                    frame_count += 1
                    
                    if frame_count % 50 == 0:
                        print(f"Processed {frame_count} frames for GIF...")
                        
                except Exception:
                    continue
            
            # Write optimized GIF
            if frames:
                duration = int(1000 / self.fps)  # Duration in milliseconds
                frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=duration,
                    loop=0,
                    optimize=True,  # Enable optimization
                    disposal=2      # Clear frame for better compression
                )
                print(f"Fast GIF saved: {gif_path} ({frame_count} frames)")
            else:
                print("No frames to save")
                
        except Exception as e:
            print(f"Error in fast GIF writer: {e}")
    
    def _write_gif_with_imageio(self, gif_path: str):
        """Original imageio-based writer (fallback)."""
        writer = None
        frame_count = 0
        
        try:
            while True:
                try:
                    frame_data = self.queue.get(timeout=1.0)
                    if frame_data is None:
                        break
                    
                    # Decompress frame data
                    frame = self._decompress_frame(frame_data)
                    if frame is None:
                        continue
                    
                    frame_uint8 = self._ensure_uint8(frame)
                    
                    if writer is None:
                        writer = imageio.get_writer(gif_path, mode='I', fps=self.fps)
                    
                    writer.append_data(frame_uint8)
                    frame_count += 1
                    
                    if frame_count % 100 == 0:
                        print(f"Written {frame_count} frames to GIF...")
                    
                except Exception:
                    continue
            
            if writer is not None:
                writer.close()
                print(f"GIF saved: {gif_path} ({frame_count} frames)")
            else:
                print("No frames to save")
                
        except Exception as e:
            print(f"Error in GIF writer process: {e}")
        finally:
            if writer is not None:
                try:
                    writer.close()
                except:
                    pass
    
    def _decompress_frame(self, frame_data) -> np.ndarray:
        """
        Decompress frame data received from queue.
        
        Args:
            frame_data: Compressed frame data dict or raw array
            
        Returns:
            Decompressed numpy array or None if failed
        """
        try:
            # Handle backward compatibility with raw arrays
            if isinstance(frame_data, np.ndarray):
                return frame_data
            
            if not isinstance(frame_data, dict):
                return None
            
            frame_type = frame_data.get('type', 'raw_float32')
            
            if frame_type == 'compressed' and OPENCV_AVAILABLE:
                # Decompress PNG data
                compressed_data = np.frombuffer(frame_data['data'], dtype=np.uint8)
                decompressed = cv2.imdecode(compressed_data, cv2.IMREAD_UNCHANGED)
                if decompressed is not None:
                    # Convert back to RGBA
                    if len(decompressed.shape) == 3 and decompressed.shape[2] == 4:
                        return cv2.cvtColor(decompressed, cv2.COLOR_BGRA2RGBA)
                    elif len(decompressed.shape) == 3 and decompressed.shape[2] == 3:
                        # Add alpha channel
                        alpha = np.ones((decompressed.shape[0], decompressed.shape[1], 1), 
                                      dtype=decompressed.dtype) * 255
                        return np.concatenate([decompressed, alpha], axis=-1)
                    return decompressed
            
            elif frame_type == 'raw_uint8':
                return frame_data['data']
            
            elif frame_type == 'raw_float32':
                return frame_data['data']
            
            return None
            
        except Exception as e:
            print(f"Failed to decompress frame: {e}")
            return None
    
    def _ensure_uint8(self, frame: np.ndarray) -> np.ndarray:
        """Ensure frame is in uint8 format."""
        if frame.dtype == np.uint8:
            return frame
        elif frame.dtype == np.float32:
            return (frame * 255).astype(np.uint8)
        else:
            return frame.astype(np.uint8)
    
    def enqueue_frame(self, frame: np.ndarray):
        """
        Add a frame to the queue for processing with optional compression.
        
        Args:
            frame (np.ndarray): Normalized RGBA numpy array (float32)
        """
        if not self.is_create_gif or self.queue is None:
            return
        
        try:
            # Check if queue is getting full (non-blocking check)
            if self.queue.full():
                print("Warning: GIF queue full, skipping frame to prevent memory buildup")
                return
            
            # Compress frame for faster queue operations
            compressed_frame = self._compress_frame(frame)
            self.queue.put(compressed_frame, block=False)
        except Exception as e:
            if "queue is full" not in str(e).lower():
                print(f"Warning: Failed to enqueue frame: {e}")
    
    def _compress_frame(self, frame: np.ndarray) -> dict:
        """
        Compress frame for efficient queue transmission.
        
        Args:
            frame: Normalized RGBA array
            
        Returns:
            Dictionary with compressed frame data
        """
        try:
            # Convert to uint8 to reduce data size
            frame_uint8 = (frame * 255).astype(np.uint8)
            
            # Optional: Use OpenCV compression if available
            if OPENCV_AVAILABLE:
                # Compress to PNG in memory (lossless, good compression)
                success, compressed = cv2.imencode('.png', 
                    cv2.cvtColor(frame_uint8, cv2.COLOR_RGBA2BGRA))
                if success:
                    return {
                        'type': 'compressed',
                        'data': compressed.tobytes(),
                        'shape': frame.shape
                    }
            
            # Fallback: send raw but optimized data
            return {
                'type': 'raw_uint8',
                'data': frame_uint8,
                'shape': frame.shape
            }
            
        except Exception:
            # Ultimate fallback
            return {
                'type': 'raw_float32',
                'data': frame,
                'shape': frame.shape
            }
    
    def end_process(self):
        """
        End the GIF creation process cleanly, processing remaining frames.
        """
        if not self.is_create_gif:
            return None
        
        if self.process is not None and self.queue is not None:
            # Monitor and report queue size while waiting for completion
            print("Finishing GIF creation...")
            
            while True:
                try:
                    queue_size = self.queue.qsize()
                    if queue_size == 0:
                        break
                    
                    print(f"Approximate number of images left in queue: {queue_size}")
                    time.sleep(2.0)
                    
                except:
                    # Some systems don't support qsize(), so we'll just wait
                    time.sleep(2.0)
                    break
            
            # Send sentinel value to stop the process
            self.queue.put(None)
            
            # Wait for process to complete
            self.process.join()
            # print("GIF creation process ended cleanly")

    def close(self):
        """
        Signal the GIF writer process to stop and wait for it to finish.
        This ensures all frames are written and the GIF file is properly closed.
        """
        if not self.is_create_gif:
            return
        
        if self.queue is not None:
            # Send sentinel value to stop the writer process
            self.queue.put(None)
            
        if self.process is not None:
            # Wait for the process to finish writing the GIF
            self.process.join(timeout=30)  # 30 second timeout
            
            if self.process.is_alive():
                print("Warning: GIF writer process did not finish within timeout, terminating...")
                self.process.terminate()
                self.process.join(timeout=5)
                
                if self.process.is_alive():
                    print("Warning: Force killing GIF writer process...")
                    self.process.kill()
            
            self.process = None
            self.queue = None
            
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        self.close()



# Debug
if __name__ == "__main__":
    # In main process:
    gif_creator = CreateOutputGIF(fps=24, is_create_gif=True, gif_file_name="myoutput")
    
    # Simulate enqueuing some frames (e.g., from a rendering loop)
    for i in range(1000000):
        random_frame = np.random.rand(200, 200, 4).astype(np.float32)  # Example RGBA frame
        gif_creator.enqueue_frame(random_frame)
        
        if i % 100 == 0:
            print(f"Enqueued frame {i}")
    
    # In case when the queue in gif_creator still has items, prevent killing child process 
    # when main process has finished running (the for _ in range(1000) loop)
    gif_creator.end_process()