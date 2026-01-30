#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SaaS Monthly Bug Analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from collections import Counter
import numpy as np

# Set Chinese font support
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
matplotlib.rcParams['axes.unicode_minus'] = False

# Read data
file_path = '2025/2025研发质量分析/Jira-项目管理 2026-01-30T12_27_55+0800.csv'
df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
bug_df = df[df['问题类型'].isin(['故障', '缺陷', 'Bug', 'bug'])].copy()

# Filter SaaS bugs
customer_col = '自定义字段(客户名称)'
env_col = '自定义字段(缺陷发现环境)'

def is_saas(row):
    env = str(row.get(env_col, '')) if pd.notna(row.get(env_col)) else ''
    customer = str(row.get(customer_col, '')) if pd.notna(row.get(customer_col)) else ''
    if 'SaaS' in env or 'saas' in env.lower():
        return True
    if customer == 'SaaS客户' or customer == 'SaaS':
        return True
    return False

saas_df = bug_df[bug_df.apply(is_saas, axis=1)].copy()
saas_df['创建日期_parsed'] = pd.to_datetime(saas_df['创建日期'], errors='coerce')
saas_df['month'] = saas_df['创建日期_parsed'].dt.month
saas_df['year'] = saas_df['创建日期_parsed'].dt.year

# Filter 2025 data
saas_2025 = saas_df[saas_df['year'] == 2025].copy()

severity_col = '自定义字段(严重程度)'
defect_cols = [c for c in bug_df.columns if '缺陷类型' in c]

output = []
output.append("=" * 100)
output.append("2025年度 SaaS Bug 月度分析报告")
output.append("=" * 100)
output.append(f"\nSaaS Bug总数(2025年): {len(saas_2025)}")

# Monthly data collection
monthly_data = {}
months = range(1, 13)

for m in months:
    month_df = saas_2025[saas_2025['month'] == m]
    
    # Basic counts
    total = len(month_df)
    resolved = len(month_df[month_df['状态'] == '完成'])
    resolution_rate = resolved / total * 100 if total > 0 else 0
    
    # Severity
    p0 = len(month_df[month_df[severity_col].str.contains('P0', na=False)])
    p1 = len(month_df[month_df[severity_col].str.contains('P1', na=False)])
    p2 = len(month_df[month_df[severity_col].str.contains('P2', na=False)])
    p3 = len(month_df[month_df[severity_col].str.contains('P3', na=False)])
    
    # Defect types
    defect_types = Counter()
    for col in defect_cols:
        for v in month_df[col].dropna():
            if v and str(v).strip():
                defect_types[str(v).strip()] += 1
    
    # Status
    status_counts = month_df['状态'].value_counts().to_dict()
    
    monthly_data[m] = {
        'total': total,
        'resolved': resolved,
        'resolution_rate': resolution_rate,
        'p0': p0,
        'p1': p1,
        'p2': p2,
        'p3': p3,
        'defect_types': defect_types,
        'status': status_counts
    }

# Print monthly details
for m in months:
    data = monthly_data[m]
    output.append(f"\n{'='*50}")
    output.append(f"【{m}月】 总数: {data['total']} | 已解决: {data['resolved']} | 解决率: {data['resolution_rate']:.1f}%")
    output.append(f"{'='*50}")
    output.append(f"  严重程度: P0={data['p0']}, P1={data['p1']}, P2={data['p2']}, P3={data['p3']}")
    
    output.append(f"  状态分布:")
    for s, c in data['status'].items():
        output.append(f"    - {s}: {c}")
    
    output.append(f"  缺陷类型Top5:")
    for dt, c in data['defect_types'].most_common(5):
        output.append(f"    - {dt}: {c}")

# Summary table
output.append("\n" + "=" * 100)
output.append("月度汇总表")
output.append("=" * 100)
output.append(f"{'月份':<6} {'总数':<6} {'已解决':<8} {'解决率':<10} {'P0':<4} {'P1':<4} {'P2':<4} {'P3':<4}")
output.append("-" * 60)
for m in months:
    d = monthly_data[m]
    output.append(f"{m}月    {d['total']:<6} {d['resolved']:<8} {d['resolution_rate']:<10.1f}% {d['p0']:<4} {d['p1']:<4} {d['p2']:<4} {d['p3']:<4}")

# Write results
with open('2025/2025研发质量分析/SaaS月度分析结果.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("分析完成，开始生成图表...")

# ========== Create Charts ==========
fig = plt.figure(figsize=(20, 20))

month_names = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
totals = [monthly_data[m]['total'] for m in months]
resolved_list = [monthly_data[m]['resolved'] for m in months]
rates = [monthly_data[m]['resolution_rate'] for m in months]
p0_list = [monthly_data[m]['p0'] for m in months]
p1_list = [monthly_data[m]['p1'] for m in months]
p2_list = [monthly_data[m]['p2'] for m in months]
p3_list = [monthly_data[m]['p3'] for m in months]

# 1. Monthly Bug count trend with resolution rate
ax1 = fig.add_subplot(3, 2, 1)
x = np.arange(len(month_names))
width = 0.35
bars1 = ax1.bar(x - width/2, totals, width, label='总数', color='#3498DB', alpha=0.8)
bars2 = ax1.bar(x + width/2, resolved_list, width, label='已解决', color='#27AE60', alpha=0.8)
ax1.set_title('SaaS月度Bug数量与解决情况', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('月份')
ax1.set_ylabel('Bug数量')
ax1.set_xticks(x)
ax1.set_xticklabels(month_names)
ax1.legend(loc='upper left')

# Add resolution rate line
ax1_twin = ax1.twinx()
ax1_twin.plot(x, rates, 'o-', color='#E74C3C', linewidth=2, markersize=6, label='解决率')
ax1_twin.set_ylabel('解决率 (%)', color='#E74C3C')
ax1_twin.tick_params(axis='y', labelcolor='#E74C3C')
ax1_twin.set_ylim(0, 120)
ax1_twin.legend(loc='upper right')

for i, (t, r) in enumerate(zip(totals, rates)):
    ax1.text(i - width/2, t + 1, str(t), ha='center', va='bottom', fontsize=9, fontweight='bold')

ax1.spines['top'].set_visible(False)

# 2. Severity stacked bar chart
ax2 = fig.add_subplot(3, 2, 2)
bar_width = 0.6
bars_p2 = ax2.bar(x, p2_list, bar_width, label='P2', color='#5DADE2')
bars_p3 = ax2.bar(x, p3_list, bar_width, bottom=p2_list, label='P3', color='#82E0AA')
bars_p1 = ax2.bar(x, p1_list, bar_width, bottom=[p2_list[i]+p3_list[i] for i in range(12)], label='P1', color='#F4D03F')
bars_p0 = ax2.bar(x, p0_list, bar_width, bottom=[p2_list[i]+p3_list[i]+p1_list[i] for i in range(12)], label='P0', color='#E74C3C')
ax2.set_title('SaaS月度Bug严重程度分布', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('月份')
ax2.set_ylabel('Bug数量')
ax2.set_xticks(x)
ax2.set_xticklabels(month_names)
ax2.legend()
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# 3. Monthly defect types heatmap-like chart
ax3 = fig.add_subplot(3, 2, 3)
# Get top defect types across all months
all_defects = Counter()
for m in months:
    all_defects.update(monthly_data[m]['defect_types'])
top_defects = [d[0] for d in all_defects.most_common(8)]

# Create matrix
defect_matrix = []
for dt in top_defects:
    row = [monthly_data[m]['defect_types'].get(dt, 0) for m in months]
    defect_matrix.append(row)

defect_matrix = np.array(defect_matrix)
im = ax3.imshow(defect_matrix, cmap='Blues', aspect='auto')
ax3.set_xticks(np.arange(12))
ax3.set_yticks(np.arange(len(top_defects)))
ax3.set_xticklabels(month_names, fontsize=9)
ax3.set_yticklabels(top_defects, fontsize=9)
ax3.set_title('SaaS月度缺陷类型分布热力图', fontsize=14, fontweight='bold', pad=15)

# Add text annotations
for i in range(len(top_defects)):
    for j in range(12):
        val = defect_matrix[i, j]
        if val > 0:
            text_color = 'white' if val > defect_matrix.max()/2 else 'black'
            ax3.text(j, i, int(val), ha='center', va='center', color=text_color, fontsize=9)

plt.colorbar(im, ax=ax3, label='Bug数量')

# 4. Resolution rate trend
ax4 = fig.add_subplot(3, 2, 4)
ax4.fill_between(x, rates, alpha=0.3, color='#27AE60')
ax4.plot(x, rates, 'o-', color='#27AE60', linewidth=2.5, markersize=8)
ax4.axhline(y=sum(rates)/12, color='red', linestyle='--', alpha=0.7, label=f'年均: {sum(rates)/12:.1f}%')
ax4.set_title('SaaS月度解决率趋势', fontsize=14, fontweight='bold', pad=15)
ax4.set_xlabel('月份')
ax4.set_ylabel('解决率 (%)')
ax4.set_xticks(x)
ax4.set_xticklabels(month_names)
ax4.set_ylim(0, 110)
ax4.legend()
for i, r in enumerate(rates):
    ax4.text(i, r + 3, f'{r:.0f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)

# 5. P1 trend (most important for SaaS)
ax5 = fig.add_subplot(3, 2, 5)
ax5.bar(x, p1_list, color='#F4D03F', edgecolor='white', width=0.6)
ax5.set_title('SaaS月度P1(核心功能问题)数量', fontsize=14, fontweight='bold', pad=15)
ax5.set_xlabel('月份')
ax5.set_ylabel('P1数量')
ax5.set_xticks(x)
ax5.set_xticklabels(month_names)
ax5.axhline(y=sum(p1_list)/12, color='red', linestyle='--', alpha=0.7, label=f'月均: {sum(p1_list)/12:.1f}')
ax5.legend()
for i, p in enumerate(p1_list):
    if p > 0:
        ax5.text(i, p + 0.3, str(p), ha='center', va='bottom', fontsize=10, fontweight='bold')
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)

# 6. Summary metrics table
ax6 = fig.add_subplot(3, 2, 6)
ax6.axis('off')

# Calculate summary metrics
total_bugs = sum(totals)
total_resolved = sum(resolved_list)
avg_rate = sum(rates) / 12
total_p0 = sum(p0_list)
total_p1 = sum(p1_list)
best_month = month_names[rates.index(max(rates))]
worst_month = month_names[rates.index(min(rates))]
max_bugs_month = month_names[totals.index(max(totals))]
min_bugs_month = month_names[totals.index(min(totals))]

summary_text = f"""
┌─────────────────────────────────────────────────────────────┐
│             SaaS 2025年度月度Bug分析汇总                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  【总体数据】                                                 │
│    年度Bug总数:     {total_bugs:>4}个                              │
│    年度已解决:      {total_resolved:>4}个                              │
│    年均解决率:      {avg_rate:>5.1f}%                             │
│                                                             │
│  【严重程度】                                                 │
│    P0(阻塞性):       {total_p0:>3}个                               │
│    P1(核心功能):     {total_p1:>3}个                               │
│                                                             │
│  【月度表现】                                                 │
│    Bug最多月份:     {max_bugs_month}({max(totals)}个)                       │
│    Bug最少月份:     {min_bugs_month}({min(totals)}个)                        │
│    解决率最高:      {best_month}({max(rates):.0f}%)                        │
│    解决率最低:      {worst_month}({min(rates):.0f}%)                        │
│                                                             │
│  【趋势分析】                                                 │
│    上半年Bug数:     {sum(totals[:6]):>4}个                              │
│    下半年Bug数:     {sum(totals[6:]):>4}个                              │
│    下半年改善:      {(sum(totals[:6])-sum(totals[6:]))/sum(totals[:6])*100 if sum(totals[:6]) else 0:>5.1f}%                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
"""
ax6.text(0.5, 0.5, summary_text, transform=ax6.transAxes, fontsize=11,
         verticalalignment='center', horizontalalignment='center',
         family='monospace', bbox=dict(boxstyle='round', facecolor='#F8F9F9', edgecolor='#BDC3C7'))

plt.tight_layout(pad=3.0)
plt.savefig('2025/2025研发质量分析/SaaS月度Bug分析图表.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("图表已保存: SaaS月度Bug分析图表.png")

# Create second figure for detailed monthly breakdown
fig2 = plt.figure(figsize=(20, 12))

# Quarterly comparison
ax21 = fig2.add_subplot(2, 2, 1)
q1 = sum(totals[0:3])
q2 = sum(totals[3:6])
q3 = sum(totals[6:9])
q4 = sum(totals[9:12])
quarters = ['Q1\n(1-3月)', 'Q2\n(4-6月)', 'Q3\n(7-9月)', 'Q4\n(10-12月)']
q_values = [q1, q2, q3, q4]
colors_q = ['#E74C3C', '#F39C12', '#27AE60', '#3498DB']
bars_q = ax21.bar(quarters, q_values, color=colors_q, edgecolor='white', width=0.6)
ax21.set_title('SaaS季度Bug数量对比', fontsize=14, fontweight='bold', pad=15)
ax21.set_ylabel('Bug数量')
for bar, val in zip(bars_q, q_values):
    ax21.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, str(val), 
              ha='center', va='bottom', fontsize=12, fontweight='bold')
    pct = val / sum(q_values) * 100
    ax21.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, f'{pct:.1f}%', 
              ha='center', va='center', fontsize=10, color='white', fontweight='bold')
ax21.spines['top'].set_visible(False)
ax21.spines['right'].set_visible(False)

# Monthly comparison with year average
ax22 = fig2.add_subplot(2, 2, 2)
avg_monthly = sum(totals) / 12
colors_monthly = ['#E74C3C' if t > avg_monthly else '#27AE60' for t in totals]
bars22 = ax22.bar(month_names, totals, color=colors_monthly, edgecolor='white', width=0.7)
ax22.axhline(y=avg_monthly, color='#3498DB', linestyle='--', linewidth=2, label=f'月均: {avg_monthly:.1f}')
ax22.set_title('SaaS各月Bug数量(红色>月均, 绿色≤月均)', fontsize=14, fontweight='bold', pad=15)
ax22.set_ylabel('Bug数量')
ax22.legend()
for bar, val in zip(bars22, totals):
    ax22.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(val), 
              ha='center', va='bottom', fontsize=10, fontweight='bold')
ax22.spines['top'].set_visible(False)
ax22.spines['right'].set_visible(False)

# Top defect types pie chart
ax23 = fig2.add_subplot(2, 2, 3)
top5_defects = all_defects.most_common(6)
defect_labels = [d[0] for d in top5_defects]
defect_values = [d[1] for d in top5_defects]
colors_pie = plt.cm.Set3(np.linspace(0, 1, len(defect_labels)))
wedges, texts, autotexts = ax23.pie(defect_values, labels=defect_labels, autopct='%1.1f%%', 
                                     colors=colors_pie, startangle=90)
ax23.set_title('SaaS年度缺陷类型分布', fontsize=14, fontweight='bold', pad=15)

# Monthly P1 with trend line
ax24 = fig2.add_subplot(2, 2, 4)
ax24.bar(month_names, p1_list, color='#F4D03F', alpha=0.7, edgecolor='white', width=0.6)
z = np.polyfit(x, p1_list, 1)
p = np.poly1d(z)
ax24.plot(x, p(x), 'r--', linewidth=2, label='趋势线')
ax24.set_title('SaaS月度P1问题趋势', fontsize=14, fontweight='bold', pad=15)
ax24.set_ylabel('P1数量')
ax24.legend()
for i, val in enumerate(p1_list):
    if val > 0:
        ax24.text(i, val + 0.2, str(val), ha='center', va='bottom', fontsize=10, fontweight='bold')
ax24.spines['top'].set_visible(False)
ax24.spines['right'].set_visible(False)

plt.tight_layout(pad=3.0)
plt.savefig('2025/2025研发质量分析/SaaS月度Bug分析图表2.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("图表已保存: SaaS月度Bug分析图表2.png")
print("分析完成!")
