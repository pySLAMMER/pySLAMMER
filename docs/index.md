---
sd_hide_title: true
:html_theme.sidebar_secondary.remove:
---
# Overview

# Welcome to pySLAMMER's documentation

pySLAMMER: **Py**thon package for **S**eismic **L**andslide **M**ovement **M**odeled using **E**arthquake **R**ecords
is tool for estimating the co-seismic displacements of landslides with rigid and flexible sliding-block analyses.
The package name and code are based on the USGS tool SLAMMER[^jibson_2013].

pySLAMMER includes the following sliding block models:

* Rigid (i.e., traditional Newmark analysis[^newmark_1965] as implemented by Jibson (1993)[^jibson_1993])
* Decoupled (per Makdisi and Seed 1978[^makdisi_1978])
* Coupled (described by Chopra and Zhang (1991)[^chopra_1991] and modified by Rathje and Bray (1999)[^rathje_1999])

## Contents
```{toctree}
:maxdepth: 2
Quickstart Guide <quickstart_guide>
Batch demo <demos/batch_demo.ipynb>
Rigid and Flexible Analysis <demos/multi_method.ipynb>
apidocs/index
```

## References


[^jibson_2013]: Jibson, R.W., Rathje, E.M., Jibson, M.W., and Lee, Y.W., 2013, SLAMMER—Seismic LAndslide Movement Modeled using Earthquake Records (ver.1.1, November 2014): U.S. Geological Survey Techniques and Methods, book 12, chap. B1, unpaged. https://pubs.usgs.gov/tm/12b1/

[^newmark_1965]: Newmark, N. M. (1965). Effects of Earthquakes on Dams and Embankments. Geotechnique, 15(2), 139–160.

[^jibson_1993]: Jibson, R. W. (1993). Predicting Earthquake-Induced Landslide Displacements Using Newmark’s Sliding Block Analysis. Transportation Research Record, 1411. https://trid.trb.org/view/384547

[^makdisi_1978]: Makdisi, F. I., & Seed, H. B. (1978). Simplified Procedure for Estimating Dam and Embankment Earthquake-Induced Deformations. Journal of the Geotechnical Engineering Division, 104(7), 849–867. https://doi.org/10.1061/AJGEB6.0000668

[^chopra_1991]:Chopra, A. K., & Zhang, L. (1991). Earthquake‐Induced Base Sliding of Concrete Gravity Dams. Journal of Structural Engineering, 117(12), 3698–3719. https://doi.org/10.1061/(ASCE)0733-9445(1991)117:12(3698)

[^rathje_1999]:Rathje, E. M., & Bray, J. D. (1999). An examination of simplified earthquake-induced displacement procedures for earth structures. Canadian Geotechnical Journal, 36(1), 72–87. https://doi.org/10.1139/cgj-36-1-72