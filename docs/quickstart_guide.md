# Quick Start Guide

## Requirements

The pyslammer package is built on Python 3.12. Earlier versions of Python 3 may work, but have not been tested.

## Installation using pip
[![PyPI][pypi-badge]][pypi-link]

Install pyslammer using `pip` from the Python Package Index (PyPI):
```python
pip install pyslammer
```
[pypi-badge]: https://img.shields.io/pypi/v/pyslammer.svg
[pypi-link]: https://pypi.org/project/pyslammer
## Basic Usage
Once pyslammer is installed, import it to your Python code.
The recommended ailas for pyslammer is `slam` using the following command:
```python
import pyslammer as slam
```

This allows use of pyslammer features within your code with the short prefix `slam.`.

For example, after importing and aliasing pyslammer as above, let's say we want to run a rigid sliding block analysis on a slope.
Assume that the slope has a yield acceleration, $k_y$, of $0.2$ g.
We can do this with the following steps: 

1. **Import a sample ground motion**

We will use the sample ground motion record `Imperial_Valley_1979_BCR-230` for this example. Refer to [insert some internal link...]
```python
histories = slam.sample_ground_motions() # Load all sample ground motions
gm = histories["Imperial_Valley_1979_BCR-230"] # Select a specific ground motion
```

2. **Perform a rigid sliding block analysis**

With the imported ground motion, `gm`, and the assumed value of $k_y$, we can perform a rigid sliding block analysis with pySLAMMER's `RigidAnalysis` object.

```python
ky = 0.2 # yield acceleration in g
result = slam.RigidAnalysis(gm.accel, gm.dt, ky) # Perform the rigid sliding block analysis and save the result
```

The key object type within pyslammer is the SlidingBlockAnalysis object.
Additionaly, the package includes a small number of sample ground motion records.

I'm a markdown file