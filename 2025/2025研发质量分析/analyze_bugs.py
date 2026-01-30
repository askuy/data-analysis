#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from collections import Counter

file_path = '2025/2025研发质量分析/Jira-项目管理 2026-01-30T12_27_55+0800.csv'
df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)

# Filter only bug types
bug_df = df[df['问题类型'].isin(['故障', '缺陷', 'Bug', 'bug'])].copy()

output = []

output.append("=" * 80)
output.append("一、Bug总体情况")
output.append("=" * 80)
output.append(f"总Bug数量: {len(bug_df)}")

# Status
output.append("\n【状态分布】")
for status, count in bug_df['状态'].value_counts().items():
    output.append(f"  {status}: {count}")

# Priority
output.append("\n【优先级分布】")
for p, c in bug_df['优先级'].value_counts().items():
    if pd.notna(p): output.append(f"  {p}: {c}")

# Severity
severity_col = '自定义字段(严重程度)'
output.append("\n【严重程度分布】")
for s, c in bug_df[severity_col].value_counts().items():
    if pd.notna(s): output.append(f"  {s}: {c}")

output.append("\n" + "=" * 80)
output.append("二、Bug类型分析")
output.append("=" * 80)

# Defect types
defect_cols = [c for c in bug_df.columns if '缺陷类型' in c]
defect_types = Counter()
for col in defect_cols:
    for v in bug_df[col].dropna():
        if v and str(v).strip(): defect_types[str(v).strip()] += 1
output.append("\n【缺陷类型分布】")
for dt, c in defect_types.most_common(15):
    output.append(f"  {dt}: {c}")

# Root cause
root_col = '自定义字段(根本原因)'
if root_col in bug_df.columns:
    output.append("\n【根本原因分布】")
    for r, c in bug_df[root_col].value_counts().head(10).items():
        if pd.notna(r) and str(r).strip(): output.append(f"  {r}: {c}")

output.append("\n" + "=" * 80)
output.append("三、Bug环境分析")
output.append("=" * 80)

env_col = '自定义字段(缺陷发现环境)'
if env_col in bug_df.columns:
    output.append("\n【缺陷发现环境分布】")
    for e, c in bug_df[env_col].value_counts().items():
        if pd.notna(e): output.append(f"  {e}: {c}")

output.append("\n" + "=" * 80)
output.append("四、归属分析")
output.append("=" * 80)

# Assignee
output.append("\n【经办人分布(Top15)】")
for a, c in bug_df['经办人'].value_counts().head(15).items():
    if pd.notna(a): output.append(f"  {a}: {c}")

# Customer
customer_col = '自定义字段(客户名称)'
if customer_col in bug_df.columns:
    output.append("\n【客户分布(Top15)】")
    for cu, c in bug_df[customer_col].value_counts().head(15).items():
        if pd.notna(cu) and str(cu).strip(): output.append(f"  {cu}: {c}")

output.append("\n" + "=" * 80)
output.append("五、时间趋势分析")
output.append("=" * 80)

bug_df['创建日期_parsed'] = pd.to_datetime(bug_df['创建日期'], errors='coerce')
bug_df['month'] = bug_df['创建日期_parsed'].dt.to_period('M')
output.append("\n【月度Bug创建趋势(2025年)】")
y2025 = bug_df[bug_df['创建日期_parsed'].dt.year == 2025]
for m, c in y2025.groupby('month').size().items():
    output.append(f"  {m}: {c}")

output.append("\n" + "=" * 80)
output.append("六、P0/P1高优先级Bug分析")
output.append("=" * 80)

p0_df = bug_df[bug_df[severity_col].str.contains('P0', na=False)]
output.append(f"\n【P0 Bug数量】: {len(p0_df)}")
output.append("\n【P0 Bug状态分布】")
for s, c in p0_df['状态'].value_counts().items():
    output.append(f"  {s}: {c}")

output.append("\n【P0 Bug客户分布(Top10)】")
for cu, c in p0_df[customer_col].value_counts().head(10).items():
    if pd.notna(cu) and str(cu).strip(): output.append(f"  {cu}: {c}")

p0_types = Counter()
for col in defect_cols:
    for v in p0_df[col].dropna():
        if v and str(v).strip(): p0_types[str(v).strip()] += 1
output.append("\n【P0 Bug缺陷类型分布】")
for dt, c in p0_types.most_common(10):
    output.append(f"  {dt}: {c}")

p1_df = bug_df[bug_df[severity_col].str.contains('P1', na=False)]
output.append(f"\n【P1 Bug数量】: {len(p1_df)}")
output.append("\n【P1 Bug状态分布】")
for s, c in p1_df['状态'].value_counts().items():
    output.append(f"  {s}: {c}")

output.append("\n" + "=" * 80)
output.append("七、未解决Bug分析")
output.append("=" * 80)

unresolved_status = ['待办', '处理中', '挂起中', '重新打开']
unresolved = bug_df[bug_df['状态'].isin(unresolved_status)]
output.append(f"\n【未解决Bug数量】: {len(unresolved)}")
output.append("\n【未解决Bug状态分布】")
for s, c in unresolved['状态'].value_counts().items():
    output.append(f"  {s}: {c}")
output.append("\n【未解决Bug严重程度分布】")
for sv, c in unresolved[severity_col].value_counts().items():
    if pd.notna(sv): output.append(f"  {sv}: {c}")

output.append("\n" + "=" * 80)
output.append("八、年度关键指标汇总")
output.append("=" * 80)

total = len(bug_df)
resolved = len(bug_df[bug_df['状态'] == '完成'])
rate = resolved / total * 100 if total > 0 else 0

p0_total = len(p0_df)
p0_res = len(p0_df[p0_df['状态'] == '完成'])
p0_rate = p0_res / p0_total * 100 if p0_total > 0 else 0

p1_total = len(p1_df)
p1_res = len(p1_df[p1_df['状态'] == '完成'])
p1_rate = p1_res / p1_total * 100 if p1_total > 0 else 0

output.append(f"\n  总Bug数: {total}")
output.append(f"  已解决Bug数: {resolved}")
output.append(f"  总体解决率: {rate:.1f}%")
output.append(f"\n  P0 Bug总数: {p0_total}")
output.append(f"  P0 Bug已解决: {p0_res}")
output.append(f"  P0 解决率: {p0_rate:.1f}%")
output.append(f"\n  P1 Bug总数: {p1_total}")
output.append(f"  P1 Bug已解决: {p1_res}")
output.append(f"  P1 解决率: {p1_rate:.1f}%")

# Write to file
with open('2025/2025研发质量分析/bug_analysis_result.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("分析完成，结果已保存到 bug_analysis_result.txt")
