#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate stability charts for CTO annual report PPT
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# Set Chinese font support
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'PingFang SC', 'Heiti SC', 'SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

# Monthly bug data
months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
saas_bugs = [162, 73, 101, 71, 59, 65, 60, 61, 41, 50, 58, 59]
private_bugs = [33, 95, 84, 81, 57, 73, 66, 36, 22, 13, 32, 50]

# Calculate statistics
saas_total = sum(saas_bugs)
private_total = sum(private_bugs)
saas_h1 = sum(saas_bugs[:6])
saas_h2 = sum(saas_bugs[6:])
private_h1 = sum(private_bugs[:6])
private_h2 = sum(private_bugs[6:])

print("=" * 50)
print("2025年度稳定性数据统计")
print("=" * 50)
print(f"\n【年度Bug总计】")
print(f"  SaaS: {saas_total}个")
print(f"  私有化: {private_total}个")
print(f"  合计: {saas_total + private_total}个")

print(f"\n【半年对比】")
print(f"  SaaS上半年: {saas_h1}个 → 下半年: {saas_h2}个 (下降{(saas_h1-saas_h2)/saas_h1*100:.1f}%)")
print(f"  私有化上半年: {private_h1}个 → 下半年: {private_h2}个 (下降{(private_h1-private_h2)/private_h1*100:.1f}%)")

print(f"\n【峰值对比】")
print(f"  SaaS: 1月峰值{saas_bugs[0]}个 → 12月{saas_bugs[-1]}个 (下降{(saas_bugs[0]-saas_bugs[-1])/saas_bugs[0]*100:.1f}%)")
print(f"  私有化: Q1均值{sum(private_bugs[:3])/3:.0f}个 → Q4均值{sum(private_bugs[9:])/3:.0f}个")

# ============================================================
# Chart 1: Monthly trend line chart
# ============================================================
fig1, ax1 = plt.subplots(figsize=(12, 6))

x = np.arange(len(months))
width = 0.35

# Line chart with markers
line1 = ax1.plot(x, saas_bugs, 'o-', color='#2196F3', linewidth=2.5, markersize=8, label='SaaS')
line2 = ax1.plot(x, private_bugs, 's-', color='#4CAF50', linewidth=2.5, markersize=8, label='私有化')

# Add data labels
for i, (s, p) in enumerate(zip(saas_bugs, private_bugs)):
    ax1.annotate(str(s), (i, s), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9, color='#1565C0')
    ax1.annotate(str(p), (i, p), textcoords="offset points", xytext=(0,-15), ha='center', fontsize=9, color='#2E7D32')

# Add trend line (moving average)
saas_ma = np.convolve(saas_bugs, np.ones(3)/3, mode='valid')
private_ma = np.convolve(private_bugs, np.ones(3)/3, mode='valid')
ax1.plot(x[1:-1], saas_ma, '--', color='#2196F3', alpha=0.5, linewidth=1.5)
ax1.plot(x[1:-1], private_ma, '--', color='#4CAF50', alpha=0.5, linewidth=1.5)

ax1.set_xlabel('月份', fontsize=12)
ax1.set_ylabel('Bug数量', fontsize=12)
ax1.set_title('2025年度Bug月度趋势 - 稳定性持续提升', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(months)
ax1.legend(loc='upper right', fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 180)

# Add annotation for key improvement
ax1.annotate('SaaS下降63.6%', xy=(11, 59), xytext=(9, 100),
            arrowprops=dict(arrowstyle='->', color='#1565C0'),
            fontsize=10, color='#1565C0', fontweight='bold')

plt.tight_layout()
plt.savefig('稳定性趋势图_月度.png', dpi=150, bbox_inches='tight', facecolor='white')
print("\n✓ 已生成: 稳定性趋势图_月度.png")

# ============================================================
# Chart 2: Half-year comparison bar chart
# ============================================================
fig2, ax2 = plt.subplots(figsize=(10, 6))

categories = ['SaaS', '私有化']
h1_data = [saas_h1, private_h1]
h2_data = [saas_h2, private_h2]

x = np.arange(len(categories))
width = 0.35

bars1 = ax2.bar(x - width/2, h1_data, width, label='上半年', color='#FF7043', edgecolor='white')
bars2 = ax2.bar(x + width/2, h2_data, width, label='下半年', color='#26A69A', edgecolor='white')

# Add data labels and percentage
for bar, val in zip(bars1, h1_data):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, str(val), 
             ha='center', va='bottom', fontsize=14, fontweight='bold')
for i, (bar, val) in enumerate(zip(bars2, h2_data)):
    decrease = (h1_data[i] - val) / h1_data[i] * 100
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, str(val), 
             ha='center', va='bottom', fontsize=14, fontweight='bold')
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, f'↓{decrease:.0f}%', 
             ha='center', va='center', fontsize=12, color='white', fontweight='bold')

ax2.set_ylabel('Bug数量', fontsize=12)
ax2.set_title('2025年度Bug半年对比 - 质量显著提升', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(categories, fontsize=14)
ax2.legend(loc='upper right', fontsize=11)
ax2.set_ylim(0, 600)

plt.tight_layout()
plt.savefig('稳定性趋势图_半年对比.png', dpi=150, bbox_inches='tight', facecolor='white')
print("✓ 已生成: 稳定性趋势图_半年对比.png")

# ============================================================
# Chart 3: Defect type pie charts
# ============================================================
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(14, 6))

# SaaS defect types
saas_types = ['代码问题', '非问题', '需求上线引入', '修改缺陷引入', '历史数据问题']
saas_values = [384, 62, 41, 18, 17]
colors_saas = ['#EF5350', '#42A5F5', '#66BB6A', '#FFA726', '#AB47BC']

wedges1, texts1, autotexts1 = ax3a.pie(saas_values, labels=saas_types, autopct='%1.1f%%',
                                        colors=colors_saas, startangle=90, 
                                        explode=(0.05, 0, 0, 0, 0))
ax3a.set_title('SaaS缺陷类型分布', fontsize=13, fontweight='bold')

# Private deployment defect types
private_types = ['代码问题', '非问题', '性能问题', '客户操作问题', '配置问题']
private_values = [159, 87, 64, 59, 46]
colors_private = ['#EF5350', '#42A5F5', '#66BB6A', '#FFA726', '#AB47BC']

wedges2, texts2, autotexts2 = ax3b.pie(private_values, labels=private_types, autopct='%1.1f%%',
                                        colors=colors_private, startangle=90,
                                        explode=(0.05, 0, 0, 0, 0))
ax3b.set_title('私有化缺陷类型分布', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('稳定性趋势图_缺陷类型.png', dpi=150, bbox_inches='tight', facecolor='white')
print("✓ 已生成: 稳定性趋势图_缺陷类型.png")

# ============================================================
# Chart 4: Key metrics dashboard (for PPT highlight)
# ============================================================
fig4, ax4 = plt.subplots(figsize=(12, 4))
ax4.axis('off')

# Create a metrics summary table style
metrics = [
    ['指标', '数值', '说明'],
    ['SaaS年度Bug下降', '63.6%', '1月162个 → 12月59个'],
    ['私有化下半年改善', '47.3%', '上半年423个 → 下半年219个'],
    ['SaaS接口稳定性', '99.99%', '全年服务可用性'],
    ['导入导出稳定性', '99.1% → 99.9%', '突破原定目标'],
]

table = ax4.table(cellText=metrics[1:], colLabels=metrics[0], 
                  loc='center', cellLoc='center',
                  colColours=['#1976D2']*3,
                  colWidths=[0.3, 0.2, 0.4])

table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 2)

# Style header
for i in range(3):
    table[(0, i)].set_text_props(color='white', fontweight='bold')

ax4.set_title('2025年度稳定性核心指标', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('稳定性趋势图_核心指标.png', dpi=150, bbox_inches='tight', facecolor='white')
print("✓ 已生成: 稳定性趋势图_核心指标.png")

plt.close('all')
print("\n" + "=" * 50)
print("图表生成完成！")
print("=" * 50)
