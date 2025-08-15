"""Demo script for SlidingBlockAnalysis."""

from pyslammer.ground_motion import GroundMotion
from pyslammer.sliding_block_analysis import SlidingBlockAnalysis

gm_dict_1 = {
    "accel": [0.1, 0.2, 0.1, -0.1, 0.0],
    "dt": 0.01,
    "name": "Dict Motion 1",
}

gm_dict_2 = {
    "accel": [0.1, 0.2, 0.1, -0.1, 0.0],
    "dt": 0.02,
    "name": "Dict Motion 2",
}

target_pga = 1


if __name__ == "__main__":
    gm_1 = GroundMotion(**gm_dict_1)
    gm_2 = GroundMotion(**gm_dict_2)
    sba_1 = SlidingBlockAnalysis(ky=0.15, ground_motion=gm_1)
    sba_2 = SlidingBlockAnalysis(ky=0.15, ground_motion=gm_2)
    print(sba_1)
