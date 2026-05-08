# pySLAMMER docs audit + interactive-notebook plan

## 1. Overall doc quality

**Strong points**
- Landing page (`index.qmd`) is well-organized with card navigation.
- `quickstart.qmd` is a clean, runnable end-to-end intro.
- `comp_SLAMMER_results.qmd` is genuinely thorough — verification with regression stats + cm-scale equivalence threshold is publication-ready.
- `motivation.qmd` clearly stakes out the "why" (escape from GUI, batch/pipeline use).
- API reference is auto-generated via quartodoc, so it'll stay current.

**Specific issues to clean up**
- **Stubs and empty pages**: `technical/glossary.qmd` says "stub", `technical/ground_motions.qmd` is 1 line / empty, `technical/tech_manual.qmd` only links to two children, `technical/verification.qmd` has commented-out links to `comp_SLAMMER_perf.qmd` and `comp_analytical.qmd` (which exist on disk but are unlinked). Either finish them, hide them from the sidebar, or replace with placeholders that say what they will become.
- **Sample-motion suite is undocumented**: there are ~20 motions in `sample_ground_motions/` with response spectra rendered in `comp_SLAMMER_results.qmd`, but no flat list/table that says "here's what's bundled and why." `_static/gm_summary.csv` exists — render it as a table on the (currently empty) `ground_motions.qmd`.

**Subjective gaps**
- Quickstart shows a rigid analysis only — nothing on the more interesting flexible methods that motivate using pySLAMMER over hand-rolled Newmark code.
- `target_pga` and `scale_factor` (built-in PGA scaling on every analysis class) are not mentioned in quickstart or rigid_flex.

## 2. Format choices for example notebooks

qmd is the canonical format for the docs. Most of the audience knows Jupyter; `quarto convert` does qmd ↔ ipynb cleanly, so a downloadable .ipynb is a true free derivative rather than a separately maintained artifact. Marimo is younger and less established; betting *most* of the docs on it carries more long-term risk than necessary. Use marimo only where its specific strength (reactive UI) is the point.

**Three kinds of notebook content** — picking the right format is a question of which kind a given notebook is, not a question of which format we prefer in general.

1. **Static literate analysis** — narrative + code + figures. Format: **qmd canonical**, .ipynb auto-derived via Quarto's download feature for users who want to run it locally. No marimo version. This is what almost every example will be (`rigid_flex`, `batch_simulations`, `pbsd_segments`, `ky_sensitivity`, `custom_ground_motion`, future verification companions, etc.).

2. **Interactive parameter exploration** — sliders, dropdowns, live recomputation; the value *is* the interactivity. Format: **marimo .py canonical**, PEP 723 inline deps, molab WASM link for one-click in-browser running. No qmd equivalent because there's nothing to render statically. Currently exactly one: `pyslammer_demo`.

3. **Playground companion to a static analysis** — same underlying computation as a kind-1 notebook, exposed with a few widgets so a curious reader can fiddle. Format: marimo. **Don't speculate-build these.** Build a kind-3 only when there's clear demand for one specific kind-1 notebook; treat it as an editorial reduction (strip prose, pick widgets, reactive figure), not a translation. The qmd is not its source — they share an analysis, not a source file.

**The pattern**, applied per example:

- **Kind 1**: `docs/examples/<topic>.qmd` is canonical. Quarto generates an ipynb download alongside the rendered HTML. No file in `notebooks/`.
- **Kind 2**: `notebooks/<topic>.py` is canonical (marimo). A short `docs/examples/<topic>.qmd` exists only to host the molab embed/links — no analysis content there.
- **Kind 3**: `notebooks/<topic>_playground.py` (marimo). Linked from the corresponding kind-1 page via a sidebar callout, but not its derivative.

**Conversion realities, briefly**

- `quarto convert` (qmd ↔ ipynb): bidirectional, clean. Chunk options (`#| label:`, `#| fig-cap:`) round-trip reliably. Treat them as two views of the same source.
- `marimo convert input.ipynb → output.py`: works, but trips on marimo's "every variable defined exactly once across the notebook" rule. For static analyses this is usually small renaming; for stateful notebooks it can be substantial. Use only when consciously promoting a kind-1 notebook to a kind-3 playground.
- `marimo export ipynb notebook.py → notebook.ipynb`: exports code but **strips interactive widgets**. The round-trip qmd → ipynb → marimo → ipynb destroys what marimo brings. Don't do it.

**Build/CI considerations**

- Quarto's `freeze: auto` already caches qmd executions; don't break it.
- Marimo notebooks live in `notebooks/`, link out to molab for live running. Don't try to embed live marimo into the Quarto site itself.
- Add marimo `.py` notebooks to a CI smoke-test that runs each one headlessly so they don't bit-rot when the API changes.
- Heavyweight kind-1 notebooks (see §3) need a precompute strategy so the docs build doesn't hang for hours.

**Contributor onboarding**

If marimo is the form for interactive demos, contributors who want to add one have to learn marimo. Lower the friction explicitly: add a short "Contributing an interactive notebook" subsection to `about/develop.qmd` linking to marimo's docs and pointing at `notebooks/pyslammer_demo.py` as the reference example.

## 3. Suite of focused example notebooks

The current docs have two examples (`rigid_flex`, `batch_simulations`) plus the new `pyslammer_demo`. The "monster notebook" trap is to keep growing one of these. Better: one notebook = one question.

pySLAMMER's value parsed into five distinct strands:

| Strand | What it sells | Notebook | Kind / Format | Runtime |
|---|---|---|---|---|
| **Interactive exploration** | "Feel" how params affect displacement | `pyslammer_demo` (built) | Kind 2 — marimo | Lightweight (molab) |
| **Method comparison & teaching** | Why flexible methods matter; what the plots show | `rigid_flex` (exists) | Kind 1 — qmd | Lightweight |
| **Parameter sweeps / sensitivity** | Why you'd leave the GUI: scan k_y, plot the curve | NEW: `ky_sensitivity` | Kind 1 — qmd | Lightweight |
| **Motion-suite & batch analysis** | Compute over a suite, build fragility-style plots | `batch_simulations` (cleanup) + NEW: `pbsd_segments` | Kind 1 — qmd | Heavyweight |
| **BYO ground motion** | Practical onramp for working engineers | NEW: `custom_ground_motion` | Kind 1 — qmd | Lightweight |

Note: there are no planned kind-3 (playground) notebooks. If demand emerges for one (e.g. someone wants to drag a slider through `ky_sensitivity`), build the playground at that point rather than speculatively. The interactive demo (`pyslammer_demo`) already covers the broad "play with parameters" use case.

**Concrete new-notebook proposals (three to build first)**

1. **`ky_sensitivity.qmd`** (kind 1) — one motion, scan k_y from 0.01 to k_max in 100 steps, plot displacement-vs-ky on log axes. ~30 lines. Sells the batch story without the cognitive load of the full motion suite.

2. **`custom_ground_motion.qmd`** (kind 1) — load a user CSV (with a built-in fallback), build `slam.GroundMotion(accel, dt, name=...)`, run an analysis. Shows that the sample suite is a convenience, not a constraint. Single most-asked practitioner question.

3. **`pbsd_segments.qmd`** (kind 1, heavyweight) — port of the SoftwareX paper's PBSD example (`temp/manuscript_assets/pbsd_example.ipynb`), made suitable for the docs. Two highway-bridge slope segments (A and B), Monte-Carlo Coupled SBA over log-normal `ky`/`Vs`, P[D > 25 cm] curves. Needs a precompute/cache strategy (see below).

### Lightweight vs heavyweight notebooks

This distinction applies primarily to kind-1 (qmd) notebooks. Kind-2 (marimo) notebooks are inherently lightweight by design — heavyweight marimo would just hang in molab WASM and isn't a category we'd build.

**Lightweight** (renders cheaply during docs build; runs in seconds locally):
- Most kind-1 qmd notebooks. Quarto's `freeze: auto` caches the rendering.
- All kind-2 marimo notebooks. Get an "Open in molab" link plus a "Download notebook (.py)" button.

**Heavyweight** (needs minutes-to-hours; can't run in docs build directly):
- Monte-Carlo suites and full motion-suite × parameter scans (`pbsd_segments`, future `fragility_curve`, the parametric verification companion).
- Always kind 1 / qmd format. Get a "Download notebook (.ipynb)" button via Quarto.
- **Precompute strategy**: notebook writes a results cache (parquet / pickle.gz) on first local run, checks for it on subsequent runs. The qmd page does *not* recompute during docs build — it loads the cache from a known location (e.g. `_static/cache/` or a release asset).
- The qmd should call out the runtime cost explicitly ("This analysis takes ~30 minutes on a modern laptop. The notebook caches results after the first run.")
- Static-fallback figure ships with the docs (e.g. the manuscript's `pbsd_example.pdf`) so the page renders meaningfully even before the cache is built.

## SoftwareX paper as a docs source

The full SoftwareX manuscript lives at `temp/01_pyslammer.tex` (Arnold & Garcia-Rivas 2026, ~490 lines). Several sections are reusable in the docs without major rewriting:

- **§3 Illustrative examples (PBSD)** → drives the `pbsd_segments.py` notebook above. Parameter table is `tab:pbsd_params` in the paper.
- **§2 Software architecture** (class inheritance figure, Coupled-method flowchart, the O(n²)→O(n) story, the Lee 2004 foundation-radiation damping equation) → fleshes out the currently bare `technical/tech_manual.qmd` and gives `glossary.qmd` real content.
- **§1 Motivation/significance** — overlaps with `about/motivation.qmd`. Either expand `motivation.qmd` to match the paper's depth (NHERI Science Plan, regional-scale framing) or leave the existing version as the short version and link the paper for the long version.
- **The Lee (2004) damping formula** (eq. \ref{eq:damp} in the paper) is currently only mentioned in a footnote of `comp_SLAMMER_results.qmd`. It's a hidden SLAMMER quirk worth surfacing in `glossary.qmd` or the tech manual.
- **Forward reference at line 270** of the paper: *"Full details on the ground motions and parametric study are available in pySLAMMER's documentation as a downloadable, executable Python notebook."* No such notebook ships with the docs today. Either build it (likely a verification-study companion to `comp_SLAMMER_results.qmd`) or revise the paper sentence before publication.

The PBSD notebook source has been pulled to `temp/manuscript_assets/pbsd_example.ipynb` from the manuscript repo (`https://github.com/lornearnold/manuscript_pyslammer`). Port the analysis from there into the docs as a kind-1 qmd rather than rewriting from scratch. Cleanups noted during review: drop the dead `itertools.product` over `[A, B] × ["coupled"]` (both branches now run only `coupled`); drop the leftover `for segment in df["segment"].unique(): df_seg = ...` block above the main plot; pare the commented-out motion names in `record_names`.

## Rollout phases

- **Phase 1 (low risk)**: finish the remaining doc bugs in §1 (technical stubs, sample-motion suite). Configure Quarto's per-page `.ipynb` download for existing kind-1 examples so the "Download notebook" button works without manual maintenance.
- **Phase 2**: build the three new focused kind-1 qmd notebooks above. PBSD draws from `temp/manuscript_assets/pbsd_example.ipynb` and §3 of the SoftwareX paper. Adopt the qmd-canonical, ipynb-derivative pattern from §2 of this plan. Wire up the precompute/cache pattern for `pbsd_segments` and any other heavyweight notebooks.
- **Phase 3**: fill the actual stubs — `tech_manual.qmd` and `glossary.qmd` from §2 of the paper; `ground_motions.qmd` from `_static/gm_summary.csv` plus the response-spectra figure already used in `comp_SLAMMER_results.qmd`. Add the "Contributing an interactive notebook" subsection to `about/develop.qmd`.

## Spillover items captured during audit

- Decide whether `comp_SLAMMER_perf.qmd` and `comp_analytical.qmd` (referenced but commented out in `verification.qmd`) should be finished, hidden, or removed.
- `tests/verification_data/results/verification_report_v0.2.3.md` is referenced from the docs as a GitHub link — consider whether the verification report should also be rendered into the Quarto site for offline readers.
- Resolve the paper's promise (line 270) of a downloadable parametric-study notebook before publication, or amend the manuscript text.
