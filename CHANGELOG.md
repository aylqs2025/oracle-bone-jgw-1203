# Changelog

## v0.3 (2026-08-10)

Released in response to peer review of the accompanying manuscript. **The polyline
shape data is byte-for-byte unchanged from v0.2**; all changes are to labels and
metadata.

### Identity and label schema

- `id` is renamed **`glyph_id`** and is the sole identifier of a glyph form. It
  corresponds to the entry number of the source library, whose ordering follows
  *Shuowen Jiezi*.
- **Pinyin no longer serves as a character identity.** In v0.2, 202 entries whose
  modern character lay outside the simplified-Chinese set carried a pinyin string in
  the `char` field. Because pinyin is not injective this collapsed distinct entries
  onto one label — six separate glyph forms were all labelled `yu`, six `xiang`,
  five `yi`. Pinyin is now an auxiliary field (`pinyin`) only.
- Of those 202 entries, **200 now carry their exact modern character and Unicode
  code point**; 2 could not be identified and are recorded as such rather than given
  an approximate label.
- New fields: `modern_char`, `char_form` (`in_simplified_set` /
  `traditional_or_variant` / `undetermined`), `encoding_status`
  (`unicode_encoded` / `not_encoded`), `pinyin`.

### Coverage

| | v0.2 | v0.3 |
|---|---:|---:|
| Entries with a Unicode code point | 1,001 | **1,201** |
| Entries labelled with pinyin only | 202 | 0 |
| Entries recorded as unidentified | 0 | 2 |

`char_form`: 994 in the simplified set,
207 traditional or variant, 2 undetermined.
210 entries changed label relative to v0.2.

### New file: `provenance_manifest.csv`

Per-entry provenance, one row per glyph: `glyph_id`, the character assignment and its
code point, `identity_confidence` (`high` / `provisional` / empty where unidentified),
`identity_note` recording the basis of each assignment, the structural description
found in the source material (`composition_note`), the number of alternative source
forms available for that entry (`n_source_variants`), any legacy private-use code
point (`pua_legacy`), and the v0.2 label (`previous_label_v0_2`).

### Encoding note

The files are UTF-8. The character set now includes CJK Extension A code points
(entries 332, 739) and one **supplementary-plane** character,
𠕋 U+2054B (entry 345). Tools that assume all characters lie in
the basic multilingual plane, or that index strings by UTF-16 code unit, may mis-handle
that entry. Read the files as UTF-8 and index by code point.

### Not changed

- Polyline coordinates, stroke order and the `(-64, 0)` / `(-64, -64)` sentinel
  convention.
- The two SVG glyph sets themselves (the SVG files are unchanged; their manifests are
  re-issued with the v0.3 field schema, and the v0.2 manifests are kept as
  `svg_*_manifest_v0_2.csv`).
- Licence: CC BY 4.0 for data, MIT for code.

The v0.2 files are retained as `jgw_1203_labeled_v0_2.csv` / `.json` for reference.

## v0.2 (2026-06-13)

Corrected a label misalignment present in v0.1, in which a subset of polylines had
been paired with the wrong modern-character labels. Polyline shape data unaffected.
