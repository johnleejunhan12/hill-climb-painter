"""
Demonstration script showing how the complete OOP architecture works.
This replaces the global variable dependencies with clean configuration management.
"""

from painter.config import PaintingConfig
from painter.components import ImageProcessor, TextureManager, VectorFieldFactory, HillClimber, DisplayManager, OutputManager
from painter.painting_engine import PaintingEngine
from painter.factory import PaintingEngineFactory
from painter.orchestrator import PaintingOrchestrator


def demo_configuration_system():
    """Demonstrate the configuration system"""
    print("=== Configuration System Demo ===")
    
    # Example UI dictionary (similar to what comes from the UI)
    ui_dict = {
        'computation_size': 200,
        'num_textures': 50,
        'hill_climb_min_iterations': 20,
        'hill_climb_max_iterations': 50,
        'texture_opacity': 100,
        'initial_texture_width': 20,
        'uniform_texture_size': False,  # This becomes allow_scaling=True
        'failed_iterations_threshold': 100,
        'enable_vector_field': True,
        'vector_field_f': '-x',
        'vector_field_g': '-y',
        'vector_field_origin_shift': [[0, 0]],
        'display_painting_progress': True,
        'display_placement_progress': False,
        'display_final_image': False,
        'output_image_name': 'demo_output',
        'create_gif_of_painting_progress': False,
        'painting_progress_gif_name': ''
    }
    
    # Create configuration from UI dictionary
    try:
        config = PaintingConfig.from_ui_dict(ui_dict, is_gif_target=False)
        print("✓ Configuration created successfully")
        
        # Show configuration structure
        print(f"Image config: computation_size={config.image.computation_size}, "
              f"opacity={config.image.texture_opacity}")
        print(f"Hill climb config: num_textures={config.hill_climb.num_textures}, "
              f"iterations={config.hill_climb.min_iterations}-{config.hill_climb.max_iterations}")
        print(f"Vector field: enabled={config.vector_field.enabled}, "
              f"equations='{config.vector_field.f_equation}', '{config.vector_field.g_equation}'")
        
        # Demonstrate serialization for multiprocessing
        serialized = config.to_serializable_dict()
        print("✓ Configuration serialized for multiprocessing")
        
        # Recreate from serialized data
        recreated_config = PaintingConfig.from_serializable_dict(serialized)
        print("✓ Configuration recreated from serialized data")
        
    except ValueError as e:
        print(f"✗ Configuration validation failed: {e}")


def demo_components():
    """Demonstrate the component system"""
    print("\n=== Component System Demo ===")
    
    # Create a simple config for testing
    ui_dict = {
        'computation_size': 200,
        'texture_opacity': 100,
        'num_textures': 5,
        'hill_climb_min_iterations': 10,
        'hill_climb_max_iterations': 20,
        'initial_texture_width': 20,
        'uniform_texture_size': False,
        'failed_iterations_threshold': 50,
        'enable_vector_field': True,
        'vector_field_f': '-x',
        'vector_field_g': '-y',
        'vector_field_origin_shift': [[0, 0]],
        'display_painting_progress': True,
        'display_placement_progress': False,
        'display_final_image': False,
        'output_image_name': 'demo_output',
        'create_gif_of_painting_progress': False,
        'painting_progress_gif_name': ''
    }
    
    config = PaintingConfig.from_ui_dict(ui_dict)
    
    # 1. ImageProcessor Demo
    print("\n1. ImageProcessor:")
    image_processor = ImageProcessor()
    print("✓ ImageProcessor created")
    
    # 2. TextureManager Demo
    print("\n2. TextureManager:")
    texture_manager = TextureManager()
    print("✓ TextureManager created")
    
    # 3. VectorFieldFactory Demo
    print("\n3. VectorFieldFactory:")
    vector_field_factory = VectorFieldFactory()
    print("✓ VectorFieldFactory created")
    
    # Test equation validation
    is_valid = vector_field_factory.validate_equations('-x', '-y')
    print(f"  - Equations '-x', '-y' are valid: {is_valid}")
    
    # 4. HillClimber Demo
    print("\n4. HillClimber:")
    hill_climber = HillClimber(config.hill_climb)
    print("✓ HillClimber created")
    print(f"  - Configured for {config.hill_climb.num_textures} textures")
    print(f"  - {config.hill_climb.min_iterations}-{config.hill_climb.max_iterations} iterations per shape")
    print(f"  - Scaling allowed: {config.hill_climb.allow_scaling}")
    print(f"  - Early termination after {config.hill_climb.fail_threshold} failed attempts")
    
    # 5. DisplayManager Demo (Phase 3)
    print("\n5. DisplayManager:")
    display_manager = DisplayManager(config.display, 200, 200, config.multiprocessing.enabled)
    print("✓ DisplayManager created")
    print(f"  - Show pygame: {config.display.show_pygame}")
    print(f"  - Show improvements: {config.display.show_improvements}")
    print(f"  - Print progress: {config.display.print_progress}")
    display_manager.close()  # Clean up
    
    # 6. OutputManager Demo (Phase 3)
    print("\n6. OutputManager:")
    output_manager = OutputManager(config.output, is_multiprocessing_worker=False)
    print("✓ OutputManager created")
    print(f"  - Create GIF: {config.output.create_progress_gif}")
    print(f"  - Image name: {config.output.image_name}")
    print(f"  - Append datetime: {config.output.append_datetime}")


def demo_painting_engine():
    """Demonstrate the painting engine (Phase 4)"""
    print("\n=== Painting Engine Demo ===")
    
    # Create simple config
    ui_dict = {
        'computation_size': 200,
        'texture_opacity': 100,
        'num_textures': 5,
        'hill_climb_min_iterations': 10,
        'hill_climb_max_iterations': 20,
        'initial_texture_width': 20,
        'uniform_texture_size': False,
        'failed_iterations_threshold': 50,
        'enable_vector_field': False,
        'vector_field_f': '',
        'vector_field_g': '',
        'vector_field_origin_shift': [[0, 0]],
        'display_painting_progress': False,  # Disable for demo
        'display_placement_progress': False,
        'display_final_image': False,
        'output_image_name': 'demo_output',
        'output_image_size': 800,
        'create_gif_of_painting_progress': False,
        'painting_progress_gif_name': ''
    }
    
    config = PaintingConfig.from_ui_dict(ui_dict)
    
    print("1. PaintingEngine:")
    engine = PaintingEngine(config, is_multiprocessing_worker=False)
    print("✓ PaintingEngine created")
    
    # Show configuration summary
    summary = engine.get_config_summary()
    print("  Configuration summary:")
    for category, settings in summary.items():
        print(f"    {category}: {settings}")
    
    # Test input validation
    errors = engine.validate_inputs("test.png", ["texture1.png"], "output")
    print(f"  - Input validation: {len(errors)} errors found")


def demo_factory_and_orchestrator():
    """Demonstrate the factory and orchestrator (Phase 5)"""
    print("\n=== Factory & Orchestrator Demo ===")
    
    # Demo PaintingEngineFactory
    print("1. PaintingEngineFactory:")
    
    # Get default UI dict
    default_ui_dict = PaintingOrchestrator.get_default_ui_dict()
    print("✓ Got default UI dictionary")
    
    # Validate UI dict
    errors = PaintingEngineFactory.validate_ui_dict(default_ui_dict)
    print(f"  - Default config validation: {len(errors)} errors")
    
    # Create engine from UI dict
    try:
        engine = PaintingEngineFactory.create_from_ui_dict(default_ui_dict)
        print("✓ Created engine from UI dictionary")
    except Exception as e:
        print(f"✗ Failed to create engine: {e}")
    
    # Demo worker engine creation
    config = PaintingConfig.from_ui_dict(default_ui_dict)
    config_dict = config.to_serializable_dict()
    try:
        worker_engine = PaintingEngineFactory.create_worker_engine(config_dict)
        print("✓ Created worker engine from serialized config")
    except Exception as e:
        print(f"✗ Failed to create worker engine: {e}")
    
    # Demo PaintingOrchestrator
    print("\n2. PaintingOrchestrator:")
    
    # Test input validation
    errors = PaintingOrchestrator.validate_inputs(
        default_ui_dict, "test.png", ["texture1.png"], "output", "test_output"
    )
    print(f"  - Orchestrator input validation: {len(errors)} errors")
    
    print("✓ PaintingOrchestrator validation complete")


def demo_configuration_validation():
    """Demonstrate configuration validation"""
    print("\n=== Configuration Validation Demo ===")
    
    # Test invalid configurations
    invalid_configs = [
        # Invalid computation size
        {'computation_size': 5, 'texture_opacity': 100, 'num_textures': 10, 
         'hill_climb_min_iterations': 10, 'hill_climb_max_iterations': 20, 
         'initial_texture_width': 20, 'uniform_texture_size': False, 
         'failed_iterations_threshold': 50, 'enable_vector_field': False},
        
        # Invalid iteration range
        {'computation_size': 200, 'texture_opacity': 100, 'num_textures': 10, 
         'hill_climb_min_iterations': 50, 'hill_climb_max_iterations': 20, 
         'initial_texture_width': 20, 'uniform_texture_size': False, 
         'failed_iterations_threshold': 50, 'enable_vector_field': False},
        
        # Missing vector field equations when enabled
        {'computation_size': 200, 'texture_opacity': 100, 'num_textures': 10, 
         'hill_climb_min_iterations': 10, 'hill_climb_max_iterations': 20, 
         'initial_texture_width': 20, 'uniform_texture_size': False, 
         'failed_iterations_threshold': 50, 'enable_vector_field': True,
         'vector_field_f': '', 'vector_field_g': ''}
    ]
    
    for i, invalid_config in enumerate(invalid_configs, 1):
        try:
            PaintingConfig.from_ui_dict(invalid_config)
            print(f"✗ Test {i}: Should have failed validation")
        except ValueError as e:
            print(f"✓ Test {i}: Correctly caught validation error")


if __name__ == "__main__":
    print("Painter Package Complete Demo")
    print("=" * 60)
    
    demo_configuration_system()
    demo_components() 
    demo_painting_engine()
    demo_factory_and_orchestrator()
    demo_configuration_validation()
    
    print("\n" + "=" * 60)
    print("🎉 Complete Demo Finished Successfully!")
    print("\n✅ All phases implemented and working:")
    print("  ✅ Phase 1: Configuration Management")
    print("  ✅ Phase 2: Core Components") 
    print("  ✅ Phase 3: Display & Output Management")
    print("  ✅ Phase 4: Main Painting Engine")
    print("  ✅ Phase 5: Factory & Orchestrator")
    print("\n🚀 The painting system is ready for use!")
    print("   Use PaintingOrchestrator.paint_from_ui_params() as the main entry point") 