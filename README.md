# pySLAMMER
Python code for calculating sliding block displacements.
As the name indicates, this program is based on the USGS software SLAMMER[^1].

Currently, pySLAMMER is in development.

When finished, this code should be able to replicate the rigorous analysis provided by [SLAMMER](https://pubs.usgs.gov/tm/12b1/) and provide more robust output (e.g., arrays of relative displacement time history instead of raster images).
More importantly, pySLAMMER will be a python module that users can install and access using familiar syntax (i.e.,`pip install pySLAMMER` and `import pySLAMMER as slam`).

At a minimum, pySLAMMER includes or will include the following sliding block models:

* [x] Rigid (i.e., traditional Newmark analysis[^2] as implemented by Jibson (1993)[^3])
* [ ] Decoupled (per Makdisi and Seed 1978[^4])
* [ ] Coupled (described by Chopra and Zhang (1991)[^5] and modified by Rathje and Bray (1999)[^6])

## Verification

The pySLAMMER models will be verified by comparison with SLAMMER results using equivalent input parameters.

## Examples

Example use cases will be demonstrated using Jupyter workbooks. 

## Use cases

PySLAMMER is being developed with large- and small-scale use cases in mind, with potential applications in research, teaching, and practice.
The ability to run sliding block simulations in batches will lend itself to large-scale simulations in research and practice, both spatially (e.g., for regional hazard analysis) and parametrically (e.g., for probabilistic analsysis).
Small-scale analyses (i.e., running a single scenario or a small set of senarios with limited variablity) will, of course, also be possible.
These use cases may be appropriate for teaching and learning, or exploratory work in reasearch and practice.
Particularly when it comes to teaching and learning, the ability to visualize and inspect analysis output is important.
And coding proficiency may be a barrier to use.
Although there are currently no plans for a standalone graphical user interface (GUI) for pySLAMMER, the example Jupyter notebooks will be designed to be accessible to those with little-to-no coding experience.

[^1]: Jibson, R.W., Rathje, E.M., Jibson, M.W., and Lee, Y.W., 2013, SLAMMER—Seismic LAndslide Movement Modeled using Earthquake Records (ver.1.1, November 2014): U.S. Geological Survey Techniques and Methods, book 12, chap. B1, unpaged. https://pubs.usgs.gov/tm/12b1/

[^2]: Newmark, N. M. (1965). Effects of Earthquakes on Dams and Embankments. Geotechnique, 15(2), 139–160.


[^3]: Jibson, R. W. (1993). Predicting Earthquake-Induced Landslide Displacements Using Newmark’s Sliding Block Analysis. Transportation Research Record, 1411. https://trid.trb.org/view/384547

[^4]: Makdisi, F. I., & Seed, H. B. (1978). Simplified Procedure for Estimating Dam and Embankment Earthquake-Induced Deformations. Journal of the Geotechnical Engineering Division, 104(7), 849–867. https://doi.org/10.1061/AJGEB6.0000668

[^5]:Chopra, A. K., & Zhang, L. (1991). Earthquake‐Induced Base Sliding of Concrete Gravity Dams. Journal of Structural Engineering, 117(12), 3698–3719. https://doi.org/10.1061/(ASCE)0733-9445(1991)117:12(3698)

[^6]:Rathje, E. M., & Bray, J. D. (1999). An examination of simplified earthquake-induced displacement procedures for earth structures. Canadian Geotechnical Journal, 36(1), 72–87. https://doi.org/10.1139/cgj-36-1-72
