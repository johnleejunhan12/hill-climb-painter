import os
import time
import numpy as np
import imageio
import multiprocessing as mp
from typing import Optional


class CreateOutputGIF:
    def __init__(self, fps: int, is_create_gif: bool, gif_file_name: str):
        """
        Initialize the GIF creator with specified parameters.
        
        Args:
            fps (int): Frames per second for the output GIF
            is_create_gif (bool): Whether to create GIF or not
            gif_file_name (str): Name of the output GIF file (without extension)
        """
        self.fps = fps
        self.is_create_gif = is_create_gif
        self.gif_file_name = gif_file_name
        
        # Initialize process and queue attributes
        self.process: Optional[mp.Process] = None
        self.queue: Optional[mp.Queue] = None
        
        if self.is_create_gif:
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            # Create queue and process
            self.queue = mp.Queue()
            self.process = mp.Process(target=self._gif_writer_process)
            self.process.start()
    
    def _gif_writer_process(self):
        """
        Process function that runs in separate process to write GIF frames.
        """
        gif_path = os.path.join("output", f"{self.gif_file_name}.gif")
        frames = []
        
        try:
            while True:
                try:
                    # Get frame from queue with timeout
                    frame = self.queue.get(timeout=1.0)
                    
                    # Check for sentinel value to stop
                    if frame is None:
                        break
                    
                    # Convert normalized float32 RGBA to uint8 (0-255)
                    frame_uint8 = (frame * 255).astype(np.uint8)
                    frames.append(frame_uint8)
                    
                except:
                    # Timeout or other exception, continue waiting
                    continue
            
            # Write all frames to GIF file
            if frames:
                imageio.mimsave(gif_path, frames, fps=self.fps)
                full_path = os.path.abspath(gif_path)
                print(f"GIF saved successfully: {full_path}")
            else:
                print("No frames to save")
                
        except Exception as e:
            print(f"Error in GIF writer process: {e}")
    
    def enqueue_frame(self, frame: np.ndarray):
        """
        Add a frame to the queue for processing.
        
        Args:
            frame (np.ndarray): Normalized RGBA numpy array (float32)
        """
        if not self.is_create_gif:
            return None
        
        if self.queue is not None:
            self.queue.put(frame)
    
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