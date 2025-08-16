"""Demo script for SlidingBlockAnalysis."""

from pyslammer.coupled_analysis import Coupled
from pyslammer.decoupled_analysis import Decoupled
from pyslammer.rigid_analysis import RigidAnalysis
from pyslammer.utilities import sample_ground_motions

sgms = sample_ground_motions()


if __name__ == "__main__":
    gm = sgms["Imperial_Valley_1979_BCR-230"]

    rigid_inputs = {"ground_motion": gm, "ky": 0.2, "scale_factor": 1.0}
    flexible_inputs = {
        "height": 50.0,
        "vs_slope": 600.0,
        "vs_base": 600.0,
        "damp_ratio": 0.05,
        "ref_strain": 0.0005,
        "soil_model": "equivalent_linear",
    }

    rigid_result = RigidAnalysis(**rigid_inputs)
    decoupled_result = Decoupled(**rigid_inputs, **flexible_inputs)
    coupled_result = Coupled(**rigid_inputs, **flexible_inputs)
    print(decoupled_result)
