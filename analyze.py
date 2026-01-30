#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTO Report Analysis - Interactive CLI Tool
Usage: python analyze.py [command] [args]

Commands:
  summary                  - Generate executive summary
  client <name>            - Search by client name
  search <keyword>         - Search by keyword
  incidents                - Show incident analysis
  products                 - Show product line progress
  export                   - Export full analysis to JSON
"""

import sys
from cto_weekly_report_analyzer import CTOWeeklyReportAnalyzer
from pathlib import Path


def load_analyzer():
    """Load analyzer with all available data."""
    analyzer = CTOWeeklyReportAnalyzer()
    data_dir = Path(__file__).parent / "2025"
    
    if data_dir.exists():
        for md_file in sorted(data_dir.glob("*.md")):
            analyzer.load_markdown_file(str(md_file))
    
    return analyzer


def cmd_summary(analyzer):
    """Print executive summary."""
    print(analyzer.get_executive_summary())


def cmd_client(analyzer, client_name):
    """Search by client name."""
    results = analyzer.search_by_client(client_name)
    print(f"\n=== Search Results for Client: {client_name} ===\n")
    
    if not results:
        print("No results found.")
        return
    
    for r in results:
        print(f"\n📅 Date: {r['date']}")
        if r['incidents']:
            print("  ⚠️ Incidents:")
            for inc in r['incidents'][:3]:
                print(f"    • {inc[:80]}...")
        print("  📝 Related Content:")
        for content in r['relevant_content'][:5]:
            print(f"    • {content[:80]}...")


def cmd_search(analyzer, keyword):
    """Search by keyword."""
    results = analyzer.search_by_keyword(keyword)
    print(f"\n=== Search Results for: {keyword} ===\n")
    
    if not results:
        print("No results found.")
        return
    
    for r in results:
        print(f"\n📅 Date: {r['date']}")
        for match in r['matches'][:5]:
            print(f"  • {match[:100]}...")


def cmd_incidents(analyzer):
    """Show incident analysis."""
    incidents = analyzer.analyze_incidents()
    
    print("\n=== INCIDENT ANALYSIS ===\n")
    print(f"Total Incidents: {incidents['total_incidents']}")
    
    print("\n📊 Top Clients by Incidents:")
    for client, count in list(incidents['client_incidents'].items())[:10]:
        bar = "█" * min(count, 20)
        print(f"  {client}: {bar} ({count})")
    
    print("\n📅 Monthly Distribution:")
    for month, count in incidents['monthly_distribution'].items():
        bar = "█" * min(count // 2, 30)
        print(f"  {month}: {bar} ({count})")
    
    print("\n🔴 Recent Incidents:")
    for inc in incidents['recent_incidents'][-10:]:
        print(f"  [{inc['date']}] {inc['description'][:70]}...")


def cmd_products(analyzer):
    """Show product line progress."""
    products = analyzer.analyze_product_progress()
    
    print("\n=== PRODUCT LINE PROGRESS ===\n")
    for product, stats in sorted(products.items(), key=lambda x: x[1]['weekly_mentions'], reverse=True):
        level = stats['activity_level']
        icon = "🔥" if level == "high" else "📈" if level == "medium" else "📊"
        print(f"\n{icon} {product}")
        print(f"   Activity Level: {level} ({stats['weekly_mentions']} weeks)")
        if stats['recent_activities']:
            print("   Recent Activities:")
            for date, activity in stats['recent_activities'][-3:]:
                print(f"     [{date}] {activity[:60]}...")


def cmd_export(analyzer):
    """Export analysis to JSON."""
    output_path = Path(__file__).parent / "weekly_report_analysis.json"
    analyzer.export_analysis(str(output_path))


def print_help():
    """Print help message."""
    print(__doc__)
    print("\nExamples:")
    print("  python analyze.py summary           # Executive summary")
    print("  python analyze.py client 滴滴       # Search for 滴滴")
    print("  python analyze.py search 故障       # Search for incidents")
    print("  python analyze.py incidents         # Incident analysis")
    print("  python analyze.py products          # Product progress")


def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    cmd = sys.argv[1].lower()
    analyzer = load_analyzer()
    
    if cmd == "summary":
        cmd_summary(analyzer)
    elif cmd == "client" and len(sys.argv) > 2:
        cmd_client(analyzer, sys.argv[2])
    elif cmd == "search" and len(sys.argv) > 2:
        cmd_search(analyzer, sys.argv[2])
    elif cmd == "incidents":
        cmd_incidents(analyzer)
    elif cmd == "products":
        cmd_products(analyzer)
    elif cmd == "export":
        cmd_export(analyzer)
    else:
        print_help()


if __name__ == "__main__":
    main()
