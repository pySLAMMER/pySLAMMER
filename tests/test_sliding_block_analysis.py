import numpy as np
import pytest

from pyslammer.constants import G_EARTH
from pyslammer.ground_motion import GroundMotion
from pyslammer.sliding_block_analysis import SlidingBlockAnalysis


class TestSlidingBlockAnalysis:
    """Test suite for SlidingBlockAnalysis class specifications."""

    @pytest.fixture
    def sample_ground_motion(self):
        """Create a sample GroundMotion for testing."""
        accel = [0.1, 0.2, 0.1, -0.1, 0.0, 0.15, -0.05]
        dt = 0.01
        return GroundMotion(accel=accel, dt=dt, name="Test Motion")

    @pytest.fixture
    def sample_gm_dict(self):
        """Create a sample ground motion dictionary for testing."""
        return {"accel": [0.1, 0.2, 0.1, -0.1, 0.0], "dt": 0.01, "name": "Dict Motion"}

    def test_valid_initialization_with_ground_motion(self, sample_ground_motion):
        """Test valid initialization with GroundMotion object."""
        ky = 0.15
        sba = SlidingBlockAnalysis(ky=ky, ground_motion=sample_ground_motion)

        assert sba.ky == ky * G_EARTH
        assert np.array_equal(sba.a_in, sample_ground_motion.accel)
        assert sba.dt == sample_ground_motion.dt
        assert sba.motion_name == sample_ground_motion.name
        assert sba.scale_factor == 1.0

    def test_valid_initialization_with_dict(self, sample_gm_dict):
        """Test valid initialization with dictionary."""
        ky = 0.2
        sba = SlidingBlockAnalysis(ky=ky, ground_motion=sample_gm_dict)

        assert sba.ky == ky * G_EARTH
        assert np.array_equal(sba.a_in, sample_gm_dict["accel"])
        assert sba.dt == sample_gm_dict["dt"]
        assert sba.motion_name == sample_gm_dict["name"]

    def test_scale_factor_application(self, sample_ground_motion):
        """Test scale factor application."""
        ky = 0.1
        scale_factor = 2.0
        sba = SlidingBlockAnalysis(
            ky=ky, ground_motion=sample_ground_motion, scale_factor=scale_factor
        )

        expected_accel = np.array(sample_ground_motion.accel) * scale_factor
        assert np.array_equal(sba.a_in, expected_accel)
        assert sba.scale_factor == scale_factor

    def test_target_pga_scaling(self, sample_ground_motion):
        """Test target PGA scaling."""
        ky = 0.1
        target_pga = 0.5
        original_pga = max(abs(sample_ground_motion.accel))
        expected_scale = target_pga / original_pga

        sba = SlidingBlockAnalysis(
            ky=ky, ground_motion=sample_ground_motion, target_pga=target_pga
        )

        assert sba.scale_factor == expected_scale
        assert max(abs(sba.a_in)) == pytest.approx(target_pga)

    def test_both_scale_factor_and_target_pga_error(self, sample_ground_motion):
        """Test ValueError when both scale_factor and target_pga are provided."""
        with pytest.raises(
            ValueError, match="Both target_pga and scale_factor cannot be provided"
        ):
            SlidingBlockAnalysis(
                ky=0.1,
                ground_motion=sample_ground_motion,
                scale_factor=2.0,
                target_pga=0.5,
            )

    def test_negative_ky_error(self, sample_ground_motion):
        """Test ValueError for negative ky with specific message."""
        ky = -0.1
        with pytest.raises(
            ValueError, match=f"Yield acceleration ky must be positive, got {ky}"
        ):
            SlidingBlockAnalysis(ky=ky, ground_motion=sample_ground_motion)

    def test_zero_ky_error(self, sample_ground_motion):
        """Test ValueError for zero ky."""
        ky = 0.0
        with pytest.raises(
            ValueError, match=f"Yield acceleration ky must be positive, got {ky}"
        ):
            SlidingBlockAnalysis(ky=ky, ground_motion=sample_ground_motion)

    def test_invalid_ground_motion_dict(self):
        """Test ValueError for invalid ground_motion dictionary."""
        # Missing required keys
        invalid_dict = {"accel": [0.1, 0.2]}  # missing 'dt'
        with pytest.raises(ValueError, match="Invalid ground_motion dictionary"):
            SlidingBlockAnalysis(ky=0.1, ground_motion=invalid_dict)

    def test_invalid_ground_motion_type(self):
        """Test TypeError for invalid ground_motion type."""
        with pytest.raises(
            TypeError, match="ground_motion must be GroundMotion object or dict"
        ):
            SlidingBlockAnalysis(ky=0.1, ground_motion="invalid_type")  # type: ignore[operator]

    def test_dict_to_ground_motion_missing_keys(self):
        """Test _dict_to_ground_motion with missing keys."""
        invalid_dict = {"accel": [0.1, 0.2]}  # missing 'dt'
        with pytest.raises(KeyError, match="Missing required keys: {'dt'}"):
            SlidingBlockAnalysis._dict_to_ground_motion(invalid_dict)

    def test_dict_to_ground_motion_with_name(self):
        """Test _dict_to_ground_motion with name provided."""
        gm_dict = {"accel": [0.1, 0.2], "dt": 0.01, "name": "Custom Name"}
        gm = SlidingBlockAnalysis._dict_to_ground_motion(gm_dict)

        assert isinstance(gm, GroundMotion)
        assert gm.name == "Custom Name"

    def test_dict_to_ground_motion_default_name(self):
        """Test _dict_to_ground_motion with default name."""
        gm_dict = {"accel": [0.1, 0.2], "dt": 0.01}
        gm = SlidingBlockAnalysis._dict_to_ground_motion(gm_dict)

        assert isinstance(gm, GroundMotion)
        assert gm.name == "None"  # Uses GroundMotion's default name

    def test_compile_base_attributes(self, sample_ground_motion):
        """Test _compile_base_attributes method behavior."""
        sba = SlidingBlockAnalysis(ky=0.1, ground_motion=sample_ground_motion)
        sba._compile_base_attributes()

        # Check ground_acc is in correct units (m/s^2)
        expected_ground_acc = sba.a_in * G_EARTH
        assert np.array_equal(sba.ground_acc, expected_ground_acc)  # type: ignore[operator]

        # Check that ground_vel and ground_disp are integrated versions
        assert sba.ground_vel is not None
        assert sba.ground_disp is not None
        assert len(sba.ground_vel) == len(sba.ground_acc)  # type: ignore[operator]
        assert len(sba.ground_disp) == len(sba.ground_acc)  # type: ignore[operator]

        # Verify integration relationship (velocity should be integral of acceleration)
        # First point should be zero (initial condition)
        assert sba.ground_vel[0] == 0.0
        assert sba.ground_disp[0] == 0.0

    def test_motion_integration_static_method(self):
        """Test _motion_integration static method."""
        motion = np.array([1.0, 2.0, 1.0, 0.0])
        dt = 0.01

        integrated = SlidingBlockAnalysis._motion_integration(motion, dt)

        # Should return array of same length
        assert len(integrated) == len(motion)
        # First value should be 0 (initial condition)
        assert integrated[0] == 0.0
        # Should be cumulative trapezoidal integration
        assert isinstance(integrated, np.ndarray)

    def test_initial_attributes_none(self, sample_ground_motion):
        """Test that analysis attributes are initially None."""
        sba = SlidingBlockAnalysis(ky=0.1, ground_motion=sample_ground_motion)

        assert sba.ground_acc is None
        assert sba.ground_vel is None
        assert sba.ground_disp is None
        assert sba.block_acc is None
        assert sba.block_vel is None
        assert sba.block_disp is None
        assert sba.sliding_vel is None
        assert sba.sliding_disp is None
        assert sba.max_sliding_disp is None
        assert sba.time is None
        assert sba._npts is None
        assert sba.method is None

    def test_plot_method_error_without_analysis(self, sample_ground_motion):
        """Test that plot() raises error when block attributes don't exist."""
        sba = SlidingBlockAnalysis(ky=0.1, ground_motion=sample_ground_motion)

        # This should fail because block_acc is None and needed for plotting
        with pytest.raises((AttributeError, IndexError, TypeError)):
            sba.sliding_block_plot()

    def test_ky_units_conversion(self, sample_ground_motion):
        """Test that ky is properly converted to m/s^2."""
        ky_in_g = 0.25
        sba = SlidingBlockAnalysis(ky=ky_in_g, ground_motion=sample_ground_motion)

        expected_ky = ky_in_g * G_EARTH
        assert sba.ky == expected_ky

    def test_default_target_pga_none(self, sample_ground_motion):
        """Test default target_pga is None."""
        sba = SlidingBlockAnalysis(ky=0.1, ground_motion=sample_ground_motion)
        # Should use default scale_factor of 1.0
        assert sba.scale_factor == 1.0

    def test_input_motion_copying(self, sample_ground_motion):
        """Test that input motion is copied, not referenced."""
        sba = SlidingBlockAnalysis(
            ky=0.1, ground_motion=sample_ground_motion, scale_factor=2.0
        )

        # Modify original ground motion
        original_accel = sample_ground_motion.accel.copy()
        sample_ground_motion.accel[0] = 999.0

        # SBA should have the scaled original values, not the modified ones
        expected_first_value = original_accel[0] * 2.0
        assert sba.a_in[0] == expected_first_value
        assert sba.a_in[0] != sample_ground_motion.accel[0] * 2.0
