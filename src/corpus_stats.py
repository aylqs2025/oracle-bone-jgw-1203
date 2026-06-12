# -*- coding: utf-8 -*-
"""
corpus_stats.py —— A: 1203 字结构复杂度语料统计 + D: 出版级规范图
纯用已验证 out_v2/params_v2.json (v2 自适应分段, 权威)；无外部依赖。
产出: out_paper/corpus_stats.txt / corpus_stats.csv / corpus_overview.png(英文标注,300dpi)
供 npj Heritage Science 的 Dataset/Analysis 节直接用。
"""
import io, sys, json, statistics as st
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HERE = Path(__file__).resolve().parent
V2 = HERE / 'out_v2' / 'params_v2.json'
OUT = HERE / 'out_paper'; OUT.mkdir(exist_ok=True)

recs = json.load(open(V2, encoding='utf-8'))
n_glyph = len(recs)

strokes_per = [r['n_strokes'] for r in recs]
subseg_per  = [r['n_subseg'] for r in recs]
err_per     = [r['recon_err'] for r in recs]

etas, absk = [], []
for r in recs:
    for stroke in r['strokes']:
        for sg in stroke:
            etas.append(sg['eta']); absk.append(abs(sg['kappa']))

n_seg = len(etas)
def q(a, p): a=sorted(a); return a[min(len(a)-1, int(p*len(a)))]

# “近直”笔元占比: |kappa| 很小 (经验阈 0.02, 论文里说明为弱曲率)
KSTRAIGHT = 0.02
near_straight = sum(1 for k in absk if k < KSTRAIGHT)

lines = []
def w(s): lines.append(s); print(s)
w('=== 1203 甲骨语料 结构复杂度统计 (v2 自适应分段) ===')
w('字形数 %d  子段总数 %d  平均 %.1f 子段/字' % (n_glyph, n_seg, n_seg/n_glyph))
w('笔画数/字   中位 %d  均值 %.1f  范围 %d–%d'
  % (q(strokes_per,.5), st.mean(strokes_per), min(strokes_per), max(strokes_per)))
w('子段数/字   中位 %d  均值 %.1f  范围 %d–%d'
  % (q(subseg_per,.5), st.mean(subseg_per), min(subseg_per), max(subseg_per)))
w('子段弧长 η  中位 %.1f  P90 %.1f' % (q(etas,.5), q(etas,.9)))
w('子段|曲率κ| 中位 %.4f  P90 %.4f' % (q(absk,.5), q(absk,.9)))
w('弱曲率(|κ|<%.2f)子段占比 %.1f%% —— 量化"甲骨刀刻笔元以低曲率简单弧为主"'
  % (KSTRAIGHT, 100*near_straight/n_seg))
w('归一化重建误差 中位 %.4f  P90 %.4f  P95 %.4f'
  % (q(err_per,.5), q(err_per,.9), q(err_per,.95)))
w('解读(论文用,诚实): 甲骨字形主要由少量低曲率弧元构成; 参数化表示以'
  ' ~%.0f 子段/字、3参/子段 即可高保真(中位误差<%.3f)重建——'
  '紧凑且可解释, 但压缩比仅约×1.5(诚实, 定位为可解释而非极致压缩)。'
  % (n_seg/n_glyph, q(err_per,.5)))

(OUT/'corpus_stats.txt').write_text('\n'.join(lines), encoding='utf-8')
with open(OUT/'corpus_stats.csv','w',encoding='utf-8-sig') as f:
    f.write('id,char,unicode,n_strokes,n_subseg,recon_err\n')
    for r in recs:
        f.write('%d,%s,%s,%d,%d,%.4f\n'
                % (r['id'], r['char'], r.get('unicode') or '',
                   r['n_strokes'], r['n_subseg'], r['recon_err']))

# ---- D: 出版级 6 面板图 (英文标注, 300dpi, 统一风格) ----
try:
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 10, 'axes.grid': True,
                         'grid.alpha': .3, 'figure.dpi': 300})
    fig, ax = plt.subplots(2, 3, figsize=(13, 7.2))
    C = '#2E5A88'
    ax[0,0].hist(strokes_per, bins=range(1, max(strokes_per)+2), color=C)
    ax[0,0].set_title('(a) Strokes per glyph'); ax[0,0].set_xlabel('# strokes'); ax[0,0].set_ylabel('# glyphs')
    ax[0,1].hist(subseg_per, bins=30, color=C)
    ax[0,1].set_title('(b) Adaptive sub-segments per glyph'); ax[0,1].set_xlabel('# sub-segments'); ax[0,1].set_ylabel('# glyphs')
    ax[0,2].hist(etas, bins=40, color=C); ax[0,2].set_yscale('log')
    ax[0,2].set_title('(c) Sub-segment arc length $\\eta$'); ax[0,2].set_xlabel('$\\eta$ (px)'); ax[0,2].set_ylabel('# sub-seg (log)')
    ax[1,0].hist(absk, bins=40, color=C); ax[1,0].set_yscale('log')
    ax[1,0].axvline(KSTRAIGHT, color='crimson', ls='--', lw=1)
    ax[1,0].set_title('(d) Sub-segment curvature $|\\kappa|$'); ax[1,0].set_xlabel('$|\\kappa|$'); ax[1,0].set_ylabel('# sub-seg (log)')
    ax[1,1].hist(err_per, bins=40, color=C)
    ax[1,1].set_title('(e) Normalized reconstruction error'); ax[1,1].set_xlabel('error'); ax[1,1].set_ylabel('# glyphs')
    ax[1,2].scatter(subseg_per, err_per, s=6, alpha=.35, color=C)
    ax[1,2].set_title('(f) Complexity vs. reconstruction error'); ax[1,2].set_xlabel('# sub-segments'); ax[1,2].set_ylabel('error')
    fig.suptitle('Structural-complexity characterization of the 1203-glyph oracle-bone parametric corpus',
                 fontsize=12)
    plt.tight_layout()
    plt.savefig(OUT/'corpus_overview.png', bbox_inches='tight')
    plt.close()
    w('图: %s (英文,300dpi,出版级)' % (OUT/'corpus_overview.png'))
except Exception as e:
    w('(渲染跳过 %s)' % e)
w('统计: %s  CSV: %s' % (OUT/'corpus_stats.txt', OUT/'corpus_stats.csv'))
