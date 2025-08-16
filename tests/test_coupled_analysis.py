import numpy as np
import pytest

from pyslammer.coupled_analysis import Coupled
from pyslammer.ground_motion import GroundMotion


class TestCoupled:
    """Test suite for Coupled class - focuses on Coupled-specific functionality."""

    @pytest.fixture
    def sample_ground_motion(self):
        """Create a sample ground motion for testing."""
        accel = [0.1, 0.3, -0.2, 0.4, -0.1, 0.0, 0.2, -0.3, 0.1, 0.0]
        dt = 0.01
        name = "Test Motion"
        return GroundMotion(accel=accel, dt=dt, name=name)

    @pytest.fixture
    def sample_coupled_params(self):
        """Create sample parameters for Coupled analysis."""
        return {
            "ky": 0.15,
            "height": 50.0,
            "vs_slope": 600.0,
            "vs_base": 600.0,
            "damp_ratio": 0.05,
            "ref_strain": 0.0005,
            "scale_factor": 1.0,
            "soil_model": "linear_elastic",
        }

    def test_string_representation(self, sample_ground_motion, sample_coupled_params):
        """Test __str__ method provides descriptive information."""
        ca = Coupled(ground_motion=sample_ground_motion, **sample_coupled_params)

        str_repr = str(ca)

        assert "Coupled" in str_repr
        assert f"{sample_coupled_params['ky']} g" in str_repr
        assert sample_ground_motion.name in str_repr
        assert f"Scale factor: {sample_coupled_params['scale_factor']}" in str_repr
        assert (
            f"Displacement: {100 * getattr(ca, 'max_sliding_disp', 0):.1f} cm"
            in str_repr
        )

    def test_equality_method(self, sample_ground_motion, sample_coupled_params):
        """Test __eq__ method for Coupled objects."""
        ca1 = Coupled(ground_motion=sample_ground_motion, **sample_coupled_params)
        ca2 = Coupled(ground_motion=sample_ground_motion, **sample_coupled_params)

        # Same parameters should be equal
        assert ca1 == ca2

        # Different ky should not be equal
        params_diff_ky = sample_coupled_params.copy()
        params_diff_ky["ky"] = 0.2
        ca3 = Coupled(ground_motion=sample_ground_motion, **params_diff_ky)
        assert ca1 != ca3

        # Different height should not be equal
        params_diff_height = sample_coupled_params.copy()
        params_diff_height["height"] = 40.0
        ca4 = Coupled(ground_motion=sample_ground_motion, **params_diff_height)
        assert ca1 != ca4

        # Different vs_slope should not be equal
        params_diff_vs = sample_coupled_params.copy()
        params_diff_vs["vs_slope"] = 500.0
        ca5 = Coupled(ground_motion=sample_ground_motion, **params_diff_vs)
        assert ca1 != ca5

    def test_coupled_analysis_specific_attributes(
        self, sample_ground_motion, sample_coupled_params
    ):
        """Test Coupled-specific attributes and behavior."""
        ca = Coupled(ground_motion=sample_ground_motion, **sample_coupled_params)

        # Test that coupled-specific attributes are set
        assert hasattr(ca, "HEA")
        assert hasattr(ca, "gamma")
        assert hasattr(ca, "_block_acc_")
        assert hasattr(ca, "_ground_acc_")
        assert hasattr(ca, "max_sliding_disp")

        # Test that arrays have correct length
        expected_length = len(sample_ground_motion.accel)
        assert len(ca.HEA) == expected_length
        assert len(ca._block_acc_) == expected_length
        assert len(ca.sliding_vel) == expected_length

        # Test that they are numpy arrays
        assert isinstance(ca.HEA, np.ndarray)
        assert isinstance(ca._block_acc_, np.ndarray)
        assert isinstance(ca.sliding_vel, np.ndarray)

        # Test that max_sliding_disp is set
        assert isinstance(ca.max_sliding_disp, (int, float, np.number))

    def test_analysis_runs_automatically(
        self, sample_ground_motion, sample_coupled_params
    ):
        """Test that analysis runs automatically during initialization."""
        ca = Coupled(ground_motion=sample_ground_motion, **sample_coupled_params)

        # These attributes should be set after initialization
        assert ca._ground_acc_ is not None
        assert ca._block_acc_ is not None
        assert ca.sliding_vel is not None
        assert ca.HEA is not None
        assert ca.max_sliding_disp is not None

    def test_coupled_inheritance_from_decoupled(
        self, sample_ground_motion, sample_coupled_params
    ):
        """Test that Coupled properly inherits from Decoupled."""
        ca = Coupled(ground_motion=sample_ground_motion, **sample_coupled_params)

        # Test that inherited attributes are present
        assert hasattr(ca, "k_y")
        assert hasattr(ca, "dt")
        assert hasattr(ca, "height")
        assert hasattr(ca, "vs_slope")
        assert hasattr(ca, "vs_base")
        assert hasattr(ca, "damp_ratio")
        assert hasattr(ca, "ref_strain")
        assert hasattr(ca, "soil_model")

        # Test that parent methods are available
        assert callable(getattr(ca, "run_sliding_analysis", None))