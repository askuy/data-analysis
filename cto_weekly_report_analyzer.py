#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTO Weekly Report Analyzer
A skill for analyzing engineering weekly reports to extract key insights.

Features:
- Parse markdown format weekly reports
- Extract key metrics: clients, projects, incidents, personnel changes
- Generate statistical analysis and trend reports
- Support incremental file addition
"""

import re
import os
from collections import defaultdict
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path
import json


@dataclass
class WeeklyEntry:
    """Represents a single weekly report entry."""
    date: str
    raw_content: str
    privatization: List[str] = field(default_factory=list)
    incidents: List[str] = field(default_factory=list)
    products: Dict[str, List[str]] = field(default_factory=dict)
    personnel: List[str] = field(default_factory=list)
    clients: Set[str] = field(default_factory=set)
    risks: List[str] = field(default_factory=list)


class CTOWeeklyReportAnalyzer:
    """
    CTO Weekly Report Analysis Tool.
    
    Designed for CTOs to quickly understand:
    1. Privatization project status and client health
    2. Product line progress (Drive, App Tables, Light Docs, Pro Docs)
    3. Incident patterns and system stability
    4. Team dynamics and personnel changes
    5. Cost optimization and resource allocation
    6. Risk identification and mitigation
    """
    
    # Known client patterns for extraction
    KNOWN_CLIENTS = [
        "滴滴", "OPPO", "oppo", "好未来", "京东", "微众银行", "招商金科", "格力",
        "TCL", "新华三", "长亮科技", "云鲸智能", "作业帮", "边锋游戏", "唯品会",
        "网易", "米哈游", "小红书", "百度", "喜马拉雅", "广东电信", "中信建投",
        "天翼云盘", "中电量子", "苏州公安", "苏州国发", "猿辅导", "乐信",
        "九江银行", "招商基金", "跨越速运", "中广核", "华为", "博纳", "中船",
        "海信", "蓝信", "卡斯柯", "宜宾辰海", "武汉铁路局", "四川准则",
    ]
    
    # Product lines to track
    PRODUCT_LINES = [
        "Drive", "应用表格", "轻文档", "专业文档", "表格计算", "极速SDK",
        "流程图", "AI", "协同编辑", "导入导出"
    ]
    
    # Incident severity keywords
    INCIDENT_KEYWORDS = ["故障", "问题", "bug", "Bug", "BUG", "异常", "失败", "报错", "P0", "P1", "P2"]
    
    def __init__(self):
        self.entries: List[WeeklyEntry] = []
        self.all_clients: Set[str] = set()
        self.client_mentions: Dict[str, int] = defaultdict(int)
        self.incident_count_by_month: Dict[str, int] = defaultdict(int)
        self.product_progress: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        
    def load_markdown_file(self, filepath: str) -> None:
        """Load and parse a markdown weekly report file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by date headers (## YYYYMMDD or # YYYYMMDD)
        date_pattern = r'^[#]{1,2}\s*(\d{8})'
        sections = re.split(date_pattern, content, flags=re.MULTILINE)
        
        # Process each section
        i = 1
        while i < len(sections) - 1:
            date_str = sections[i]
            section_content = sections[i + 1] if i + 1 < len(sections) else ""
            
            entry = self._parse_section(date_str, section_content)
            self.entries.append(entry)
            
            # Update global stats
            self.all_clients.update(entry.clients)
            for client in entry.clients:
                self.client_mentions[client] += 1
                
            i += 2
            
        print(f"Loaded {len(self.entries)} weekly entries from {filepath}")
    
    def _parse_section(self, date_str: str, content: str) -> WeeklyEntry:
        """Parse a single weekly section."""
        entry = WeeklyEntry(date=date_str, raw_content=content)
        
        # Extract clients mentioned
        for client in self.KNOWN_CLIENTS:
            if client in content:
                entry.clients.add(client)
        
        # Extract incidents
        for line in content.split('\n'):
            for keyword in self.INCIDENT_KEYWORDS:
                if keyword in line and len(line.strip()) > 5:
                    entry.incidents.append(line.strip())
                    break
        
        # Extract product line mentions
        for product in self.PRODUCT_LINES:
            if product in content:
                # Find relevant lines
                for line in content.split('\n'):
                    if product in line and len(line.strip()) > 5:
                        if product not in entry.products:
                            entry.products[product] = []
                        entry.products[product].append(line.strip())
        
        # Extract personnel changes
        personnel_keywords = ["人员", "离职", "入职", "调整", "组长", "负责人"]
        for line in content.split('\n'):
            for keyword in personnel_keywords:
                if keyword in line:
                    entry.personnel.append(line.strip())
                    break
        
        # Extract privatization items
        if "私有化" in content:
            priv_section = self._extract_section(content, "私有化")
            entry.privatization = [l.strip() for l in priv_section.split('\n') if l.strip()]
        
        return entry
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a named section from content."""
        pattern = rf'\*\s*{section_name}.*?(?=\*\s*[A-Za-z\u4e00-\u9fff]|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(0) if match else ""
    
    def analyze_client_health(self) -> Dict[str, Dict]:
        """Analyze client health based on mention frequency and incident patterns."""
        client_health = {}
        
        for client in self.all_clients:
            mentions = self.client_mentions[client]
            incidents = 0
            
            for entry in self.entries:
                if client in entry.clients:
                    for incident in entry.incidents:
                        if client in incident:
                            incidents += 1
            
            # Health score: higher mentions with lower incident ratio is better
            incident_ratio = incidents / max(mentions, 1)
            health_score = "healthy" if incident_ratio < 0.2 else "attention" if incident_ratio < 0.5 else "critical"
            
            client_health[client] = {
                "total_mentions": mentions,
                "incident_count": incidents,
                "incident_ratio": round(incident_ratio, 2),
                "health_status": health_score
            }
        
        return dict(sorted(client_health.items(), key=lambda x: x[1]["total_mentions"], reverse=True))
    
    def analyze_product_progress(self) -> Dict[str, Dict]:
        """Analyze product line development progress."""
        product_stats = {}
        
        for product in self.PRODUCT_LINES:
            mentions = 0
            activities = []
            
            for entry in self.entries:
                if product in entry.products:
                    mentions += 1
                    activities.extend([(entry.date, a) for a in entry.products[product][:3]])
            
            product_stats[product] = {
                "weekly_mentions": mentions,
                "activity_level": "high" if mentions > 20 else "medium" if mentions > 10 else "low",
                "recent_activities": activities[-5:] if activities else []
            }
        
        return product_stats
    
    def analyze_incidents(self) -> Dict[str, any]:
        """Analyze incident patterns and trends."""
        all_incidents = []
        monthly_incidents = defaultdict(int)
        client_incidents = defaultdict(int)
        
        for entry in self.entries:
            year = entry.date[:4]
            month = entry.date[4:6]
            month_key = f"{year}-{month}"
            
            for incident in entry.incidents:
                all_incidents.append({
                    "date": entry.date,
                    "description": incident[:100]
                })
                monthly_incidents[month_key] += 1
                
                # Attribute to client if mentioned
                for client in entry.clients:
                    if client in incident:
                        client_incidents[client] += 1
        
        return {
            "total_incidents": len(all_incidents),
            "monthly_distribution": dict(sorted(monthly_incidents.items())),
            "client_incidents": dict(sorted(client_incidents.items(), key=lambda x: x[1], reverse=True)[:10]),
            "recent_incidents": all_incidents[-10:]
        }
    
    def analyze_personnel(self) -> Dict[str, any]:
        """Analyze personnel changes and team dynamics."""
        all_personnel_events = []
        
        for entry in self.entries:
            for event in entry.personnel:
                if event and len(event) > 3:
                    all_personnel_events.append({
                        "date": entry.date,
                        "event": event
                    })
        
        return {
            "total_events": len(all_personnel_events),
            "events": all_personnel_events
        }
    
    def get_executive_summary(self) -> str:
        """Generate an executive summary for CTO review."""
        client_health = self.analyze_client_health()
        product_progress = self.analyze_product_progress()
        incidents = self.analyze_incidents()
        personnel = self.analyze_personnel()
        
        # Find clients needing attention
        attention_clients = [c for c, h in client_health.items() if h["health_status"] in ["attention", "critical"]]
        top_clients = list(client_health.keys())[:10]
        
        # Find most active products
        active_products = sorted(product_progress.items(), key=lambda x: x[1]["weekly_mentions"], reverse=True)[:5]
        
        summary = f"""
================================================================================
                    CTO WEEKLY REPORT ANALYSIS SUMMARY
================================================================================

📊 OVERVIEW
-----------
• Analysis Period: {self.entries[-1].date if self.entries else 'N/A'} - {self.entries[0].date if self.entries else 'N/A'}
• Total Weekly Reports Analyzed: {len(self.entries)}
• Total Clients Tracked: {len(self.all_clients)}
• Total Incidents Recorded: {incidents['total_incidents']}

👥 TOP 10 CLIENTS BY ENGAGEMENT
-------------------------------
{self._format_client_list(top_clients, client_health)}

⚠️  CLIENTS REQUIRING ATTENTION
-------------------------------
{self._format_attention_clients(attention_clients, client_health)}

🚀 PRODUCT LINE ACTIVITY
------------------------
{self._format_product_activity(active_products)}

📉 INCIDENT TRENDS (Monthly)
----------------------------
{self._format_monthly_incidents(incidents['monthly_distribution'])}

👔 PERSONNEL CHANGES
--------------------
Total Personnel Events: {personnel['total_events']}
Recent Events:
{self._format_personnel_events(personnel['events'][-5:])}

================================================================================
"""
        return summary
    
    def _format_client_list(self, clients: List[str], health: Dict) -> str:
        """Format client list for summary."""
        lines = []
        for i, client in enumerate(clients, 1):
            h = health.get(client, {})
            status_icon = "✅" if h.get("health_status") == "healthy" else "⚠️" if h.get("health_status") == "attention" else "🔴"
            lines.append(f"  {i:2}. {status_icon} {client}: {h.get('total_mentions', 0)} mentions, {h.get('incident_count', 0)} incidents")
        return '\n'.join(lines) if lines else "  No clients found"
    
    def _format_attention_clients(self, clients: List[str], health: Dict) -> str:
        """Format attention-needed clients."""
        if not clients:
            return "  ✅ All clients are in healthy status"
        lines = []
        for client in clients[:5]:
            h = health.get(client, {})
            lines.append(f"  • {client}: incident ratio {h.get('incident_ratio', 0):.0%}")
        return '\n'.join(lines)
    
    def _format_product_activity(self, products: List) -> str:
        """Format product activity summary."""
        lines = []
        for product, stats in products:
            icon = "🔥" if stats["activity_level"] == "high" else "📈" if stats["activity_level"] == "medium" else "📊"
            lines.append(f"  {icon} {product}: {stats['weekly_mentions']} weeks active ({stats['activity_level']})")
        return '\n'.join(lines) if lines else "  No product activity tracked"
    
    def _format_monthly_incidents(self, monthly: Dict) -> str:
        """Format monthly incident distribution."""
        lines = []
        for month, count in list(monthly.items())[-6:]:
            bar = "█" * min(count // 2, 20)
            lines.append(f"  {month}: {bar} ({count})")
        return '\n'.join(lines) if lines else "  No incidents recorded"
    
    def _format_personnel_events(self, events: List) -> str:
        """Format personnel events."""
        lines = []
        for event in events:
            lines.append(f"  • [{event['date']}] {event['event'][:60]}...")
        return '\n'.join(lines) if lines else "  No recent personnel events"
    
    def search_by_client(self, client_name: str) -> List[Dict]:
        """Search all entries related to a specific client."""
        results = []
        for entry in self.entries:
            if client_name in entry.raw_content:
                # Extract relevant lines
                relevant_lines = []
                for line in entry.raw_content.split('\n'):
                    if client_name in line:
                        relevant_lines.append(line.strip())
                
                results.append({
                    "date": entry.date,
                    "incidents": [i for i in entry.incidents if client_name in i],
                    "relevant_content": relevant_lines[:10]
                })
        return results
    
    def search_by_keyword(self, keyword: str) -> List[Dict]:
        """Search all entries containing a keyword."""
        results = []
        for entry in self.entries:
            if keyword in entry.raw_content:
                relevant_lines = []
                for line in entry.raw_content.split('\n'):
                    if keyword in line:
                        relevant_lines.append(line.strip())
                
                results.append({
                    "date": entry.date,
                    "matches": relevant_lines[:10]
                })
        return results
    
    def export_analysis(self, output_path: str) -> None:
        """Export full analysis to JSON file."""
        analysis = {
            "generated_at": datetime.now().isoformat(),
            "total_entries": len(self.entries),
            "date_range": {
                "start": self.entries[-1].date if self.entries else None,
                "end": self.entries[0].date if self.entries else None
            },
            "client_health": self.analyze_client_health(),
            "product_progress": self.analyze_product_progress(),
            "incidents": self.analyze_incidents(),
            "personnel": self.analyze_personnel()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        print(f"Analysis exported to {output_path}")


def main():
    """Main entry point for the analyzer."""
    analyzer = CTOWeeklyReportAnalyzer()
    
    # Load all markdown files from the 2025 directory
    data_dir = Path(__file__).parent / "2025"
    
    if data_dir.exists():
        for md_file in sorted(data_dir.glob("*.md")):
            print(f"Loading: {md_file}")
            analyzer.load_markdown_file(str(md_file))
    
    # Generate and print executive summary
    print(analyzer.get_executive_summary())
    
    # Export detailed analysis
    output_path = Path(__file__).parent / "weekly_report_analysis.json"
    analyzer.export_analysis(str(output_path))
    
    return analyzer


if __name__ == "__main__":
    analyzer = main()
