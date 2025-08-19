#!/usr/bin/env python3
"""
Convenience script for running verification tests.

This script provides easy access to different test suites without needing
to remember complex pytest command lines.
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle the result."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print()
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
    else:
        print(f"❌ {description} - FAILED")
        
    return result.returncode


def main():
    """Main test runner."""
    if len(sys.argv) < 2:
        print("Usage: python run_verification_tests.py <test_suite>")
        print()
        print("Available test suites:")
        print("  fast      - Run fast unit tests only")
        print("  slow      - Run comprehensive verification tests")
        print("  all       - Run all tests")
        print("  framework - Run framework unit tests")
        print("  legacy    - Run legacy verification tests")
        print("  ci        - Run CI-style test suite")
        sys.exit(1)
    
    test_suite = sys.argv[1].lower()
    base_env = {"PYTHONPATH": str(Path(__file__).parent)}
    
    # Set up environment
    import os
    os.environ.update(base_env)
    
    if test_suite == "fast":
        return_code = run_command([
            "uv", "run", "pytest", "test_verification.py", 
            "-m", "not slow", "-v"
        ], "Fast Verification Tests")
        
    elif test_suite == "slow":
        return_code = run_command([
            "uv", "run", "pytest", "test_verification.py",
            "-m", "slow", "--runslow", "-v"
        ], "Slow Verification Tests")
        
    elif test_suite == "all":
        # Run fast tests first
        fast_result = run_command([
            "uv", "run", "pytest", "test_verification.py",
            "-m", "not slow", "-v"
        ], "Fast Tests")
        
        if fast_result == 0:
            # Only run slow tests if fast tests pass
            return_code = run_command([
                "uv", "run", "pytest", "test_verification.py",
                "-m", "slow", "--runslow", "-v"
            ], "Slow Tests")
        else:
            print("\n❌ Fast tests failed, skipping slow tests")
            return_code = fast_result
            
    elif test_suite == "framework":
        # Run individual framework component tests
        tests = [
            ("test_phase2_infrastructure.py", "Phase 2 Infrastructure"),
            ("test_phase5_comparisons.py", "Phase 5 Comparisons")
        ]
        
        return_code = 0
        for test_file, description in tests:
            result = run_command([
                "uv", "run", "python", test_file
            ], description)
            if result != 0:
                return_code = result
                
    elif test_suite == "legacy":
        return_code = run_command([
            "uv", "run", "pytest", "test_verification.py::TestLegacyVerification",
            "--runslow", "-v"
        ], "Legacy Verification Tests")
        
    elif test_suite == "ci":
        # CI-style test suite (fast tests + small verification sample)
        tests = [
            (["uv", "run", "pytest", "test_verification.py", "-m", "not slow", "-v"], 
             "Fast Unit Tests"),
            (["uv", "run", "python", "-m", "verification", "run", "--max-tests", "5", "--methods", "rigid"], 
             "Small Verification Sample (Rigid Only)"),
            (["uv", "run", "python", "-m", "verification", "cache", "--status"], 
             "Cache Status Check")
        ]
        
        return_code = 0
        for cmd, description in tests:
            result = run_command(cmd, description)
            if result != 0:
                return_code = result
                
    else:
        print(f"Unknown test suite: {test_suite}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    if return_code == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("💥 SOME TESTS FAILED!")
    print(f"{'='*60}")
    
    sys.exit(return_code)


if __name__ == "__main__":
    main()