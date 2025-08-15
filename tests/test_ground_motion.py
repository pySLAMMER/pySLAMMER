import numpy as np
import pytest

from pyslammer.ground_motion import GroundMotion


class TestGroundMotion:
    """Test suite for GroundMotion class specifications."""

    def test_valid_initialization(self):
        """Test valid GroundMotion initialization."""
        accel = [0.1, 0.2, 0.1, -0.1, 0.0]
        dt = 0.01
        name = "Test Motion"

        gm = GroundMotion(accel=accel, dt=dt, name=name)

        assert isinstance(gm.accel, np.ndarray)
        assert np.array_equal(gm.accel, np.array(accel))
        assert gm.dt == dt
        assert gm.name == name
        assert gm.pga == 0.2
        assert len(gm.accel) == len(accel)

    def test_accel_conversion_error(self):
        """Test ValueError for accel that can't be converted to numpy array."""
        with pytest.raises(
            ValueError, match="Could not convert accel to numeric array"
        ):
            GroundMotion(accel=["a", "b", "c"], dt=0.01)

    def test_accel_not_1d(self):
        """Test ValueError for accel that isn't 1 dimensional."""
        accel_2d = [[1, 2], [3, 4]]
        with pytest.raises(ValueError, match="accel must be 1-dimensional, got 2D"):
            GroundMotion(accel=accel_2d, dt=0.01)

    def test_negative_dt(self):
        """Test ValueError for negative dt."""
        with pytest.raises(
            ValueError, match="Time step dt must be positive, got -0.01"
        ):
            GroundMotion(accel=[0.1, 0.2], dt=-0.01)

    def test_zero_dt(self):
        """Test ValueError for zero dt."""
        with pytest.raises(ValueError, match="Time step dt must be positive, got 0"):
            GroundMotion(accel=[0.1, 0.2], dt=0)

    def test_large_dt_warning(self):
        """Test warning for dt greater than 0.1."""
        with pytest.warns(UserWarning, match="Time step dt=0.2000s is unusually large"):
            GroundMotion(accel=[0.1, 0.2], dt=0.2)

    def test_boundary_dt_values(self):
        """Test dt boundary values."""
        # Should work without warning
        gm1 = GroundMotion(accel=[0.1, 0.2], dt=0.1)
        assert gm1.dt == 0.1

        # Should work without warning
        gm2 = GroundMotion(accel=[0.1, 0.2], dt=0.001)
        assert gm2.dt == 0.001

        # Just above 0.1 should warn
        with pytest.warns(UserWarning):
            GroundMotion(accel=[0.1, 0.2], dt=0.1001)

    def test_default_name(self):
        """Test default name parameter."""
        gm = GroundMotion(accel=[0.1, 0.2], dt=0.01)
        assert gm.name == "None"

    def test_array_like_inputs(self):
        """Test various array-like inputs for accel."""
        # List
        gm1 = GroundMotion(accel=[0.1, 0.2], dt=0.01)
        assert isinstance(gm1.accel, np.ndarray)

        # Numpy array
        gm2 = GroundMotion(accel=np.array([0.1, 0.2]), dt=0.01)
        assert isinstance(gm2.accel, np.ndarray)

        # Tuple
        gm3 = GroundMotion(accel=(0.1, 0.2), dt=0.01)
        assert isinstance(gm3.accel, np.ndarray)

    def test_pga_calculation(self):
        """Test peak ground acceleration calculation."""
        # Test with positive peak
        gm1 = GroundMotion(accel=[0.1, 0.5, 0.2], dt=0.01)
        assert gm1.pga == 0.5

        # Test with negative peak
        gm2 = GroundMotion(accel=[0.1, -0.7, 0.2], dt=0.01)
        assert gm2.pga == 0.7

        # Test with zero - should trigger warning
        with pytest.warns(UserWarning, match="This ground motion has zero amplitude"):
            gm3 = GroundMotion(accel=[0.0, 0.0, 0.0], dt=0.01)
        assert gm3.pga == 0.0
        assert np.isnan(gm3.mean_period)  # Should be NaN for zero amplitude

    def test_mean_period_calculation(self):
        """Test that mean period is computed correctly."""
        # Simple sine wave with period of 1 second should have a mean period close to 1
        t = np.linspace(0, 10, 1000)
        accel = np.sin(2 * np.pi * t)
        gm = GroundMotion(accel=accel, dt=0.01)

        # Check that mean period is close to expected value of 1 second
        expected_period = 1.0
        tolerance = 1e-4  # Relaxed tolerance for numerical computation
        assert abs(gm.mean_period - expected_period) < tolerance, (
            f"Mean period {gm.mean_period} not within tolerance {tolerance} of expected {expected_period}"
        )
        assert isinstance(gm.mean_period, float)

    def test_string_representation(self):
        """Test __str__ method provides descriptive information."""
        gm = GroundMotion(accel=[0.1, 0.3, 0.2], dt=0.01, name="Test")
        str_repr = str(gm)

        assert "Test" in str_repr
        assert "0.30 g" in str_repr  # PGA
        assert "0.010 s" in str_repr  # dt
        assert "3" in str_repr  # npts
        assert "Ground Motion" in str_repr

    def test_string_representation_with_different_values(self):
        """Test __str__ method with different parameter values."""
        gm = GroundMotion(
            accel=[0.05, -0.15, 0.25, 0.1], dt=0.005, name="Different Motion"
        )
        str_repr = str(gm)

        # Should contain the specific values
        assert "Different Motion" in str_repr
        assert "0.25 g" in str_repr  # PGA should be max absolute value
        assert "0.005 s" in str_repr  # dt
        assert "4" in str_repr  # npts
        assert "Ground Motion" in str_repr

    def test_string_representation_default_name(self):
        """Test __str__ method with default name."""
        gm = GroundMotion(accel=[0.1, 0.2], dt=0.01)
        str_repr = str(gm)

        # Should contain default name
        assert "None" in str_repr
        assert "Ground Motion" in str_repr

    def test_equality_method(self):
        """Test __eq__ method for GroundMotion objects."""
        accel = [0.1, 0.2, -0.1]
        dt = 0.01
        name = "Test"

        gm1 = GroundMotion(accel=accel, dt=dt, name=name)
        gm2 = GroundMotion(accel=accel, dt=dt, name=name)

        # Same parameters should be equal
        assert gm1 == gm2

        # Different acceleration should not be equal
        gm3 = GroundMotion(accel=[0.1, 0.3, -0.1], dt=dt, name=name)
        assert gm1 != gm3

        # Different dt should not be equal
        gm4 = GroundMotion(accel=accel, dt=0.02, name=name)
        assert gm1 != gm4

        # Different name should not be equal
        gm5 = GroundMotion(accel=accel, dt=dt, name="Different")
        assert gm1 != gm5

        # Not equal to non-GroundMotion objects
        assert gm1 != "not a ground motion"
        assert gm1 != 42
