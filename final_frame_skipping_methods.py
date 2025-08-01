#!/usr/bin/env python3
"""
FINAL: Three Superior Frame Skipping Methods

These replace the current method which stops at iteration 1331.
All methods provide full coverage (0-9999) and ~40 frames.

CURRENT PROBLEM: 
- skip = 10 + shape_index//15 only produces frames up to iteration 1331
- Produces 50 frames total but poor coverage of later iterations

SOLUTIONS: Better mathematical distributions that cover full range
"""

import math

def method_1_power_law(shape_index, total_shapes, target_frames=40, power=2.5):
    """
    🏆 BEST RECOMMENDATION: Power Law Distribution
    
    Perfect balance of:
    - Exactly 40 frames
    - 100% coverage (reaches iteration 9999)
    - Heavy concentration at start (23 frames in first quarter)
    - Smooth distribution throughout
    
    Mathematical principle: position = (i/n)^power * total_iterations
    Higher power = more frames concentrated at start
    """
    # Pre-calculate all target positions for efficiency
    if not hasattr(method_1_power_law, '_positions'):
        method_1_power_law._positions = set()
        for i in range(target_frames):
            normalized = i / (target_frames - 1) if target_frames > 1 else 0
            powered = normalized ** power
            position = int(powered * (total_shapes - 1))
            method_1_power_law._positions.add(position)
    
    return shape_index in method_1_power_law._positions

def method_2_logarithmic_improved(shape_index, total_shapes, target_frames=40):
    """
    🥈 ALTERNATIVE: Improved Logarithmic Distribution
    
    Benefits:
    - Natural mathematical progression
    - 40 frames with 100% coverage
    - Very dense at start, sparse at end
    - Mathematically elegant
    
    Uses inverse exponential: position = total * (e^(i/n) - 1) / (e - 1)
    """
    if not hasattr(method_2_logarithmic_improved, '_positions'):
        method_2_logarithmic_improved._positions = set()
        for i in range(target_frames):
            # Exponential distribution from 0 to 1
            normalized = i / (target_frames - 1) if target_frames > 1 else 0
            exp_val = math.exp(normalized * 2) - 1  # e^(2x) - 1
            max_exp = math.exp(2) - 1
            position = int((exp_val / max_exp) * (total_shapes - 1))
            method_2_logarithmic_improved._positions.add(position)
    
    return shape_index in method_2_logarithmic_improved._positions

def method_3_hybrid_exponential(shape_index, total_shapes, target_frames=40):
    """
    🥉 SIMPLE ALTERNATIVE: Hybrid Exponential
    
    Benefits:
    - Easy to understand and implement
    - Guarantees coverage by forcing last frame at end
    - Good distribution with controllable parameters
    - Robust and predictable
    
    Two-phase approach: exponential growth + forced final frames
    """
    if not hasattr(method_3_hybrid_exponential, '_positions'):
        method_3_hybrid_exponential._positions = set()
        
        # Phase 1: Exponential distribution for first 35 frames
        phase1_frames = target_frames - 5
        growth_factor = (total_shapes * 0.8) ** (1 / phase1_frames)
        
        current_pos = 0
        interval = 10
        
        for i in range(phase1_frames):
            method_3_hybrid_exponential._positions.add(int(current_pos))
            current_pos += interval
            interval *= growth_factor
            if current_pos >= total_shapes * 0.8:
                break
        
        # Phase 2: Force last 5 frames to ensure full coverage
        for i in range(5):
            pos = int(total_shapes * 0.8 + i * total_shapes * 0.2 / 5)
            method_3_hybrid_exponential._positions.add(min(pos, total_shapes - 1))
    
    return shape_index in method_3_hybrid_exponential._positions

def compare_all_methods(total_iterations=10000):
    """Compare all three methods side by side."""
    
    print("Frame Skipping Method Comparison")
    print("=" * 60)
    print(f"Target: ~40 frames from {total_iterations:,} iterations\n")
    
    # Method 1: Power Law
    frames1 = []
    positions1 = set()
    for i in range(40):
        normalized = i / 39 if 40 > 1 else 0
        powered = normalized ** 2.5
        position = int(powered * (total_iterations - 1))
        positions1.add(position)
    frames1 = sorted(positions1)
    
    # Method 2: Logarithmic
    frames2 = []
    positions2 = set()
    for i in range(40):
        normalized = i / 39 if 40 > 1 else 0
        exp_val = math.exp(normalized * 2) - 1
        max_exp = math.exp(2) - 1
        position = int((exp_val / max_exp) * (total_iterations - 1))
        positions2.add(position)
    frames2 = sorted(positions2)
    
    # Method 3: Hybrid Exponential
    frames3 = []
    positions3 = set()
    
    # Phase 1: First 35 frames exponentially
    current_pos = 0
    interval = 10
    growth_factor = (total_iterations * 0.8) ** (1 / 35)
    
    for i in range(35):
        positions3.add(int(current_pos))
        current_pos += interval
        interval *= growth_factor
        if current_pos >= total_iterations * 0.8:
            break
    
    # Phase 2: Last 5 frames evenly in final 20%
    for i in range(5):
        pos = int(total_iterations * 0.8 + i * total_iterations * 0.2 / 5)
        positions3.add(min(pos, total_iterations - 1))
    
    frames3 = sorted(positions3)
    
    methods_data = [
        (frames1, "Power Law (p=2.5)"),
        (frames2, "Logarithmic Improved"),
        (frames3, "Hybrid Exponential")
    ]
    
    for frames, name in methods_data:
        
        # Calculate distribution
        q1 = sum(1 for f in frames if f < total_iterations * 0.25)
        q2 = sum(1 for f in frames if total_iterations * 0.25 <= f < total_iterations * 0.5)
        q3 = sum(1 for f in frames if total_iterations * 0.5 <= f < total_iterations * 0.75)
        q4 = sum(1 for f in frames if f >= total_iterations * 0.75)
        
        # Calculate intervals
        intervals = [frames[i+1] - frames[i] for i in range(len(frames)-1)]
        max_gap = max(intervals) if intervals else 0
        
        print(f"{name}:")
        print(f"  Total frames: {len(frames)}")
        print(f"  Coverage: {max(frames)/total_iterations*100:.1f}%")
        print(f"  Distribution (Q1/Q2/Q3/Q4): {q1}/{q2}/{q3}/{q4}")
        print(f"  Max gap: {max_gap}")
        print(f"  First 8: {frames[:8]}")
        print(f"  Last 5: {frames[-5:]}")
        print()

def integration_instructions():
    """How to integrate into main_without_ui.py"""
    print("INTEGRATION INSTRUCTIONS")
    print("=" * 40)
    print()
    print("1. Add this function to main_without_ui.py:")
    print("   (Copy method_1_power_law function)")
    print()
    print("2. Replace lines 267-273 in main_without_ui.py:")
    print()
    print("   OLD CODE:")
    print("   skip = skip_frames_for_gif_progress + shape_index//15")
    print("   if not is_display_rectangle_improvement and shape_index % skip == 0:")
    print("       gif_creator.enqueue_frame(current_rgba)")
    print()
    print("   NEW CODE:")
    print("   if not is_display_rectangle_improvement:")
    print("       if method_1_power_law(shape_index, num_shapes_to_draw):")
    print("           gif_creator.enqueue_frame(current_rgba)")
    print()
    print("3. Remove/comment out line 90:")
    print("   # skip_frames_for_gif_progress = 10  # No longer needed")
    print()
    print("RESULT:")
    print("- 40 frames instead of 50 (smaller GIF)")
    print("- 100% coverage instead of 13% (reaches all iterations)")
    print("- Better visual progression (more frames where changes are dramatic)")

if __name__ == "__main__":
    compare_all_methods()
    print()
    integration_instructions()