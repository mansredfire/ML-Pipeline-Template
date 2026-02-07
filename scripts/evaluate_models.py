#!/usr/bin/env python3
"""
Model evaluation script
Evaluates trained models on test data
"""

import argparse
from pathlib import Path
import sys
import pickle
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.classifier import Classifier
from src.models.priority_predictor import PriorityPredictor
from src.features.feature_engineer import FeatureEngineer
from rich.console import Console
from rich.table import Table


console = Console()


def main():
    parser = argparse.ArgumentParser(description='Evaluate trained models')
    
    parser.add_argument(
        '--models-dir',
        default='data/models',
        help='Directory containing trained models'
    )
    
    parser.add_argument(
        '--test-data',
        help='Path to test data (pickle file with DataRecords)'
    )
    
    args = parser.parse_args()
    
    models_dir = Path(args.models_dir)
    
    console.print("[bold cyan]MODEL EVALUATION[/bold cyan]\n")
    
    # Load feature engineer
    console.print("Loading FeatureEngineer...")
    feature_engineer = FeatureEngineer()
    feature_engineer.load(str(models_dir / 'feature_engineer.pkl'))
    
    # Load models
    console.print("Loading Classifier...")
    import pickle
    with open(str(models_dir / 'classifier.pkl'), 'rb') as f:
        cls_data = pickle.load(f)
    classifier_model = cls_data.get('model')
    label_encoder = cls_data.get('label_encoder')
    
    console.print("Loading PriorityPredictor...")
    with open(str(models_dir / 'priority_predictor.pkl'), 'rb') as f:
        prio_data = pickle.load(f)
    
    # Load test data if provided
    if args.test_data:
        console.print(f"\nLoading test data from {args.test_data}...")
        
        with open(args.test_data, 'rb') as f:
            test_reports = pickle.load(f)
        
        console.print(f"Loaded {len(test_reports)} test reports\n")
        
        # Extract features
        console.print("Extracting features...")
        features_df = feature_engineer.transform(test_reports)
        
        # Prepare data
        y_true = features_df['record_type'].values
        X = features_df.drop(['record_type', 'severity', 'priority_score'], axis=1, errors='ignore')
        numeric_cols = X.select_dtypes(include=['number']).columns
        X = X[numeric_cols]
        
        # Evaluate
        console.print("\nEvaluating Classifier...")
        eval_results = record_predictor.evaluate(
            pd.DataFrame(X),
            pd.Series(y_true),
            method='averaging'
        )
        
        # Display results
        console.print(f"\n[bold]Overall Metrics:[/bold]")
        console.print(f"  Accuracy: {eval_results['accuracy']:.4f}")
        console.print(f"  F1 Score: {eval_results['f1_score']:.4f}")
        
        # Per-class metrics
        console.print(f"\n[bold]Per-Class Metrics:[/bold]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Class")
        table.add_column("Precision", justify="right")
        table.add_column("Recall", justify="right")
        table.add_column("F1-Score", justify="right")
        table.add_column("Support", justify="right")
        
        for i, class_label in enumerate(eval_results['class_labels']):
            table.add_row(
                class_label,
                f"{eval_results['precision_per_class'][i]:.3f}",
                f"{eval_results['recall_per_class'][i]:.3f}",
                f"{eval_results['f1_per_class'][i]:.3f}",
                str(eval_results['support_per_class'][i])
            )
        
        console.print(table)
    
    else:
        console.print("\n[yellow]No test data provided. Use --test-data to evaluate.[/yellow]")
    
    # Model info
    console.print(f"\n[bold]Model Information:[/bold]")
    console.print(f"  Classifier model: {'loaded' if classifier_model else 'not found'}")
    console.print(f"  Label encoder: {'loaded' if label_encoder else 'not found'}")
    if hasattr(feature_engineer, 'feature_stats'):
        console.print(f"  Features: {len(feature_engineer.feature_stats.get('mean', {}))}")
    
    console.print("\n[green]✅ All models loaded successfully[/green]")


if __name__ == '__main__':
    main()
