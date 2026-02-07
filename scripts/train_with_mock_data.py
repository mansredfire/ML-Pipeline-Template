#!/usr/bin/env python3
"""
Train models using mock data
Perfect for testing and development
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from rich.console import Console
from rich.panel import Panel
import pickle

from test_with_mock_data import generate_mock_reports

console = Console()

def main():
    """Train models with mock data"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Train models with mock data')
    parser.add_argument('--reports', type=int, default=1000, 
                       help='Number of mock reports to generate (default: 1000)')
    parser.add_argument('--quick', action='store_true',
                       help='Quick training mode')
    
    args = parser.parse_args()
    
    # Show banner
    console.print()
    console.print(Panel.fit(
        "[bold white]🤖 ML Pipeline Template[/bold white]\n"
        "[cyan]Model Training with Mock Data[/cyan]\n\n"
        f"Generating: {args.reports} reports",
        border_style="blue"
    ))
    console.print()
    
    # Generate mock data
    console.print("[bold green]Step 1: Generating mock data records...[/bold green]\n")
    reports = generate_mock_reports(count=args.reports)
    
    console.print(f"[bold green]✅ Generated {len(reports)} reports[/bold green]\n")
    
    # Save mock data
    data_dir = Path('data') / 'raw'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    mock_file = data_dir / 'mock_training_data.pkl'
    
    with open(mock_file, 'wb') as f:
        pickle.dump(reports, f)
    
    console.print(f"[cyan]💾 Saved mock data to: {mock_file}[/cyan]\n")
    
    # Training
    console.print("[bold green]Step 2: Training models...[/bold green]\n")
    console.print("[yellow]Note: Training may take 5-15 minutes[/yellow]\n")
    
    try:
        # Import here to catch any import errors
        from src.training.pipeline import TrainingPipeline
        
        # Create pipeline
        pipeline = TrainingPipeline()
        
        console.print(f"[cyan]→ Loaded {len(reports)} mock reports[/cyan]\n")
        
        # Preprocess
        console.print("[cyan]→ Preprocessing data...[/cyan]")
        pipeline.processed_reports = pipeline.preprocess_data(reports)
        console.print(f"[green]✓ Preprocessed {len(pipeline.processed_reports)} reports[/green]\n")
        
        # Feature engineering - pass the reports as argument
        console.print("[cyan]→ Engineering features...[/cyan]")
        pipeline.feature_data = pipeline.engineer_features(pipeline.processed_reports)
        console.print(f"[green]✓ Features engineered[/green]\n")
        
        # Train record model
        console.print("[cyan]→ Training record classifier...[/cyan]")
        try:
            pipeline.train_record_model(pipeline.feature_data)
        except TypeError:
            pipeline.train_record_model()
        console.print("[green]✓ Record classifier trained[/green]\n")
        
        # Train severity model
        console.print("[cyan]→ Training severity predictor...[/cyan]")
        try:
            pipeline.train_severity_model(pipeline.feature_data)
        except TypeError:
            pipeline.train_severity_model()
        console.print("[green]✓ Severity predictor trained[/green]\n")
        
        # Train chain detector
        console.print("[cyan]→ Training chain detector...[/cyan]")
        try:
            pipeline.train_pattern_detector(pipeline.processed_reports)
        except TypeError:
            pipeline.train_pattern_detector()
        console.print("[green]✓ Chain detector trained[/green]\n")
        
        # Save models
        console.print("[cyan]→ Saving models...[/cyan]")
        pipeline.save_models()
        console.print(f"[green]✓ Models saved to: data\\models[/green]\n")
        
        # Summary
        console.print()
        console.print(Panel.fit(
            "[bold green]✅ Training Complete![/bold green]\n\n"
            f"Reports Processed: {len(pipeline.processed_reports)}\n"
            "Models Trained: 3\n\n"
            "Models saved to: data\\models\\\n"
            "Ready for predictions!",
            title="📊 Summary",
            border_style="green"
        ))
        
        console.print("\n[bold cyan]Next steps:[/bold cyan]")
        console.print("  python scripts\\analyze_target.py --domain AAPL\n")
        
    except ImportError as e:
        console.print(f"\n[bold red]❌ Import Error:[/bold red]")
        console.print(f"[red]{e}[/red]")
        console.print("\n[yellow]Missing module. Installing required packages...[/yellow]\n")
        console.print("Run: pip install -r requirements.txt\n")
        return 1
        
    except AttributeError as e:
        console.print(f"\n[bold red]❌ Attribute Error:[/bold red]")
        console.print(f"[red]{e}[/red]")
        console.print("\n[yellow]The TrainingPipeline class may be incomplete.[/yellow]")
        console.print("Check: src\\training\\pipeline.py\n")
        import traceback
        traceback.print_exc()
        return 1
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error:[/bold red]")
        console.print(f"[red]{e}[/red]\n")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
