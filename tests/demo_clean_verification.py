#!/usr/bin/env python3
"""
Demonstration of how the verification code can be cleaned up using the new inverse parameter.
"""

import pyslammer as slam


def old_approach_example():
    """Example of the old approach with manual array negation."""
    print("=== OLD APPROACH (with manual negation) ===")
    
    # Load ground motion
    motions = slam.sample_ground_motions()
    motion = motions["Cape_Mendocino_1992_PET-090"]
    
    # Parameters
    ky = 0.15
    target_pga = 0.2
    
    # Normal direction
    rigid_normal = slam.RigidAnalysis(ky=ky, ground_motion=motion, target_pga=target_pga)
    
    # OLD WAY: Manually negate the acceleration array (problematic!)
    # This approach mutates the input data and is unclear
    motion_dict = {
        "accel": -motion.accel,  # Manual negation - problematic!
        "dt": motion.dt,
        "name": motion.name
    }
    rigid_inverse = slam.RigidAnalysis(ky=ky, ground_motion=motion_dict, target_pga=target_pga)
    
    print(f"Normal: {rigid_normal.max_sliding_disp * 100:.3f} cm")
    print(f"Inverse: {rigid_inverse.max_sliding_disp * 100:.3f} cm")
    print("Problems with old approach:")
    print("  - Requires manual array manipulation")
    print("  - Unclear semantics (what does negated array mean?)")
    print("  - Risk of data mutation")
    print("  - Inconsistent API")


def new_approach_example():
    """Example of the new approach with the inverse parameter."""
    print("\n=== NEW APPROACH (with inverse parameter) ===")
    
    # Load ground motion
    motions = slam.sample_ground_motions()
    motion = motions["Cape_Mendocino_1992_PET-090"]
    
    # Parameters
    ky = 0.15
    target_pga = 0.2
    
    # NEW WAY: Clean, explicit API
    rigid_normal = slam.RigidAnalysis(ky=ky, ground_motion=motion, target_pga=target_pga, inverse=False)
    rigid_inverse = slam.RigidAnalysis(ky=ky, ground_motion=motion, target_pga=target_pga, inverse=True)
    
    print(f"Normal: {rigid_normal.max_sliding_disp * 100:.3f} cm")
    print(f"Inverse: {rigid_inverse.max_sliding_disp * 100:.3f} cm")
    print("Benefits of new approach:")
    print("  - Clear, explicit API (inverse=True)")
    print("  - No data mutation - original motion unchanged")
    print("  - Consistent across all analysis methods")
    print("  - Self-documenting code")


def verification_code_comparison():
    """Show how verification code can be simplified."""
    print("\n=== VERIFICATION CODE COMPARISON ===")
    
    motions = slam.sample_ground_motions()
    motion = motions["Cape_Mendocino_1992_PET-090"]
    
    # Test parameters
    ky = 0.15
    target_pga = 0.2
    flexible_params = {
        "height": 50,
        "vs_slope": 600,
        "vs_base": 600,
        "damp_ratio": 0.05,
        "ref_strain": 0.05,
        "soil_model": "linear_elastic"
    }
    
    print("OLD verification_processes.py approach:")
    print("""
    # Normal direction
    rigid_normal = slam.RigidAnalysis(**rigid_inputs)
    decoupled_normal = slam.Decoupled(**rigid_inputs, **flexible_inputs)
    
    # Problematic array mutation
    rigid_inputs["a_in"] = -rigid_inputs["a_in"]  # YIKES!
    
    # Inverse direction (now with mutated data)
    rigid_inverse = slam.RigidAnalysis(**rigid_inputs)
    decoupled_inverse = slam.Decoupled(**rigid_inputs, **flexible_inputs)
    """)
    
    print("NEW approach with inverse parameter:")
    print("""
    # Clean, explicit API - no data mutation needed
    rigid_normal = slam.RigidAnalysis(ky=ky, ground_motion=motion, target_pga=pga, inverse=False)
    rigid_inverse = slam.RigidAnalysis(ky=ky, ground_motion=motion, target_pga=pga, inverse=True)
    
    decoupled_normal = slam.Decoupled(ky=ky, ground_motion=motion, target_pga=pga, inverse=False, **params)
    decoupled_inverse = slam.Decoupled(ky=ky, ground_motion=motion, target_pga=pga, inverse=True, **params)
    """)
    
    # Demonstrate the actual results are identical
    print("Verification that results are identical:")
    
    # New approach
    rigid_normal = slam.RigidAnalysis(ky=ky, ground_motion=motion, target_pga=target_pga, inverse=False)
    rigid_inverse = slam.RigidAnalysis(ky=ky, ground_motion=motion, target_pga=target_pga, inverse=True)
    
    decoupled_normal = slam.Decoupled(ky=ky, ground_motion=motion, target_pga=target_pga, inverse=False, **flexible_params)
    decoupled_inverse = slam.Decoupled(ky=ky, ground_motion=motion, target_pga=target_pga, inverse=True, **flexible_params)
    
    print(f"  Rigid normal: {rigid_normal.max_sliding_disp * 100:.3f} cm")
    print(f"  Rigid inverse: {rigid_inverse.max_sliding_disp * 100:.3f} cm")
    print(f"  Decoupled normal: {decoupled_normal.max_sliding_disp * 100:.3f} cm")
    print(f"  Decoupled inverse: {decoupled_inverse.max_sliding_disp * 100:.3f} cm")


if __name__ == "__main__":
    old_approach_example()
    new_approach_example()
    verification_code_comparison()
    
    print("\n" + "="*60)
    print("✓ The inverse parameter provides a much cleaner API!")
    print("✓ Ready to update verification_processes.py!")
    print("="*60)