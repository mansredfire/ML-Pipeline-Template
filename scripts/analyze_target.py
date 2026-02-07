#!/usr/bin/env python3
"""
Company stock event prediction script
Analyzes a company for predicted stock events
"""

import argparse
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.inference.predictor import Predictor
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree


console = Console()


def display_results(results: dict):
    """Display analysis results in a nice format"""
    
    # Header
    console.print(f"\n[bold cyan]{'='*70}[/bold cyan]")
    console.print(f"[bold cyan]ML PIPELINE TEMPLATE - STOCK EVENT PREDICTIONS[/bold cyan]")
    console.print(f"[bold cyan]{'='*70}[/bold cyan]\n")
    
    # Company info
    console.print(Panel(
        f"[bold]Ticker:[/bold] {results['target']}\n"
        f"[bold]Company:[/bold] {results['company']}\n"
        f"[bold]Data Sources:[/bold] {', '.join(results['technology_stack'])}",
        title="Company Information",
        border_style="cyan"
    ))
    
    # Risk score
    risk_score = results['risk_score']
    
    if risk_score >= 8:
        risk_level = 'critical'
    elif risk_score >= 6:
        risk_level = 'high'
    elif risk_score >= 4:
        risk_level = 'medium'
    else:
        risk_level = 'low'
    
    risk_color = {
        'critical': 'red',
        'high': 'orange1',
        'medium': 'yellow',
        'low': 'green'
    }.get(risk_level, 'white')
    
    console.print(f"\n[bold]Risk Score:[/bold] [{risk_color}]{risk_score}/10 ({risk_level.upper()})[/{risk_color}]\n")
    
    # Record predictions
    console.print("[bold underline]Predicted Financial Events:[/bold underline]\n")
    
    results_table = Table(show_header=True, header_style="bold magenta")
    results_table.add_column("Rank", style="dim", width=6)
    results_table.add_column("Record", width=25)
    results_table.add_column("Probability", justify="right", width=12)
    results_table.add_column("Confidence", width=12)
    results_table.add_column("Priority", justify="center", width=10)
    
    for idx, rec in enumerate(results['predictions'][:10], 1):
        results_table.add_row(
            str(idx),
            rec['record_type'],
            f"{rec['probability']:.1%}",
            rec['confidence'],
            ""
        )
    
    console.print(results_table)
    
    # Chains
    if results['chain_predictions']:
        console.print(f"\n[bold underline]Chain Reactions Detected:[/bold underline]\n")
        
        for chain in results['chain_predictions'][:5]:
            console.print(
                f"  [red]⚠[/red] {chain['name']} "
                f"(Score: {chain['relevance_score']}/10)"
            )
            console.print(f"     {chain['description']}")
            console.print()
    
    # Strategy
    console.print("[bold underline]What To Look At Next:[/bold underline]\n")
    
    strategy = results['test_strategy']
    
    if strategy.get('priority_records'):
        console.print("[bold]Top event types to watch:[/bold]")
        for rec in strategy['priority_records'][:5]:
            console.print(f"  • {rec}")
        console.print()
    
    if strategy.get('recommended_tools'):
        console.print("[bold]Recommended tools:[/bold]")
        for tool in strategy['recommended_tools'][:5]:
            console.print(f"  • {tool}")
        console.print()
    
    # Recommendations
    if results.get('recommendations'):
        console.print("[bold underline]Recommendations:[/bold underline]\n")
        
        for i, rec in enumerate(results['recommendations'][:5], 1):
            console.print(f"  {i}. {rec}")
    
    console.print(f"\n[bold cyan]{'='*70}[/bold cyan]\n")


def main():
    parser = argparse.ArgumentParser(description='Analyze company for stock event predictions')
    
    parser.add_argument(
        '--domain',
        '-d',
        required=True,
        help='Company stock ticker like AAPL, MSFT, TSLA'
    )
    
    parser.add_argument(
        '--company',
        '-c',
        help='Company name'
    )
    
    parser.add_argument(
        '--tech',
        '-t',
        nargs='+',
        help='Data sources like YahooFinance GoogleFinance'
    )
    
    parser.add_argument(
        '--endpoints',
        '-e',
        nargs='+',
        help='API endpoints to test'
    )
    
    parser.add_argument(
        '--auth',
        action='store_true',
        help='Target requires authentication'
    )
    
    parser.add_argument(
        '--api',
        action='store_true',
        help='Target has API endpoints'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        help='Output file (JSON)'
    )
    
    parser.add_argument(
        '--models-dir',
        default='data/models',
        help='Directory containing trained models'
    )
    
    args = parser.parse_args()
    
    # Build target info
    target_info = {
        'domain': args.domain,
        'company_name': args.company or args.domain.split('.')[0].title(),
        'technology_stack': args.tech or [],
        'endpoints': args.endpoints or ['/'],
        'auth_required': args.auth,
        'has_api': args.api
    }
    
    # Load predictor
    console.print("[cyan]Loading models...[/cyan]")
    predictor = Predictor(models_dir=args.models_dir)
    
    # Analyze
    console.print(f"[cyan]Analyzing {args.domain}...[/cyan]")
    results = predictor.analyze_target(target_info)
    
    # Display results
    display_results(results)
    
    # Save to file
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        console.print(f"[green]✓ Results saved to {args.output}[/green]")


if __name__ == '__main__':
    main()
