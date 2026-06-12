# Figure captions (npj Heritage Science manuscript v0.2)

**Fig. 1. Structural-complexity characterization of the 1,203-glyph oracle-bone parametric corpus.**
(a) Distribution of the number of strokes per glyph. (b) Distribution of the number of
adaptive sub-segments per glyph produced by the method of Section 4 (median 10, mean 10.3).
(c) Distribution of sub-segment arc length η (log y-axis). (d) Distribution of
sub-segment signed-curvature magnitude |κ| (log y-axis); the dashed line marks the
weak-curvature threshold |κ| = 0.02, below which 72.2% of all sub-segments lie.
(e) Distribution of per-glyph normalized reconstruction error (median 0.0026, P90 0.015).
(f) Per-glyph complexity (sub-segments) versus normalized reconstruction error;
the relationship is weakly negative (Spearman ρ = −0.125, n = 1,203, p < 10⁻⁴) because
the adaptive procedure allocates additional sub-segments to harder strokes.

**Fig. 2. Rate–distortion behaviour of the error-driven adaptive arc-segmentation.**
Mean sub-segments per glyph (representation cost) versus mean normalized reconstruction
error (distortion) as the tolerance is swept over {0.20, 0.12, 0.08, 0.06, 0.04, 0.025,
0.015}. The curve exhibits diminishing returns, consistent with the corpus being
dominated by simple low-curvature strokes; the operating point reported in this paper is
tol = 0.06.

**Fig. 3. Adaptive segmentation removes the single-arc over-shoot artefact on hook
strokes.** Eight glyphs that exhibit the largest reconstruction error under a
non-adaptive mean-curvature single-arc fit are shown. Gray: original polyline strokes
from the dataset. Red: piecewise constant-curvature reconstruction produced by the
adaptive procedure (Section 4.2). The spurious circular over-shoot characteristic of a
single-arc fit on hook-bearing strokes is largely eliminated by error-driven splitting,
with a minor residual on the sharpest hooks (acknowledged in Section 7, item 2).

**Fig. 4. Sample of the released SVG glyph set.** Forty glyphs drawn at random from the
1,203 SVG files derived by exporting the parametric reconstruction. Each SVG specifies a
viewBox sized to the glyph's bounding box with proportional stroke width and is fully
resolution-independent. Glyph labels are the corresponding modern Chinese characters.

**Fig. 5. Interpretable parametric controllability of the oracle-bone representation.**
All three panels operate on the **same glyph "安"** (deciphered OBS, 10 sub-segments,
recon. error 0.0037), demonstrating that the three parametric knobs act on one and the
same parameter vector. (a) **Curvature control.** Scaling the per-sub-segment curvature
κ by factors {0, 0.5, 1, 1.5, 2} varies stroke curvature continuously from straight to
strongly curved; at κ × 2 the upper 宀 component closes into a complete loop —
a direct visual illustration of the binary primitive class {straight ∪ circular arcs}
declared in §4.1 and acknowledged as a limitation in §7 item 2. (b) **Direction
control.** Adding a constant Δα ∈ {−20°, −10°, 0°, +10°, +20°} to every sub-segment's
direction rotates strokes coherently. (c) **Within-glyph parameter-space traversal.**
Linearly interpolating the glyph's parameters at t ∈ {0, 0.25, 0.5, 0.75, 1} toward a
controlled variant defined by (κ × 2, Δα = +15°) yields a smooth, structurally-
consistent sequence. The traversal in (c) varies parameters within a single glyph;
arbitrary cross-glyph morphing requires explicit structural correspondence and is not
claimed (Section 7, item 5).
