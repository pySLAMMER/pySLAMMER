from .coupled_analysis import *
from .decoupled_analysis import *
from .ground_motion import GroundMotion
from .rigid_analysis import *
from .sliding_block_analysis import *
from .utilities import *

# Make version available
try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # Python < 3.8 fallback
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("pyslammer")
except PackageNotFoundError:
    __version__ = "unknown"
