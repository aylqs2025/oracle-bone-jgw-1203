# -*- coding: utf-8 -*-
"""
C: SVG 矢量字形导出 —— 把 v2 参数化重建结果导为标准 SVG（分辨率无关的遗产产物）。
纯用已验证 jgw_1203 + v2 管线；无外部依赖。
产出: out_paper/svg/<id>.svg (1203 个) + manifest.csv + 预览图 svg_preview.png
诚实口径: 导出的是"参数化重建"而非原始点(论文一致——SVG 正是为展示参数化表示可直接
变成可用矢量资源); ~少数尖钩残留(已记 Limitations)随之带入, 不藏。
"""
import io, sys, json
from pathlib import Path
# 复用已验证管线; 注意: import 已把 stdout 包成 utf-8, 勿重复包装
from stroke_param_fit_v2 import parse_strokes, fit_stroke, reconstruct
from stroke_param_fit_min import DATA

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out_paper'
SVGDIR = OUT / 'svg'; SVGDIR.mkdir(parents=True, exist_ok=True)
TOL = 0.06                                   # 与论文 v2 报告口径一致

data = json.load(open(DATA, encoding='utf-8'))


def glyph_to_paths(stroke_str):
    """返回 (paths, bbox)；paths=每笔画一条重建折线点序列"""
    polys = parse_strokes(stroke_str)
    paths, pts_all = [], []
    for P in polys:
        subs, _ = fit_stroke(P, TOL)
        rec = []
        for pr in subs:
            rec += reconstruct(pr['start'], pr['alpha'], pr['eta'], pr['kappa'])
        if len(rec) >= 2:
            paths.append(rec); pts_all += rec
    if not pts_all:
        return [], None
    xs = [x for x, y in pts_all]; ys = [y for x, y in pts_all]
    return paths, (min(xs), min(ys), max(xs), max(ys))


def write_svg(path, paths, bbox, pad=4):
    x0, y0, x1, y1 = bbox
    W = (x1 - x0) + 2 * pad
    H = (y1 - y0) + 2 * pad
    sw = max(W, H) * 0.035                     # 笔宽随字号
    def tx(x): return round(x - x0 + pad, 2)
    def ty(y): return round(y - y0 + pad, 2)    # 数据已是屏幕坐标(y 向下), SVG 同向, 不翻
    d = []
    for poly in paths:
        seg = 'M %s %s ' % (tx(poly[0][0]), ty(poly[0][1]))
        seg += ' '.join('L %s %s' % (tx(x), ty(y)) for x, y in poly[1:])
        d.append('<path d="%s" fill="none" stroke="#111" '
                 'stroke-width="%.2f" stroke-linecap="round" '
                 'stroke-linejoin="round"/>' % (seg, sw))
    svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<svg xmlns="http://www.w3.org/2000/svg" '
           'viewBox="0 0 %.2f %.2f">\n%s\n</svg>\n'
           % (W, H, '\n'.join(d)))
    path.write_text(svg, encoding='utf-8')


man = ['id,char,unicode,svg']
ok = skip = 0
for d in data:
    paths, bbox = glyph_to_paths(d['stroke'])
    if not paths:
        skip += 1; continue
    fn = '%04d.svg' % d['id']                  # id 命名最稳(避免PUA/非法字符)
    write_svg(SVGDIR / fn, paths, bbox)
    man.append('%d,%s,%s,%s' % (d['id'], d['char'], d.get('unicode') or '', fn))
    ok += 1
(OUT / 'svg_manifest.csv').write_text('\n'.join(man), encoding='utf-8-sig')

print('=== C: SVG 导出 ===')
print('成功导出 %d 个 SVG → %s' % (ok, SVGDIR))
print('跳过(无可重建笔画) %d' % skip)
print('清单: %s' % (OUT / 'svg_manifest.csv'))
# 抽查一个 SVG 文本是否良构
sample = sorted(SVGDIR.glob('*.svg'))[0]
head = sample.read_text(encoding='utf-8')[:240]
print('样例 %s 头部:\n%s' % (sample.name, head))

# 预览(与 SVG 同几何, 用于肉眼核验—— 遵守"先看图再下结论")
try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    fp = fm.FontProperties(fname='C:/Windows/Fonts/simhei.ttf')
    pick = data[::len(data)//40][:40]
    fig, axes = plt.subplots(5, 8, figsize=(15, 9))
    for ax, d in zip(axes.flat, pick):
        paths, bbox = glyph_to_paths(d['stroke'])
        for poly in paths:
            ax.plot([x for x, y in poly], [y for x, y in poly],
                    '-', lw=2, color='#111')
        ax.set_aspect('equal'); ax.invert_yaxis(); ax.axis('off')
        ax.set_title('%s' % d['char'], fontproperties=fp, fontsize=11)
    fig.suptitle('SVG export preview (parametric reconstruction, sample 40/1203)',
                 fontsize=12)
    plt.tight_layout()
    plt.savefig(OUT / 'svg_preview.png', dpi=130, bbox_inches='tight')
    plt.close()
    print('预览图: %s' % (OUT / 'svg_preview.png'))
except Exception as e:
    print('(预览跳过 %s)' % e)
