import numpy as np
import pytest

from pyslammer.decoupled_analysis import Decoupled
from pyslammer.ground_motion import GroundMotion


class TestDecoupled:
    """Test suite for Decoupled class - focuses on Decoupled-specific functionality."""

    @pytest.fixture
    def sample_ground_motion(self):
        """Create a sample ground motion for testing."""
        accel = [0.1, 0.3, -0.2, 0.4, -0.1, 0.0, 0.2, -0.3, 0.1, 0.0]
        dt = 0.01
        name = "Test Motion"
        return GroundMotion(accel=accel, dt=dt, name=name)

    @pytest.fixture
    def sample_decoupled_params(self):
        """Create sample parameters for Decoupled analysis."""
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

    def test_string_representation(self, sample_ground_motion, sample_decoupled_params):
        """Test __str__ method provides descriptive information."""
        da = Decoupled(ground_motion=sample_ground_motion, **sample_decoupled_params)

        str_repr = str(da)

        assert "Decoupled" in str_repr
        assert f"{sample_decoupled_params['ky']} g" in str_repr
        assert sample_ground_motion.name in str_repr
        assert f"Scale factor: {sample_decoupled_params['scale_factor']}" in str_repr
        assert (
            f"Displacement: {100 * getattr(da, 'max_sliding_disp', 0):.1f} cm"
            in str_repr
        )

    def test_equality_method(self, sample_ground_motion, sample_decoupled_params):
        """Test __eq__ method for Decoupled objects."""
        da1 = Decoupled(ground_motion=sample_ground_motion, **sample_decoupled_params)
        da2 = Decoupled(ground_motion=sample_ground_motion, **sample_decoupled_params)

        # Same parameters should be equal
        assert da1 == da2

        # Different ky should not be equal
        params_diff_ky = sample_decoupled_params.copy()
        params_diff_ky["ky"] = 0.2
        da3 = Decoupled(ground_motion=sample_ground_motion, **params_diff_ky)
        assert da1 != da3

        # Different scale_factor should not be equal
        params_diff_scale = sample_decoupled_params.copy()
        params_diff_scale["scale_factor"] = 1.5
        da4 = Decoupled(ground_motion=sample_ground_motion, **params_diff_scale)
        assert da1 != da4

    def test_decoupled_analysis_specific_attributes(
        self, sample_ground_motion, sample_decoupled_params
    ):
        """Test Decoupled-specific attributes and behavior."""
        da = Decoupled(ground_motion=sample_ground_motion, **sample_decoupled_params)

        # Test that decoupled-specific attributes are set
        assert hasattr(da, "HEA")
        assert hasattr(da, "sliding_vel")
        assert hasattr(da, "block_disp")
        assert hasattr(da, "_ground_acc_")
        assert hasattr(da, "max_sliding_disp")

        # Test that arrays have correct length
        expected_length = len(sample_ground_motion.accel)
        assert len(da.HEA) == expected_length
        assert len(da.sliding_vel) == expected_length
        assert len(da.block_disp) == expected_length
        assert len(da._ground_acc_) == expected_length

        # Test that they are numpy arrays
        assert isinstance(da.HEA, np.ndarray)
        assert isinstance(da.sliding_vel, np.ndarray)
        assert isinstance(da.block_disp, np.ndarray)
        assert isinstance(da._ground_acc_, np.ndarray)

        # Test that max_sliding_disp is set
        assert isinstance(da.max_sliding_disp, (int, float, np.number))

    def test_analysis_runs_automatically(
        self, sample_ground_motion, sample_decoupled_params
    ):
        """Test that analysis runs automatically during initialization."""
        da = Decoupled(ground_motion=sample_ground_motion, **sample_decoupled_params)

        # These attributes should be set after initialization
        assert da._ground_acc_ is not None
        assert da.sliding_vel is not None
        assert da.block_disp is not None
        assert da.HEA is not None
        assert da.max_sliding_disp is not None

    def test_decoupled_inheritance_from_sliding_block_analysis(
        self, sample_ground_motion, sample_decoupled_params
    ):
        """Test that Decoupled properly inherits from SlidingBlockAnalysis."""
        da = Decoupled(ground_motion=sample_ground_motion, **sample_decoupled_params)

        # Test that inherited attributes are present
        assert hasattr(da, "ky")
        assert hasattr(da, "dt")
        assert hasattr(da, "scale_factor")
        assert hasattr(da, "a_in")
        assert hasattr(da, "ground_motion")

        # Test that parent methods are available
        assert callable(getattr(da, "run_sliding_analysis", None))

    def test_k_y_function_assignment(
        self, sample_ground_motion, sample_decoupled_params
    ):
        """Test that k_y function is properly assigned."""
        da = Decoupled(ground_motion=sample_ground_motion, **sample_decoupled_params)

        # Test that k_y is callable
        assert callable(da.k_y)

        # Test that k_y returns expected value for constant case
        assert da.k_y(0.0) == sample_decoupled_params["ky"]
        assert da.k_y(10.0) == sample_decoupled_params["ky"]