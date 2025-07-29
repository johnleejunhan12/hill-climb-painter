import numpy as np
import random
import time
from multiprocessing import Process, Queue, Value
import ctypes

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

class PygameDisplayProcess:
    def __init__(self, height, width, is_show_pygame_display):
        self.is_show_pygame_display = is_show_pygame_display

        if is_show_pygame_display:
            self.queue = Queue(maxsize=2)  # Small buffer size
            self.closed_flag = Value(ctypes.c_bool, False)
            self.process = Process(target=self._run_display, args=(self.queue, self.closed_flag, width, height))
            self.process.start()
        else:
            self.queue = None
            self.closed_flag = Value(ctypes.c_bool, True)
            self.process = None

    def _run_display(self, queue, closed_flag, width, height):
        if self.is_show_pygame_display:
            # Initialize pygame display window with resizable flag
            pygame.display.init()
            pygame.font.init()
            screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            pygame.display.set_caption("Pygame Display")
            
            font = pygame.font.Font(None, 24)
            running = True
            clock = pygame.time.Clock()
            last_print_time = time.time()
            
            current_img = None
            window_width, window_height = width, height  # Track current window size
            img_shape = None  # Will be set when first image arrives

            while running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        closed_flag.value = True
                    elif event.type == pygame.VIDEORESIZE:
                        window_width, window_height = event.w, event.h
                        screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

                # Method 1: Drain queue and keep only the latest image
                latest_img = None
                items_processed = 0
                
                while not queue.empty():
                    try:
                        latest_img = queue.get_nowait()
                        items_processed += 1
                    except:
                        break
                
                # Update current image if we got a new one
                if latest_img is not None:
                    current_img = latest_img
                    img_shape = current_img.shape if current_img is not None else None
                    # if items_processed > 1:
                    #     print(f"Skipped {items_processed - 1} frames to stay current")
                
                # Display the current image, scaling to fit window while preserving aspect ratio
                if current_img is not None and img_shape is not None:
                    img = (current_img * 255).astype(np.uint8)
                    img_h, img_w = img_shape[0], img_shape[1]
                    img_surface = pygame.image.frombuffer(img.tobytes(), (img_w, img_h), 'RGBA')

                    # Calculate scale factor and position for aspect ratio preservation
                    scale = min(window_width / img_w, window_height / img_h)
                    scaled_w, scaled_h = int(img_w * scale), int(img_h * scale)
                    scaled_surface = pygame.transform.smoothscale(img_surface, (scaled_w, scaled_h))

                    # Center the image
                    x = (window_width - scaled_w) // 2
                    y = (window_height - scaled_h) // 2
                    screen.fill((0, 0, 0))  # Fill background with black
                    screen.blit(scaled_surface, (x, y))
                else:
                    screen.fill((0, 0, 0))
                
                pygame.display.flip()
                
                clock.tick(500)

            pygame.quit()

    def update_display(self, img):
        """Enqueues image, dropping old ones if queue is full"""
        if self.is_show_pygame_display and not self.closed_flag.value:
            try:
                # Try to put without blocking
                self.queue.put_nowait(img.copy())
            except:
                # Queue is full, clear it and put the new image
                try:
                    while not self.queue.empty():
                        self.queue.get_nowait()
                except:
                    pass
                try:
                    self.queue.put_nowait(img.copy())
                except:
                    pass  # If still fails, just skip this frame

    def was_closed(self):
        """Check if the display window was closed by the user."""
        if self.is_show_pygame_display:
            return self.closed_flag.value
        return False

    def close(self):
        """Method to end pygame display process"""
        if self.is_show_pygame_display and self.process:

            if self.queue is not None:
                # First, drain the queue to prevent join_thread() from hanging
                try:
                    while not self.queue.empty():
                        self.queue.get_nowait()
                except:
                    pass
                
                self.queue.close()

                # Add timeout to prevent indefinite hanging
                try:
                    self.queue.join_thread()
                except:
                    print("join_thread failed, but continuing...")
                
            # Terminate the process if it's still alive
            if self.process.is_alive():
                self.process.terminate()

            # Join with timeout to prevent hanging
            self.process.join(timeout=2.0)
            if self.process.is_alive():
                print("Process didn't terminate gracefully, forcing...")
                self.process.kill()
                self.process.join()




# Debugging
if __name__ == "__main__":
    h, w = 300, 400
    display = PygameDisplayProcess(h, w, True)

    try:
        for i in range(500):
            img = np.zeros((h, w, 4), dtype=np.float32)
            img[..., 0] = random.random()
            img[..., 3] = 1.0
            display.update_display(img)
            
            if i % 100 == 0:
                print(f"Iteration {i}")

            if display.was_closed():
                print("Window was closed. Exiting loop.")
                break
                
    finally:
        print("hello")
        display.close()







