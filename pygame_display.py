# import time
# import pygame
# import numpy as np
# import random


# class PygameDisplay:
#     def __init__(self, display_height, display_width):
#         self.display_height = display_height
#         self.display_width = display_width
#         self.screen = None # display window will be created unless update_display is called"""

#     def initialize_screen(self):
#         if self.screen is None:
#             pygame.display.init()
#             self.screen = pygame.display.set_mode((self.display_width, self.display_height))
#             pygame.display.set_caption("Hill climbing")

#     def wait_until_closed(self):
#         """Keeps the window open until the user closes it."""
#         running = True
#         while running:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     running = False
#         pygame.quit()

#     def update_display(self, current_image_to_display):
#         """Update the pygame display with the current image (float32 [0,1] RGBA)."""
#         self.initialize_screen()
        
#         # Convert float32 [0,1] to uint8 [0,255]
#         current_image = (current_image_to_display.copy() * 255).astype(np.uint8)

#         # Ensure the array is contiguous and in the right shape (h, w, 4)
#         if current_image.shape[2] != 4:
#             raise ValueError("Image must be RGBA (4 channels)")

#         # Get dimensions (note: current_image.shape = (h, w, 4))
#         height, width = current_image.shape[:2]

#         # Create a Pygame surface from the numpy array
#         surface = pygame.image.frombuffer(
#             current_image.tobytes(),  # Raw byte data
#             (width, height),  # Dimensions (w, h)
#             'RGBA'  # Pixel format
#         )

#         # Display the image
#         self.screen.blit(surface, (0, 0))
#         pygame.display.flip()



# if __name__ == "__main__":
    
#     display = PygameDisplay(500, 500)

#     for i in range(100):
#         # Create test image
#         img = np.zeros((500, 500, 4), dtype=np.float32)
#         img[..., 0] = random.random()
#         img[..., 3] = 1.0  # Alpha
#         display.update_display(img)  # Only now the window appears
#         time.sleep(0.5)
#         display.wait_until_closed()





import pygame
import numpy as np
import random
import time

from multiprocessing import Process, Queue, Value
import ctypes

class PygameDisplayProcess:
    def __init__(self, width, height):
        self.queue = Queue()
        self.closed_flag = Value(ctypes.c_bool, False)  # Shared boolean
        self.process = Process(target=self._run_display, args=(self.queue, self.closed_flag, width, height))
        self.process.start()

    def _run_display(self, queue, closed_flag, width, height):
        pygame.display.init()
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pygame Display")

        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    closed_flag.value = True  # Notify main process

            if not queue.empty():
                img = queue.get()
                img = (img * 255).astype(np.uint8)
                surface = pygame.image.frombuffer(img.tobytes(), (width, height), 'RGBA')
                screen.blit(surface, (0, 0))
                pygame.display.flip()

            clock.tick(30)

        pygame.quit()

    def update_display(self, img):
        if not self.closed_flag.value:  # Optional: prevent sending after window is closed
            self.queue.put(img.copy())

    def was_closed(self):
        """Check if the display window was closed by the user."""
        return self.closed_flag.value

    def close(self):
        self.process.terminate()
        self.process.join()



if __name__ == "__main__":
    display = PygameDisplayProcess(500, 500)

    try:
        for _ in range(100):


            img = np.zeros((500, 500, 4), dtype=np.float32)
            img[..., 0] = random.random()
            img[..., 3] = 1.0
            display.update_display(img)
            time.sleep(0.5)
            print(f"shape {_}")

            if display.was_closed():
                print("Window was closed. Exiting loop.")
                break
    finally:
        display.close()