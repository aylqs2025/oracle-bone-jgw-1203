# -*- coding: utf-8 -*-
"""
stroke_param_fit_min.py  —— 甲骨文笔段参数化拟合（最小可跑版 / 描述性闭式估计）

输入 : ../txt/jgw_1203_labeled.json   (1203 个带标签甲骨矢量字形)
做什么:
  1. 解析每个字形的笔段折线（格式: 点数,-64,0,x,y,...,-64,...,-64,-64）
  2. 对每条笔段闭式估计三个可从二维骨架辨识的参数:
        α  笔段方向角 (start->end 弦方向, rad)
        η  幅度/尺度 (弧长, 像素)
        κ  局部曲率 (内点 Menger 曲率均值, 带符号)
     注: θ(刃角)/d(入刀深度) 不在此处——二维骨架不可辨识, 后续作可控风格隐变量
  3. 用 (起点, α, η, κ) 以"恒曲率圆弧"重建笔段
  4. 量化 重建 vs 原始 的归一化误差 (这是评估 3 参表达力的诚实基线数字)
  5. 导出参数 JSON + 抽样对照图供肉眼核验

这是整条 PR 技术链的第一块地基, 不依赖任何待定项。
"""
import os, io, sys, json, math
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HERE = Path(__file__).resolve().parent
# release-layout aware data path: ../data/ or fallback ../txt/
DATA = (HERE.parent / 'data' / 'jgw_1203_labeled.json')
if not DATA.exists():
    DATA = HERE.parent / 'txt' / 'jgw_1203_labeled.json'
OUT  = HERE / 'out_min'
OUT.mkdir(exist_ok=True)

EPS = 1e-9


# ----------------------------------------------------------------------
# 1. 解析
# ----------------------------------------------------------------------
def parse_strokes(stroke_str):
    """'点数,-64,0,x,y,...,-64,...' -> [[(x,y),...], ...]  (按 -64 切笔段, 去段首标志 0)"""
    nums = [int(t) for t in stroke_str.split(',') if t.strip() not in ('', '-')]
    body = nums[1:]                       # 去掉首位“点数”
    segs, cur = [], []
    for v in body:
        if v == -64:
            if cur:
                segs.append(cur); cur = []
        else:
            cur.append(v)
    if cur:
        segs.append(cur)
    polylines = []
    for seg in segs:
        if seg and seg[0] == 0:           # 段首标志位 0
            seg = seg[1:]
        pts = [(seg[i], seg[i + 1]) for i in range(0, len(seg) - 1, 2)]
        if len(pts) >= 2:
            polylines.append(pts)
    return polylines


# ----------------------------------------------------------------------
# 2. 闭式参数估计
# ----------------------------------------------------------------------
def _dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _menger(A, B, C):
    """三点外接圆曲率 (带符号): 4*signed_area / (|AB||BC||CA|)"""
    ab, bc, ca = _dist(A, B), _dist(B, C), _dist(C, A)
    if ab < EPS or bc < EPS or ca < EPS:
        return 0.0
    cross = (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])
    return 2.0 * cross / (ab * bc * ca)   # = 4 * (cross/2) / (ab*bc*ca)


def fit_segment(P):
    """返回 dict(alpha, eta, kappa, chord, n)"""
    S, E = P[0], P[-1]
    alpha = math.atan2(E[1] - S[1], E[0] - S[0])           # 弦方向
    arclen = sum(_dist(P[i], P[i + 1]) for i in range(len(P) - 1))
    chord = _dist(S, E)
    if len(P) >= 3:
        ks = [_menger(P[i - 1], P[i], P[i + 1]) for i in range(1, len(P) - 1)]
        kappa = sum(ks) / len(ks)                           # 带符号均值
    else:
        kappa = 0.0
    return {'alpha': alpha, 'eta': arclen, 'kappa': kappa,
            'chord': chord, 'n': len(P), 'start': S}


# ----------------------------------------------------------------------
# 3. 由 (start, alpha, eta, kappa) 恒曲率重建
# ----------------------------------------------------------------------
def reconstruct(start, alpha, eta, kappa, m=24):
    """恒曲率圆弧; 令重建弧的弦方向≈alpha (θ0 = alpha - kappa*eta/2)"""
    Sx, Sy = start
    if abs(kappa) < 1e-4 or eta < EPS:                      # 近直线
        return [(Sx + (eta * i / m) * math.cos(alpha),
                 Sy + (eta * i / m) * math.sin(alpha)) for i in range(m + 1)]
    th0 = alpha - kappa * eta / 2.0
    pts = []
    for i in range(m + 1):
        s = eta * i / m
        h = th0 + kappa * s
        x = Sx + (math.sin(h) - math.sin(th0)) / kappa
        y = Sy + (-math.cos(h) + math.cos(th0)) / kappa
        pts.append((x, y))
    return pts


# ----------------------------------------------------------------------
# 4. 误差: 原始点到重建折线的平均最近距离 / 字形对角线
# ----------------------------------------------------------------------
def _pt_to_polyline(p, poly):
    best = float('inf')
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        vx, vy = b[0] - a[0], b[1] - a[1]
        L2 = vx * vx + vy * vy
        if L2 < EPS:
            d = _dist(p, a)
        else:
            t = max(0.0, min(1.0, ((p[0]-a[0])*vx + (p[1]-a[1])*vy) / L2))
            d = _dist(p, (a[0]+t*vx, a[1]+t*vy))
        best = min(best, d)
    return best


def glyph_error(polylines, params_list):
    allpts = [pt for P in polylines for pt in P]
    xs = [x for x, y in allpts]; ys = [y for x, y in allpts]
    diag = math.hypot(max(xs)-min(xs), max(ys)-min(ys)) or 1.0
    tot_w = err = 0.0
    for P, pr in zip(polylines, params_list):
        rec = reconstruct(pr['start'], pr['alpha'], pr['eta'], pr['kappa'])
        e = sum(_pt_to_polyline(p, rec) for p in P) / len(P)
        w = pr['eta'] or 1.0                   # 按笔段长度加权
        err += e * w; tot_w += w
    return (err / tot_w) / diag if tot_w else 0.0


# ----------------------------------------------------------------------
# 5. 主流程
# ----------------------------------------------------------------------
def main():
    data = json.load(open(DATA, encoding='utf-8'))
    out_records, errors = [], []
    for d in data:
        polys = parse_strokes(d['stroke'])
        if not polys:
            continue
        ps = [fit_segment(P) for P in polys]
        ge = glyph_error(polys, ps)
        errors.append(ge)
        out_records.append({
            'id': d['id'], 'char': d['char'], 'unicode': d.get('unicode'),
            'n_strokes': len(ps),
            'segments': [{'alpha': round(p['alpha'], 4),
                          'eta': round(p['eta'], 3),
                          'kappa': round(p['kappa'], 5),
                          'n': p['n']} for p in ps],
            'recon_err': round(ge, 4),
        })
    json.dump(out_records, open(OUT / 'params_min.json', 'w', encoding='utf-8'),
              ensure_ascii=False)

    errors.sort()
    n = len(errors)
    def pct(q): return errors[min(n - 1, int(q * n))]
    print('=== 最小版拟合体检（1203 甲骨）===')
    print('成功拟合字形: %d' % n)
    seg_total = sum(r['n_strokes'] for r in out_records)
    print('笔段总数: %d  平均每字 %.1f 段' % (seg_total, seg_total / n))
    print('归一化重建误差(原始点->3参圆弧重建): '
          '中位=%.3f  P25=%.3f  P75=%.3f  P90=%.3f'
          % (pct(.5), pct(.25), pct(.75), pct(.90)))
    print('解读: 这是"恒曲率3参理想化"的诚实表达力下限;'
          ' 误差越大说明真实笔段越需后续 分层/优化/隐变量 来补——'
          '此数字即论文 baseline 锚点。')

    # 抽样对照图（误差由小到大取 12 个，覆盖好/中/差）
    try:
        import matplotlib; matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib import font_manager as fm
        fp = fm.FontProperties(fname='C:/Windows/Fonts/simhei.ttf')
        idx = sorted(range(len(out_records)), key=lambda i: out_records[i]['recon_err'])
        pick = [idx[int(k*(len(idx)-1)/11)] for k in range(12)]
        fig, axes = plt.subplots(3, 4, figsize=(13, 10))
        for ax, gi in zip(axes.flat, pick):
            rec = out_records[gi]
            polys = parse_strokes(data[gi]['stroke'])
            ps = [fit_segment(P) for P in polys]
            for P in polys:
                ax.plot([x for x, y in P], [y for x, y in P],
                        '-', lw=3, color='0.7')
            for p in ps:
                R = reconstruct(p['start'], p['alpha'], p['eta'], p['kappa'])
                ax.plot([x for x, y in R], [y for x, y in R],
                        '-', lw=1.6, color='crimson')
            ax.set_aspect('equal'); ax.invert_yaxis(); ax.axis('off')
            ax.set_title('#%d %s  err=%.3f'
                         % (rec['id'], rec['char'], rec['recon_err']),
                         fontproperties=fp, fontsize=11)
        fig.suptitle('灰=原始笔段  红=(α,η,κ)恒曲率重建  (左上误差小→右下误差大)',
                     fontproperties=fp, fontsize=13)
        plt.tight_layout()
        plt.savefig(OUT / 'recon_sample.png', dpi=100, bbox_inches='tight')
        plt.close()
        print('对照图: %s' % (OUT / 'recon_sample.png'))
    except Exception as e:
        print('(渲染跳过: %s)' % e)

    print('参数导出: %s' % (OUT / 'params_min.json'))


if __name__ == '__main__':
    main()
