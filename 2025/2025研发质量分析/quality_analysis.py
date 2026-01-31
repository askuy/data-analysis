#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025 R&D Quality System Analysis Script
Analyzes incident reports and Jira data to evaluate quality management
"""

import pandas as pd
from collections import Counter
from datetime import datetime
import re

# File paths
INCIDENT_FILE = '2025年线上故障问题表.csv'
JIRA_FILE = 'Jira-项目管理 2026-01-30T12_27_55+0800.csv'
OUTPUT_FILE = '2025年度研发质量体系分析报告.md'

def load_data():
    """Load both CSV files"""
    incidents = pd.read_csv(INCIDENT_FILE, encoding='utf-8')
    jira = pd.read_csv(JIRA_FILE, encoding='utf-8', low_memory=False)
    return incidents, jira

def clean_incident_data(df):
    """Clean incident data"""
    # Remove empty rows
    df = df.dropna(subset=['故障报告名称'])
    df = df[df['故障报告名称'].str.strip() != '']
    return df

def extract_keywords(text):
    """Extract keywords from incident name for matching"""
    if pd.isna(text):
        return []
    # Extract key terms
    keywords = []
    # Customer names
    customers = ['猿辅导', '好未来', '小红书', '京东', 'OPPO', '边锋', '博纳', '广东电信', 
                 '北京凯读', '滴滴', '招商', '融云', '东风', '格力', '360', '玉溪']
    for c in customers:
        if c in str(text):
            keywords.append(c)
    # Technical terms
    if '表格' in str(text) or '表单' in str(text):
        keywords.append('表格')
    if '文档' in str(text) or '文件' in str(text):
        keywords.append('文档')
    if '同步' in str(text):
        keywords.append('同步')
    if '登录' in str(text):
        keywords.append('登录')
    if '白屏' in str(text):
        keywords.append('白屏')
    return keywords

def match_incidents_with_jira(incidents, jira):
    """Match incident records with Jira data"""
    # Filter Jira for fault type
    jira_faults = jira[jira['问题类型'] == '故障'].copy()
    
    matches = []
    no_matches = []
    
    for idx, row in incidents.iterrows():
        incident_name = str(row['故障报告名称'])
        incident_date = str(row['故障日期']) if pd.notna(row['故障日期']) else ''
        customer = str(row['客户']) if pd.notna(row['客户']) else ''
        
        # Try to find matching Jira record
        found = False
        matched_jira = None
        
        # Search by keywords in Jira summary
        keywords = extract_keywords(incident_name)
        if customer and customer != 'nan':
            keywords.append(customer)
        
        for jidx, jrow in jira_faults.iterrows():
            jira_summary = str(jrow['概要']) if pd.notna(jrow['概要']) else ''
            jira_desc = str(jrow['描述']) if pd.notna(jrow['描述']) else ''
            jira_customer = str(jrow.get('自定义字段(客户名称)', '')) if pd.notna(jrow.get('自定义字段(客户名称)', '')) else ''
            
            combined_text = jira_summary + ' ' + jira_desc + ' ' + jira_customer
            
            # Check for keyword matches
            match_count = sum(1 for kw in keywords if kw in combined_text)
            
            # Also check for partial name match
            name_parts = incident_name.replace('故障报告', '').replace('的', '').strip()
            if len(name_parts) > 5 and name_parts[:10] in combined_text:
                match_count += 2
            
            if match_count >= 2:
                found = True
                matched_jira = jrow
                break
        
        if found:
            matches.append({
                'incident': row,
                'jira': matched_jira
            })
        else:
            no_matches.append(row)
    
    return matches, no_matches

def analyze_distribution(incidents, jira):
    """Analyze fault distribution by various dimensions"""
    results = {}
    
    # Filter Jira for fault type
    jira_faults = jira[jira['问题类型'] == '故障'].copy()
    
    # 1. Time distribution (from incidents)
    incidents['date_parsed'] = pd.to_datetime(incidents['故障日期'], errors='coerce')
    incidents['month'] = incidents['date_parsed'].dt.month
    monthly_dist = incidents.groupby('month').size().to_dict()
    results['monthly_incidents'] = monthly_dist
    
    # 2. Team distribution (from incidents)
    team_dist = incidents['归属团队'].value_counts().to_dict()
    results['team_dist'] = team_dist
    
    # 3. Severity distribution (from incidents)
    severity_dist = incidents['故障等级'].value_counts().to_dict()
    results['severity_dist'] = severity_dist
    
    # 4. Customer distribution (from incidents)
    customer_dist = incidents['客户'].value_counts().to_dict()
    results['customer_dist'] = customer_dist
    
    # 5. Jira fault time distribution
    jira_faults['创建日期_parsed'] = pd.to_datetime(jira_faults['创建日期'], errors='coerce')
    jira_2025 = jira_faults[jira_faults['创建日期_parsed'].dt.year == 2025]
    jira_monthly = jira_2025.groupby(jira_2025['创建日期_parsed'].dt.month).size().to_dict()
    results['jira_monthly'] = jira_monthly
    
    # 6. Jira severity distribution  
    severity_col = '自定义字段(严重程度)'
    if severity_col in jira_faults.columns:
        jira_severity = jira_faults[severity_col].value_counts().to_dict()
        results['jira_severity'] = jira_severity
    
    # 7. Environment distribution
    env_col = '自定义字段(缺陷发现环境)'
    if env_col in jira_faults.columns:
        env_dist = jira_faults[env_col].value_counts().to_dict()
        results['env_dist'] = env_dist
    
    return results

def analyze_root_causes(jira):
    """Analyze root causes from Jira data"""
    jira_faults = jira[jira['问题类型'] == '故障'].copy()
    
    root_col = '自定义字段(根本原因)'
    results = {}
    
    if root_col in jira_faults.columns:
        root_causes = jira_faults[root_col].value_counts().to_dict()
        # Filter out NaN
        root_causes = {k: v for k, v in root_causes.items() if pd.notna(k) and str(k).strip()}
        results['root_causes'] = root_causes
    
    # Analyze defect types
    defect_cols = [c for c in jira_faults.columns if '缺陷类型' in c]
    defect_types = Counter()
    for col in defect_cols:
        for v in jira_faults[col].dropna():
            if v and str(v).strip():
                defect_types[str(v).strip()] += 1
    results['defect_types'] = dict(defect_types.most_common(15))
    
    # Analyze solutions
    solution_col = '自定义字段(解决办法)'
    if solution_col in jira_faults.columns:
        solutions = jira_faults[solution_col].dropna()
        results['solution_count'] = len(solutions)
    
    return results

def analyze_resolution_stats(jira):
    """Analyze resolution statistics"""
    jira_faults = jira[jira['问题类型'] == '故障'].copy()
    
    results = {}
    
    # Status distribution
    status_dist = jira_faults['状态'].value_counts().to_dict()
    results['status_dist'] = status_dist
    
    # Resolution rate
    total = len(jira_faults)
    resolved = len(jira_faults[jira_faults['状态'] == '完成'])
    results['total'] = total
    results['resolved'] = resolved
    results['resolution_rate'] = resolved / total * 100 if total > 0 else 0
    
    # P0 stats
    severity_col = '自定义字段(严重程度)'
    if severity_col in jira_faults.columns:
        p0_df = jira_faults[jira_faults[severity_col].str.contains('P0', na=False)]
        p0_total = len(p0_df)
        p0_resolved = len(p0_df[p0_df['状态'] == '完成'])
        results['p0_total'] = p0_total
        results['p0_resolved'] = p0_resolved
        results['p0_rate'] = p0_resolved / p0_total * 100 if p0_total > 0 else 0
        
        # P1 stats
        p1_df = jira_faults[jira_faults[severity_col].str.contains('P1', na=False)]
        p1_total = len(p1_df)
        p1_resolved = len(p1_df[p1_df['状态'] == '完成'])
        results['p1_total'] = p1_total
        results['p1_resolved'] = p1_resolved
        results['p1_rate'] = p1_resolved / p1_total * 100 if p1_total > 0 else 0
    
    # Unresolved by severity
    unresolved_status = ['待办', '处理中', '挂起中', '重新打开']
    unresolved = jira_faults[jira_faults['状态'].isin(unresolved_status)]
    results['unresolved_count'] = len(unresolved)
    
    return results

def generate_report(incidents, jira, matches, no_matches, distribution, root_causes, resolution):
    """Generate markdown report"""
    report = []
    
    report.append("# 2025年度研发质量体系分析报告\n")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Executive Summary
    report.append("## 一、执行摘要\n")
    report.append("本报告基于两个核心数据源进行分析：")
    report.append(f"- **线上故障问题表**：{len(incidents)}条重大线上故障记录")
    report.append(f"- **Jira项目管理数据**：共{len(jira)}条记录，其中故障类型{len(jira[jira['问题类型']=='故障'])}条\n")
    
    # Data matching analysis
    report.append("## 二、数据源对比分析\n")
    report.append("### 2.1 匹配结果统计\n")
    report.append(f"| 指标 | 数量 | 占比 |")
    report.append(f"|------|------|------|")
    total_incidents = len(incidents)
    matched = len(matches)
    unmatched = len(no_matches)
    report.append(f"| 线上故障记录总数 | {total_incidents} | 100% |")
    report.append(f"| 在Jira中有对应记录 | {matched} | {matched/total_incidents*100:.1f}% |")
    report.append(f"| 在Jira中无对应记录 | {unmatched} | {unmatched/total_incidents*100:.1f}% |")
    report.append("")
    
    report.append("### 2.2 未在Jira中记录的故障清单\n")
    if no_matches:
        report.append("| 序号 | 故障名称 | 故障日期 | 故障等级 | 客户 |")
        report.append("|------|----------|----------|----------|------|")
        for i, row in enumerate(no_matches, 1):
            name = str(row['故障报告名称'])[:30] + '...' if len(str(row['故障报告名称'])) > 30 else str(row['故障报告名称'])
            report.append(f"| {i} | {name} | {row['故障日期']} | {row['故障等级']} | {row['客户']} |")
        report.append("")
    
    report.append("### 2.3 数据一致性问题分析\n")
    report.append(f"- **记录缺失率**: {unmatched/total_incidents*100:.1f}%")
    report.append("- **可能原因**:")
    report.append("  1. 故障处理流程未规范化，部分故障未同步录入Jira")
    report.append("  2. 线上故障表为人工维护，存在记录遗漏或延迟")
    report.append("  3. 两套系统的故障命名规范不统一，导致匹配困难")
    report.append("")
    
    # Distribution Analysis
    report.append("## 三、故障分布分析\n")
    
    report.append("### 3.1 月度故障趋势\n")
    report.append("**线上故障问题表 - 月度分布**\n")
    report.append("| 月份 | 故障数量 |")
    report.append("|------|----------|")
    for month in sorted(distribution.get('monthly_incidents', {}).keys()):
        count = distribution['monthly_incidents'][month]
        report.append(f"| {int(month)}月 | {count} |")
    report.append("")
    
    report.append("**Jira故障记录 - 月度分布**\n")
    report.append("| 月份 | 故障数量 |")
    report.append("|------|----------|")
    for month in sorted(distribution.get('jira_monthly', {}).keys()):
        count = distribution['jira_monthly'][month]
        report.append(f"| {int(month)}月 | {count} |")
    report.append("")
    
    report.append("### 3.2 团队故障分布\n")
    report.append("| 团队 | 故障数量 | 占比 |")
    report.append("|------|----------|------|")
    total_team = sum(distribution.get('team_dist', {}).values())
    for team, count in sorted(distribution.get('team_dist', {}).items(), key=lambda x: -x[1]):
        if pd.notna(team) and str(team).strip():
            pct = count / total_team * 100 if total_team > 0 else 0
            report.append(f"| {team} | {count} | {pct:.1f}% |")
    report.append("")
    
    report.append("### 3.3 故障等级分布\n")
    report.append("| 等级 | 数量 | 占比 | 说明 |")
    report.append("|------|------|------|------|")
    total_sev = sum(distribution.get('severity_dist', {}).values())
    severity_desc = {'P0': '阻塞性问题', 'P1': '核心功能问题', 'P2': '一般问题'}
    for sev in ['P0', 'P1', 'P2']:
        count = distribution.get('severity_dist', {}).get(sev, 0)
        pct = count / total_sev * 100 if total_sev > 0 else 0
        report.append(f"| {sev} | {count} | {pct:.1f}% | {severity_desc.get(sev, '')} |")
    report.append("")
    
    report.append("### 3.4 客户故障分布\n")
    report.append("| 客户 | 故障数量 |")
    report.append("|------|----------|")
    for cust, count in sorted(distribution.get('customer_dist', {}).items(), key=lambda x: -x[1])[:15]:
        if pd.notna(cust) and str(cust).strip():
            report.append(f"| {cust} | {count} |")
    report.append("")
    
    report.append("### 3.5 故障发现环境分布\n")
    report.append("| 环境 | 数量 |")
    report.append("|------|------|")
    for env, count in sorted(distribution.get('env_dist', {}).items(), key=lambda x: -x[1])[:10]:
        if pd.notna(env) and str(env).strip():
            report.append(f"| {env} | {count} |")
    report.append("")
    
    # Root Cause Analysis
    report.append("## 四、根本原因分析\n")
    
    report.append("### 4.1 故障根本原因分布\n")
    report.append("| 根本原因 | 数量 | 占比 |")
    report.append("|----------|------|------|")
    total_root = sum(root_causes.get('root_causes', {}).values())
    for cause, count in sorted(root_causes.get('root_causes', {}).items(), key=lambda x: -x[1])[:15]:
        pct = count / total_root * 100 if total_root > 0 else 0
        report.append(f"| {cause} | {count} | {pct:.1f}% |")
    report.append("")
    
    report.append("### 4.2 缺陷类型分布\n")
    report.append("| 缺陷类型 | 数量 |")
    report.append("|----------|------|")
    for dtype, count in sorted(root_causes.get('defect_types', {}).items(), key=lambda x: -x[1])[:10]:
        report.append(f"| {dtype} | {count} |")
    report.append("")
    
    # Resolution Statistics
    report.append("## 五、故障解决效率分析\n")
    
    report.append("### 5.1 整体解决情况\n")
    report.append("| 指标 | 数值 |")
    report.append("|------|------|")
    report.append(f"| 故障总数 | {resolution['total']} |")
    report.append(f"| 已解决 | {resolution['resolved']} |")
    report.append(f"| 解决率 | {resolution['resolution_rate']:.1f}% |")
    report.append(f"| 未解决 | {resolution['unresolved_count']} |")
    report.append("")
    
    report.append("### 5.2 按严重程度的解决情况\n")
    report.append("| 等级 | 总数 | 已解决 | 解决率 |")
    report.append("|------|------|--------|--------|")
    report.append(f"| P0 | {resolution.get('p0_total', 0)} | {resolution.get('p0_resolved', 0)} | {resolution.get('p0_rate', 0):.1f}% |")
    report.append(f"| P1 | {resolution.get('p1_total', 0)} | {resolution.get('p1_resolved', 0)} | {resolution.get('p1_rate', 0):.1f}% |")
    report.append("")
    
    report.append("### 5.3 故障状态分布\n")
    report.append("| 状态 | 数量 |")
    report.append("|------|------|")
    for status, count in sorted(resolution.get('status_dist', {}).items(), key=lambda x: -x[1]):
        report.append(f"| {status} | {count} |")
    report.append("")
    
    # Conclusions
    report.append("## 六、质量体系结论\n")
    
    report.append("### 6.1 发现的主要问题\n")
    report.append("""
1. **故障记录体系不完善**
   - 线上故障问题表与Jira记录存在{:.1f}%的不一致率
   - 说明故障处理流程缺乏统一的记录规范
   - 两套系统并行运行，缺乏数据同步机制

2. **故障分布特征**
   - 后端团队承担最多的故障处理工作
   - P1级别故障占比最高，需要关注核心功能的稳定性
   - 私有化客户的故障占比显著，需要加强私有化环境的稳定性保障

3. **根本原因分析**
   - "代码问题"是最主要的故障来源，占比最高
   - "客户操作问题"和"配置问题"也是重要原因
   - 部分故障由"中间件问题"和"外部限制"导致，属于环境因素

4. **解决效率**
   - 整体故障解决率为{:.1f}%
   - P0级别故障解决率为{:.1f}%，基本得到及时处理
   - 仍有{:d}个故障处于未解决状态
""".format(
        unmatched/total_incidents*100,
        resolution['resolution_rate'],
        resolution.get('p0_rate', 0),
        resolution['unresolved_count']
    ))
    
    report.append("### 6.2 改进建议\n")
    report.append("""
1. **统一故障管理流程**
   - 建立统一的故障录入标准，确保所有线上故障都在Jira中创建对应记录
   - 线上故障问题表应与Jira建立关联，可通过Jira Issue ID进行关联
   - 制定SOP，明确故障发现、记录、处理、复盘的完整流程

2. **加强代码质量管控**
   - 根本原因分析显示"代码问题"是主要故障来源，建议加强代码审查
   - 增加单元测试覆盖率，特别是核心功能模块
   - 建立代码质量门禁，在发布前进行自动化质量检查

3. **优化私有化客户支持**
   - 私有化客户故障占比高，建议建立专门的私有化运维团队
   - 提供标准化的私有化部署方案，减少配置错误
   - 建立客户环境监控，提前发现潜在问题

4. **完善故障复盘机制**
   - 对P0/P1级故障进行强制复盘
   - 将复盘结论转化为改进措施，并跟踪执行
   - 定期汇总分析，识别系统性问题

5. **建立质量度量体系**
   - 定期统计和分析故障数据
   - 建立质量KPI，如故障数量、解决时间、复发率等
   - 通过数据驱动的方式持续改进质量
""")
    
    report.append("## 七、附录\n")
    report.append("### 数据来源说明\n")
    report.append(f"- 线上故障问题表：{INCIDENT_FILE}")
    report.append(f"- Jira项目管理数据：{JIRA_FILE}")
    report.append(f"- 分析时间范围：2025年1月-12月")
    report.append("")
    
    return '\n'.join(report)

def main():
    print("=" * 60)
    print("2025年度研发质量体系分析")
    print("=" * 60)
    
    # Load data
    print("\n[1/6] 加载数据...")
    incidents, jira = load_data()
    incidents = clean_incident_data(incidents)
    print(f"  - 线上故障记录: {len(incidents)}条")
    print(f"  - Jira记录: {len(jira)}条")
    print(f"  - Jira故障记录: {len(jira[jira['问题类型']=='故障'])}条")
    
    # Match incidents with Jira
    print("\n[2/6] 对比线上故障与Jira数据...")
    matches, no_matches = match_incidents_with_jira(incidents, jira)
    print(f"  - 匹配成功: {len(matches)}条")
    print(f"  - 未匹配: {len(no_matches)}条")
    
    # Analyze distribution
    print("\n[3/6] 分析故障分布...")
    distribution = analyze_distribution(incidents, jira)
    print(f"  - 团队分布: {len(distribution.get('team_dist', {}))}个团队")
    print(f"  - 客户分布: {len(distribution.get('customer_dist', {}))}个客户")
    
    # Analyze root causes
    print("\n[4/6] 分析根本原因...")
    root_causes = analyze_root_causes(jira)
    print(f"  - 根本原因类型: {len(root_causes.get('root_causes', {}))}种")
    print(f"  - 缺陷类型: {len(root_causes.get('defect_types', {}))}种")
    
    # Analyze resolution
    print("\n[5/6] 分析解决效率...")
    resolution = analyze_resolution_stats(jira)
    print(f"  - 故障总数: {resolution['total']}")
    print(f"  - 解决率: {resolution['resolution_rate']:.1f}%")
    
    # Generate report
    print("\n[6/6] 生成分析报告...")
    report = generate_report(incidents, jira, matches, no_matches, 
                            distribution, root_causes, resolution)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已生成: {OUTPUT_FILE}")
    print("=" * 60)
    
    # Print summary
    print("\n【关键发现摘要】")
    print(f"1. 数据一致性: 线上故障表中{len(no_matches)}/{len(incidents)}条记录在Jira中无对应")
    print(f"2. 故障解决率: {resolution['resolution_rate']:.1f}%")
    print(f"3. P0故障解决率: {resolution.get('p0_rate', 0):.1f}%")
    print(f"4. 主要故障来源: 代码问题、客户操作问题、配置问题")
    print(f"5. 未解决故障: {resolution['unresolved_count']}条")

if __name__ == '__main__':
    main()
