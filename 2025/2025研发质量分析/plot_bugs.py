#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bug Data Visualization
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

# Create figure with multiple subplots
fig = plt.figure(figsize=(20, 24))

# 1. Monthly trend chart
ax1 = fig.add_subplot(3, 2, 1)
bug_df['创建日期_parsed'] = pd.to_datetime(bug_df['创建日期'], errors='coerce')
y2025 = bug_df[bug_df['创建日期_parsed'].dt.year == 2025]
monthly = y2025.groupby(y2025['创建日期_parsed'].dt.month).size()
months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
values = [monthly.get(i, 0) for i in range(1, 13)]
bars = ax1.bar(months, values, color='#4A90D9', edgecolor='white', linewidth=0.7)
ax1.set_title('2025年月度Bug数量趋势', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('月份', fontsize=11)
ax1.set_ylabel('Bug数量', fontsize=11)
ax1.set_ylim(0, max(values) * 1.2)
for bar, val in zip(bars, values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5, str(val), 
             ha='center', va='bottom', fontsize=10, fontweight='bold')
ax1.axhline(y=sum(values)/12, color='red', linestyle='--', alpha=0.7, label=f'月均: {sum(values)/12:.0f}')
ax1.legend()
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# 2. Severity distribution pie chart
ax2 = fig.add_subplot(3, 2, 2)
severity_col = '自定义字段(严重程度)'
severity_counts = bug_df[severity_col].value_counts()
labels = ['P2\n非核心功能问题', 'P3\n不影响功能', 'P1\n核心功能问题', 'P0\n阻塞性问题']
sizes = [severity_counts.get('P2（非核心功能问题）', 0), 
         severity_counts.get('P3（不影响客户功能使用问题）', 0),
         severity_counts.get('P1（核心功能问题）', 0),
         severity_counts.get('P0（阻塞性问题）', 0)]
colors = ['#5DADE2', '#82E0AA', '#F4D03F', '#E74C3C']
explode = (0, 0, 0.05, 0.1)
wedges, texts, autotexts = ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
                                    colors=colors, explode=explode, shadow=True)
ax2.set_title('Bug严重程度分布', fontsize=14, fontweight='bold', pad=15)
for autotext in autotexts:
    autotext.set_fontsize(10)
    autotext.set_fontweight('bold')

# 3. Defect type bar chart (horizontal)
ax3 = fig.add_subplot(3, 2, 3)
defect_cols = [c for c in bug_df.columns if '缺陷类型' in c]
defect_types = Counter()
for col in defect_cols:
    for v in bug_df[col].dropna():
        if v and str(v).strip(): 
            defect_types[str(v).strip()] += 1
top_defects = defect_types.most_common(10)
defect_names = [d[0] for d in top_defects][::-1]
defect_values = [d[1] for d in top_defects][::-1]
colors_defect = plt.cm.Blues(np.linspace(0.3, 0.9, len(defect_names)))
bars3 = ax3.barh(defect_names, defect_values, color=colors_defect, edgecolor='white', height=0.7)
ax3.set_title('Bug缺陷类型分布 Top10', fontsize=14, fontweight='bold', pad=15)
ax3.set_xlabel('数量', fontsize=11)
for bar, val in zip(bars3, defect_values):
    ax3.text(val + 5, bar.get_y() + bar.get_height()/2, str(val), 
             ha='left', va='center', fontsize=10, fontweight='bold')
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)

# 4. Status distribution
ax4 = fig.add_subplot(3, 2, 4)
status_counts = bug_df['状态'].value_counts()
status_labels = ['完成', '待办', '挂起中', '处理中', '其他']
status_values = [status_counts.get('完成', 0), 
                 status_counts.get('待办', 0),
                 status_counts.get('挂起中', 0),
                 status_counts.get('处理中', 0),
                 sum(status_counts) - status_counts.get('完成', 0) - status_counts.get('待办', 0) - status_counts.get('挂起中', 0) - status_counts.get('处理中', 0)]
colors_status = ['#27AE60', '#3498DB', '#F39C12', '#9B59B6', '#95A5A6']
wedges4, texts4, autotexts4 = ax4.pie(status_values, labels=status_labels, autopct='%1.1f%%', 
                                       startangle=90, colors=colors_status)
ax4.set_title('Bug状态分布', fontsize=14, fontweight='bold', pad=15)
for autotext in autotexts4:
    autotext.set_fontsize(10)
    autotext.set_fontweight('bold')

# 5. Top customers bar chart
ax5 = fig.add_subplot(3, 2, 5)
customer_col = '自定义字段(客户名称)'
customer_counts = bug_df[customer_col].value_counts().head(10)
customer_names = list(customer_counts.index)[::-1]
customer_values = list(customer_counts.values)[::-1]
colors_customer = plt.cm.Oranges(np.linspace(0.3, 0.9, len(customer_names)))
bars5 = ax5.barh(customer_names, customer_values, color=colors_customer, edgecolor='white', height=0.7)
ax5.set_title('客户Bug分布 Top10', fontsize=14, fontweight='bold', pad=15)
ax5.set_xlabel('Bug数量', fontsize=11)
for bar, val in zip(bars5, customer_values):
    ax5.text(val + 3, bar.get_y() + bar.get_height()/2, str(val), 
             ha='left', va='center', fontsize=10, fontweight='bold')
ax5.spines['top'].set_visible(False)
ax5.spines['right'].set_visible(False)

# 6. P0/P1 resolution rate comparison
ax6 = fig.add_subplot(3, 2, 6)
p0_df = bug_df[bug_df[severity_col].str.contains('P0', na=False)]
p1_df = bug_df[bug_df[severity_col].str.contains('P1', na=False)]
p0_total = len(p0_df)
p0_resolved = len(p0_df[p0_df['状态'] == '完成'])
p1_total = len(p1_df)
p1_resolved = len(p1_df[p1_df['状态'] == '完成'])
total_bugs = len(bug_df)
total_resolved = len(bug_df[bug_df['状态'] == '完成'])

categories = ['P0阻塞性问题', 'P1核心功能问题', '总体']
totals = [p0_total, p1_total, total_bugs]
resolved = [p0_resolved, p1_resolved, total_resolved]
rates = [p0_resolved/p0_total*100 if p0_total else 0, 
         p1_resolved/p1_total*100 if p1_total else 0,
         total_resolved/total_bugs*100 if total_bugs else 0]

x = np.arange(len(categories))
width = 0.35
bars_total = ax6.bar(x - width/2, totals, width, label='总数', color='#85C1E9', edgecolor='white')
bars_resolved = ax6.bar(x + width/2, resolved, width, label='已解决', color='#27AE60', edgecolor='white')
ax6.set_title('Bug解决率对比', fontsize=14, fontweight='bold', pad=15)
ax6.set_ylabel('数量', fontsize=11)
ax6.set_xticks(x)
ax6.set_xticklabels(categories, fontsize=11)
ax6.legend()

# Add resolution rate labels
for i, (t, r, rate) in enumerate(zip(totals, resolved, rates)):
    ax6.text(i, max(t, r) + 20, f'解决率: {rate:.1f}%', ha='center', fontsize=11, fontweight='bold', color='#E74C3C')

ax6.spines['top'].set_visible(False)
ax6.spines['right'].set_visible(False)

plt.tight_layout(pad=3.0)
plt.savefig('2025/2025研发质量分析/2025年度Bug分析图表.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("图表已保存到: 2025/2025研发质量分析/2025年度Bug分析图表.png")

# Create a second figure for additional charts
fig2 = plt.figure(figsize=(16, 10))

# Quarter comparison
ax7 = fig2.add_subplot(2, 2, 1)
q1 = sum([monthly.get(i, 0) for i in [1, 2, 3]])
q2 = sum([monthly.get(i, 0) for i in [4, 5, 6]])
q3 = sum([monthly.get(i, 0) for i in [7, 8, 9]])
q4 = sum([monthly.get(i, 0) for i in [10, 11, 12]])
quarters = ['Q1', 'Q2', 'Q3', 'Q4']
q_values = [q1, q2, q3, q4]
colors_q = ['#E74C3C', '#F39C12', '#27AE60', '#3498DB']
bars7 = ax7.bar(quarters, q_values, color=colors_q, edgecolor='white', width=0.6)
ax7.set_title('2025年季度Bug数量对比', fontsize=14, fontweight='bold', pad=15)
ax7.set_ylabel('Bug数量', fontsize=11)
for bar, val in zip(bars7, q_values):
    ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10, str(val), 
             ha='center', va='bottom', fontsize=12, fontweight='bold')
    pct = val / sum(q_values) * 100
    ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2, f'{pct:.1f}%', 
             ha='center', va='center', fontsize=10, color='white', fontweight='bold')
ax7.spines['top'].set_visible(False)
ax7.spines['right'].set_visible(False)

# P0 customer distribution
ax8 = fig2.add_subplot(2, 2, 2)
p0_customers = p0_df[customer_col].value_counts()
p0_cust_names = list(p0_customers.index)
p0_cust_values = list(p0_customers.values)
colors_p0 = plt.cm.Reds(np.linspace(0.3, 0.9, len(p0_cust_names)))
wedges8, texts8, autotexts8 = ax8.pie(p0_cust_values, labels=p0_cust_names, autopct='%1.1f%%', 
                                       startangle=90, colors=colors_p0)
ax8.set_title('P0阻塞性问题客户分布', fontsize=14, fontweight='bold', pad=15)
for autotext in autotexts8:
    autotext.set_fontsize(9)

# Assignee workload
ax9 = fig2.add_subplot(2, 2, 3)
assignee_counts = bug_df['经办人'].value_counts().head(10)
assignee_names = list(assignee_counts.index)[::-1]
assignee_values = list(assignee_counts.values)[::-1]
colors_assignee = plt.cm.Greens(np.linspace(0.3, 0.9, len(assignee_names)))
bars9 = ax9.barh(assignee_names, assignee_values, color=colors_assignee, edgecolor='white', height=0.7)
ax9.set_title('Bug经办人处理量 Top10', fontsize=14, fontweight='bold', pad=15)
ax9.set_xlabel('处理数量', fontsize=11)
for bar, val in zip(bars9, assignee_values):
    ax9.text(val + 2, bar.get_y() + bar.get_height()/2, str(val), 
             ha='left', va='center', fontsize=10, fontweight='bold')
ax9.spines['top'].set_visible(False)
ax9.spines['right'].set_visible(False)

# P0 defect types
ax10 = fig2.add_subplot(2, 2, 4)
p0_types = Counter()
for col in defect_cols:
    for v in p0_df[col].dropna():
        if v and str(v).strip(): 
            p0_types[str(v).strip()] += 1
p0_type_items = p0_types.most_common()
p0_type_names = [d[0] for d in p0_type_items]
p0_type_values = [d[1] for d in p0_type_items]
colors_p0_type = plt.cm.Purples(np.linspace(0.3, 0.9, len(p0_type_names)))
bars10 = ax10.bar(range(len(p0_type_names)), p0_type_values, color=colors_p0_type, edgecolor='white')
ax10.set_title('P0问题缺陷类型分布', fontsize=14, fontweight='bold', pad=15)
ax10.set_ylabel('数量', fontsize=11)
ax10.set_xticks(range(len(p0_type_names)))
ax10.set_xticklabels(p0_type_names, rotation=45, ha='right', fontsize=9)
for bar, val in zip(bars10, p0_type_values):
    ax10.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(val), 
             ha='center', va='bottom', fontsize=10, fontweight='bold')
ax10.spines['top'].set_visible(False)
ax10.spines['right'].set_visible(False)

plt.tight_layout(pad=3.0)
plt.savefig('2025/2025研发质量分析/2025年度Bug分析图表2.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("图表已保存到: 2025/2025研发质量分析/2025年度Bug分析图表2.png")
