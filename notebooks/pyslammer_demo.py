# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "pyslammer>=0.2.3",
#     "numpy",
#     "scipy",
#     "matplotlib",
#     "plotly==6.7.0",
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

    A minimal demonstration of [pySLAMMER](https://pypi.org/project/pyslammer/). Pick sample ground motion, target PGA, analysis type, and slope parameters below.
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
    return


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
    direction = mo.ui.radio(
        options=["Normal", "Inverse"],
        value="Normal",
        inline=True,
    )
    return direction, ky, motion_name, target_pga


@app.cell(hide_code=True)
def _(mo):
    height = mo.ui.number(start=1, stop=200, step=1, value=30, full_width=True)
    vs_slope = mo.ui.number(start=10, stop=2000, step=50, value=600, full_width=True)
    vs_base = mo.ui.number(start=10, stop=2000, step=50, value=600, full_width=True)
    damp_ratio = mo.ui.number(start=0.0, stop=0.50, step=0.01, value=0.05, full_width=True)
    soil_model = mo.ui.dropdown(
        options=["linear_elastic", "equivalent_linear"],
        value="equivalent_linear",
        full_width=True,
    )
    ref_strain = mo.ui.number(start=0.00005, stop=0.01, step=0.00001, value=0.0005, full_width=True)
    return damp_ratio, height, ref_strain, soil_model, vs_base, vs_slope


@app.cell(hide_code=True)
def _(
    analysis_type,
    damp_ratio,
    height,
    ky,
    mo,
    ref_strain,
    soil_model,
    vs_base,
    vs_slope,
):
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
        ]
        if soil_model.value == "equivalent_linear":
            slope_items.append(_row("Reference strain", ref_strain))
    slope_panel = mo.vstack(slope_items, gap=0.5, align="stretch")
    return (slope_panel,)


@app.cell(hide_code=True)
def _(direction, mo, motion_name, target_pga):
    def _row(label, widget, label_w_px=170):
        return mo.hstack(
            [mo.Html(f'<div style="width:{label_w_px}px">{label}</div>'), widget],
            align="center", justify="start", gap=0.5,
        )

    gm_panel = mo.vstack([
        mo.md("**Ground motion parameters**"),
        _row("Ground motion", motion_name),
        _row("Target PGA (g)", target_pga),
        _row("Direction", direction),
    ], gap=0.5, align="stretch")
    return (gm_panel,)


@app.cell(hide_code=True)
def _(
    analysis_type,
    damp_ratio,
    direction,
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
    gm = motions[motion_name.value]
    scale_kwargs = dict(
        target_pga=target_pga.value,
        inverse=(direction.value == "Inverse"),
    )

    if analysis_type.value == "Rigid":
        result = slam.RigidAnalysis(ky.value, gm, **scale_kwargs)
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
            result = slam.Decoupled(ky.value, gm, **flex_kwargs, **scale_kwargs)
        else:
            result = slam.Coupled(ky.value, gm, **flex_kwargs, **scale_kwargs)
        result._compile_sliding_attributes()
    return (result,)


@app.cell(hide_code=True)
def _(mo, result):
    disp_md = mo.md(f"**Total sliding displacement:** {result.max_sliding_disp:.3f} m")
    return (disp_md,)


@app.cell(hide_code=True)
def _(mo, result):
    import numpy as np
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from pyslammer.utilities import G_EARTH

    # Match matplotlib tab colors
    _BLOCK = "black"
    _BASE = "#1f77b4"   # tab:blue
    _INPUT = "#7f7f7f"  # tab:gray

    # Single scaling knob: bump base font size; line widths and most tick/
    # title sizes are derived from it. Plotly's defaults render thinner than
    # matplotlib at the same nominal sizes (CSS-px vs. matplotlib points), so
    # we scale up here to match the matplotlib feel.
    _BASE_FONT = 14
    _LINE_W = 1.9

    result._compile_sliding_attributes()
    _t = np.arange(0, result._npts * result.dt, result.dt)
    _pga = float(np.max(np.abs(result.a_in)))
    _motion_name = getattr(result, "motion_name", "Unknown")
    _summary = (
        f"{type(result).__name__} | ky: {result.ky:.2f}g | "
        f"Motion: {_motion_name} (PGA: {_pga:.2f}g)"
    )

    _plotly_fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04,
    )

    _has_hea = hasattr(result, "HEA") and result.HEA is not None
    if _has_hea:
        _plotly_fig.add_trace(go.Scatter(
            x=_t, y=result._ground_acc_ / G_EARTH,
            mode="lines", name="Input Acc.",
            line=dict(color=_INPUT, width=_LINE_W),
            legendgroup="r1",
        ), row=1, col=1)
        _plotly_fig.add_trace(go.Scatter(
            x=_t, y=result.HEA / G_EARTH,
            mode="lines", name="Base Acc.",
            line=dict(color=_BASE, width=_LINE_W),
            legendgroup="r1",
        ), row=1, col=1)
    else:
        _plotly_fig.add_trace(go.Scatter(
            x=_t, y=result._ground_acc_ / G_EARTH,
            mode="lines", name="Base Acc.",
            line=dict(color=_BASE, width=_LINE_W),
            legendgroup="r1",
        ), row=1, col=1)

    _plotly_fig.add_trace(go.Scatter(
        x=_t, y=result._block_acc_ / G_EARTH,
        mode="lines", name="Block Acc.",
        line=dict(color=_BLOCK, width=_LINE_W),
        legendgroup="r1",
    ), row=1, col=1)

    _plotly_fig.add_trace(go.Scatter(
        x=_t, y=result.sliding_vel,
        mode="lines", name="Sliding Vel.",
        line=dict(color=_BLOCK, width=_LINE_W),
        legendgroup="r2",
    ), row=2, col=1)

    _plotly_fig.add_trace(go.Scatter(
        x=_t, y=result.sliding_disp,
        mode="lines", name="Sliding Disp.",
        line=dict(color=_BLOCK, width=_LINE_W),
        legendgroup="r3",
    ), row=3, col=1)

    _plotly_fig.update_layout(
        title=dict(
            text=_summary, x=0.5, xanchor="center", y=0.985,
            font=dict(size=_BASE_FONT, color="black"),
        ),
        font=dict(
            family="Arial, DejaVu Sans, Liberation Sans, Helvetica, sans-serif",
            size=_BASE_FONT, color="black",
        ),
        margin=dict(l=70, r=20, t=45, b=50),
        height=520,
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=True,
        legend=dict(
            bgcolor="white", bordercolor="white",
            font=dict(size=_BASE_FONT - 1, color="black"),
            x=0.995, xanchor="right", y=0.995, yanchor="top",
            tracegroupgap=0,
        ),
    )

    # Plotly only supports a single legend, so emulate per-subplot legends
    # (matplotlib places legends inside each axis): keep row-1 in the legend
    # and annotate rows 2 and 3 directly.
    _plotly_fig.update_traces(showlegend=False, selector=dict(legendgroup="r2"))
    _plotly_fig.update_traces(showlegend=False, selector=dict(legendgroup="r3"))
    _plotly_fig.add_annotation(
        xref="x2 domain", yref="y2 domain", x=0.99, y=0.97,
        xanchor="right", yanchor="top",
        text="Sliding Vel.", showarrow=False,
        bgcolor="white", bordercolor="white",
        font=dict(size=_BASE_FONT - 1, color="black"),
    )
    _plotly_fig.add_annotation(
        xref="x3 domain", yref="y3 domain", x=0.99, y=0.03,
        xanchor="right", yanchor="bottom",
        text="Sliding Disp.", showarrow=False,
        bgcolor="white", bordercolor="white",
        font=dict(size=_BASE_FONT - 1, color="black"),
    )

    # Axis styling: white background, single-level (coarser) gridlines, and
    # auto-ticks tuned to a smaller count than plotly's default.
    _axis_common = dict(
        showgrid=True, gridcolor="#d9d9d9", gridwidth=1,
        zeroline=False, showline=True, linecolor="#444", linewidth=1,
        mirror=True, ticks="outside", ticklen=5,
        tickfont=dict(size=_BASE_FONT - 1, color="black"),
        nticks=8,
    )
    _plotly_fig.update_xaxes(**_axis_common, range=[_t[0], _t[-1]])
    _yaxis_kwargs = {**_axis_common, 'nticks': 5}
    _plotly_fig.update_yaxes(**_yaxis_kwargs)
    _plotly_fig.update_yaxes(title_text="Acc. (g)", row=1, col=1,
                     title_font=dict(size=_BASE_FONT, color="black"))
    _plotly_fig.update_yaxes(title_text="Vel. (m/s)", row=2, col=1,
                     title_font=dict(size=_BASE_FONT, color="black"))
    _plotly_fig.update_yaxes(title_text="Disp. (m)", row=3, col=1,
                     title_font=dict(size=_BASE_FONT, color="black"))
    _plotly_fig.update_xaxes(title_text="Time (s)", row=3, col=1,
                     title_font=dict(size=_BASE_FONT, color="black"))

    # Curated modebar: download, box-zoom, pan, reset axes only.
    fig = mo.ui.plotly(
        _plotly_fig,
        config={
            "modeBarButtons": [["toImage", "zoom2d", "pan2d", "resetScale2d"]],
            "displaylogo": False,
        },
    )
    return (fig,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
