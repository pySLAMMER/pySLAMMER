# pySLAMMER

[![PyPI](https://img.shields.io/pypi/v/pyslammer.svg)](https://pypi.org/project/pyslammer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyslammer.svg)](https://pypi.org/project/pyslammer)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15385355.svg)](https://doi.org/10.5281/zenodo.15385355)

pySLAMMER (**Py**thon package for **S**eismic **LA**ndslide **M**ovement **M**odeled using **E**arthquake **R**ecords)
is a tool for estimating the co-seismic displacements of landslides with rigid and flexible sliding-block analyses.
The package name and code are based on the USGS tool [SLAMMER](https://pubs.usgs.gov/tm/12b1/)[^1].

### Features

- **Rigid** sliding block analysis
- **Decoupled** flexible sliding block analysis
- **Coupled** flexible sliding block analysis
- Built-in sample earthquake ground motion records
- Visualization tools for analysis results
- Verified against the original USGS SLAMMER

## Installation

```bash
pip install pyslammer
```

## Quick example

```python
import pyslammer as slam

# Load a sample ground motion record
motions = slam.sample_ground_motions()
gm = motions["Imperial_Valley_1979_BCR-230"]

# Run a rigid sliding block analysis
ky = 0.2  # yield acceleration in g
result = slam.RigidAnalysis(ky, gm)

print(f"Sliding displacement: {result.max_sliding_disp:.3f} m")
```

## Documentation

Please see the [documentation](https://pyslammer.github.io/pySLAMMER_docs/) for the quickstart guide, examples, API reference, and technical manual.

## How to cite

Please include citations for both the pySLAMMER code and software paper if you use pySLAMMER.

**Code:**

Arnold, L., & Garcia-Rivas, D. (2025). Pyslammer (Version v0.2.2) [Python]. Zenodo. https://doi.org/10.5281/zenodo.15385355

**Software paper:**

Arnold, L., & Garcia-Rivas, D. (2026). pySLAMMER: a Python package for Seismic LAndslide Movement Modeled using Earthquake Records. *SoftwareX*, 34, 102599. https://doi.org/10.1016/j.softx.2026.102599

## License

pySLAMMER is licensed under the [GNU General Public License v3.0](LICENSE.txt).

[^1]: Jibson, R.W., Rathje, E.M., Jibson, M.W., and Lee, Y.W., 2013, SLAMMER—Seismic LAndslide Movement Modeled using Earthquake Records (ver.1.1, November 2014): U.S. Geological Survey Techniques and Methods, book 12, chap. B1, unpaged. https://pubs.usgs.gov/tm/12b1/
