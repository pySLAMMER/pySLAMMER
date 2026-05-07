# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "pyslammer>=0.2.3",
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

    A minimal demonstration of [pySLAMMER](https://pypi.org/project/pyslammer/). Pick sample ground motion, target PGA, an analysis type and set the slope parameters below.
    """)
    return


@app.cell(hide_code=True)
def _(analysis_type, disp_md, fig, gm_panel, mo, slope_panel):
    _type_panel = mo.vstack(
        [mo.md("**Analysis type**"), analysis_type],
        gap=0.5, align="stretch",
    )

    _output_card = mo.callout(
        mo.vstack([fig, disp_md], gap=0.0, align="stretch"),
        kind="neutral",
    )

    _spacer = mo.Html('<div style="height: 2.5rem; min-height: 2.5rem; flex-shrink: 0;"></div>')

    _left_column = mo.vstack(
        [_spacer, mo.vstack([gm_panel, _type_panel, slope_panel], gap=0.5, align="stretch")],
        gap=0, align="stretch",
    )

    mo.hstack(
        [_left_column, _output_card],
        widths=[1, 2],
        align="start",
        gap=1.0,
    )
    return


@app.cell
def _():
    import pyslammer as slam
    motions = slam.sample_ground_motions()
    return motions, slam


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


@app.cell(hide_code=True)
def _(mo):
    analysis_type = mo.ui.radio(
        options=["Rigid", "Decoupled", "Coupled"],
        value="Coupled",
        inline=True,
    )
    return (analysis_type,)


@app.cell(hide_code=True)
def _(mo, motions):
    ky = mo.ui.number(start=0.05, stop=0.5, step=0.01, value=0.2, full_width=True)
    motion_name = mo.ui.dropdown(
        options=sorted(motions.keys()),
        value="Imperial_Valley_1979_BCR-230",
        full_width=True,
    )
    target_pga = mo.ui.number(start=0.05, stop=1.5, step=0.05, value=0.5, full_width=True)
    return ky, motion_name, target_pga


@app.cell(hide_code=True)
def _(analysis_type, ky, mo):
    height = mo.ui.number(start=10, stop=200, step=5, value=50, full_width=True)
    vs_slope = mo.ui.number(start=100, stop=1500, step=50, value=600, full_width=True)
    vs_base = mo.ui.number(start=100, stop=2000, step=50, value=600, full_width=True)
    damp_ratio = mo.ui.number(start=0.01, stop=0.20, step=0.01, value=0.05, full_width=True)
    soil_model = mo.ui.dropdown(
        options=["linear_elastic", "equivalent_linear"],
        value="equivalent_linear",
        full_width=True,
    )
    ref_strain = mo.ui.number(start=1e-5, stop=1e-2, step=1e-4, value=5e-4, full_width=True)

    def _row(label, widget, label_w_px=170):
        return mo.hstack(
            [mo.Html(f'<div style="width:{label_w_px}px">{label}</div>'), widget],
            align="center", justify="start", gap=0.5,
        )

    slope_items = [mo.md("**Slope parameters**"), _row("Yield acceleration k_y (g)", ky)]
    if analysis_type.value != "Rigid":
        slope_items += [
            _row("Slope height (m)", height),
            _row("Vs slope (m/s)", vs_slope),
            _row("Vs base (m/s)", vs_base),
            _row("Damping ratio", damp_ratio),
            _row("Soil model", soil_model),
            _row("Reference strain", ref_strain),
        ]
    slope_panel = mo.vstack(slope_items, gap=0.5, align="stretch")
    return (
        damp_ratio,
        height,
        ref_strain,
        slope_panel,
        soil_model,
        vs_base,
        vs_slope,
    )


@app.cell(hide_code=True)
def _(mo, motion_name, target_pga):
    def _row(label, widget, label_w_px=170):
        return mo.hstack(
            [mo.Html(f'<div style="width:{label_w_px}px">{label}</div>'), widget],
            align="center", justify="start", gap=0.5,
        )

    gm_panel = mo.vstack([
        mo.md("**Ground motion parameters**"),
        _row("Ground motion", motion_name),
        _row("Target PGA (g)", target_pga),
    ], gap=0.5, align="stretch")
    return (gm_panel,)


@app.cell(hide_code=True)
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
    target_pga,
    vs_base,
    vs_slope,
):
    _gm_raw = motions[motion_name.value]
    _scale = target_pga.value / _gm_raw.pga if _gm_raw.pga > 0 else 1.0
    gm = slam.GroundMotion(_gm_raw.accel * _scale, _gm_raw.dt, name=_gm_raw.name)

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
    return (result,)


@app.cell(hide_code=True)
def _(mo, result):
    disp_md = mo.md(f"**Total sliding displacement:** {result.max_sliding_disp:.3f} m")
    return (disp_md,)


@app.cell(hide_code=True)
def _(plot_style_applied, result):
    _ = plot_style_applied  # ensure plot config runs first
    fig = result.sliding_block_plot()
    return (fig,)


if __name__ == "__main__":
    app.run()
