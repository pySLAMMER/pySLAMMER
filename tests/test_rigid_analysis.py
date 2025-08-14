import numpy as np
import pytest

from pyslammer.ground_motion import GroundMotion
from pyslammer.rigid_analysis import RigidAnalysis


class TestRigidAnalysis:
    """Test suite for RigidAnalysis class - focuses on RigidAnalysis-specific functionality."""

    @pytest.fixture
    def sample_ground_motion(self):
        """Create a sample ground motion for testing."""
        accel = [0.1, 0.3, -0.2, 0.4, -0.1, 0.0, 0.2, -0.3, 0.1, 0.0]
        dt = 0.01
        name = "Test Motion"
        return GroundMotion(accel=accel, dt=dt, name=name)

    def test_str_method(self, sample_ground_motion):
        """Test __str__ method - RigidAnalysis specific implementation."""
        ky = 0.2
        ra = RigidAnalysis(ky=ky, ground_motion=sample_ground_motion)

        str_repr = str(ra)

        # Should contain key information
        assert "RigidAnalysis" in str_repr
        assert f"{ky:.3f}g" in str_repr
        assert "max_disp" in str_repr
        assert "m)" in str_repr  # units

    def test_repr_method(self, sample_ground_motion):
        """Test __repr__ method - RigidAnalysis specific implementation."""
        ky = 0.15
        scale_factor = 1.2

        ra = RigidAnalysis(
            ky=ky, ground_motion=sample_ground_motion, scale_factor=scale_factor
        )

        repr_str = repr(ra)

        # Should contain enough info to recreate the object
        assert "RigidAnalysis" in repr_str
        assert "ground_motion=" in repr_str
        assert "scale_factor=" in repr_str
        assert str(scale_factor) in repr_str

    def test_run_rigid_analysis_attribute_lengths(self, sample_ground_motion):
        """Test that run_rigid_analysis creates attributes with correct lengths."""
        ky = 0.2
        ra = RigidAnalysis(ky=ky, ground_motion=sample_ground_motion)

        expected_length = len(sample_ground_motion.accel)

        # Test that key arrays have the correct length
        assert len(ra.ground_acc) == expected_length
        assert len(ra.block_acc) == expected_length
        assert len(ra.sliding_vel) == expected_length
        assert len(ra.sliding_disp) == expected_length

        # Test that they are numpy arrays
        assert isinstance(ra.ground_acc, np.ndarray)
        assert isinstance(ra.block_acc, np.ndarray)
        assert isinstance(ra.sliding_vel, np.ndarray)
        assert isinstance(ra.sliding_disp, np.ndarray)

        # Test that max_sliding_disp is set
        assert hasattr(ra, "max_sliding_disp")
        assert isinstance(ra.max_sliding_disp, (int, float, np.number))

    def test_analysis_runs_automatically(self, sample_ground_motion):
        """Test that analysis runs automatically during initialization."""
        ra = RigidAnalysis(ky=0.2, ground_motion=sample_ground_motion)

        # These attributes should be set after initialization
        assert ra.ground_acc is not None
        assert ra.block_acc is not None
        assert ra.sliding_vel is not None
        assert ra.sliding_disp is not None
        assert ra.max_sliding_disp is not None

    def test_rigid_analysis_specific_attributes(self, sample_ground_motion):
        """Test RigidAnalysis-specific attributes and behavior."""
        ky = 0.25
        ra = RigidAnalysis(ky=ky, ground_motion=sample_ground_motion)

        # Test that ground_acc is properly set in m/s^2
        assert ra.ground_acc is not None
        expected_ground_acc = np.array(sample_ground_motion.accel) * 9.80665
        np.testing.assert_array_almost_equal(ra.ground_acc, expected_ground_acc)

        # Test that _npts is set correctly
        assert ra._npts == len(sample_ground_motion.accel)

        # Test that run_rigid_analysis was called (evidenced by populated arrays)
        assert all(isinstance(arr, np.ndarray) for arr in [
            ra.block_acc, ra.sliding_vel, ra.sliding_disp
        ])
