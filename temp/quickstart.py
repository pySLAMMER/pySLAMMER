import marimo

__generated_with = "0.11.25"
app = marimo.App(app_title="pySLAMMER Quickstart", css_file="marimo.css")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Quickstart
        ## Requirements

        The pyslammer package is built on Python 3.12.
        Earlier versions of Python 3 may work, but have not been tested.

        ## Installation using pip
        [![PyPI][pypi-badge]][pypi-link]


        Install pyslamer using `pip` from the Python Package Index (PyPI):
        ```bash
        pip install pyslammer
        ```

        [pypi-badge]: https://img.shields.io/pypi/v/pyslammer.svg
        [pypi-link]: https://pypi.org/project/pyslammer
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Basic Usage
        With `pyslammer` installed, basic usage involves the following steps:

        1. Import the `pyslammer` module
        2. Import a ground motion
        3. Perform a sliding block analysis
        4. View results

        ### Import the pyslammer module
        The recommended ailas for pyslammer is `slam`:
        """
    )
    return


@app.cell
def _():
    import pyslammer as slam
    return (slam,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""This allows use of pyslammer features within your code with the short prefix `slam`.""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Import a sample ground motion

        We will use the sample ground motion record `Imperial_Valley_1979_BCR-230` for this example. Refer to [TODO: add internal link] for details on the included sample ground motions.
        """
    )
    return


@app.cell
def _(slam):
    histories = slam.sample_ground_motions() # Load all sample ground motions
    gm = histories["Imperial_Valley_1979_BCR-230"] # Select a specific ground motion
    for history in histories:
        print(history)
    return gm, histories, history


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### Perform a sliding block analysis
        The primary object type within pyslammer is the `SlidingBlockAnalysis` object.
        At a minimum any `SlidingBlockAnalysis` requires a yield acceleration for the slope ($k_y$) and an input ground motion.
        For this example, let's use the `RigidAnalysis` subclass of `SlidingBlockAnalysis` to run a rigid sliding block analysis on a slope with a yield acceleration of $0.2$ g.

        With the imported ground motion, `gm`, and the assumed value of $k_y$, we can perform a rigid sliding block analysis with pySLAMMER's `RigidAnalysis` object. This simultaneously creates an instance of `RigidAnalysis` and performs the analysis, which is stored as `result`:
        """
    )
    return


@app.cell
def _(gm, slam):
    ky = 0.2 # yield acceleration in g
    result = slam.RigidAnalysis(gm.accel, gm.dt, ky)
    return ky, result


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ### View results

        The primary output of the sliding block analysis is the final displacement (`SlidingBlockAnalysis.max_sliding_disp`).
        By default, all lengths in pySLAMMER are in meters.
        The cell below shows the displacement induced by the sample ground motion in the example:

        Like all of pySLAMMER's analysis methods, `RigidAnalysis` inherits a plotting function from its parent class (`SlidingBlockAnalysis`). You can display the plots using `result.sliding_block_plot()`:
        """
    )
    return


@app.cell
def _(gm, ky, result):
    print(f"Slope yield acc: {ky:.2f} g \nGround motion: {gm.name}; PGA: {gm.pga:.2f} g \nSliding displacement: {result.max_sliding_disp:.3f} m")
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        The primary output of the sliding block analysis is the final displacement (`SlidingBlockAnalysis.max_sliding_disp`).
        By default, all lengths in pySLAMMER are in meters.
        The cell below shows the displacement induced by the sample ground motion in the example:
        """
    )
    return


@app.cell
def _(result):
    # mpl.use("svg")
    asdf = result.sliding_block_plot()#[0] # Save only the first returned value, the Figure.
    # mo.mpl.interactive(plt.gcf())
    # mo.as_html(asdf)
    asdf
    return (asdf,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""In addition to the final displacement, the displacement, velocity, and acceleration time histories of the block are returned as numpy arrays. See the documentation for the `SlidingBlockAnalysis`class for a detailed description of all the results.""")
    return


@app.cell(hide_code=True)
def _():
    # Notebook setup
    import marimo as mo
    import matplotlib as mpl
    mpl.use("svg")
    return mo, mpl


if __name__ == "__main__":
    app.run()
