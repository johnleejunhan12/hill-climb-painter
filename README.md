# Hill Climb Painter

A Python desktop application that transforms images into paintings
![Image](/readme_stuff/hill_climb_painter.gif "Hill Climb Painter")

## Overview

Hill Climb Painter is an image reconstruction algorithm that transforms images and short animations into painted representations by sequentially placing textured brush strokes. A greedy hill-climbing algorithm is used to iteratively optimize each stroke’s position, rotation, and scale, minimizing the visual difference between the target image and the canvas.

Each brush stroke is assessed for its visual impact before being applied to the canvas, ensuring that only those contributing meaningful detail are added. As more strokes are layered, coarse and abstract forms are gradually refined into a structured and balanced composition, blending realistic detail with the textured aesthetics of impressionism.

## Features

![Image](/readme_stuff/ui_owl.png "Painting of an owl")

### 🎨 Painting application
- **Multiple Format Support**: PNG, JPG, JPEG, and animated GIF inputs
- **High-Resolution Output**: Specify a desired resolution of the final painting (up to 4K)
- **Texture-Based Painting**: Use custom PNG textures such as brush strokes or shapes


### ⏰ Real-Time Visualization
- **Live Painting Display**: Watch the algorithm work in real-time in a pygame display
- **Progress Tracking**: Visualize improvements of texture placements during optimisation process
- **Painting Progress GIFs**: Save time-lapse animations of painting progress

### ⚙️ GUI for parameter customization
- **Persistent settings**: Selected target, texture and parameters are automatically saved
- **Texture Count**: Change how abstract or detailed the painting should be
- **Canvas Computation Size**: Balance between painting quality and speed
- **Texture Optimization**: Adjust iteration ranges and termination thresholds
- **Texture Properties**: Modify size, opacity and scaling behavior of texture
- **Vector Field Equations**: Align textures to a mathematically defined vector field



### ⚡ Performance optimisation
- **Numba Acceleration**: JIT compilation for expensive functions
- **Multiprocessing Support**: Paint multiple GIF frames in parallel



## Installation and setup
### Prerequisites
- Python 3.7 or higher
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/johnleejunhan12/hill-climb-painter.git
cd hill-climb-painter
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```






## Usage
### Step 1: Run the application
```bash
python main.py
```
### Step 2: Select target and textures



### Step 3: Adjust parameters

### Step 4: View the painting process

### Step 5: Obtaining the saved painting





### Creative constraints


### 1) Different textures
The textures used are not limited to just brushstrokes. We can use various shapes such as circles, triangles and squares as the texture. We can also use unusual textures such as lines to produce a chaotic and scribbly abstract rendition of the original image.

### 2) Disable scaling of texture
By setting an initial texture size and restricting it, we can achieve painting styles like pointillism, where small textures are applied in patterns to form an image.



### 3) Vector fields

Vector fields `(f(x,y), g(x,y))` allow us to control texture directionality by constraining brush strokes to align with the field's flow. To demonstrate this, we create a radial sink pattern using the vector field `(-x, -y)`, which causes textures to converge toward a central point. By positioning this convergence point at the cat's nose `(267, 279)`, all brush strokes naturally flow inward, creating a focal point that draws the viewer's attention. 
![Image](/readme_stuff/cat_vector.png "Setting a vector field")
![Image](/readme_stuff/cat.gif "Vector field aligned textures")

### 2) Prevent resizing of textures

### 3) 



## How it works
To generate a painted approximation of a target image using textures, we begin by initializing a blank canvas with the average RGB color of the target image. In this example, we will use 11 different paintstrokes as textures. 
![Image](/readme_stuff/how_work_1.png "Target, texture and canvas")
<br><br>
Initially, a random paint stroke is selected. It is assigned a random scale, position, and rotation. As seen in the image below, its color is computed by taking the average of the RGB values within the corresponding region of the target.
![Image](/readme_stuff/how_work_2_v2.png "Target and canvas")
<br><br>
Next, we need to determine whether the placement of a paint stroke is "good" or "bad".
To achieve this, we define a quantitative scoring system that satisfies the following criteria:


#### **Reward good placements that**:
- **Add more detail** to empty or blurry regions of the canvas, bringing it closer to the target image by filling in underdeveloped areas.
- **Use a suitable color** that closely resembles the corresponding region in the target image. This ensures the paint stroke blends naturally into the canvas.  
  > *Note:* Since the stroke's color is calculated using the average RGB values of the region it would cover, the most suitable colors occur when the target region has low color variance. The painted result will look more cohesive if strokes are placed in areas of consistent color rather than highly varied regions.
- **Maximize coverage** by filling in large areas of empty or blurry canvas without overwriting existing details.



#### Penalize bad placements that:
- **Make the canvas worse** by reducing its similarity to the target image. Such strokes are destructive and lead to a sloppier final result.
- **Overwrite already detailed or accurate areas**, which can undo valuable work already done in previous strokes.
- **Contribute little to no meaningful detail**. For example, placing tiny strokes in nearly empty areas. In such cases, using larger strokes would be more effective and should be encouraged.


### Scoring heuristic:
**1) Finding the error between the target image and canvas**

Pixel errors are calculated using root sum of squared difference between RGB values of the target and canvas.
![Image](/readme_stuff/how_work_3.png "Target, texture and canvas")
<br><br>

**2) Finding the error between the target image and canvas with paint stroke**

We calculate pixel errors again using the same formula but with the texture drawn onto the canvas
![Image](/readme_stuff/how_work_4.png "Target, texture and canvas")
<br><br>

**3) Obtain the difference between errors**

The final score is calculated by taking the difference in errors before and after the texture was added. As seen in the color map plot, textures that are well placed receive a higher score as they reduce the total pixel error between the canvas and target image.
![Image](/readme_stuff/good_score.png "Target, texture and canvas")
<br><br>
#### **Penalizing sub-optimal placements**
If the texture was placed in a suboptimal configuration, it will be penalized as shown in the red (negative) regions of the scoring color plot.
![Image](/readme_stuff/bad_placement.png "Target, texture and canvas")
![Image](/readme_stuff/bad_score.png "Target, texture and canvas")

***

### Greedy Hill Climbing

After an initial score is obtained, the texture undergoes random perturbations to its position, rotation, and scale. After each adjustment, the score is recalculated. If the new configuration yields a higher score, it is accepted; otherwise, the previous configuration is retained. 

![Image](/readme_stuff/scoring_texture_progress.gif "Target, texture and canvas")


This iterative process continues until an iteration limit is reached or terminates after a specified number of failed iterations without further improvement. 

***

### Painting the image
By repeatedly applying the same optimization technique across several hundred strokes, we gradually build up the image, layer by layer, until a coherent painting emerges. The GIF below illustrates the overall painting process where each stroke's position, scale, and rotation are optimized using greedy hill climbing before being committed to the canvas.

![Image](/readme_stuff/mona_lisa_gif_final.gif "Mona Lisa")




## 🎨 What It Does

Hill Climb Painter transforms any image or GIF into a painted version by:

1. **Loading target images** (PNG, JPG, JPEG, GIF) and texture files (PNG)
2. **Optimizing texture placement** using hill climbing algorithm to minimize difference with target
3. **Applying vector field guidance** for directional brush strokes (optional)
4. **Generating high-resolution outputs** with painting progress visualization
5. **Creating animated results** for GIFs with multiprocessing support

## ✨ Key Features

### 🖼️ Image Processing
- **Multiple Format Support**: PNG, JPG, JPEG, and animated GIF inputs
- **Texture-Based Painting**: Use custom PNG textures as brush strokes
- **High-Resolution Output**: Generate images larger than computation size
- **Batch Processing**: Paint multiple frames with multiprocessing

### 🧮 Advanced Algorithm
- **Hill Climbing Optimization**: Iteratively improves texture placement
- **Vector Field Guidance**: Mathematical equations control brush direction
- **Adaptive Iterations**: More optimization for complex areas
- **Early Termination**: Stops when no improvement is found

### 🎛️ Extensive Customization
- **Computation Size**: Balance between quality and speed (10-1000px)
- **Texture Count**: Number of brush strokes (10-10000)
- **Texture Properties**: Size, opacity, scaling behavior
- **Optimization Settings**: Iteration ranges, termination thresholds
- **Vector Field Equations**: Custom mathematical functions (e.g., `-x`, `sin(y)`)

### 📺 Real-Time Visualization
- **Live Painting Display**: Watch the algorithm work in real-time
- **Progress Tracking**: See individual texture improvements
- **Final Image Display**: Preview results immediately
- **Painting Progress GIFs**: Create time-lapse animations

### ⚡ Performance Features
- **Multiprocessing Support**: Parallel frame processing for GIFs
- **Numba Acceleration**: JIT compilation for critical loops
- **Memory Efficient**: Optimized for large images and long animations

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- Virtual environment (recommended)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/hill-climb-painter.git
cd hill-climb-painter
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Dependencies
- **numpy**: Numerical computing for image arrays
- **matplotlib**: Plotting and final image display
- **Pillow**: Image processing (PNG/JPEG/GIF handling)
- **numba**: JIT compilation for performance
- **pygame**: Real-time painting progress display
- **imageio**: GIF creation from frames
- **sympy**: Vector field equation parsing

## 🎮 How to Run

### Main Application (With UI)
```bash
python main.py
```

This launches the full GUI experience:
1. **Target & Texture Selection**: Choose your target image/GIF and texture files
2. **Parameter Configuration**: Customize all painting settings through the UI
3. **Real-Time Painting**: Watch the algorithm work with live visualization
4. **Output Management**: Results saved to `output/` folder




## Parameter configuration



### 4. Configure Parameters

#### **Image Settings**
- **Computation Size**: Resize target for processing (larger = slower but more detailed)
- **Texture Count**: Number of brush strokes to place
- **Texture Opacity**: Transparency of each brush stroke

#### **Optimization Settings**
- **Hill Climb Iterations**: Range of optimization steps per texture
- **Failed Iteration Threshold**: Stop early if no improvement
- **Allow Texture Scaling**: Let textures resize during optimization

#### **Vector Field (Optional)**
- **Enable Vector Field**: Add directional guidance to brush strokes
- **Equations**: Set f(x,y) and g(x,y) functions (e.g., `-x`, `sin(y)`, `x*y`)
- **Origin Shift**: Move the field center point

#### **Output Settings**
- **Output Size**: Final image resolution
- **Create Progress GIF**: Generate time-lapse animation
- **Multiprocessing**: Enable parallel processing for GIFs

### 5. Run & Monitor
- Click "Run" to start the painting algorithm
- Watch real-time progress in the pygame window
- Monitor console output for detailed progress

### 6. Results
Generated files in `output/` folder:
- **High-resolution painted image** (`painted_image_output.png`)
- **Painting progress GIF** (if enabled)
- **Painted GIF frames** (for animated targets)

## 🧬 Vector Field Examples

Vector fields add directional flow to brush strokes:

```python
# Radial sink (converges to center)
f = "-x"
g = "-y"

# Rotational flow
f = "-y" 
g = "x"

# Wave patterns
f = "sin(x)"
g = "cos(y)"

# Complex combinations
f = "-x + sin(y)"
g = "-y + cos(x)"
```

## ⚙️ Advanced Configuration

### Performance Tuning
- **Computation Size**: 50-200 for testing, 300-600 for final output
- **Texture Count**: 100-500 for speed, 1000-5000 for quality
- **Multiprocessing**: Enable for GIFs with 10+ frames

### Quality Settings
- **High Quality**: Large computation size, many textures, high iterations
- **Fast Preview**: Small computation size, few textures, low iterations
- **Balanced**: Medium settings with early termination enabled

### Memory Considerations
- Large GIFs may require significant RAM
- Enable multiprocessing to distribute load
- Consider reducing frame count for very long animations

## 🔧 Troubleshooting

### Common Issues

**"No texture pngs found"**
- Ensure PNG files are in the `texture/` folder
- Check file extensions are `.png` (lowercase)

**"Vector field equations invalid"**
- Use `x` and `y` as variables
- Include `*` for multiplication: `x*y` not `xy`
- Valid functions: `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `abs`

**Performance Issues**
- Reduce computation size or texture count
- Enable early termination
- Use multiprocessing for GIFs

**Memory Errors**
- Reduce computation size
- Process fewer GIF frames
- Close other applications

## 📷 Image Display Troubleshooting

If `![Image](readme_stuff/rainy_original.jpg)` is not displaying:

- **Check the file path:**  
  The path must be relative to the README location.  
  Example: If README is in the root and image is in `readme_stuff/`, use `readme_stuff/rainy_original.jpg`.

- **Verify the file exists:**  
  Make sure `rainy_original.jpg` is present in the `readme_stuff/` folder.

- **Check file extension and case:**  
  File extensions are case-sensitive on some systems.  
  Ensure the file is named exactly `rainy_original.jpg`.

- **GitHub cache:**  
  Sometimes GitHub caches images. Try refreshing or clearing your browser cache.

- **Corrupt image:**  
  Make sure the image file is not corrupted and can be opened locally.

- **Permissions:**  
  The image file should be committed and pushed to the repository.

Example Markdown:


![Image](/readme_stuff/rainy_orignal.jpg)


## 📊 Example Results

The algorithm can produce various artistic styles depending on:
- **Texture choice**: Brush textures, watercolor effects, pointillism
- **Vector field**: Directional flow, swirls, radial patterns  
- **Parameter tuning**: Smooth blending vs. distinct strokes

## 🏗️ Architecture

The project uses a clean OOP architecture:

- **Orchestrator Pattern**: Single entry point (`PaintingOrchestrator`)
- **Component Separation**: Modular design with clear responsibilities
- **Configuration Management**: Structured config objects replace global variables
- **Factory Pattern**: Clean dependency injection
- **Context Managers**: Automatic resource cleanup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Acknowledgments

- Hill climbing optimization algorithm
- Numba team for JIT acceleration
- Pygame community for real-time visualization
- Contributors and testers

![Image](/readme_stuff/gato.png "Mr Cat")

![Image](/readme_stuff/shrek_gif_painted.gif "Somebody")

---

**Ready to create your painted masterpiece? 🎨**

```bash
python main.py
```


## 📁 Project Structure

```
hill-climb-painter/
├── main.py                          # Main GUI application
├── main_without_ui.py               # Command-line version
├── requirements.txt                 # Python dependencies
├── painter/                         # Core painting engine (OOP architecture)
│   ├── orchestrator.py             # Main entry point
│   ├── painting_engine.py          # Core algorithm coordination
│   ├── config.py                   # Configuration management
│   └── components/                  # Modular components
│       ├── hill_climber.py         # Optimization algorithm
│       ├── image_processor.py      # Image loading/processing
│       ├── texture_manager.py      # Texture handling
│       ├── vector_field_factory.py # Vector field creation
│       ├── display_manager.py      # Real-time visualization
│       └── output_manager.py       # Result generation
├── user_interface/                  # GUI components
│   ├── parameter_ui.py             # Main parameter interface
│   ├── target_texture_select_ui.py # File selection UI
│   ├── vector_field_equation_ui.py # Vector field editor
│   └── parameters.json             # UI state persistence
├── utils/                          # Utility functions
│   ├── rectangle.py                # Shape optimization (Numba accelerated)
│   ├── vector_field.py             # Vector field mathematics
│   ├── utilities.py                # Image processing utilities
│   └── file_operations.py          # File management
├── target/                         # Place target images here
├── texture/                        # Place texture PNG files here
├── output/                         # Generated results
├── original_gif_frames/            # Extracted GIF frames (auto-created)
└── painted_gif_frames/             # Painted frames (auto-created)
```
