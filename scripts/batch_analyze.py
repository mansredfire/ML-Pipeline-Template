#!/usr/bin/env python3
"""
Batch analysis script
Analyzes multiple targets from a file
"""

import argparse
import json
import csv
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.inference.predictor import Predictor
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


console = Console()


def read_targets_from_file(filepath: str) -> list:
    """Read targets from CSV or JSON file"""
    
    path = Path(filepath)
    
    if path.suffix == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    
    elif path.suffix == '.csv':
        targets = []
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                target = {
                    'domain': row['domain'],
                    'company_name': row.get('company', ''),
                    'technology_stack': row.get('tech_stack', '').split(',') if row.get('tech_stack') else [],
                    'endpoints': row.get('endpoints', '/').split(','),
                    'auth_required': row.get('auth_required', 'false').lower() == 'true',
                    'has_api': row.get('has_api', 'false').lower() == 'true'
                }
                targets.append(target)
        return targets
    
    elif path.suffix == '.txt':
        targets = []
        with open(path, 'r') as f:
            for line in f:
                domain = line.strip()
                if domain and not domain.startswith('#'):
                    targets.append({
                        'domain': domain,
                        'company_name': '',
                        'technology_stack': [],
                        'endpoints': ['/'],
                        'auth_required': False,
                        'has_api': False
                    })
        return targets
    
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")


def main():
    parser = argparse.ArgumentParser(description='Batch analyze multiple targets')
    
    parser.add_argument(
        '--input',
        '-i',
        required=True,
        help='Input file (CSV, JSON, or TXT with one domain per line)'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        required=True,
        help='Output file (JSON)'
    )
    
    parser.add_argument(
        '--models-dir',
        default='data/models',
        help='Directory containing trained models'
    )
    
    parser.add_argument(
        '--threads',
        type=int,
        default=1,
        help='Number of parallel threads (not implemented yet)'
    )
    
    args = parser.parse_args()
    
    # Read targets
    console.print(f"[cyan]Reading targets from {args.input}...[/cyan]")
    targets = read_targets_from_file(args.input)
    console.print(f"[green]✓ Loaded {len(targets)} targets[/green]\n")
    
    # Load predictor
    console.print("[cyan]Loading models...[/cyan]")
    predictor = Predictor(models_dir=args.models_dir)
    console.print("[green]✓ Models loaded[/green]\n")
    
    # Analyze targets
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Analyzing targets...", total=len(targets))
        
        for i, target in enumerate(targets, 1):
            progress.update(
                task, 
                description=f"[cyan]Analyzing {i}/{len(targets)}: {target['domain']}",
                advance=1
            )
            
            try:
                result = predictor.analyze_target(target)
                results.append(result)
            except Exception as e:
                console.print(f"[red]✗ Error analyzing {target['domain']}: {e}[/red]")
                results.append({
                    'target': target['domain'],
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
    
    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    console.print(f"\n[green]✓ Analyzed {len(targets)} targets[/green]")
    console.print(f"[green]✓ Results saved to {args.output}[/green]")
    
    # Summary
    successful = sum(1 for r in results if 'error' not in r)
    failed = len(results) - successful
    
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Successful: {successful}")
    console.print(f"  Failed: {failed}")
    
    # High risk targets
    high_risk = [r for r in results if 'risk_level' in r and r['risk_level'] in ['critical', 'high']]
    if high_risk:
        console.print(f"\n[bold red]⚠ High Risk Targets ({len(high_risk)}):[/bold red]")
        for r in high_risk[:10]:
            console.print(f"  • {r['target']} - Risk: {r['risk_score']}/10")


if __name__ == '__main__':
    main()
