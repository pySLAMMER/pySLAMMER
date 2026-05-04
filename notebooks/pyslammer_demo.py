# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "pyslammer>=0.2.2",
#     "numpy",
#     "scipy",
#     "matplotlib",
# ]
# ///

import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # pySLAMMER demo

    A minimal demonstration of [pySLAMMER](https://pypi.org/project/pyslammer/):
    a Python implementation of the USGS SLAMMER seismic sliding-block analysis tool.

    Pick a sample ground motion and a yield acceleration, then run a rigid sliding block analysis.
    """)
    return


@app.cell
def _():
    import pyslammer as slam
    motions = slam.sample_ground_motions()
    return motions, slam


@app.cell(hide_code=True)
def _(mo):
    analysis_type = mo.ui.radio(
        options=["Rigid", "Decoupled", "Coupled"],
        value="Rigid",
        label="Analysis type",
        inline=True,
    )
    analysis_type
    return (analysis_type,)


@app.cell
def _(mo, motions):
    motion_name = mo.ui.dropdown(
        options=sorted(motions.keys()),
        value="Imperial_Valley_1979_BCR-230",
        label="Ground motion",
    )
    ky = mo.ui.slider(
        start=0.05, stop=0.5, step=0.01, value=0.2,
        label="Yield acceleration k_y (g)", show_value=True,
    )
    mo.hstack([motion_name, ky])
    return ky, motion_name


@app.cell(hide_code=True)
def _(analysis_type, mo):
    height = mo.ui.slider(start=10, stop=200, step=5, value=50,
                           label="Slope height (m)", show_value=True)
    vs_slope = mo.ui.slider(start=100, stop=1500, step=50, value=600,
                             label="Vs slope (m/s)", show_value=True)
    vs_base = mo.ui.slider(start=100, stop=2000, step=50, value=600,
                            label="Vs base (m/s)", show_value=True)
    damp_ratio = mo.ui.slider(start=0.01, stop=0.20, step=0.01, value=0.05,
                               label="Damping ratio", show_value=True)
    soil_model = mo.ui.dropdown(
        options=["linear_elastic", "equivalent_linear"],
        value="equivalent_linear",
        label="Soil model",
    )
    ref_strain = mo.ui.number(start=1e-5, stop=1e-2, step=1e-4, value=5e-4,
                              label="Reference strain")

    if analysis_type.value == "Rigid":
        flex_panel = mo.md("*Rigid analysis: no flexible-block parameters needed.*")
    else:
        flex_panel = mo.vstack([
            mo.md("**Flexible-block parameters**"),
            height, vs_slope, vs_base, damp_ratio, soil_model, ref_strain,
        ])
    flex_panel
    return damp_ratio, height, ref_strain, soil_model, vs_base, vs_slope


@app.cell
def _(
    analysis_type,
    damp_ratio,
    height,
    ky,
    motion_name,
    motions,
    ref_strain,
    slam,
    soil_model,
    vs_base,
    vs_slope,
):
    gm = motions[motion_name.value]

    if analysis_type.value == "Rigid":
        result = slam.RigidAnalysis(ky.value, gm)
    else:
        flex_kwargs = dict(
            height=height.value,
            vs_slope=vs_slope.value,
            vs_base=vs_base.value,
            damp_ratio=damp_ratio.value,
            soil_model=soil_model.value,
            ref_strain=ref_strain.value,
        )
        if analysis_type.value == "Decoupled":
            result = slam.Decoupled(ky.value, gm, **flex_kwargs)
        else:
            result = slam.Coupled(ky.value, gm, **flex_kwargs)
        result._compile_sliding_attributes()
    return gm, result


@app.cell
def _(analysis_type, gm, ky, mo, result):
    mo.md(f"""
    **Analysis type:** {analysis_type.value}  
    **Ground motion:** {gm.name};
    **PGA:** {gm.pga:.3f} g  
    **Yield acceleration k_y:** {ky.value:.2f} g  
    **Sliding displacement:** {result.max_sliding_disp:.3f} m  
    """)
    return


@app.cell
def _(plot_style_applied, result):
    _ = plot_style_applied  # ensure plot config runs first
    fig = result.sliding_block_plot()
    fig
    return


@app.cell(hide_code=True)
def _(slam):
    # --- Notebook plot configuration ---
    # Defined here (rather than at the top) to keep configuration out of the
    # narrative flow. marimo's reactive graph runs cells in dependency order,
    # not file order, so this still runs before any cell that reads
    # `plot_style_applied`.

    # Font fallbacks: pyslammer's bundled style asks for Arial only, which
    # triggers a matplotlib warning on systems without it (e.g. molab/Pyodide).
    # Listing alternates lets matplotlib silently fall back to DejaVu Sans.
    slam.utilities.psfigstyle["font.sans-serif"] = [
        "Arial", "DejaVu Sans", "Liberation Sans", "Helvetica", "sans-serif",
    ]

    # DPI for inline figure rendering. matplotlib defaults to 100; bumping this
    # makes figures crisper in environments that don\'t upscale SVG output.
    slam.utilities.psfigstyle["figure.dpi"] = 200

    plot_style_applied = True
    return (plot_style_applied,)


if __name__ == "__main__":
    app.run()
