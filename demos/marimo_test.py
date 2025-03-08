import marimo

__generated_with = "0.11.17"
app = marimo.App()


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Basic usage

        Once pyslammer is installed, import it to your Python code.
        The recommended ailas for pyslammer is `slam` using the following command:
        """
    )
    return


@app.cell
def _():
    import pyslammer as slam
    return (slam,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        This allows use of pyslammer features within your code with the short prefix `slam`.

        For example, after importing and aliasing pyslammer as above, let's say we want to run a rigid sliding block analysis on a slope.
        Assume that the slope has a yield acceleration, $k_y$, of $0.2$ g.
        We can do this with the following steps: 

        1. Import a ground motion
        2. Perform a rigid sliding block analysis
        3. Plot the analysis result
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Import a sample ground motion

        We will use the sample ground motion record `Imperial_Valley_1979_BCR-230` for this example. Refer to [TODO: add internal link] for details on the included sample ground motions.
        """
    )
    return


@app.cell
def _(slam):
    histories = slam.sample_ground_motions() # Load all sample ground motions
    gm = histories["Imperial_Valley_1979_BCR-230"] # Select a specific ground motion
    # Other motions to try:
    # "Chi-Chi_1999_TCU068-090", "Loma_Prieta_1989_HSP-000", "Northridge_VSP-360", "Imperial_Valley_1979_BCR-230"
    return gm, histories


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Perform a rigid sliding block analysis
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
        ## Plot the analysis result
        Like all of pySLAMMER's analysis methods, `RigidAnalysis` inherits a plotting function from its parent class (`SlidingBlockAnalysis`). You can display the plots using

        ```python
        result.sliding_block_plot()
        ```
        """
    )
    return


@app.cell
def _(result):
    result.sliding_block_plot() # Save only the first returned value, the Figure.
    return


@app.cell(hide_code=True)
def _():
    # Notebook setup
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
