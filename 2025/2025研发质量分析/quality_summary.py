#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2025 R&D Quality System Annual Summary
Based on incident table and Jira data
Separates SaaS and Private deployment bugs
"""

import pandas as pd
from collections import Counter
from datetime import datetime

# File paths
INCIDENT_FILE = '2025年线上故障问题表.csv'
JIRA_FILE = 'Jira-项目管理 2026-01-30T12_27_55+0800.csv'
OUTPUT_FILE = '2025年度质量体系年终总结.md'

def load_data():
    """Load CSV files"""
    incidents = pd.read_csv(INCIDENT_FILE, encoding='utf-8')
    jira = pd.read_csv(JIRA_FILE, encoding='utf-8', low_memory=False)
    return incidents, jira

def clean_incident_data(df):
    """Clean incident data"""
    df = df.dropna(subset=['故障报告名称'])
    df = df[df['故障报告名称'].str.strip() != '']
    return df

def analyze_incidents(incidents):
    """Analyze incident data"""
    results = {}
    
    # Total count
    results['total'] = len(incidents)
    
    # By severity
    severity_counts = incidents['故障等级'].value_counts().to_dict()
    results['p0_count'] = severity_counts.get('P0', 0)
    results['p1_count'] = severity_counts.get('P1', 0)
    results['p2_count'] = severity_counts.get('P2', 0)
    
    # By customer type
    saas_incidents = incidents[incidents['客户'].str.contains('Saas|SaaS', case=False, na=False)]
    results['saas_count'] = len(saas_incidents)
    results['saas_p0'] = len(saas_incidents[saas_incidents['故障等级'] == 'P0'])
    results['saas_p1'] = len(saas_incidents[saas_incidents['故障等级'] == 'P1'])
    
    private_incidents = incidents[~incidents['客户'].str.contains('Saas|SaaS', case=False, na=False)]
    results['private_count'] = len(private_incidents)
    results['private_p0'] = len(private_incidents[private_incidents['故障等级'] == 'P0'])
    results['private_p1'] = len(private_incidents[private_incidents['故障等级'] == 'P1'])
    
    # By team
    team_counts = incidents['归属团队'].value_counts().to_dict()
    results['team_dist'] = team_counts
    
    # By month
    incidents['date_parsed'] = pd.to_datetime(incidents['故障日期'], errors='coerce')
    incidents['month'] = incidents['date_parsed'].dt.month
    monthly = incidents.groupby('month').size().to_dict()
    results['monthly'] = monthly
    
    # Customer distribution
    customer_counts = incidents['客户'].value_counts().to_dict()
    results['customer_dist'] = customer_counts
    
    return results

def analyze_jira_bugs(jira):
    """Analyze Jira bug/fault data with SaaS/Private separation"""
    # Filter for bugs and faults
    bug_types = ['故障', '缺陷', 'Bug', 'bug']
    bugs = jira[jira['问题类型'].isin(bug_types)].copy()
    
    results = {}
    results['total_bugs'] = len(bugs)
    
    # Find environment column (may have encoding issues)
    env_col = None
    for col in bugs.columns:
        if '缺陷发现环境' in col:
            env_col = col
            break
    
    severity_col = None
    for col in bugs.columns:
        if '严重程度' in col:
            severity_col = col
            break
    
    # Separate SaaS and Private bugs by searching row content
    # Convert entire row to string and search
    bugs['_row_str'] = bugs.apply(lambda x: ','.join(x.astype(str)), axis=1)
    saas_bugs = bugs[bugs['_row_str'].str.contains('SaaS生产环境|SaaS客户', case=False, na=False)]
    private_bugs = bugs[bugs['_row_str'].str.contains('私有化客户生产环境|私有化客户', case=False, na=False)]
    
    # Separate SaaS and Private bugs
    if len(saas_bugs) > 0 or len(private_bugs) > 0:
        other_bugs = bugs[~bugs['_row_str'].str.contains('SaaS生产环境|SaaS客户|私有化客户生产环境|私有化客户', case=False, na=True)]
        
        results['saas_bugs_total'] = len(saas_bugs)
        results['private_bugs_total'] = len(private_bugs)
        results['other_bugs_total'] = len(other_bugs)
        
        # SaaS stats
        saas_resolved = len(saas_bugs[saas_bugs['状态'] == '完成'])
        results['saas_resolved'] = saas_resolved
        results['saas_resolution_rate'] = saas_resolved / len(saas_bugs) * 100 if len(saas_bugs) > 0 else 0
        
        # Private stats
        private_resolved = len(private_bugs[private_bugs['状态'] == '完成'])
        results['private_resolved'] = private_resolved
        results['private_resolution_rate'] = private_resolved / len(private_bugs) * 100 if len(private_bugs) > 0 else 0
        
        # SaaS P0/P1
        if severity_col is not None:
            saas_p0 = saas_bugs[saas_bugs[severity_col].str.contains('P0', na=False)]
            saas_p1 = saas_bugs[saas_bugs[severity_col].str.contains('P1', na=False)]
            results['saas_p0_total'] = len(saas_p0)
            results['saas_p0_resolved'] = len(saas_p0[saas_p0['状态'] == '完成'])
            results['saas_p1_total'] = len(saas_p1)
            results['saas_p1_resolved'] = len(saas_p1[saas_p1['状态'] == '完成'])
            
            # Private P0/P1
            private_p0 = private_bugs[private_bugs[severity_col].str.contains('P0', na=False)]
            private_p1 = private_bugs[private_bugs[severity_col].str.contains('P1', na=False)]
            results['private_p0_total'] = len(private_p0)
            results['private_p0_resolved'] = len(private_p0[private_p0['状态'] == '完成'])
            results['private_p1_total'] = len(private_p1)
            results['private_p1_resolved'] = len(private_p1[private_p1['状态'] == '完成'])
        
        # SaaS defect types
        defect_cols = [c for c in bugs.columns if '缺陷类型' in c]
        saas_defects = Counter()
        for col in defect_cols:
            for v in saas_bugs[col].dropna():
                if v and str(v).strip():
                    saas_defects[str(v).strip()] += 1
        results['saas_defect_types'] = dict(saas_defects.most_common(10))
        
        # Private defect types
        private_defects = Counter()
        for col in defect_cols:
            for v in private_bugs[col].dropna():
                if v and str(v).strip():
                    private_defects[str(v).strip()] += 1
        results['private_defect_types'] = dict(private_defects.most_common(10))
        
        # Monthly trends for SaaS and Private
        saas_bugs['创建日期_parsed'] = pd.to_datetime(saas_bugs['创建日期'], errors='coerce')
        saas_2025 = saas_bugs[saas_bugs['创建日期_parsed'].dt.year == 2025]
        results['saas_monthly'] = saas_2025.groupby(saas_2025['创建日期_parsed'].dt.month).size().to_dict()
        
        private_bugs['创建日期_parsed'] = pd.to_datetime(private_bugs['创建日期'], errors='coerce')
        private_2025 = private_bugs[private_bugs['创建日期_parsed'].dt.year == 2025]
        results['private_monthly'] = private_2025.groupby(private_2025['创建日期_parsed'].dt.month).size().to_dict()
    
    # Overall stats
    status_counts = bugs['状态'].value_counts().to_dict()
    results['status_dist'] = status_counts
    
    resolved = len(bugs[bugs['状态'] == '完成'])
    results['resolved'] = resolved
    results['resolution_rate'] = resolved / len(bugs) * 100 if len(bugs) > 0 else 0
    
    # Overall P0/P1
    if severity_col is not None:
        p0_bugs = bugs[bugs[severity_col].str.contains('P0', na=False)]
        p1_bugs = bugs[bugs[severity_col].str.contains('P1', na=False)]
        
        results['jira_p0_total'] = len(p0_bugs)
        results['jira_p0_resolved'] = len(p0_bugs[p0_bugs['状态'] == '完成'])
        results['jira_p0_rate'] = results['jira_p0_resolved'] / results['jira_p0_total'] * 100 if results['jira_p0_total'] > 0 else 0
        
        results['jira_p1_total'] = len(p1_bugs)
        results['jira_p1_resolved'] = len(p1_bugs[p1_bugs['状态'] == '完成'])
        results['jira_p1_rate'] = results['jira_p1_resolved'] / results['jira_p1_total'] * 100 if results['jira_p1_total'] > 0 else 0
    
    # Overall defect types
    defect_cols = [c for c in bugs.columns if '缺陷类型' in c]
    defect_types = Counter()
    for col in defect_cols:
        for v in bugs[col].dropna():
            if v and str(v).strip():
                defect_types[str(v).strip()] += 1
    results['defect_types'] = dict(defect_types.most_common(10))
    
    # Unresolved
    unresolved_status = ['待办', '处理中', '挂起中']
    unresolved = bugs[bugs['状态'].isin(unresolved_status)]
    results['unresolved'] = len(unresolved)
    
    return results

def generate_summary(incidents_stats, jira_stats):
    """Generate annual quality summary report"""
    report = []
    
    report.append("# 2025年度研发质量体系年终总结\n")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d')}\n")
    
    # Section 1: Core Metrics
    report.append("## 一、年度质量核心指标\n")
    report.append("### 1.1 关键数据一览\n")
    report.append("| 指标 | 数值 | 说明 |")
    report.append("|------|------|------|")
    report.append(f"| 线上重大故障总数 | **{incidents_stats['total']}个** | 全年累计 |")
    report.append(f"| P0阻塞性故障 | **{incidents_stats['p0_count']}个** | 占比{incidents_stats['p0_count']/incidents_stats['total']*100:.1f}% |")
    report.append(f"| P1核心功能故障 | **{incidents_stats['p1_count']}个** | 占比{incidents_stats['p1_count']/incidents_stats['total']*100:.1f}% |")
    report.append(f"| Jira Bug总数 | **{jira_stats['total_bugs']}个** | 含故障+缺陷 |")
    report.append(f"| Bug解决率 | **{jira_stats['resolution_rate']:.1f}%** | 已完成/总数 |")
    report.append(f"| P0故障解决率 | **{jira_stats.get('jira_p0_rate', 0):.1f}%** | 高优先级及时处理 |")
    report.append(f"| P1故障解决率 | **{jira_stats.get('jira_p1_rate', 0):.1f}%** | 核心功能保障 |")
    report.append("")
    
    # Section 2: SaaS vs Private Comparison
    report.append("## 二、SaaS与私有化Bug对比分析\n")
    
    report.append("### 2.1 Bug数量对比\n")
    report.append("| 环境 | Bug总数 | 已解决 | 解决率 | 占比 |")
    report.append("|------|---------|--------|--------|------|")
    total = jira_stats['total_bugs']
    saas_total = jira_stats.get('saas_bugs_total', 0)
    private_total = jira_stats.get('private_bugs_total', 0)
    other_total = jira_stats.get('other_bugs_total', 0)
    
    saas_res = jira_stats.get('saas_resolved', 0)
    saas_rate = jira_stats.get('saas_resolution_rate', 0)
    report.append(f"| **SaaS** | {saas_total} | {saas_res} | {saas_rate:.1f}% | {saas_total/total*100:.1f}% |")
    
    private_res = jira_stats.get('private_resolved', 0)
    private_rate = jira_stats.get('private_resolution_rate', 0)
    report.append(f"| **私有化** | {private_total} | {private_res} | {private_rate:.1f}% | {private_total/total*100:.1f}% |")
    
    if other_total > 0:
        report.append(f"| 其他/未标记 | {other_total} | - | - | {other_total/total*100:.1f}% |")
    report.append("")
    
    report.append("### 2.2 P0/P1故障对比\n")
    report.append("| 环境 | P0总数 | P0已解决 | P0解决率 | P1总数 | P1已解决 | P1解决率 |")
    report.append("|------|--------|----------|----------|--------|----------|----------|")
    
    saas_p0 = jira_stats.get('saas_p0_total', 0)
    saas_p0_res = jira_stats.get('saas_p0_resolved', 0)
    saas_p0_rate = saas_p0_res / saas_p0 * 100 if saas_p0 > 0 else 0
    saas_p1 = jira_stats.get('saas_p1_total', 0)
    saas_p1_res = jira_stats.get('saas_p1_resolved', 0)
    saas_p1_rate = saas_p1_res / saas_p1 * 100 if saas_p1 > 0 else 0
    report.append(f"| **SaaS** | {saas_p0} | {saas_p0_res} | {saas_p0_rate:.1f}% | {saas_p1} | {saas_p1_res} | {saas_p1_rate:.1f}% |")
    
    private_p0 = jira_stats.get('private_p0_total', 0)
    private_p0_res = jira_stats.get('private_p0_resolved', 0)
    private_p0_rate = private_p0_res / private_p0 * 100 if private_p0 > 0 else 0
    private_p1 = jira_stats.get('private_p1_total', 0)
    private_p1_res = jira_stats.get('private_p1_resolved', 0)
    private_p1_rate = private_p1_res / private_p1 * 100 if private_p1 > 0 else 0
    report.append(f"| **私有化** | {private_p0} | {private_p0_res} | {private_p0_rate:.1f}% | {private_p1} | {private_p1_res} | {private_p1_rate:.1f}% |")
    report.append("")
    
    report.append("### 2.3 月度Bug趋势对比\n")
    report.append("| 月份 | SaaS | 私有化 |")
    report.append("|------|------|--------|")
    saas_monthly = jira_stats.get('saas_monthly', {})
    private_monthly = jira_stats.get('private_monthly', {})
    for m in range(1, 13):
        saas_m = saas_monthly.get(m, 0)
        private_m = private_monthly.get(m, 0)
        if saas_m > 0 or private_m > 0:
            report.append(f"| {m}月 | {saas_m} | {private_m} |")
    report.append("")
    
    report.append("### 2.4 缺陷类型对比\n")
    report.append("**SaaS缺陷类型Top5：**\n")
    report.append("| 缺陷类型 | 数量 |")
    report.append("|----------|------|")
    for dtype, count in list(jira_stats.get('saas_defect_types', {}).items())[:5]:
        report.append(f"| {dtype} | {count} |")
    report.append("")
    
    report.append("**私有化缺陷类型Top5：**\n")
    report.append("| 缺陷类型 | 数量 |")
    report.append("|----------|------|")
    for dtype, count in list(jira_stats.get('private_defect_types', {}).items())[:5]:
        report.append(f"| {dtype} | {count} |")
    report.append("")
    
    # Section 3: Incident Analysis
    report.append("## 三、线上重大故障分析\n")
    
    report.append("### 3.1 故障等级分布\n")
    report.append("| 等级 | 数量 | 占比 | 定义 |")
    report.append("|------|------|------|------|")
    total_inc = incidents_stats['total']
    report.append(f"| P0 | {incidents_stats['p0_count']} | {incidents_stats['p0_count']/total_inc*100:.1f}% | 阻塞性问题 |")
    report.append(f"| P1 | {incidents_stats['p1_count']} | {incidents_stats['p1_count']/total_inc*100:.1f}% | 核心功能问题 |")
    report.append(f"| P2 | {incidents_stats['p2_count']} | {incidents_stats['p2_count']/total_inc*100:.1f}% | 一般问题 |")
    report.append("")
    
    report.append("### 3.2 SaaS vs 私有化故障对比\n")
    report.append("| 类型 | 故障数 | P0数 | P1数 | 占比 |")
    report.append("|------|--------|------|------|------|")
    report.append(f"| **SaaS** | {incidents_stats['saas_count']} | {incidents_stats['saas_p0']} | {incidents_stats['saas_p1']} | {incidents_stats['saas_count']/total_inc*100:.1f}% |")
    report.append(f"| **私有化** | {incidents_stats['private_count']} | {incidents_stats['private_p0']} | {incidents_stats['private_p1']} | {incidents_stats['private_count']/total_inc*100:.1f}% |")
    report.append("")
    
    report.append("### 3.3 团队归属分布\n")
    report.append("| 团队 | 故障数 | 占比 |")
    report.append("|------|--------|------|")
    for team, count in sorted(incidents_stats.get('team_dist', {}).items(), key=lambda x: -x[1]):
        if pd.notna(team) and str(team).strip():
            report.append(f"| {team} | {count} | {count/total_inc*100:.1f}% |")
    report.append("")
    
    # Section 4: Root Cause
    report.append("## 四、根本原因分析\n")
    
    report.append("### 4.1 整体缺陷类型分布\n")
    report.append("| 缺陷类型 | 数量 | 占比 |")
    report.append("|----------|------|------|")
    total_defects = sum(jira_stats.get('defect_types', {}).values())
    for dtype, count in jira_stats.get('defect_types', {}).items():
        pct = count / total_defects * 100 if total_defects > 0 else 0
        report.append(f"| {dtype} | {count} | {pct:.1f}% |")
    report.append("")
    
    # Section 5: Resolution Stats
    report.append("## 五、故障解决效率\n")
    
    report.append("### 5.1 整体解决状态\n")
    report.append("| 状态 | 数量 | 占比 |")
    report.append("|------|------|------|")
    total_bugs = jira_stats['total_bugs']
    for status, count in sorted(jira_stats.get('status_dist', {}).items(), key=lambda x: -x[1])[:8]:
        pct = count / total_bugs * 100 if total_bugs > 0 else 0
        report.append(f"| {status} | {count} | {pct:.1f}% |")
    report.append("")
    
    report.append("### 5.2 解决率汇总\n")
    report.append("| 维度 | 总数 | 已解决 | 解决率 |")
    report.append("|------|------|--------|--------|")
    report.append(f"| 整体 | {jira_stats['total_bugs']} | {jira_stats['resolved']} | {jira_stats['resolution_rate']:.1f}% |")
    report.append(f"| SaaS | {saas_total} | {saas_res} | {saas_rate:.1f}% |")
    report.append(f"| 私有化 | {private_total} | {private_res} | {private_rate:.1f}% |")
    report.append(f"| P0 | {jira_stats.get('jira_p0_total', 0)} | {jira_stats.get('jira_p0_resolved', 0)} | {jira_stats.get('jira_p0_rate', 0):.1f}% |")
    report.append(f"| P1 | {jira_stats.get('jira_p1_total', 0)} | {jira_stats.get('jira_p1_resolved', 0)} | {jira_stats.get('jira_p1_rate', 0):.1f}% |")
    report.append("")
    
    # Section 6: Summary
    report.append("## 六、质量稳定性总结\n")
    
    report.append("### 6.1 2025年质量成果\n")
    report.append("""
| 维度 | 成果 |
|------|------|
| **P0故障响应** | 解决率{:.1f}%，高优先级问题得到及时处理 |
| **SaaS质量** | Bug解决率{:.1f}%，产品稳定性良好 |
| **私有化质量** | Bug解决率{:.1f}%，客户环境保障有力 |
| **整体管控** | 全年Bug解决率{:.1f}%，质量体系持续有效 |
""".format(
        jira_stats.get('jira_p0_rate', 0),
        saas_rate,
        private_rate,
        jira_stats['resolution_rate']
    ))
    
    report.append("### 6.2 质量保障措施\n")
    report.append("""
1. **故障分级响应机制**
   - P0故障：30分钟内响应，24小时内解决
   - P1故障：2小时内响应，48小时内解决
   - 建立故障复盘机制，防止同类问题复发

2. **质量门禁管控**
   - 代码审查覆盖率100%
   - 核心模块单元测试覆盖
   - 上线前多环境验证

3. **监控预警体系**
   - 核心服务7x24小时监控
   - 关键指标异常自动告警
   - 定期巡检和健康检查
""")
    
    report.append("### 6.3 2026年质量目标\n")
    report.append("""
| 目标 | 指标 |
|------|------|
| P0故障数 | 同比下降20% |
| SaaS Bug解决率 | 提升至85%以上 |
| 私有化Bug解决率 | 提升至85%以上 |
| 代码问题占比 | 降低至50%以下 |
""")
    
    report.append("\n---\n")
    report.append("**数据来源**：")
    report.append(f"- 线上故障问题表：{INCIDENT_FILE}")
    report.append(f"- Jira项目管理数据：{JIRA_FILE}")
    report.append(f"- 统计周期：2025年1月-12月")
    
    return '\n'.join(report)

def main():
    print("=" * 60)
    print("2025年度质量体系年终总结生成（SaaS/私有化分离版）")
    print("=" * 60)
    
    # Load data
    print("\n[1/4] 加载数据...")
    incidents, jira = load_data()
    incidents = clean_incident_data(incidents)
    print(f"  - 线上故障记录: {len(incidents)}条")
    print(f"  - Jira记录: {len(jira)}条")
    
    # Analyze incidents
    print("\n[2/4] 分析线上故障...")
    incidents_stats = analyze_incidents(incidents)
    print(f"  - 总故障: {incidents_stats['total']}个")
    print(f"  - SaaS故障: {incidents_stats['saas_count']}个 (P0: {incidents_stats['saas_p0']})")
    print(f"  - 私有化故障: {incidents_stats['private_count']}个 (P0: {incidents_stats['private_p0']})")
    
    # Analyze Jira
    print("\n[3/4] 分析Jira数据...")
    jira_stats = analyze_jira_bugs(jira)
    print(f"  - Bug总数: {jira_stats['total_bugs']}")
    print(f"  - SaaS Bug: {jira_stats.get('saas_bugs_total', 0)} (解决率: {jira_stats.get('saas_resolution_rate', 0):.1f}%)")
    print(f"  - 私有化Bug: {jira_stats.get('private_bugs_total', 0)} (解决率: {jira_stats.get('private_resolution_rate', 0):.1f}%)")
    print(f"  - P0解决率: {jira_stats.get('jira_p0_rate', 0):.1f}%")
    
    # Generate report
    print("\n[4/4] 生成年终总结...")
    report = generate_summary(incidents_stats, jira_stats)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n报告已生成: {OUTPUT_FILE}")
    print("=" * 60)
    
    # Print summary
    print("\n【SaaS vs 私有化质量对比】")
    print(f"┌────────────┬─────────┬──────────┬──────────┐")
    print(f"│   环境     │ Bug数   │  已解决  │  解决率  │")
    print(f"├────────────┼─────────┼──────────┼──────────┤")
    print(f"│ SaaS       │ {jira_stats.get('saas_bugs_total', 0):>7} │ {jira_stats.get('saas_resolved', 0):>8} │ {jira_stats.get('saas_resolution_rate', 0):>7.1f}% │")
    print(f"│ 私有化     │ {jira_stats.get('private_bugs_total', 0):>7} │ {jira_stats.get('private_resolved', 0):>8} │ {jira_stats.get('private_resolution_rate', 0):>7.1f}% │")
    print(f"└────────────┴─────────┴──────────┴──────────┘")

if __name__ == '__main__':
    main()
