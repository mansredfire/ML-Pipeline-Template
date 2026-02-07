# Scripts Reference & Workflows

Complete guide to all ML Pipeline Template scripts and common workflows.

---

## Available Scripts

All scripts are in the `scripts/` directory.

| Script | Purpose | Key Arguments |
|---|---|---|
| `train_with_mock_data.py` | Generate mock stock data and train models | `--reports`, `--quick` |
| `test_with_mock_data.py` | Generate and display mock data (no training) | — |
| `train_model.py` | Train from config file | `--config`, `--quick`, `--models` |
| `analyze_target.py` | Analyze a single company | `--domain`, `--tech`, `--output` |
| `batch_analyze.py` | Analyze multiple companies | `--input`, `--output`, `--threads` |
| `evaluate_models.py` | Evaluate trained models | `--models-dir`, `--test-data` |

---

## Script Reference

### train_with_mock_data.py

The main script for getting started. Generates fake stock event records (like "Stock Goes Up," "Bad Forecast," etc.) and trains the models on them.

```bash
python scripts/train_with_mock_data.py --reports 1000
python scripts/train_with_mock_data.py --quick --reports 500
```

| Argument | Default | Description |
|---|---|---|
| `--reports` | `1000` | Number of mock records to generate |
| `--quick` | off | Quick training mode (faster, less data) |

**Output:** Trained model `.pkl` files in `data/models/`.

---

### test_with_mock_data.py

Generates mock data and displays it in the terminal. Useful for seeing what the mock data looks like without training anything.

```bash
python scripts/test_with_mock_data.py
```

No arguments. Just run it and look at the output.

---

### train_model.py

Trains models using a YAML configuration file. Gives you more control over the training process.

```bash
python scripts/train_model.py
python scripts/train_model.py --config config/training_config.yaml --quick
python scripts/train_model.py --models record severity
```

| Argument | Default | Description |
|---|---|---|
| `--config` | `config/training_config.yaml` | Path to training config |
| `--quick` | off | Quick training mode |
| `--skip-collection` | off | Skip data collection, use cached data |
| `--models` | `all` | Which models: `record`, `severity`, `chain`, or `all` |

**Output:** Trained model `.pkl` files in `data/models/`.

---

### analyze_target.py

Runs predictions for a single company using your trained models. Pass a stock ticker (like AAPL) and it predicts what stock events are most likely.

```bash
python scripts/analyze_target.py --domain AAPL
python scripts/analyze_target.py --domain TSLA --tech YahooFinance GoogleFinance --output results.json
```

| Argument | Short | Required | Default | Description |
|---|---|---|---|---|
| `--domain` | `-d` | Yes | — | Company stock ticker (e.g., AAPL, MSFT, TSLA) |
| `--company` | `-c` | No | — | Company name |
| `--tech` | `-t` | No | — | Data sources (space-separated) |
| `--endpoints` | `-e` | No | — | API endpoints (space-separated) |
| `--auth` | — | No | off | Data source requires login |
| `--api` | — | No | off | Company has API data feeds |
| `--output` | `-o` | No | — | Save results to this file (JSON) |
| `--models-dir` | — | No | `data/models` | Folder containing trained models |

**Prerequisite:** Models must be trained first (run `train_with_mock_data.py`).

---

### batch_analyze.py

Analyzes multiple companies at once from a CSV or JSON file.

```bash
python scripts/batch_analyze.py --input companies.csv --output results.json
python scripts/batch_analyze.py --input companies.csv --output results.json --threads 4
```

| Argument | Short | Required | Default | Description |
|---|---|---|---|---|
| `--input` | `-i` | Yes | — | Input file (CSV with stock tickers) |
| `--output` | `-o` | Yes | — | Output file (JSON results) |
| `--models-dir` | — | No | `data/models` | Models folder |
| `--threads` | — | No | `1` | Number of parallel threads |

Your `companies.csv` should have a column with stock tickers (like AAPL, MSFT, TSLA).

---

### evaluate_models.py

Checks how well your trained models are performing.

```bash
python scripts/evaluate_models.py
python scripts/evaluate_models.py --models-dir data/models --test-data data/test.pkl
```

| Argument | Default | Description |
|---|---|---|
| `--models-dir` | `data/models` | Folder containing trained models |
| `--test-data` | — | Path to test data (pickle file) |

---

## Common Workflows

### Workflow 1: Quick Start with Mock Data

Get the full pipeline running in under a minute.

```bash
# Train models on 1000 fake stock events
python scripts/train_with_mock_data.py --quick --reports 1000

# Analyze a company
python scripts/analyze_target.py --domain AAPL

# Run the API
python app.py
```

---

### Workflow 2: Iterative Training

Start small and increase data to find the right balance of speed and accuracy.

```bash
# Quick test — 100 records
python scripts/train_with_mock_data.py --quick --reports 100

# Better accuracy — 1000 records
python scripts/train_with_mock_data.py --reports 1000

# Full training — 5000 records
python scripts/train_with_mock_data.py --reports 5000
```

---

### Workflow 3: Model Evaluation

Train models and then check how well they perform.

```bash
# Train
python scripts/train_with_mock_data.py --reports 1000

# Evaluate
python scripts/evaluate_models.py --models-dir data/models
```

---

### Workflow 4: Batch Analysis

Analyze many companies at once after training.

```bash
# Train first
python scripts/train_with_mock_data.py --reports 1000

# Analyze companies in bulk
python scripts/batch_analyze.py --input companies.csv --output results.json --threads 4
```

Your `companies.csv` should have a column with stock tickers.

---

### Workflow 5: Model Versioning

Back up models before retraining so you can compare or go back.

```powershell
# Windows
Copy-Item -Path data\models -Destination data\models_v1 -Recurse

# Linux/Mac
cp -r data/models data/models_v1
```

Then retrain:
```bash
python scripts/train_with_mock_data.py --reports 2000
```

Compare by running `evaluate_models.py` against both folders.

---

### Workflow 6: Config-Based Training

Use the YAML config for full control.

```bash
# Edit config
notepad config/training_config.yaml    # Windows
nano config/training_config.yaml       # Linux/Mac

# Train specific models only
python scripts/train_model.py --models record severity

# Train all models
python scripts/train_model.py --config config/training_config.yaml
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| "Models not found" | Train first: `python scripts/train_with_mock_data.py --quick --reports 1000` |
| "No such file or directory" | Make sure you're in the project root folder |
| Low accuracy | Increase `--reports` count, or use more training data |
| Training too slow | Use `--quick` flag or reduce `--reports` |
| Script won't run | Make sure `PYTHONPATH` is set and `(venv)` is active |

---

## Quick Command Reference

```bash
# Train with mock data
python scripts/train_with_mock_data.py --quick --reports 1000

# Train from config
python scripts/train_model.py --config config/training_config.yaml

# Analyze a company
python scripts/analyze_target.py --domain AAPL

# Analyze many companies
python scripts/batch_analyze.py --input companies.csv --output results.json

# Check model performance
python scripts/evaluate_models.py --models-dir data/models

# Start API server
python app.py
```
