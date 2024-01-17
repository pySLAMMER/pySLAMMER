# sliding_block
Python code for calculating sliding block displacements.

When finished, this code should be able to replicate the output currently provided by [SLAMMER](https://pubs.usgs.gov/tm/12b1/) as well as connect to Design Safe's [ground motion database](https://www.designsafe-ci.org/data/browser/public/designsafe.storage.published/PRJ-3031).

SLAMMER was developed by M. Jibson, who has posted what I *think* is the full [source code on GitHub](https://github.com/mjibson/slammer).

The general workflow of all sliding block models: **Input**: Slope parameters, recorded ground motion; **Output** Time-history of accumulated displacement.

Sliding block models to include:
* [ ] Rigid (Newmark)
* [ ] Decoupled (Makdisi and Seed)
* [ ] Coupled (Kramer and Smith)

https://pubs.usgs.gov/tm/12b1/
