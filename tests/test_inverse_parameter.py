#!/usr/bin/env python3
"""
Test script to verify the new inverse parameter works correctly.
"""

import numpy as np
import pyslammer as slam


def test_inverse_parameter():
    """Test that the inverse parameter correctly inverts the results."""
    print("=== Testing Inverse Parameter ===")
    
    # Load a sample ground motion
    motions = slam.sample_ground_motions()
    motion_key = "Cape_Mendocino_1992_PET-090"
    motion = motions[motion_key]
    
    # Test parameters
    ky = 0.15
    target_pga = 0.2
    
    print(f"Testing with {motion_key}")
    print(f"ky = {ky} g, target_pga = {target_pga} g")
    
    # Test rigid analysis
    print("\n--- Rigid Analysis ---")
    rigid_normal = slam.RigidAnalysis(ky=ky, ground_motion=motion, target_pga=target_pga, inverse=False)
    rigid_inverse = slam.RigidAnalysis(ky=ky, ground_motion=motion, target_pga=target_pga, inverse=True)
    
    print(f"Normal displacement: {rigid_normal.max_sliding_disp * 100:.3f} cm")
    print(f"Inverse displacement: {rigid_inverse.max_sliding_disp * 100:.3f} cm")
    print(f"Normal scale factor: {rigid_normal.scale_factor:.3f}")
    print(f"Inverse scale factor: {rigid_inverse.scale_factor:.3f}")
    
    # Verify that inverse has opposite scale factor
    assert rigid_inverse.scale_factor == -rigid_normal.scale_factor, "Scale factors should be opposites"
    
    # Test decoupled analysis
    print("\n--- Decoupled Analysis ---")
    flexible_params = {
        "height": 50,
        "vs_slope": 600,
        "vs_base": 600,
        "damp_ratio": 0.05,
        "ref_strain": 0.05,
        "soil_model": "linear_elastic"
    }
    
    decoupled_normal = slam.Decoupled(
        ky=ky, ground_motion=motion, target_pga=target_pga, inverse=False, **flexible_params
    )
    decoupled_inverse = slam.Decoupled(
        ky=ky, ground_motion=motion, target_pga=target_pga, inverse=True, **flexible_params
    )
    
    print(f"Normal displacement: {decoupled_normal.max_sliding_disp * 100:.3f} cm")
    print(f"Inverse displacement: {decoupled_inverse.max_sliding_disp * 100:.3f} cm")
    print(f"Normal scale factor: {decoupled_normal.scale_factor:.3f}")
    print(f"Inverse scale factor: {decoupled_inverse.scale_factor:.3f}")
    
    # Verify that inverse has opposite scale factor
    assert decoupled_inverse.scale_factor == -decoupled_normal.scale_factor, "Scale factors should be opposites"
    
    # Test coupled analysis
    print("\n--- Coupled Analysis ---")
    coupled_normal = slam.Coupled(
        ky=ky, ground_motion=motion, target_pga=target_pga, inverse=False, **flexible_params
    )
    coupled_inverse = slam.Coupled(
        ky=ky, ground_motion=motion, target_pga=target_pga, inverse=True, **flexible_params
    )
    
    print(f"Normal displacement: {coupled_normal.max_sliding_disp * 100:.3f} cm")
    print(f"Inverse displacement: {coupled_inverse.max_sliding_disp * 100:.3f} cm")
    print(f"Normal scale factor: {coupled_normal.scale_factor:.3f}")
    print(f"Inverse scale factor: {coupled_inverse.scale_factor:.3f}")
    
    # Verify that inverse has opposite scale factor
    assert coupled_inverse.scale_factor == -coupled_normal.scale_factor, "Scale factors should be opposites"
    
    print("\n✓ All tests passed! The inverse parameter works correctly.")


def test_old_vs_new_approach():
    """Compare the old approach (manual negation) vs new approach (inverse parameter)."""
    print("\n=== Comparing Old vs New Approach ===")
    
    # Load a sample ground motion
    motions = slam.sample_ground_motions()
    motion_key = "Cape_Mendocino_1992_PET-090"
    motion = motions[motion_key]
    
    ky = 0.15
    target_pga = 0.2
    
    # Old approach: manually create GroundMotion with negated acceleration
    import copy
    old_motion = copy.deepcopy(motion)
    old_motion.accel = -motion.accel  # Manually negate
    old_motion.name = f"{motion.name}_inverted"
    
    rigid_old_inverse = slam.RigidAnalysis(ky=ky, ground_motion=old_motion, target_pga=target_pga)
    
    # New approach: use inverse parameter
    rigid_new_inverse = slam.RigidAnalysis(ky=ky, ground_motion=motion, target_pga=target_pga, inverse=True)
    
    print(f"Old approach displacement: {rigid_old_inverse.max_sliding_disp * 100:.6f} cm")
    print(f"New approach displacement: {rigid_new_inverse.max_sliding_disp * 100:.6f} cm")
    print(f"Difference: {abs(rigid_old_inverse.max_sliding_disp - rigid_new_inverse.max_sliding_disp) * 100:.8f} cm")
    
    # They should be very close (accounting for floating point precision)
    assert abs(rigid_old_inverse.max_sliding_disp - rigid_new_inverse.max_sliding_disp) < 1e-10, \
        "Old and new approaches should give identical results"
    
    print("✓ Old and new approaches give identical results!")


if __name__ == "__main__":
    test_inverse_parameter()
    test_old_vs_new_approach()
    print("\n=== All Tests Passed! ===")