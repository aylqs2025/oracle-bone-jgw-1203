# -*- coding: utf-8 -*-
"""
碳基风格化 + 双 SVG 发布
- 三栏对照图: polyline-faithful | parametric default v2 | parametric + max_turn=π/3
- 输出 svg_polyline/ (折线直连, 碳基保真)
- 输出 svg_carving/  (参数化 + 单子段最大转角 π/3, 抑制视觉"大圆")
- 用预定义的高曲率代表字做并置预览
"""
import io, sys, json, math, shutil
from pathlib import Path
from stroke_param_fit_min import parse_strokes, DATA
from stroke_param_fit_v2 import fit_stroke, reconstruct

HERE = Path(__file__).resolve().parent
OUT  = HERE / 'out_paper'
SVG_POLY = OUT / 'svg_polyline'; SVG_POLY.mkdir(exist_ok=True)
SVG_CARV = OUT / 'svg_carving';  SVG_CARV.mkdir(exist_ok=True)
TOL = 0.06
MAX_TURN = math.pi / 3                          # 60° / 子段

data = json.load(open(DATA, encoding='utf-8'))
by_id = {d['id']: d for d in data}


# ----------------------------------------------------------
# 工具
# ----------------------------------------------------------
def write_svg(path, paths, bbox, pad=4, color='#111'):
    x0, y0, x1, y1 = bbox
    W = (x1 - x0) + 2 * pad
    H = (y1 - y0) + 2 * pad
    sw = max(W, H) * 0.035
    def tx(x): return round(x - x0 + pad, 2)
    def ty(y): return round(y - y0 + pad, 2)    # 数据已是屏幕坐标(y 向下), SVG 同向, 不翻
    d = []
    for poly in paths:
        if len(poly) < 2: continue
        seg = 'M %s %s ' % (tx(poly[0][0]), ty(poly[0][1]))
        seg += ' '.join('L %s %s' % (tx(x), ty(y)) for x, y in poly[1:])
        d.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.2f" '
                 'stroke-linecap="round" stroke-linejoin="round"/>'
                 % (seg, color, sw))
    svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.2f %.2f">\n'
           '%s\n</svg>\n' % (W, H, '\n'.join(d)))
    path.write_text(svg, encoding='utf-8')


def bbox_of(paths):
    pts = [pt for p in paths for pt in p]
    if not pts: return None
    xs = [x for x, y in pts]; ys = [y for x, y in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def polyline_paths(stroke_str):
    return parse_strokes(stroke_str)


def parametric_paths(stroke_str, max_turn=None):
    out = []
    for P in parse_strokes(stroke_str):
        subs, _ = fit_stroke(P, TOL, max_turn=max_turn)
        rec = []
        for pr in subs:
            rec += reconstruct(pr['start'], pr['alpha'], pr['eta'], pr['kappa'])
        if len(rec) >= 2: out.append(rec)
    return out


# ----------------------------------------------------------
# 1) 双 SVG 集导出 (1203 字)
# ----------------------------------------------------------
man_poly = ['id,char,unicode,svg']
man_carv = ['id,char,unicode,svg']
nseg_default = nseg_carving = 0; n_with_data = 0
for d in data:
    polys_raw = polyline_paths(d['stroke'])
    if not polys_raw: continue
    bb = bbox_of(polys_raw); fn = '%04d.svg' % d['id']
    write_svg(SVG_POLY / fn, polys_raw, bb, color='#111')
    man_poly.append('%d,%s,%s,%s' % (d['id'], d['char'], d.get('unicode') or '', fn))

    polys_carv = parametric_paths(d['stroke'], max_turn=MAX_TURN)
    if polys_carv:
        bb2 = bbox_of(polys_carv)
        write_svg(SVG_CARV / fn, polys_carv, bb2, color='#111')
        man_carv.append('%d,%s,%s,%s' % (d['id'], d['char'], d.get('unicode') or '', fn))

    # 统计子段数变化
    from stroke_param_fit_v2 import fit_stroke as fs
    for P in parse_strokes(d['stroke']):
        nseg_default += len(fs(P, TOL)[0])
        nseg_carving += len(fs(P, TOL, max_turn=MAX_TURN)[0])
    n_with_data += 1

(OUT / 'svg_polyline_manifest.csv').write_text('\n'.join(man_poly), encoding='utf-8-sig')
(OUT / 'svg_carving_manifest.csv').write_text('\n'.join(man_carv), encoding='utf-8-sig')
print('=== 双 SVG 集 ===')
print('  svg_polyline/  : %d 个 (碳基保真,直连折线)' % len(list(SVG_POLY.glob('*.svg'))))
print('  svg_carving/   : %d 个 (参数化, max_turn=π/3)' % len(list(SVG_CARV.glob('*.svg'))))
print('  默认 v2 子段总数 = %d   /  carving (max_turn=π/3) = %d   (%+d, +%.1f%%)'
      % (nseg_default, nseg_carving, nseg_carving - nseg_default,
         100*(nseg_carving - nseg_default)/nseg_default))


# ----------------------------------------------------------
# 2) 三栏对照图: 取代表性"易显圆"高曲率字
# ----------------------------------------------------------
# 从已 v2 拟合记录中挑高 mean|κ| + 中等复杂度
v2 = json.load(open(HERE/'out_v2'/'params_v2.json', encoding='utf-8'))
def mk(r):
    ks = [abs(sg['kappa']) for s in r['strokes'] for sg in s]
    return sum(ks)/len(ks) if ks else 0
cands = sorted([r for r in v2 if 6 <= r['n_subseg'] <= 16],
               key=lambda r: -mk(r))[:8]
picks_all = [by_id[r['id']] for r in cands]
# 去掉第 4 行和最后一行 (索引 3 和 7), 余 6 字
picks = [d for i, d in enumerate(picks_all) if i not in (3, 7)]

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fp = fm.FontProperties(fname='C:/Windows/Fonts/simhei.ttf')

N = len(picks)
fig, axes = plt.subplots(N, 2, figsize=(7.5, 2.1 * N + 1.6))
cols = ['Polyline-faithful\n(svg_polyline; visual fidelity)',
        'Parametric (default v2)\n(svg_parametric; analytical canonical)']
for i, d in enumerate(picks):
    PA = polyline_paths(d['stroke'])
    PB = parametric_paths(d['stroke'], max_turn=None)
    for j, P in enumerate((PA, PB)):
        ax = axes[i, j]
        for poly in P:
            ax.plot([x for x, y in poly], [y for x, y in poly],
                    '-', lw=2, color='#111')
        ax.set_aspect('equal'); ax.invert_yaxis(); ax.axis('off')
        if i == 0:
            ax.set_title(cols[j], fontsize=13)
    label = d.get('char') or f"id={d['id']}"   # 标签 disputed 时显示 id
    axes[i, 0].set_ylabel(label, rotation=0, labelpad=28,
                          fontproperties=fp, fontsize=18, va='center')
fig.suptitle(
    'Two release flavors on identical high-curvature glyphs.\n'
    'Polyline-faithful (left) preserves visual carving fidelity; '
    'parametric (right) is the analytical canonical form.\n'
    'Visible differences are a design consequence of the primitive class '
    '(§4.1), not a defect.',
    fontsize=12.5, y=0.995)
plt.tight_layout(rect=[0.04, 0, 1, 0.94])
plt.savefig(OUT/'figs_final'/'fig06_styles.png',
            dpi=200, bbox_inches='tight')
plt.close()
print('对照图: %s (%d 字)' % (OUT/'figs_final'/'fig06_styles.png', N))
