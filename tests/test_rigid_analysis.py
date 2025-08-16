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

    def test_string_representation(self, sample_ground_motion):
        """Test __str__ method provides descriptive information."""
        ky = 0.15
        scale_factor = 1.2
        ra = RigidAnalysis(
            ky=ky, ground_motion=sample_ground_motion, scale_factor=scale_factor
        )

        str_repr = str(ra)

        assert "RigidAnalysis" in str_repr
        assert f"{ky} g" in str_repr
        assert sample_ground_motion.name in str_repr
        assert f"Scale factor: {scale_factor}" in str_repr
        assert (
            f"Displacement: {100 * getattr(ra, 'max_sliding_disp', 0):.1f} cm"
            in str_repr
        )

    def test_equality_method(self, sample_ground_motion):
        """Test __eq__ method for RigidAnalysis objects."""
        ky = 0.2
        scale_factor = 1.0

        ra1 = RigidAnalysis(
            ky=ky, ground_motion=sample_ground_motion, scale_factor=scale_factor
        )
        ra2 = RigidAnalysis(
            ky=ky, ground_motion=sample_ground_motion, scale_factor=scale_factor
        )

        # Same parameters should be equal
        assert ra1 == ra2

        # Different ky should not be equal
        ra3 = RigidAnalysis(
            ky=0.3, ground_motion=sample_ground_motion, scale_factor=scale_factor
        )
        assert ra1 != ra3

        # Different scale_factor should not be equal
        ra4 = RigidAnalysis(ky=ky, ground_motion=sample_ground_motion, scale_factor=1.5)
        assert ra1 != ra4

    def test_run_rigid_analysis_attribute_lengths(self, sample_ground_motion):
        """Test that run_rigid_analysis creates attributes with correct lengths."""
        ky = 0.2
        ra = RigidAnalysis(ky=ky, ground_motion=sample_ground_motion)

        expected_length = len(sample_ground_motion.accel)

        # Test that key arrays have the correct length
        assert len(ra._ground_acc_) == expected_length
        assert len(ra._block_acc_) == expected_length
        assert len(ra.sliding_vel) == expected_length
        assert len(ra.sliding_disp) == expected_length

        # Test that they are numpy arrays
        assert isinstance(ra._ground_acc_, np.ndarray)
        assert isinstance(ra._block_acc_, np.ndarray)
        assert isinstance(ra.sliding_vel, np.ndarray)
        assert isinstance(ra.sliding_disp, np.ndarray)

        # Test that max_sliding_disp is set
        assert hasattr(ra, "max_sliding_disp")
        assert isinstance(ra.max_sliding_disp, (int, float, np.number))

    def test_analysis_runs_automatically(self, sample_ground_motion):
        """Test that analysis runs automatically during initialization."""
        ra = RigidAnalysis(ky=0.2, ground_motion=sample_ground_motion)

        # These attributes should be set after initialization
        assert ra._ground_acc_ is not None
        assert ra._block_acc_ is not None
        assert ra.sliding_vel is not None
        assert ra.sliding_disp is not None
        assert ra.max_sliding_disp is not None

    def test_rigid_analysis_specific_attributes(self, sample_ground_motion):
        """Test RigidAnalysis-specific attributes and behavior."""
        ky = 0.25
        ra = RigidAnalysis(ky=ky, ground_motion=sample_ground_motion)

        # Test that _ground_acc_ is properly set in m/s^2
        assert ra._ground_acc_ is not None
        expected_ground_acc = np.array(sample_ground_motion.accel) * 9.80665
        np.testing.assert_array_almost_equal(ra._ground_acc_, expected_ground_acc)

        # Test that run_rigid_analysis was called (evidenced by populated arrays)
        assert all(
            isinstance(arr, np.ndarray)
            for arr in [ra._block_acc_, ra.sliding_vel, ra.sliding_disp]
        )
