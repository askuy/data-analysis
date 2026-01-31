#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SaaS vs Private Deployment Bug Analysis
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

# Classify SaaS vs Private based on environment and customer
env_col = '自定义字段(缺陷发现环境)'
customer_col = '自定义字段(客户名称)'

def classify_deployment(row):
    env = str(row.get(env_col, '')) if pd.notna(row.get(env_col)) else ''
    customer = str(row.get(customer_col, '')) if pd.notna(row.get(customer_col)) else ''
    
    # Check environment first
    if 'SaaS' in env or 'saas' in env.lower():
        return 'SaaS'
    if '私有化' in env:
        return '私有化'
    
    # Check customer name
    if customer == 'SaaS客户' or 'SaaS' in customer:
        return 'SaaS'
    
    # SDK customers are typically private deployment
    if 'SDK' in customer or 'sdk' in customer.lower():
        return '私有化'
    
    # Known private customers
    private_keywords = ['福田', '南方电网', 'OPPO', '广东电信', '唯品会', '好未来', '招商', 
                       '新华三', '跨越', 'TCL', '百度', '小红书', '格力', '猿辅导', 
                       '360', '玉溪', '东风', '融云', '滴滴', '作业帮']
    for kw in private_keywords:
        if kw in customer:
            return '私有化'
    
    # Default based on environment content
    if customer and customer.strip():
        return '私有化'
    
    return '未分类'

bug_df['部署类型'] = bug_df.apply(classify_deployment, axis=1)

# Separate dataframes
saas_df = bug_df[bug_df['部署类型'] == 'SaaS']
private_df = bug_df[bug_df['部署类型'] == '私有化']
unclassified_df = bug_df[bug_df['部署类型'] == '未分类']

severity_col = '自定义字段(严重程度)'
defect_cols = [c for c in bug_df.columns if '缺陷类型' in c]

# Output analysis results
output = []
output.append("=" * 80)
output.append("2025年度Bug分析报告 - SaaS vs 私有化对比")
output.append("=" * 80)

output.append(f"\n【数据分类概况】")
output.append(f"  SaaS Bug数量: {len(saas_df)}")
output.append(f"  私有化 Bug数量: {len(private_df)}")
output.append(f"  未分类 Bug数量: {len(unclassified_df)}")
output.append(f"  总计: {len(bug_df)}")

# ========== SaaS Analysis ==========
output.append("\n" + "=" * 80)
output.append("一、SaaS Bug分析")
output.append("=" * 80)

output.append(f"\n【SaaS Bug总数】: {len(saas_df)}")

output.append("\n【状态分布】")
for s, c in saas_df['状态'].value_counts().items():
    output.append(f"  {s}: {c}")

output.append("\n【严重程度分布】")
for s, c in saas_df[severity_col].value_counts().items():
    if pd.notna(s): output.append(f"  {s}: {c}")

output.append("\n【缺陷类型分布】")
saas_defects = Counter()
for col in defect_cols:
    for v in saas_df[col].dropna():
        if v and str(v).strip(): saas_defects[str(v).strip()] += 1
for dt, c in saas_defects.most_common(10):
    output.append(f"  {dt}: {c}")

# SaaS monthly trend
saas_df['创建日期_parsed'] = pd.to_datetime(saas_df['创建日期'], errors='coerce')
saas_2025 = saas_df[saas_df['创建日期_parsed'].dt.year == 2025]
output.append("\n【月度趋势(2025年)】")
saas_monthly = saas_2025.groupby(saas_2025['创建日期_parsed'].dt.month).size()
for m in range(1, 13):
    output.append(f"  {m}月: {saas_monthly.get(m, 0)}")

# SaaS P0/P1
saas_p0 = saas_df[saas_df[severity_col].str.contains('P0', na=False)]
saas_p1 = saas_df[saas_df[severity_col].str.contains('P1', na=False)]
saas_resolved = len(saas_df[saas_df['状态'] == '完成'])
saas_p0_resolved = len(saas_p0[saas_p0['状态'] == '完成'])
saas_p1_resolved = len(saas_p1[saas_p1['状态'] == '完成'])

output.append(f"\n【SaaS关键指标】")
output.append(f"  总数: {len(saas_df)}, 已解决: {saas_resolved}, 解决率: {saas_resolved/len(saas_df)*100:.1f}%")
output.append(f"  P0: {len(saas_p0)}, 已解决: {saas_p0_resolved}, 解决率: {saas_p0_resolved/len(saas_p0)*100 if len(saas_p0) else 0:.1f}%")
output.append(f"  P1: {len(saas_p1)}, 已解决: {saas_p1_resolved}, 解决率: {saas_p1_resolved/len(saas_p1)*100 if len(saas_p1) else 0:.1f}%")

# ========== Private Analysis ==========
output.append("\n" + "=" * 80)
output.append("二、私有化 Bug分析")
output.append("=" * 80)

output.append(f"\n【私有化 Bug总数】: {len(private_df)}")

output.append("\n【状态分布】")
for s, c in private_df['状态'].value_counts().items():
    output.append(f"  {s}: {c}")

output.append("\n【严重程度分布】")
for s, c in private_df[severity_col].value_counts().items():
    if pd.notna(s): output.append(f"  {s}: {c}")

output.append("\n【缺陷类型分布】")
private_defects = Counter()
for col in defect_cols:
    for v in private_df[col].dropna():
        if v and str(v).strip(): private_defects[str(v).strip()] += 1
for dt, c in private_defects.most_common(10):
    output.append(f"  {dt}: {c}")

# Private monthly trend
private_df['创建日期_parsed'] = pd.to_datetime(private_df['创建日期'], errors='coerce')
private_2025 = private_df[private_df['创建日期_parsed'].dt.year == 2025]
output.append("\n【月度趋势(2025年)】")
private_monthly = private_2025.groupby(private_2025['创建日期_parsed'].dt.month).size()
for m in range(1, 13):
    output.append(f"  {m}月: {private_monthly.get(m, 0)}")

# Private customers breakdown
output.append("\n【私有化客户Bug分布Top15】")
for cu, c in private_df[customer_col].value_counts().head(15).items():
    if pd.notna(cu) and str(cu).strip(): output.append(f"  {cu}: {c}")

# Private P0/P1
private_p0 = private_df[private_df[severity_col].str.contains('P0', na=False)]
private_p1 = private_df[private_df[severity_col].str.contains('P1', na=False)]
private_resolved = len(private_df[private_df['状态'] == '完成'])
private_p0_resolved = len(private_p0[private_p0['状态'] == '完成'])
private_p1_resolved = len(private_p1[private_p1['状态'] == '完成'])

output.append(f"\n【私有化关键指标】")
output.append(f"  总数: {len(private_df)}, 已解决: {private_resolved}, 解决率: {private_resolved/len(private_df)*100:.1f}%")
output.append(f"  P0: {len(private_p0)}, 已解决: {private_p0_resolved}, 解决率: {private_p0_resolved/len(private_p0)*100 if len(private_p0) else 0:.1f}%")
output.append(f"  P1: {len(private_p1)}, 已解决: {private_p1_resolved}, 解决率: {private_p1_resolved/len(private_p1)*100 if len(private_p1) else 0:.1f}%")

# P0 customers for private
output.append("\n【私有化P0问题客户分布】")
for cu, c in private_p0[customer_col].value_counts().items():
    if pd.notna(cu) and str(cu).strip(): output.append(f"  {cu}: {c}")

# ========== Comparison ==========
output.append("\n" + "=" * 80)
output.append("三、SaaS vs 私有化 对比汇总")
output.append("=" * 80)

output.append("\n【Bug数量对比】")
output.append(f"  SaaS: {len(saas_df)} ({len(saas_df)/len(bug_df)*100:.1f}%)")
output.append(f"  私有化: {len(private_df)} ({len(private_df)/len(bug_df)*100:.1f}%)")

output.append("\n【解决率对比】")
output.append(f"  SaaS: {saas_resolved/len(saas_df)*100:.1f}%")
output.append(f"  私有化: {private_resolved/len(private_df)*100:.1f}%")

output.append("\n【P0解决率对比】")
output.append(f"  SaaS P0: {len(saas_p0)}个, 解决率 {saas_p0_resolved/len(saas_p0)*100 if len(saas_p0) else 0:.1f}%")
output.append(f"  私有化 P0: {len(private_p0)}个, 解决率 {private_p0_resolved/len(private_p0)*100 if len(private_p0) else 0:.1f}%")

output.append("\n【P1解决率对比】")
output.append(f"  SaaS P1: {len(saas_p1)}个, 解决率 {saas_p1_resolved/len(saas_p1)*100 if len(saas_p1) else 0:.1f}%")
output.append(f"  私有化 P1: {len(private_p1)}个, 解决率 {private_p1_resolved/len(private_p1)*100 if len(private_p1) else 0:.1f}%")

# Write results
with open('2025/2025研发质量分析/SaaS私有化对比分析结果.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("分析完成，结果已保存")

# ========== Create Charts ==========
print("正在生成图表...")

# Figure 1: Main comparison charts
fig1 = plt.figure(figsize=(20, 16))

# 1.1 Bug count comparison (pie)
ax1 = fig1.add_subplot(2, 3, 1)
sizes = [len(saas_df), len(private_df), len(unclassified_df)]
labels = [f'SaaS\n{len(saas_df)}个', f'私有化\n{len(private_df)}个', f'未分类\n{len(unclassified_df)}个']
colors = ['#3498DB', '#E74C3C', '#95A5A6']
if sizes[2] == 0:
    sizes = sizes[:2]
    labels = labels[:2]
    colors = colors[:2]
wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, 
                                    explode=[0.02]*len(sizes), shadow=True)
ax1.set_title('Bug数量分布: SaaS vs 私有化', fontsize=14, fontweight='bold', pad=15)

# 1.2 Resolution rate comparison
ax2 = fig1.add_subplot(2, 3, 2)
categories = ['SaaS', '私有化']
totals = [len(saas_df), len(private_df)]
resolved_counts = [saas_resolved, private_resolved]
x = np.arange(len(categories))
width = 0.35
bars_total = ax2.bar(x - width/2, totals, width, label='总数', color='#85C1E9')
bars_resolved = ax2.bar(x + width/2, resolved_counts, width, label='已解决', color='#27AE60')
ax2.set_title('Bug解决情况对比', fontsize=14, fontweight='bold', pad=15)
ax2.set_ylabel('数量')
ax2.set_xticks(x)
ax2.set_xticklabels(categories, fontsize=12)
ax2.legend()
for i, (t, r) in enumerate(zip(totals, resolved_counts)):
    rate = r/t*100 if t else 0
    ax2.text(i, max(t, r) + 20, f'{rate:.1f}%', ha='center', fontsize=12, fontweight='bold', color='#E74C3C')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# 1.3 P0/P1 comparison
ax3 = fig1.add_subplot(2, 3, 3)
p_categories = ['SaaS P0', 'SaaS P1', '私有化 P0', '私有化 P1']
p_totals = [len(saas_p0), len(saas_p1), len(private_p0), len(private_p1)]
p_resolved = [saas_p0_resolved, saas_p1_resolved, private_p0_resolved, private_p1_resolved]
x3 = np.arange(len(p_categories))
bars_p_total = ax3.bar(x3 - width/2, p_totals, width, label='总数', color='#F5B7B1')
bars_p_resolved = ax3.bar(x3 + width/2, p_resolved, width, label='已解决', color='#82E0AA')
ax3.set_title('P0/P1问题对比', fontsize=14, fontweight='bold', pad=15)
ax3.set_ylabel('数量')
ax3.set_xticks(x3)
ax3.set_xticklabels(p_categories, fontsize=10)
ax3.legend()
for i, (t, r) in enumerate(zip(p_totals, p_resolved)):
    rate = r/t*100 if t else 0
    ax3.text(i, max(t, r) + 2, f'{rate:.0f}%', ha='center', fontsize=10, fontweight='bold', color='#E74C3C')
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# 1.4 Monthly trend comparison
ax4 = fig1.add_subplot(2, 3, 4)
months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
saas_monthly_vals = [saas_monthly.get(i, 0) for i in range(1, 13)]
private_monthly_vals = [private_monthly.get(i, 0) for i in range(1, 13)]
x4 = np.arange(len(months))
ax4.plot(x4, saas_monthly_vals, 'o-', color='#3498DB', linewidth=2, markersize=8, label='SaaS')
ax4.plot(x4, private_monthly_vals, 's-', color='#E74C3C', linewidth=2, markersize=8, label='私有化')
ax4.set_title('月度Bug趋势对比', fontsize=14, fontweight='bold', pad=15)
ax4.set_xlabel('月份')
ax4.set_ylabel('Bug数量')
ax4.set_xticks(x4)
ax4.set_xticklabels(months, fontsize=9)
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.spines['top'].set_visible(False)
ax4.spines['right'].set_visible(False)

# 1.5 SaaS severity distribution
ax5 = fig1.add_subplot(2, 3, 5)
saas_severity = saas_df[severity_col].value_counts()
sev_labels = ['P2', 'P3', 'P1', 'P0']
sev_values = [saas_severity.get('P2（非核心功能问题）', 0),
              saas_severity.get('P3（不影响客户功能使用问题）', 0),
              saas_severity.get('P1（核心功能问题）', 0),
              saas_severity.get('P0（阻塞性问题）', 0)]
colors_sev = ['#5DADE2', '#82E0AA', '#F4D03F', '#E74C3C']
bars5 = ax5.bar(sev_labels, sev_values, color=colors_sev, edgecolor='white')
ax5.set_title('SaaS Bug严重程度分布', fontsize=14, fontweight='bold', pad=15)
ax5.set_ylabel('数量')
for bar, val in zip(bars5, sev_values):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, str(val), 
             ha='center', va='bottom', fontsize=11, fontweight='bold')
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)

# 1.6 Private severity distribution
ax6 = fig1.add_subplot(2, 3, 6)
private_severity = private_df[severity_col].value_counts()
priv_sev_values = [private_severity.get('P2（非核心功能问题）', 0),
                   private_severity.get('P3（不影响客户功能使用问题）', 0),
                   private_severity.get('P1（核心功能问题）', 0),
                   private_severity.get('P0（阻塞性问题）', 0)]
bars6 = ax6.bar(sev_labels, priv_sev_values, color=colors_sev, edgecolor='white')
ax6.set_title('私有化 Bug严重程度分布', fontsize=14, fontweight='bold', pad=15)
ax6.set_ylabel('数量')
for bar, val in zip(bars6, priv_sev_values):
    ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val), 
             ha='center', va='bottom', fontsize=11, fontweight='bold')
ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)

plt.tight_layout(pad=3.0)
plt.savefig('2025/2025研发质量分析/SaaS私有化对比图表1.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

# Figure 2: Detailed analysis
fig2 = plt.figure(figsize=(20, 12))

# 2.1 SaaS defect types
ax21 = fig2.add_subplot(2, 3, 1)
saas_defect_items = saas_defects.most_common(8)
saas_dt_names = [d[0] for d in saas_defect_items][::-1]
saas_dt_values = [d[1] for d in saas_defect_items][::-1]
colors_dt = plt.cm.Blues(np.linspace(0.3, 0.9, len(saas_dt_names)))
bars21 = ax21.barh(saas_dt_names, saas_dt_values, color=colors_dt, height=0.7)
ax21.set_title('SaaS缺陷类型Top8', fontsize=14, fontweight='bold', pad=15)
ax21.set_xlabel('数量')
for bar, val in zip(bars21, saas_dt_values):
    ax21.text(val + 2, bar.get_y() + bar.get_height()/2, str(val), 
              ha='left', va='center', fontsize=10, fontweight='bold')
ax21.spines['top'].set_visible(False)
ax21.spines['right'].set_visible(False)

# 2.2 Private defect types
ax22 = fig2.add_subplot(2, 3, 2)
private_defect_items = private_defects.most_common(8)
priv_dt_names = [d[0] for d in private_defect_items][::-1]
priv_dt_values = [d[1] for d in private_defect_items][::-1]
colors_dt2 = plt.cm.Oranges(np.linspace(0.3, 0.9, len(priv_dt_names)))
bars22 = ax22.barh(priv_dt_names, priv_dt_values, color=colors_dt2, height=0.7)
ax22.set_title('私有化缺陷类型Top8', fontsize=14, fontweight='bold', pad=15)
ax22.set_xlabel('数量')
for bar, val in zip(bars22, priv_dt_values):
    ax22.text(val + 2, bar.get_y() + bar.get_height()/2, str(val), 
              ha='left', va='center', fontsize=10, fontweight='bold')
ax22.spines['top'].set_visible(False)
ax22.spines['right'].set_visible(False)

# 2.3 Private customers
ax23 = fig2.add_subplot(2, 3, 3)
priv_cust = private_df[customer_col].value_counts().head(10)
priv_cust_names = list(priv_cust.index)[::-1]
priv_cust_values = list(priv_cust.values)[::-1]
colors_cust = plt.cm.Reds(np.linspace(0.3, 0.9, len(priv_cust_names)))
bars23 = ax23.barh(priv_cust_names, priv_cust_values, color=colors_cust, height=0.7)
ax23.set_title('私有化客户Bug分布Top10', fontsize=14, fontweight='bold', pad=15)
ax23.set_xlabel('Bug数量')
for bar, val in zip(bars23, priv_cust_values):
    ax23.text(val + 1, bar.get_y() + bar.get_height()/2, str(val), 
              ha='left', va='center', fontsize=10, fontweight='bold')
ax23.spines['top'].set_visible(False)
ax23.spines['right'].set_visible(False)

# 2.4 Quarterly comparison
ax24 = fig2.add_subplot(2, 3, 4)
saas_q = [sum([saas_monthly.get(i, 0) for i in [1,2,3]]),
          sum([saas_monthly.get(i, 0) for i in [4,5,6]]),
          sum([saas_monthly.get(i, 0) for i in [7,8,9]]),
          sum([saas_monthly.get(i, 0) for i in [10,11,12]])]
priv_q = [sum([private_monthly.get(i, 0) for i in [1,2,3]]),
          sum([private_monthly.get(i, 0) for i in [4,5,6]]),
          sum([private_monthly.get(i, 0) for i in [7,8,9]]),
          sum([private_monthly.get(i, 0) for i in [10,11,12]])]
quarters = ['Q1', 'Q2', 'Q3', 'Q4']
x24 = np.arange(len(quarters))
bars_saas_q = ax24.bar(x24 - width/2, saas_q, width, label='SaaS', color='#3498DB')
bars_priv_q = ax24.bar(x24 + width/2, priv_q, width, label='私有化', color='#E74C3C')
ax24.set_title('季度Bug对比', fontsize=14, fontweight='bold', pad=15)
ax24.set_ylabel('Bug数量')
ax24.set_xticks(x24)
ax24.set_xticklabels(quarters, fontsize=12)
ax24.legend()
for bar, val in zip(bars_saas_q, saas_q):
    ax24.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val), 
              ha='center', va='bottom', fontsize=10, fontweight='bold', color='#3498DB')
for bar, val in zip(bars_priv_q, priv_q):
    ax24.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, str(val), 
              ha='center', va='bottom', fontsize=10, fontweight='bold', color='#E74C3C')
ax24.spines['top'].set_visible(False)
ax24.spines['right'].set_visible(False)

# 2.5 Private P0 customers
ax25 = fig2.add_subplot(2, 3, 5)
p0_cust = private_p0[customer_col].value_counts()
if len(p0_cust) > 0:
    p0_cust_names = list(p0_cust.index)
    p0_cust_values = list(p0_cust.values)
    colors_p0 = plt.cm.Reds(np.linspace(0.4, 0.9, len(p0_cust_names)))
    wedges25, texts25, autotexts25 = ax25.pie(p0_cust_values, labels=p0_cust_names, autopct='%1.1f%%', 
                                               colors=colors_p0, startangle=90)
    ax25.set_title('私有化P0问题客户分布', fontsize=14, fontweight='bold', pad=15)
else:
    ax25.text(0.5, 0.5, '无P0数据', ha='center', va='center', fontsize=14)
    ax25.set_title('私有化P0问题客户分布', fontsize=14, fontweight='bold', pad=15)

# 2.6 Key metrics summary
ax26 = fig2.add_subplot(2, 3, 6)
ax26.axis('off')
summary_text = f"""
╔══════════════════════════════════════════╗
║       SaaS vs 私有化 关键指标对比         ║
╠══════════════════════════════════════════╣
║                                          ║
║  【Bug数量】                              ║
║    SaaS:    {len(saas_df):>5}个  ({len(saas_df)/len(bug_df)*100:>5.1f}%)       ║
║    私有化:  {len(private_df):>5}个  ({len(private_df)/len(bug_df)*100:>5.1f}%)       ║
║                                          ║
║  【总体解决率】                           ║
║    SaaS:    {saas_resolved/len(saas_df)*100:>5.1f}%                   ║
║    私有化:  {private_resolved/len(private_df)*100:>5.1f}%                   ║
║                                          ║
║  【P0阻塞问题】                           ║
║    SaaS:    {len(saas_p0):>3}个, 解决率 {saas_p0_resolved/len(saas_p0)*100 if len(saas_p0) else 0:>5.1f}%     ║
║    私有化:  {len(private_p0):>3}个, 解决率 {private_p0_resolved/len(private_p0)*100 if len(private_p0) else 0:>5.1f}%     ║
║                                          ║
║  【P1核心问题】                           ║
║    SaaS:    {len(saas_p1):>3}个, 解决率 {saas_p1_resolved/len(saas_p1)*100 if len(saas_p1) else 0:>5.1f}%     ║
║    私有化:  {len(private_p1):>3}个, 解决率 {private_p1_resolved/len(private_p1)*100 if len(private_p1) else 0:>5.1f}%     ║
║                                          ║
╚══════════════════════════════════════════╝
"""
ax26.text(0.5, 0.5, summary_text, transform=ax26.transAxes, fontsize=11,
          verticalalignment='center', horizontalalignment='center',
          family='monospace', bbox=dict(boxstyle='round', facecolor='#F8F9F9', edgecolor='#BDC3C7'))

plt.tight_layout(pad=3.0)
plt.savefig('2025/2025研发质量分析/SaaS私有化对比图表2.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("图表已保存:")
print("  - SaaS私有化对比图表1.png")
print("  - SaaS私有化对比图表2.png")
