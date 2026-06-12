# Oracle-Bone Glyphs: Parametric Vector Dataset & Tools

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
| `char` | modern Chinese character corresponding to the deciphered glyph (present for 927 verified entries; empty when `_label_disputed`) |
| `unicode` | hex code point if the character has a standard Unicode (present for 927 verified entries) |
| `n_points`, `n_strokes` | descriptive counts |
| `stroke` | DDLJC-style vector polyline: `N, -64, 0, x, y, x, y, …, -64, 0, …, -64, -64` (point count, `-64` stroke separator, `0` segment flag, integer (x, y) pairs, `-64, -64` glyph terminator) |
| `_label_disputed` | (boolean, optional) present when the original `char`/`unicode` label failed an independent geometric consistency check against the AY甲骨文 reference font and was cleared pending manual review |
| `_audit_status` | (string, optional) WARN or SEVERE — severity of the cleared mismatch |

## Label quality

All 1,203 polyline shapes in this dataset are verified; each has been visually
checked against its source. The `char` / `unicode` modern-character labels,
however, were independently re-audited against the AY甲骨文 reference font (a
1,203-glyph OTF font using PUA U+E002–U+E4B4) via geometric (width/height ratio)
consistency. The audit places each entry in one of four grades:

- **OK** (681 entries, 56.6 %) — wh ratio matches reference within 1.4×
- **OK_LOOSE** (246, 20.4 %) — within 2×
- **WARN** (75, 6.2 %) — within 4×, suspicious
- **SEVERE** (201, 16.7 %) — exceeds 4×, almost certainly mislabeled

Following the priority of not publishing potentially misaligned labels, the
`char` / `unicode` fields of all WARN and SEVERE entries with unicode labels (89
entries) have been **cleared in this release** and marked with
`_label_disputed: true`. A further 187 entries had no `char`/`unicode` label to
begin with. In total, **927 of 1,203 (77.1 %) entries carry a verified label**;
the remaining 276 entries provide polyline data only, pending manual review in
future versions.

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
