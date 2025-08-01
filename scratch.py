def compute_power_law_frame_positions(total_shapes: int, target_frames: int = 40, power: float = 2.5) -> set:
    """
    Pre-compute frame positions using power law distribution.
    
    Args:
        total_shapes: Total number of shapes to be painted
        target_frames: Desired number of frames (~40)
        power: Power law exponent (higher = more frames at start)
        
    Returns:
        Set of shape indices where frames should be recorded
    """
    positions = []
    for i in range(target_frames):
        normalized = i / (target_frames - 1) if target_frames > 1 else 0
        powered = normalized ** power
        position = int(powered * (total_shapes - 1))
        positions.append(position)
    return positions


if __name__ == "__main__":
    positions = compute_power_law_frame_positions(total_shapes=10000, target_frames=60, power=2.5)
    print(positions)
    print(len(positions))