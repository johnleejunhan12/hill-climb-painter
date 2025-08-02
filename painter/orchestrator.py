"""
Main orchestrator for the painting system - lightweight entry point.
"""

from typing import List, Dict, Any
from .factory import PaintingEngineFactory


class PaintingOrchestrator:
    """
    Main entry point for the painting system.
    Provides a simple interface that handles all the complexity internally.
    """
    
    @staticmethod
    def paint_from_ui_params(ui_dict: Dict[str, Any], target_path: str, 
                           texture_paths: List[str], output_folder: str, 
                           filename: str, is_gif_target: bool = False) -> bool:
        """
        Paint an image using parameters from the UI.
        This is the main entry point for single image painting.
        
        Args:
            ui_dict: Dictionary containing UI parameters
            target_path: Path to target image file
            texture_paths: List of texture file paths
            output_folder: Folder to save output
            filename: Output filename
            is_gif_target: Whether the target is a GIF file
            
        Returns:
            True if painting completed successfully, False otherwise
        """
        try:
            # Validate inputs
            errors = PaintingOrchestrator.validate_inputs(
                ui_dict, target_path, texture_paths, output_folder, filename
            )
            if errors:
                print(f"❌ Validation errors: {'; '.join(errors)}")
                return False
            
            # Create engine and execute painting
            engine = PaintingEngineFactory.create_from_ui_dict(
                ui_dict, is_gif_target, is_multiprocessing_worker=False
            )
            
            # Print configuration summary
            config_summary = engine.get_config_summary()
            print("🎨 Painting Configuration:")
            for category, settings in config_summary.items():
                print(f"  {category}: {settings}")
            
            # Execute painting
            return engine.paint_image(target_path, texture_paths, output_folder, filename)
            
        except Exception as e:
            print(f"❌ Orchestrator error: {e}")
            return False
    
    @staticmethod
    def paint_batch_frames(frame_paths: List[str], texture_paths: List[str],
                          output_folder: str, ui_dict: Dict[str, Any], 
                          use_multiprocessing: bool = False) -> bool:
        """
        Paint multiple frames (for GIF processing).
        
        Args:
            frame_paths: List of frame image paths
            texture_paths: List of texture file paths
            output_folder: Folder to save outputs
            ui_dict: UI parameter dictionary
            use_multiprocessing: Whether to use multiprocessing
            
        Returns:
            True if all frames painted successfully, False otherwise
        """
        if use_multiprocessing:
            return PaintingOrchestrator._paint_batch_parallel(
                frame_paths, texture_paths, output_folder, ui_dict
            )
        else:
            return PaintingOrchestrator._paint_batch_sequential(
                frame_paths, texture_paths, output_folder, ui_dict
            )
    
    @staticmethod
    def _paint_batch_sequential(frame_paths: List[str], texture_paths: List[str],
                               output_folder: str, ui_dict: Dict[str, Any]) -> bool:
        """Paint frames sequentially with per-frame vector field support"""
        try:
            print(f"🔄 Painting {len(frame_paths)} frames sequentially...")
            
            # Extract vector field coordinates for per-frame processing
            coordinates = ui_dict.get("vector_field_origin_shift", [[0, 0]])
            has_per_frame_coords = len(coordinates) > 1
            
            if has_per_frame_coords and ui_dict.get("enable_vector_field", False):
                print(f"📍 Using per-frame vector field coordinates ({len(coordinates)} coordinates available)")
            
            for i, frame_path in enumerate(frame_paths):
                # Create frame-specific ui_dict with updated vector field coordinates
                frame_ui_dict = ui_dict.copy()
                
                # Extract frame-specific coordinates if available
                if has_per_frame_coords and i < len(coordinates):
                    frame_ui_dict["vector_field_origin_shift"] = [coordinates[i]]
                    coord_info = f"coords=({coordinates[i][0]}, {coordinates[i][1]})" if len(coordinates[i]) >= 2 else "coords=default"
                else:
                    coord_info = "coords=default"
                
                # Create engine for this frame with frame-specific config
                engine = PaintingEngineFactory.create_from_ui_dict(
                    frame_ui_dict, is_gif_target=True, is_multiprocessing_worker=False
                )
                
                filename = f"frame_{i:04d}"
                print(f"  Processing frame {i+1}/{len(frame_paths)}: {coord_info}")
                
                success = engine.paint_image(frame_path, texture_paths, output_folder, filename)
                if not success:
                    print(f"❌ Failed to paint frame {i}: {frame_path}")
                    return False
            
            if has_per_frame_coords:
                print(f"✅ Successfully painted {len(frame_paths)} frames with frame-specific vector fields")
            else:
                print(f"✅ Successfully painted {len(frame_paths)} frames")
            return True
            
        except Exception as e:
            print(f"❌ Batch sequential painting failed: {e}")
            return False
    
    @staticmethod
    def _paint_batch_parallel(frame_paths: List[str], texture_paths: List[str],
                             output_folder: str, ui_dict: Dict[str, Any]) -> bool:
        """Paint frames using multiprocessing with per-frame vector field support"""
        try:
            import multiprocessing
            from .config import PaintingConfig

            coordinates = ui_dict.get("vector_field_origin_shift", [[0, 0]])
            has_per_frame_coords = len(coordinates) > 1
            
            if has_per_frame_coords and ui_dict.get("enable_vector_field", False):
                print(f"📍 Using per-frame vector field coordinates ({len(coordinates)} coordinates available)")
            
            # Prepare work items with frame-specific coordinates
            work_items = []
            for i, frame_path in enumerate(frame_paths):
                # Create frame-specific ui_dict
                frame_ui_dict = ui_dict.copy()
                if has_per_frame_coords and i < len(coordinates):
                    frame_ui_dict["vector_field_origin_shift"] = [coordinates[i]]
                
                # Create frame-specific config
                config = PaintingConfig.from_ui_dict(frame_ui_dict, is_gif_target=True)
                config_dict = config.to_serializable_dict()
                config_dict['ui_dict'] = frame_ui_dict
                
                work_items.append({
                    'frame_path': frame_path,
                    'texture_paths': texture_paths,
                    'output_folder': output_folder,
                    'filename': f"frame_{i:04d}",
                    'config_dict': config_dict,
                    'frame_index': i  # Include frame index for debugging
                })

            # Determine worker count
            cpu_percentage = work_items[0]['config_dict']['multiprocessing']['cpu_usage_percentage']
            num_workers = max(1, int(multiprocessing.cpu_count() * cpu_percentage))
            num_workers = min(num_workers, len(work_items))
            
            print(f"🔄 Painting {len(frame_paths)} frames using {num_workers} workers...")
            
            # Execute in parallel
            with multiprocessing.Pool(processes=num_workers) as pool:
                results = pool.map(_paint_worker_function, work_items)
            
            # Check results
            successful = sum(results)
            total = len(results)
            
            if successful == total:
                if has_per_frame_coords:
                    print(f"✅ Successfully painted {successful}/{total} frames with frame-specific vector fields")
                else:
                    print(f"✅ Successfully painted {successful}/{total} frames")
                return True
            else:
                print(f"⚠ Painted {successful}/{total} frames (some failed)")
                return False
                
        except Exception as e:
            print(f"❌ Batch parallel painting failed: {e}")
            return False
    
    @staticmethod
    def validate_inputs(ui_dict: Dict[str, Any], target_path: str, 
                       texture_paths: List[str], output_folder: str, 
                       filename: str) -> List[str]:
        """
        Validate all inputs for painting operation.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate UI dictionary
        ui_errors = PaintingEngineFactory.validate_ui_dict(ui_dict)
        errors.extend(ui_errors)
        
        # Validate file paths
        if not target_path or not target_path.strip():
            errors.append("Target path cannot be empty")
        
        if not texture_paths or len(texture_paths) == 0:
            errors.append("At least one texture path must be provided")
        
        if not output_folder or not output_folder.strip():
            errors.append("Output folder cannot be empty")
        
        if not filename or not filename.strip():
            errors.append("Filename cannot be empty")
        
        return errors
    
    @staticmethod
    def get_default_ui_dict() -> Dict[str, Any]:
        """
        Get a default UI dictionary for testing purposes.
        
        Returns:
            Default UI parameter dictionary
        """
        return {
            'computation_size': 200,
            'num_textures': 50,
            'hill_climb_min_iterations': 20,
            'hill_climb_max_iterations': 50,
            'texture_opacity': 100,
            'initial_texture_width': 20,
            'uniform_texture_size': False,
            'failed_iterations_threshold': 100,
            'enable_vector_field': False,
            'vector_field_f': '',
            'vector_field_g': '',
            'vector_field_origin_shift': [[0, 0]],
            'display_painting_progress': True,
            'display_placement_progress': False,
            'display_final_image': False,
            'output_image_name': 'painted_output',
            'create_gif_of_painting_progress': False,
            'painting_progress_gif_name': ''
        }


def _paint_worker_function(work_item: Dict[str, Any]) -> bool:
    """
    Worker function for multiprocessing.
    Must be at module level for Windows compatibility.
    
    Args:
        work_item: Dictionary containing work parameters
        
    Returns:
        True if painting succeeded, False otherwise
    """
    try:
        # Extract work parameters
        frame_path = work_item['frame_path']
        texture_paths = work_item['texture_paths']
        output_folder = work_item['output_folder']
        filename = work_item['filename']
        config_dict = work_item['config_dict']
        
        # Create worker engine
        engine = PaintingEngineFactory.create_worker_engine(config_dict)
        
        # Execute painting
        return engine.paint_image(frame_path, texture_paths, output_folder, filename)
        
    except Exception as e:
        print(f"❌ Worker failed for {work_item.get('frame_path', 'unknown')}: {e}")
        return False 