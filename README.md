# Oracle-Bone Glyphs: Parametric Vector Dataset & Tools

> **v0.2 (2026-06-13).** Labels in this release supersede those of v0.1, in
> which a small subset of polylines had been mis-paired with their `char` /
> `unicode` labels. The polyline shape data itself was unaffected. 1,001 of
> 1,203 entries carry standard CJK Unicode code points; the remaining 202 are
> non-simplified characters labelled with pinyin (no standard code point
> exists).

> Open release accompanying the manuscript
> *Interpretable Parametric Foundation for Oracle Bone Script: Dataset, Adaptive Arc
> Segmentation, and SVG Resource* (npj Heritage Science, in submission).

This repository releases **1,203 deciphered oracle bone glyphs** in an interpretable
parametric vector form (per-sub-segment direction α, magnitude η, signed curvature κ),
together with the fitting / analysis pipeline and a derived resolution-independent SVG
glyph set.

## What's inside

```
release/
├── README.md
├── LICENSE-CODE             MIT (covers /src)
├── LICENSE-DATA             CC-BY 4.0 (covers /data and /figs)
├── requirements.txt
├── data/
│   ├── jgw_1203_labeled.json        1,203 glyphs: id, char, unicode, strokes (polyline)
│   ├── jgw_1203_labeled.csv         flattened CSV view
│   ├── svg_polyline/                1,203 SVGs: straight-segment polyline (visual fidelity)
│   ├── svg_polyline_manifest.csv    id, char, unicode, svg filename
│   ├── svg_parametric/              1,203 SVGs: parametric reconstruction (analytical canonical)
│   └── svg_parametric_manifest.csv  id, char, unicode, svg filename
├── src/
│   ├── stroke_param_fit_min.py     closed-form (α, η, κ); single-arc reconstruction
│   ├── stroke_param_fit_v2.py      error-driven adaptive arc segmentation (main method)
│   ├── corpus_stats.py             corpus-level structural statistics + Fig. 1
│   ├── svg_export.py               parametric reconstruction → SVG (single-set helper)
│   ├── carving_dual.py             dual SVG export + two-flavor comparison (Fig. 6)
│   └── param_control_demo.py       interpretable controllability demo (Fig. 5)
└── figs/
    ├── fig01.png ... fig06_styles.png  six manuscript figures, 300 dpi
    └── figure_captions.md          publication-grade captions
```

## Quick start

Requirements: Python ≥ 3.10, `matplotlib` (only stdlib otherwise).

```
pip install -r requirements.txt
cd src
python stroke_param_fit_min.py        # writes out_min/  (single-arc baseline)
python stroke_param_fit_v2.py         # writes out_v2/   (adaptive segmentation; main)
python corpus_stats.py                # writes out_paper/  (Fig. 1 + stats)
python svg_export.py                  # writes out_paper/svg/  (single-set helper)
python carving_dual.py                # writes out_paper/svg_polyline/, svg_carving/ + Fig. 6 comparison
python param_control_demo.py          # writes out_paper/param_control.png  (Fig. 5)
```

The pipeline is fully deterministic and reproduces every quantitative result in the
manuscript (median normalized reconstruction error 0.0026; P90 0.015; mean 10.3
sub-segments per glyph; 72.2 % weak-curvature sub-segments).

## Data format

Each entry in `jgw_1203_labeled.json` contains:

| field | meaning |
|---|---|
| `id` | integer 1..1203 |
| `char` | modern Chinese character (single CJK code point) **or** pinyin string (for 202 entries whose modern form is not in the simplified character set) |
| `unicode` | hex code point if `char` is a single CJK character (empty for the 202 pinyin entries) |
| `n_points`, `n_strokes` | descriptive counts derived from `stroke` |
| `stroke` | DDLJC-style vector polyline: `N, -64, 0, x, y, x, y, …, -64, 0, …, -64, -64` (point count, `-64` stroke separator, `0` segment flag, integer (x, y) pairs, `-64, -64` glyph terminator) |

## Label coverage

All 1,203 polyline shapes in the dataset are paired with their correct
`(char, unicode)` labels.

- **1,001 of 1,203 (83.2 %)** entries carry a standard CJK Unicode code point
  in the `unicode` field; the `char` field is a single Chinese character.
- **202 of 1,203 (16.8 %)** entries carry a pinyin string in the `char` field
  and have no value in the `unicode` field, because the modern form of the
  underlying character is not in the simplified-Chinese set.

The release supersedes a transient earlier (v0.1) version in which a small
subset of polylines had been mis-paired with their `char` / `unicode` labels.
The polyline shape data itself was unaffected; only the label association
was incorrect.

## Citation

If you use this resource, please cite the accompanying manuscript:

> [authors]. *Interpretable Parametric Foundation for Oracle Bone Script: Dataset,
> Adaptive Arc Segmentation, and SVG Resource.* npj Heritage Science, 2026
> (in submission).

## License

- Code (`/src`) — MIT (see `LICENSE-CODE`).
- Data and figures (`/data`, `/figs`) — Creative Commons Attribution 4.0 International
  (CC-BY 4.0; see `LICENSE-DATA`).

## Honest scope

This release covers **single-script, single representative glyph per character**.
Allographic variation, cross-stage script evolution, and scribe-group ("贞人")
interpretable style analysis are explicitly out of scope and identified as future work
in the manuscript. The constant-curvature reconstruction exhibits small residual loops
on the sharpest hook sub-segments (a minority); finer curvature-aware primitives are
deferred to subsequent work.

## Contact

[corresponding author email — TO FILL]
