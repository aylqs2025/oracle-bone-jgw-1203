# Oracle-Bone Glyphs: Parametric Vector Dataset & Tools

> **v0.3 (2026-08-10).** Label and metadata release; **polyline shape data is
> unchanged from v0.2**. Pinyin no longer serves as a character identity: of the
> 202 entries that carried a pinyin string in v0.2, **200 now carry their exact
> modern character and Unicode code point**, and 2 are recorded as unidentified.
> `id` is renamed `glyph_id`. A per-entry `provenance_manifest.csv` is added. See
> [CHANGELOG.md](CHANGELOG.md) for the full list of changes and for the v0.2 and
> v0.1 history.
>
> **Encoding.** Files are UTF-8 and include CJK Extension A characters and one
> supplementary-plane character (𠕋 U+2054B). Read as UTF-8 and index by code
> point, not by UTF-16 code unit.

> Open release accompanying the manuscript
> *An Interpretable Parametric Representation and Open Dataset for Oracle Bone Script: Adaptive Arc Segmentation and SVG Resource*
> (npj Heritage Science, 2026; accepted).

This repository releases **1,203 oracle bone glyph forms** in an interpretable
parametric vector form (per-sub-segment direction α, magnitude η, signed curvature κ),
together with the fitting / analysis pipeline and a derived resolution-independent SVG
glyph set.

## Identity and label fields

`glyph_id` is the sole identifier of a glyph form. It is the entry number of the
source library, whose ordering follows *Shuowen Jiezi*.

| Field | Meaning |
|---|---|
| `glyph_id` | stable unique identity of the glyph form |
| `modern_char` | modern character assigned to the entry (empty if unidentified) |
| `unicode` | code point of `modern_char`, where that character is encoded |
| `char_form` | `in_simplified_set` / `traditional_or_variant` / `undetermined` |
| `encoding_status` | `unicode_encoded` / `not_encoded` |
| `pinyin` | modern Mandarin reading — an **auxiliary search field only** |

Two properties are worth stating explicitly:

- **`modern_char` is not a unique key.** 33 modern characters in this release are each
  assigned to more than one entry — entries 39 and 283 are both 萑, for instance. This
  reflects documented paleographic differentiation, not duplicate labelling. Resolve
  identity through `glyph_id`.
- **Unicode encoding status refers to the modern character, not to the oracle-bone
  form.** Oracle bone script is not itself encoded in Unicode; none of the 1,203
  released forms has a code point of its own.

## What's inside

```
release/
├── README.md
├── LICENSE-CODE             MIT (covers /src)
├── LICENSE-DATA             CC-BY 4.0 (covers /data and /figs)
├── requirements.txt
├── data/
│   ├── jgw_1203_labeled.json        1,203 glyphs: glyph_id, modern_char, unicode,
│   │                                 char_form, encoding_status, pinyin, strokes
│   ├── jgw_1203_labeled.csv         flattened CSV view
│   ├── provenance_manifest.csv      per-entry provenance: identity_confidence,
│   │                                 identity_note, composition_note,
│   │                                 n_source_variants, previous_label_v0_2
│   ├── jgw_1203_labeled_v0_2.*      superseded v0.2 labels, kept for reference
│   ├── svg_polyline/                1,203 SVGs: straight-segment polyline (visual fidelity)
│   ├── svg_polyline_manifest.csv    glyph_id, modern_char, unicode, char_form, svg
│   ├── svg_parametric/              1,203 SVGs: parametric reconstruction (analytical canonical)
│   └── svg_parametric_manifest.csv  glyph_id, modern_char, unicode, char_form, svg
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

> Qing-sheng Li and Yu-lin Bian. *An Interpretable Parametric Representation and Open Dataset for Oracle Bone Script: Adaptive Arc Segmentation and SVG Resource.*
> npj Heritage Science (2026). Accepted.

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

aylqs@163.com
