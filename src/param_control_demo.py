# -*- coding: utf-8 -*-
"""
B: 参数可控形变 + 参数空间插值演示 (论文 Application 节)
证明可解释参数 (α 方向 / η 幅度 / κ 曲率) 是"可控的"——刻意改一个参数,
字形按可预期方式变化; 两字在参数空间可平滑插值。黑箱位图表示做不到这点。
纯 jgw_1203 + 已验证 v2 管线; 无外部依赖。
诚实定位: 这是"可控性的可视化说明", 非生成方法贡献; 插值需结构对应(同口径写进 Limitations)。
产出: out_paper/param_control.png (英文,出版级)
"""
import io, sys, json, math
from pathlib import Path
from stroke_param_fit_v2 import parse_strokes, fit_stroke, reconstruct
from stroke_param_fit_min import DATA

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out_paper'; OUT.mkdir(exist_ok=True)
TOL = 0.06
data = json.load(open(DATA, encoding='utf-8'))
by_id = {d['id']: d for d in data}


def stroke_params(stroke_str):
    """-> [[subseg_pr,...]  per stroke];  pr: start/alpha/eta/kappa"""
    return [fit_stroke(P, TOL)[0] for P in parse_strokes(stroke_str)]


def chained_recon(strokes, perturb=None):
    """逐笔画链式重建: 子段 k+1 接在 k 的末端 -> 扰动可沿笔画连贯传播。
    perturb(a,e,k)-> (a,e,k)"""
    out = []
    for subs in strokes:
        if not subs:
            continue
        cur = subs[0]['start']
        pts = []
        for pr in subs:
            a, e, k = pr['alpha'], pr['eta'], pr['kappa']
            if perturb:
                a, e, k = perturb(a, e, k)
            seg = reconstruct(cur, a, e, k)
            pts += seg
            cur = seg[-1]                      # 链式: 下一子段接末端
        out.append(pts)
    return out


def draw(ax, paths, color='#111', lw=2):
    for p in paths:
        ax.plot([x for x, y in p], [y for x, y in p], '-', lw=lw, color=color)
    ax.set_aspect('equal'); ax.invert_yaxis(); ax.axis('off')


# 选样(修正第一版缺陷):
#  - κ 演示必须选"高曲率"字, 否则看不出曲率可控(邦那种近直字无效)
#  - 方向演示选干净中等复杂字
#  - 插值改"自变体"(字→其受控变体), 结构天然一致, 诚实; 跨字 morph 作 Limitations
v2 = json.load(open(HERE/'out_v2'/'params_v2.json', encoding='utf-8'))
by_id_v2 = {r['id']: r for r in v2}


def mean_absk(r):
    ks = [abs(sg['kappa']) for s in r['strokes'] for sg in s]
    return sum(ks)/len(ks) if ks else 0.0


# κ-demo: 高平均曲率 + 误差小(干净) + 复杂度适中
kcand = [r for r in v2 if 5 <= r['n_subseg'] <= 14 and r['recon_err'] < 0.02]
kcand.sort(key=lambda r: -mean_absk(r))
KID = kcand[0]['id']
# α-demo: 干净中等复杂(误差小, 6~12 子段)
acand = sorted([r for r in v2 if 6 <= r['n_subseg'] <= 12],
               key=lambda r: r['recon_err'])
AID = acand[0]['id']
# 插值-demo(自变体): 取一个干净中等字
IID = acand[1]['id']
demo_ids = [KID, AID, IID]

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fp = fm.FontProperties(fname='C:/Windows/Fonts/simhei.ttf')

fig = plt.figure(figsize=(15, 9))
gs = fig.add_gridspec(3, 5, hspace=0.35, wspace=0.1)

# 行1: κ 曲率可控 (×0 直线化 → ×1 原 → ×2 加曲)
kf = [0.0, 0.5, 1.0, 1.5, 2.0]
gid = demo_ids[0]; S = stroke_params(by_id[gid]['stroke'])
for j, f in enumerate(kf):
    ax = fig.add_subplot(gs[0, j])
    draw(ax, chained_recon(S, lambda a, e, k, f=f: (a, e, k*f)))
    ax.set_title(r'$\kappa \times %.1f$' % f, fontproperties=fp, fontsize=11)
fig.add_subplot(gs[0, 0]).axis('off')
fig.text(0.085, 0.78, '(a) Curvature control  字: %s' % by_id[gid]['char'],
         fontproperties=fp, fontsize=12)

# 行2: α 方向可控 (整体旋转 Δα)
da = [-20, -10, 0, 10, 20]
gid = demo_ids[1]; S = stroke_params(by_id[gid]['stroke'])
for j, deg in enumerate(da):
    ax = fig.add_subplot(gs[1, j])
    r = math.radians(deg)
    draw(ax, chained_recon(S, lambda a, e, k, r=r: (a + r, e, k)))
    ax.set_title(r'$\Delta\alpha = %d^\circ$' % deg, fontproperties=fp, fontsize=11)
fig.text(0.085, 0.5, '(b) Direction control  字: %s' % by_id[gid]['char'],
         fontproperties=fp, fontsize=12)

# 行3: 参数空间"自变体"插值 —— 字 → 其受控变体(κ×2 且 Δα+15°)
#   结构天然一致, 诚实演示参数流形可平滑遍历; 跨字 morph 需结构对应(写入 Limitations)
S = stroke_params(by_id[IID]['stroke'])
DKA = math.radians(15.0)
ts = [0.0, 0.25, 0.5, 0.75, 1.0]
for j, t in enumerate(ts):
    ax = fig.add_subplot(gs[2, j])
    # 目标 = (α+15°, η, κ×2);  线性 t 遍历 原→目标
    paths = chained_recon(
        S, lambda a, e, k, t=t: (a + t*DKA, e, k*(1.0 + t*1.0)))
    draw(ax, paths, color='#7A2E88')
    ax.set_title('t = %.2f' % t, fontproperties=fp, fontsize=11)
fig.text(0.085, 0.22,
         '(c) Parameter-space traversal: %s → controlled variant (κ×2, Δα+15°)'
         % by_id[IID]['char'], fontproperties=fp, fontsize=12)

fig.suptitle('Interpretable parametric controllability of the oracle-bone representation',
             fontsize=13)
plt.savefig(OUT/'param_control.png', dpi=200, bbox_inches='tight')
plt.close()
print('=== B: 参数可控形变 + 自变体插值 (修正版) ===')
print('曲率控制 id=%d(%s) 平均|κ|=%.3f  方向控制 id=%d(%s)  插值(自变体) id=%d(%s)'
      % (KID, by_id[KID]['char'], mean_absk(by_id_v2[KID]),
         AID, by_id[AID]['char'], IID, by_id[IID]['char']))
print('图: %s' % (OUT/'param_control.png'))
