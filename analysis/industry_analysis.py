#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
21-23年客户行业分析脚本
生成行业占比分析报告（HTML格式）
"""

import csv
import json
from collections import Counter, defaultdict

# ============================================================
# 行业清洗映射表 - 将杂乱的行业名归并为标准类别
# ============================================================
INDUSTRY_MAP = {
    # 互联网/软件/游戏
    '互联网/游戏/软件-二级行业': '互联网/软件/游戏',
    '互联网/游戏/软件-二级行业软件和信息技术服务': '互联网/软件/游戏',
    '互联网/游戏/软件-二级行业互联网/游戏/软件-二级行业': '互联网/软件/游戏',
    '软件和信息技术服务': '互联网/软件/游戏',
    '游戏行业': '互联网/软件/游戏',
    '其他软件和信息技术服务': '互联网/软件/游戏',

    # 零售/电商
    '零售/电商': '零售/电商',
    '消费/生产/零售': '零售/电商',
    '消费/生产/零售零售/电商': '零售/电商',
    '消费/生产/零售消费/生产/零售': '零售/电商',
    '消费/生产/零售其他': '零售/电商',
    '其他零售/电商': '零售/电商',
    '贸易/交通/物流零售/电商': '零售/电商',

    # 教育/培训
    '教育/培训': '教育/培训',
    '在线教育/培训': '教育/培训',
    '教育/培训在线教育/培训': '教育/培训',
    '教育/培训教育/培训': '教育/培训',
    '公立教育/学校': '教育/培训',
    '其他在线教育/培训': '教育/培训',

    # 广告/传媒/文娱
    '广告/传媒/文体娱乐': '广告/传媒/文娱',
    '文化/体育和娱乐业': '广告/传媒/文娱',
    '广告/公关/营销': '广告/传媒/文娱',
    '新媒体/媒体/自媒体': '广告/传媒/文娱',
    '广告/传媒/文体娱乐广告/传媒/文体娱乐': '广告/传媒/文娱',
    '广告/传媒/文体娱乐文化/体育和娱乐业': '广告/传媒/文娱',
    '文化/体育和娱乐业文化/体育和娱乐业': '广告/传媒/文娱',

    # 贸易/物流
    '贸易/交通/物流': '贸易/物流',
    '国际/国内贸易': '贸易/物流',
    '交通运输/仓储和物流业': '贸易/物流',
    '贸易/交通/物流国际/国内贸易': '贸易/物流',
    '贸易/交通/物流贸易/交通/物流': '贸易/物流',

    # 制造业
    '传统制造业': '制造业',
    '创新/高端制造业': '制造业',
    '汽车/机械/重工': '制造业',

    # 金融
    '金融/保险/证券/投资': '金融',
    '金融业': '金融',

    # 服务业
    '服务/外包/中介': '服务业',
    '餐饮/住宿': '服务业',

    # 电子/通信/硬件
    '电子/通信/硬件': '电子/通信/硬件',

    # 房地产/建筑
    '房地产/建筑/物业': '房地产/建筑',
    '房地产业及建筑': '房地产/建筑',
    '工程/基建': '房地产/建筑',

    # 医疗/制药
    '制药/医疗': '医疗/制药',
    '医疗机构': '医疗/制药',
    '生物/制药': '医疗/制药',

    # 能源
    '能源化工/环保': '能源/化工',

    # 公益/社团
    '公益组织/社团': '公益/社团',
    '公益组织': '公益/社团',

    # 政府/事业单位
    '政府机关/事业单位': '政府/事业单位',
    '政府/事业单位': '政府/事业单位',

    # 其他
    '其他': '其他',
    '其他其他': '其他',
}


def clean_industry(raw):
    """清洗行业名称"""
    raw = raw.strip()
    if not raw:
        return '未知'
    if raw in INDUSTRY_MAP:
        return INDUSTRY_MAP[raw]
    # 尝试模糊匹配
    for key, val in INDUSTRY_MAP.items():
        if key in raw or raw in key:
            return val
    return '其他'


def parse_year(date_str):
    """从合同确认时间中提取年份"""
    date_str = date_str.strip()
    if not date_str:
        return None
    try:
        return int(date_str.split('/')[0])
    except:
        return None


def load_data(filepath):
    """加载CSV数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)


def analyze(rows):
    """核心分析逻辑"""
    results = {}

    # --- 总体行业分布 ---
    all_industries = []
    year_industries = defaultdict(list)
    year_biz_type = defaultdict(lambda: defaultdict(int))
    province_data = defaultdict(int)
    size_data = defaultdict(int)
    source_data = defaultdict(int)

    for r in rows:
        ind = clean_industry(r['行业合并'])
        year = parse_year(r['合同确认时间'])
        biz_type = r['订单业务类型'].strip()
        province = r['所属省份'].strip()
        size = r['企业人数'].strip()
        source = r['来源'].strip()

        all_industries.append(ind)

        if year:
            year_industries[year].append(ind)
            if biz_type:
                year_biz_type[year][biz_type] += 1

        if province:
            province_data[province] += 1
        if size:
            size_data[size] += 1
        if source:
            source_data[source] += 1

    # 总体行业排名
    total_count = len(all_industries)
    ind_counter = Counter(all_industries)
    industry_ranking = []
    for name, count in ind_counter.most_common():
        industry_ranking.append({
            'name': name,
            'count': count,
            'pct': round(count / total_count * 100, 2)
        })
    results['total_orders'] = total_count
    results['industry_ranking'] = industry_ranking

    # 逐年行业分布
    yearly = {}
    for year in sorted(year_industries.keys()):
        items = year_industries[year]
        yc = Counter(items)
        ytotal = len(items)
        ranking = []
        for name, count in yc.most_common():
            ranking.append({
                'name': name,
                'count': count,
                'pct': round(count / ytotal * 100, 2)
            })
        yearly[year] = {
            'total': ytotal,
            'ranking': ranking
        }
    results['yearly'] = yearly

    # 年度趋势（Top 行业逐年变化）
    top_industries = [x['name'] for x in industry_ranking[:10]]
    trend_data = {}
    for ind in top_industries:
        trend_data[ind] = {}
        for year in sorted(year_industries.keys()):
            yc = Counter(year_industries[year])
            ytotal = len(year_industries[year])
            trend_data[ind][year] = round(yc.get(ind, 0) / ytotal * 100, 2)
    results['trend'] = trend_data
    results['years'] = sorted(year_industries.keys())

    # 业务类型
    biz_type_summary = {}
    for year in sorted(year_biz_type.keys()):
        biz_type_summary[year] = dict(year_biz_type[year])
    results['biz_type'] = biz_type_summary

    # 省份 Top 15
    province_ranking = sorted(province_data.items(), key=lambda x: -x[1])[:15]
    results['province_ranking'] = [{'name': k, 'count': v} for k, v in province_ranking]

    # 企业规模
    size_order = ['1-15人', '16-50人', '51-100人', '101-200人', '201-500人', '501-1000人', '1001-3000人', '3000人以上']
    size_ranking = []
    for s in size_order:
        if s in size_data:
            size_ranking.append({'name': s, 'count': size_data[s]})
    # 加入不在预定顺序中的
    for s, c in size_data.items():
        if s not in size_order:
            size_ranking.append({'name': s, 'count': c})
    results['size_ranking'] = size_ranking

    # 来源 Top 10
    source_ranking = sorted(source_data.items(), key=lambda x: -x[1])[:10]
    results['source_ranking'] = [{'name': k, 'count': v} for k, v in source_ranking]

    # 年度增长率
    year_totals = {}
    for year in sorted(year_industries.keys()):
        year_totals[year] = len(year_industries[year])
    results['year_totals'] = year_totals

    # 行业集中度 (CR3, CR5, CR10)
    top3 = sum(x['pct'] for x in industry_ranking[:3])
    top5 = sum(x['pct'] for x in industry_ranking[:5])
    top10 = sum(x['pct'] for x in industry_ranking[:10])
    results['concentration'] = {'CR3': round(top3, 2), 'CR5': round(top5, 2), 'CR10': round(top10, 2)}

    # 逐年行业集中度
    yearly_concentration = {}
    for year in sorted(yearly.keys()):
        r = yearly[year]['ranking']
        yearly_concentration[year] = {
            'CR3': round(sum(x['pct'] for x in r[:3]), 2),
            'CR5': round(sum(x['pct'] for x in r[:5]), 2),
            'CR10': round(sum(x['pct'] for x in r[:10]), 2),
        }
    results['yearly_concentration'] = yearly_concentration

    return results


def main():
    rows = load_data('analysis/21-23年客户数据.csv')
    results = analyze(rows)

    # 输出 JSON 供 HTML 使用
    with open('analysis/analysis_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"分析完成! 共处理 {results['total_orders']} 条订单数据")
    print(f"行业分类: {len(results['industry_ranking'])} 个")
    print(f"数据已输出到 analysis/analysis_data.json")


if __name__ == '__main__':
    main()
