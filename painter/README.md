# Painter Package - Clean OOP Architecture

This package provides a clean, object-oriented architecture for the hill-climb painting algorithm, replacing the global variable dependencies with proper configuration management and component separation.

## ✅ Phase 1: Configuration Management (COMPLETED)

### Overview
Replaces scattered global variables with structured configuration objects.

### Components

#### Configuration Classes
- **`ImageConfig`** - Image processing and sizing parameters
- **`HillClimbConfig`** - Hill climbing optimization parameters  
- **`VectorFieldConfig`** - Vector field guidance parameters
- **`DisplayConfig`** - Display and visualization options
- **`OutputConfig`** - Output generation settings
- **`MultiprocessingConfig`** - Multiprocessing options

#### Main Configuration Class
- **`PaintingConfig`** - Aggregates all configuration objects
  - `from_ui_dict()` - Creates config from UI parameter dictionary
  - `to_serializable_dict()` - Converts to serializable format for multiprocessing
  - `from_serializable_dict()` - Recreates config from serialized data
  - Built-in validation for all parameters

### Benefits
- ✅ **No Global Variables** - All parameters properly encapsulated
- ✅ **Type Safety** - Strong typing with dataclasses
- ✅ **Validation** - Automatic parameter validation with clear error messages
- ✅ **Multiprocessing Safe** - Serializable configurations
- ✅ **Easy Testing** - Isolated configuration objects

## ✅ Phase 2: Core Components (COMPLETED)

### Overview
Encapsulates painting algorithm components with clear responsibilities.

### Components

#### `ImageProcessor`
Handles image loading and canvas creation.
```python
processor = ImageProcessor()
target = processor.load_target(filepath, config.image)
canvas = processor.create_canvas(target)
height, width = processor.get_canvas_dimensions(target)
```

#### `TextureManager`
Manages texture loading and organization.
```python
manager = TextureManager()
texture_dict = manager.load_textures(texture_paths, config.image)
texture_key, texture_data = manager.get_random_texture()
greyscale_alpha, height, width = manager.get_texture_info(key)
```

#### `VectorFieldFactory`
Creates vector field objects from configurations.
```python
factory = VectorFieldFactory()
vector_field = factory.create_from_config(config.vector_field, height, width)
is_valid = factory.validate_equations('-x', '-y')
```

#### `HillClimber`
Handles optimization logic for shape placement.
```python
climber = HillClimber(config.hill_climb)
result = climber.optimize_shape(target, texture_key, texture_data, canvas, vector_field, shape_index)
updated_canvas = climber.apply_shape_to_canvas(canvas, target, result, texture_data)
```

### Benefits
- ✅ **Single Responsibility** - Each component has one clear purpose
- ✅ **Dependency Injection** - Components receive dependencies explicitly
- ✅ **Easy Testing** - Components can be unit tested independently
- ✅ **Reusable** - Components can be used in different contexts
- ✅ **Clear Interfaces** - Well-defined methods and return types

## ✅ Phase 3: Display & Output Management (COMPLETED)

### Overview
Manages visualization and output generation with clean separation of concerns.

### Components

#### `DisplayManager`
Handles pygame displays and matplotlib visualization.
```python
with DisplayManager(config.display, height, width) as display_mgr:
    display_mgr.update_display(canvas)
    display_mgr.show_final_image(canvas)
    if display_mgr.was_closed():
        break  # User closed window
```

#### `OutputManager`
Manages high-resolution image creation and progress GIFs.
```python
with OutputManager(config.output, is_multiprocessing_worker=False) as output_mgr:
    output_mgr.setup_output_generators(texture_dict, height, width, target, output_size)
    output_mgr.record_frame(canvas)
    output_mgr.enqueue_shape_for_output(optimization_result)
    output_mgr.finalize_and_save(output_folder, filename)
```

### Benefits
- ✅ **Context Management** - Automatic resource cleanup
- ✅ **Separation of Concerns** - Display and output handled independently
- ✅ **Multiprocessing Safe** - Proper handling of worker vs main process modes
- ✅ **Error Handling** - Graceful degradation when displays fail

## ✅ Phase 4: Main Painting Engine (COMPLETED)

### Overview
Orchestrates all components to execute the complete painting algorithm.

### Main Class

#### `PaintingEngine`
The core engine that coordinates all components.
```python
engine = PaintingEngine(config, is_multiprocessing_worker=False)
success = engine.paint_image(target_path, texture_paths, output_folder, filename)

# Get configuration summary
summary = engine.get_config_summary()

# Validate inputs
errors = engine.validate_inputs(target_path, texture_paths, output_folder)
```

### Benefits
- ✅ **Orchestration** - Clean coordination of all components
- ✅ **Context Management** - Proper setup and cleanup
- ✅ **Error Handling** - Comprehensive error management
- ✅ **Progress Reporting** - Clear feedback during painting process

## ✅ Phase 5: Factory & Orchestrator (COMPLETED)

### Overview
Provides factory methods and lightweight entry points for the painting system.

### Components

#### `PaintingEngineFactory`
Factory for creating engine instances with dependency injection.
```python
# Create from UI parameters
engine = PaintingEngineFactory.create_from_ui_dict(ui_dict, is_gif_target=False)

# Create for multiprocessing worker
worker_engine = PaintingEngineFactory.create_worker_engine(config_dict)

# Validate configuration
errors = PaintingEngineFactory.validate_ui_dict(ui_dict)
```

#### `PaintingOrchestrator`
Main entry point - lightweight orchestrator that handles all complexity.
```python
# Paint single image
success = PaintingOrchestrator.paint_from_ui_params(
    ui_dict=ui_parameters,
    target_path="image.png",
    texture_paths=["texture1.png", "texture2.png"],
    output_folder="output",
    filename="painted_image"
)

# Paint batch frames (GIF processing)
success = PaintingOrchestrator.paint_batch_frames(
    frame_paths=gif_frames,
    texture_paths=texture_paths,
    output_folder="painted_frames",
    ui_dict=ui_parameters,
    use_multiprocessing=True
)
```

### Benefits
- ✅ **Simple Interface** - Single entry point for all operations
- ✅ **Factory Pattern** - Clean dependency injection
- ✅ **Multiprocessing Support** - Built-in parallel processing for batch operations
- ✅ **Input Validation** - Comprehensive validation before processing

## Complete Usage Example

```python
from painter import PaintingOrchestrator

# Example UI parameters (from your parameter UI)
ui_parameters = {
    'computation_size': 200,
    'num_textures': 100,
    'hill_climb_min_iterations': 20,
    'hill_climb_max_iterations': 50,
    'texture_opacity': 100,
    'initial_texture_width': 20,
    'uniform_texture_size': False,
    'failed_iterations_threshold': 100,
    'enable_vector_field': True,
    'vector_field_f': '-x',
    'vector_field_g': '-y',
    'vector_field_origin_shift': [[100, 150]],
    'display_painting_progress': True,
    'display_placement_progress': False,
    'display_final_image': True,
    'output_image_name': 'my_painted_image',
    'output_image_size': 2000,
    'create_gif_of_painting_progress': True,
    'painting_progress_gif_name': 'painting_progress'
}

# Paint a single image
success = PaintingOrchestrator.paint_from_ui_params(
    ui_dict=ui_parameters,
    target_path="target/my_image.jpg",
    texture_paths=["texture/brush1.png", "texture/brush2.png"],
    output_folder="output",
    filename="painted_result",
    is_gif_target=False
)

if success:
    print("🎉 Painting completed successfully!")
else:
    print("❌ Painting failed")
```

## Integration with main.py

The `run_painting_algorithm` function in `main.py` has been completely rewritten to use this new architecture:

```python
def run_painting_algorithm(param_dict):
    """Execute the painting algorithm using the new OOP architecture."""
    
    is_gif_target = TARGET_FILEPATH.lower().endswith('.gif')
    
    if is_gif_target:
        # Handle GIF - paint multiple frames
        success = PaintingOrchestrator.paint_batch_frames(
            frame_paths=ORIGINAL_GIF_FRAMES_FILE_PATH_LIST,
            texture_paths=TEXTURE_FILEPATH_LIST,
            output_folder=PAINTED_GIF_FRAMES_FULL_FOLDER_PATH,
            ui_dict=param_dict,
            use_multiprocessing=param_dict.get('enable_multiprocessing', False)
        )
    else:
        # Handle single image
        success = PaintingOrchestrator.paint_from_ui_params(
            ui_dict=param_dict,
            target_path=TARGET_FILEPATH,
            texture_paths=TEXTURE_FILEPATH_LIST,
            output_folder=get_output_folder_full_filepath(),
            filename=param_dict.get('output_image_name', 'painted_image'),
            is_gif_target=False
        )
```

## Testing

Run the comprehensive demo to see all components in action:
```bash
python -m painter.demo
```

## Architecture Benefits

This complete architecture provides:

1. **Maintainability** - Changes isolated to specific components
2. **Testability** - Each component can be unit tested
3. **Extensibility** - Easy to add new features without breaking existing code
4. **Readability** - Clear separation of concerns
5. **Multiprocessing Safety** - No unpicklable objects or global state
6. **Performance** - Efficient component reuse and clean interfaces
7. **Error Handling** - Comprehensive error management at all levels
8. **Resource Management** - Proper cleanup with context managers
9. **Progress Reporting** - Clear feedback during long operations
10. **Configuration Validation** - Prevents runtime errors with early validation

## Multiprocessing Support

The system includes built-in multiprocessing support for batch operations:

- **Serializable Configurations** - All configs can be safely passed between processes
- **Worker Functions** - Module-level functions compatible with Windows multiprocessing
- **Resource Management** - Proper handling of displays and outputs in worker processes
- **Error Handling** - Failed workers don't crash the entire batch

## Migration from Global Variables

The implementation completely eliminates the global variable dependencies:

| Old Global Variables | New Architecture |
|---------------------|------------------|
| `resize_target_shorter_side_of_target` | `config.image.computation_size` |
| `num_shapes_to_draw` | `config.hill_climb.num_textures` |
| `min_hill_climb_iterations` | `config.hill_climb.min_iterations` |
| `is_enable_vector_field` | `config.vector_field.enabled` |
| `vector_field_function` | Created by `VectorFieldFactory` |
| `is_show_pygame_display_window` | `config.display.show_pygame` |
| And 15+ other globals... | All properly encapsulated |

The transformation is complete - the monolithic, global-variable-dependent code is now a clean, professional, maintainable system that follows established software engineering principles. 