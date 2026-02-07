#!/usr/bin/env python3
"""
Test visual collection with realistic mock data
Generates fake data records for testing the pipeline
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import random
import time
from datetime import datetime, timedelta
from src.collectors.data_sources import DataRecord
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Realistic record data
RECORD_TYPES = {
    'Stock Goes Up': {
        'titles': [
            'Company made more money than expected this quarter',
            'Sales were higher than what analysts predicted',
            'Profits beat expectations thanks to strong demand',
            'Company reported better-than-expected results'
        ],
        'severity': ['high', 'medium'],
        'bounties': (500, 3000),
        'category_id': 'CAT-001'
    },
    'Stock Goes Down': {
        'titles': [
            'Company made less money than expected this quarter',
            'Sales came in lower than predicted',
            'Profits missed expectations due to rising costs',
            'Company reported worse-than-expected results'
        ],
        'severity': ['critical', 'high'],
        'bounties': (1000, 5000),
        'category_id': 'CAT-002'
    },
    'Good Forecast': {
        'titles': [
            'Company says next quarter will be better than expected',
            'Management raised their prediction for future sales',
            'Company expects to grow faster than originally planned',
            'Outlook improved — company is more confident about the future'
        ],
        'severity': ['high', 'medium'],
        'bounties': (800, 4000),
        'category_id': 'CAT-003'
    },
    'Bad Forecast': {
        'titles': [
            'Company says next quarter will be worse than expected',
            'Management lowered their prediction for future sales',
            'Company expects slower growth going forward',
            'Outlook worsened — company is less confident about the future'
        ],
        'severity': ['critical', 'high'],
        'bounties': (1500, 6000),
        'category_id': 'CAT-004'
    },
    'Analyst Says Buy': {
        'titles': [
            'Wall Street analyst recommends buying this stock',
            'Analyst raised their price target for the stock',
            'Research firm upgraded the stock to a buy rating',
            'Analyst says the stock is undervalued right now'
        ],
        'severity': ['medium', 'high'],
        'bounties': (300, 2000),
        'category_id': 'CAT-005'
    },
    'Analyst Says Sell': {
        'titles': [
            'Wall Street analyst recommends selling this stock',
            'Analyst lowered their price target for the stock',
            'Research firm downgraded the stock to a sell rating',
            'Analyst says the stock is overvalued right now'
        ],
        'severity': ['critical', 'high'],
        'bounties': (2000, 8000),
        'category_id': 'CAT-006'
    },
    'Pays More Dividends': {
        'titles': [
            'Company is paying shareholders more money per share',
            'Dividend payment increased — good sign for investors',
            'Company announced a special bonus payment to shareholders',
            'Board approved a bigger quarterly payout to investors'
        ],
        'severity': ['medium', 'high'],
        'bounties': (500, 3000),
        'category_id': 'CAT-007'
    },
    'Buying Back Stock': {
        'titles': [
            'Company is spending money to buy back its own shares',
            'New share buyback program announced',
            'Company plans to reduce total shares by repurchasing stock',
            'Board approved billions in stock repurchases'
        ],
        'severity': ['medium', 'low'],
        'bounties': (200, 1500),
        'category_id': 'CAT-008'
    },
    'Company Merger': {
        'titles': [
            'Company is buying another company',
            'Two companies announced they are merging together',
            'Company is selling off part of its business',
            'Takeover offer made at a premium price'
        ],
        'severity': ['critical'],
        'bounties': (5000, 15000),
        'category_id': 'CAT-009'
    },
    'Government Action': {
        'titles': [
            'Government approved the companys new product',
            'Government opened an investigation into the company',
            'New law or regulation affects the companys business',
            'Company disclosed a government inquiry in its filing'
        ],
        'severity': ['critical', 'high'],
        'bounties': (1000, 5000),
        'category_id': 'CAT-010'
    }
}

COMPANIES = [
    {'name': 'Apple', 'domain': 'AAPL', 'program': 'tech'},
    {'name': 'Microsoft', 'domain': 'MSFT', 'program': 'tech'},
    {'name': 'Amazon', 'domain': 'AMZN', 'program': 'tech'},
    {'name': 'Google', 'domain': 'GOOGL', 'program': 'tech'},
    {'name': 'Tesla', 'domain': 'TSLA', 'program': 'auto'},
    {'name': 'Netflix', 'domain': 'NFLX', 'program': 'entertainment'},
    {'name': 'Nike', 'domain': 'NKE', 'program': 'retail'},
    {'name': 'Coca-Cola', 'domain': 'KO', 'program': 'food'},
    {'name': 'Disney', 'domain': 'DIS', 'program': 'entertainment'},
    {'name': 'Walmart', 'domain': 'WMT', 'program': 'retail'}
]

TECH_STACKS = [
    ['Yahoo Finance', 'Python', 'Excel'],
    ['Google Finance', 'Python', 'CSV files'],
    ['News API', 'Python', 'SQLite'],
    ['SEC Filings', 'Python', 'PostgreSQL'],
    ['Stock Screener', 'Python', 'Pandas'],
    ['Financial News', 'Python', 'JSON files'],
]

def generate_mock_report(report_id: int) -> DataRecord:
    """Generate a single mock financial event record"""
    
    # Select random event type
    rec_type = random.choice(list(RECORD_TYPES.keys()))
    rec_data = RECORD_TYPES[rec_type]
    
    # Select random company
    company = random.choice(COMPANIES)
    
    # Select impact level and estimated price move
    severity = random.choice(rec_data['severity'])
    move_min, move_max = rec_data['bounties']
    price_move = random.randint(move_min, move_max)
    
    # Adjust price move based on impact
    if severity == 'critical':
        price_move = int(price_move * 1.5)
    elif severity == 'low':
        price_move = int(price_move * 0.5)
    
    # Generate dates
    days_ago = random.randint(1, 365)
    resolved_date = datetime.now() - timedelta(days=days_ago)
    created_date = resolved_date - timedelta(days=random.randint(1, 30))
    
    # Select title
    title = random.choice(rec_data['titles'])
    
    # Select data sources
    tech_stack = random.choice(TECH_STACKS)
    
    # Market impact score based on severity
    priority_scores = {
        'critical': (9.0, 10.0),
        'high': (7.0, 8.9),
        'medium': (4.0, 6.9),
        'low': (0.1, 3.9)
    }
    priority_min, priority_max = priority_scores[severity]
    priority_score = round(random.uniform(priority_min, priority_max), 1)
    
    sectors = ['Technology', 'Healthcare', 'Financials', 'Consumer', 'Energy', 'Industrials']
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    
    # Create record
    report = DataRecord(
        report_id=f"evt_{report_id}",
        platform='mock',
        target_domain=company['domain'],
        target_company=company['name'],
        target_program=company['program'],
        record_type=rec_type,
        severity=severity,
        priority_score=priority_score,
        technology_stack=tech_stack,
        endpoint=f"/api/v{random.randint(1,2)}/{random.choice(['earnings', 'filings', 'estimates', 'ratings', 'dividends'])}",
        http_method=random.choice(['GET', 'POST']),
        category=random.choice(sectors),
        description=title,
        details=[],
        impact=f"{severity.capitalize()} market impact - {rec_type}",
        remediation=f"Check the {random.choice(quarters)} report and analyst predictions",
        created_date=created_date,
        resolved_date=resolved_date,
        reward_amount=price_move,
        source_quality=random.randint(50, 5000),
        authentication_required=random.choice([True, False]),
        privileges_required=random.choice(['none', 'low', 'high']),
        user_interaction=random.choice([True, False]),
        complexity=random.choice(['low', 'medium', 'high']),
        tags=[],
        domain_category=random.choice(sectors),
        category_id=rec_data['category_id'],
        raw_data={}
    )
    
    return report

def generate_mock_reports(count: int = 50) -> list:
    """Generate multiple mock reports"""
    
    console.print(f"\n[bold cyan]🔧 Generating {count} realistic mock data records...[/bold cyan]\n")
    
    reports = []
    
    for i in range(count):
        report = generate_mock_report(i + 1)
        reports.append(report)
        
        # Show progress
        if (i + 1) % 10 == 0:
            console.print(f"  Generated {i + 1}/{count} reports...")
    
    console.print(f"\n[bold green]✅ Successfully generated {len(reports)} mock reports![/bold green]\n")
    
    return reports

def display_report_summary(reports: list):
    """Display a summary of generated reports"""
    
    # Count by severity
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for report in reports:
        severity_counts[report.severity] = severity_counts.get(report.severity, 0) + 1
    
    # Count by record type
    type_counts = {}
    for report in reports:
        type_counts[report.record_type] = type_counts.get(report.record_type, 0) + 1
    
    # Count by company
    company_counts = {}
    for report in reports:
        company_counts[report.target_company] = company_counts.get(report.target_company, 0) + 1
    
    # Display severity distribution
    console.print("[bold]📊 Severity Distribution:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Severity", style="cyan")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Percentage", justify="right", style="yellow")
    
    total = len(reports)
    for severity in ['critical', 'high', 'medium', 'low']:
        count = severity_counts.get(severity, 0)
        percentage = (count / total * 100) if total > 0 else 0
        table.add_row(severity.capitalize(), str(count), f"{percentage:.1f}%")
    
    console.print(table)
    console.print()
    
    # Display top record types
    console.print("[bold]🎯 Top Record Types:[/bold]")
    top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for rtype, count in top_types:
        console.print(f"  • {rtype}: {count}")
    console.print()
    
    # Display top companies
    console.print("[bold]🏢 Top Companies:[/bold]")
    top_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    for company, count in top_companies:
        console.print(f"  • {company}: {count}")
    console.print()
    
    # Display sample reports
    console.print("[bold]📋 Sample Reports:[/bold]")
    for i, report in enumerate(reports[:5], 1):
        severity_color = {
            'critical': 'red',
            'high': 'yellow',
            'medium': 'blue',
            'low': 'green'
        }.get(report.severity, 'white')
        
        console.print(f"  {i}. [{severity_color}][{report.severity.upper()}][/{severity_color}] "
                     f"{report.record_type} in {report.target_company} - ${report.reward_amount}")
    
    console.print()

def test_with_visual_collector(reports: list):
    """Test the visual collector with mock data"""
    
    console.print("[bold cyan]🚀 Testing Visual Collector with Mock Data...[/bold cyan]\n")
    
    # Import the visual collector
    try:
        from scripts.collect_data_visual import VisualCollector
        
        collector = VisualCollector()
        
        # Simulate streaming reports
        console.print("Simulating live data collection...\n")
        
        for report in reports[:10]:  # Test with first 10
            # Add to collector
            report.source = 'Mock Source'
            report.time = datetime.now().strftime('%H:%M:%S')
            
            collector.collected_reports.append(report.__dict__)
            collector.stats['total'] += 1
            collector.stats['mock'] += 1
            
            if report.severity in collector.stats:
                collector.stats[report.severity] += 1
            
            time.sleep(0.2)  # Simulate delay
        
        console.print(f"[bold green]✅ Visual collector test complete![/bold green]")
        console.print(f"   Processed {len(reports[:10])} mock reports\n")
        
    except ImportError as e:
        console.print(f"[yellow]⚠️  Could not import visual collector: {e}[/yellow]")
        console.print("   This is okay - the mock data is ready to use!\n")

def main():
    """Main entry point"""
    
    console.print()
    console.print(Panel.fit(
        "[bold white]🤖 ML Pipeline Template[/bold white]\n"
        "[cyan]Mock Data Generator[/cyan]\n\n"
        "Generates realistic data records for testing",
        border_style="blue"
    ))
    console.print()
    
    # Generate reports
    reports = generate_mock_reports(count=50)
    
    # Display summary
    display_report_summary(reports)
    
    # Test visual collector
    test_with_visual_collector(reports)
    
    # Save to file
    import json
    from pathlib import Path
    
    output_dir = Path('data/raw')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"mock_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Convert reports to dict for JSON serialization
    reports_dict = []
    for report in reports:
        report_dict = {
            'report_id': report.report_id,
            'platform': report.platform,
            'target_domain': report.target_domain,
            'target_company': report.target_company,
            'target_program': report.target_program,
            'record_type': report.record_type,
            'severity': report.severity,
            'priority_score': report.priority_score,
            'technology_stack': report.technology_stack,
            'endpoint': report.endpoint,
            'http_method': report.http_method,
            'category': report.category,
            'description': report.description,
            'reward_amount': report.reward_amount,
            'source_quality': report.source_quality,
            'authentication_required': report.authentication_required,
            'privileges_required': report.privileges_required,
            'user_interaction': report.user_interaction,
            'complexity': report.complexity,
            'domain_category': report.domain_category,
            'category_id': report.category_id,
            'created_date': report.created_date.isoformat() if report.created_date else None,
            'resolved_date': report.resolved_date.isoformat() if report.resolved_date else None
        }
        reports_dict.append(report_dict)
    
    with open(output_file, 'w') as f:
        json.dump(reports_dict, f, indent=2)
    
    console.print(f"[bold cyan]💾 Saved mock data to:[/bold cyan] {output_file}\n")
    console.print("[bold green]✨ Mock data generation complete![/bold green]")
    console.print("\nYou can now use this data for:")
    console.print("  • Training ML models")
    console.print("  • Testing the analysis pipeline")
    console.print("  • Demonstrating the visual UI")
    console.print("  • Development and debugging\n")

if __name__ == "__main__":
    main()
