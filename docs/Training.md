# Training Guide

How to train models with ML Pipeline Template.

---

## Overview

This pipeline trains machine learning models to predict what kind of stock event is happening (like "Stock Goes Up" or "Analyst Says Sell") and how important it is. It comes with fake data so you can learn how everything works before using real data.

### What Gets Trained

| Model | What It Does | How It Works |
|---|---|---|
| **Classifier** | Predicts the event type (e.g. "Stock Goes Up", "Bad Forecast") | 3 models working together: RandomForest, CatBoost, GradientBoosting |
| **Priority Predictor** | Predicts how important the event is (critical/high/medium/low) | RandomForest with cross-validation (tests itself 5 times to make sure it's accurate) |
| **Pattern Detector** | Finds chain reactions (e.g. bad results → analyst says sell → forecast gets worse) | Rule-based — no ML, just if/then logic |

### How Training Works (Step by Step)

1. **Load data** — either fake data from the mock generator or your own records
2. **Clean it up** — remove duplicates, fix missing values, add extra info
3. **Turn it into numbers** — extract ~28 number features from each record
4. **Train** — 80% of data for training, 20% saved for testing
5. **Test** — check accuracy on the 20% the model hasn't seen
6. **Save** — models saved as `.pkl` files to `data/models/`

---

## Training with Mock Data

The fastest way to try it out. Creates fake stock event records and trains on them.

### Quick Start
```bash
python scripts/train_with_mock_data.py --quick --reports 1000
```

### Arguments

| Argument | Default | What It Does |
|---|---|---|
| `--reports` | `1000` | How many fake records to create |
| `--quick` | off | Faster training (uses less data) |

### What the Mock Data Looks Like

Each fake record includes:
- **Event type** — one of 10 categories like "Stock Goes Up," "Bad Forecast," "Company Merger," etc.
- **How serious it is** — critical, high, medium, or low
- **Impact score** — a number from 0 to 10
- **Company** — a well-known company like Apple, Tesla, Netflix, etc.
- **Data sources** — where the data came from (Yahoo Finance, Google Finance, etc.)
- **Description** — a plain-English sentence describing what happened
- **Other details** — complexity, date, category, and more

The data is randomly spread across all event types so the model gets practice with each one.

---

## Training from Config

For more control, use `train_model.py` with a YAML config file:

```bash
python scripts/train_model.py --config config/training_config.yaml
```

### Arguments

| Argument | Default | What It Does |
|---|---|---|
| `--config` | `config/training_config.yaml` | Path to the config file |
| `--quick` | off | Faster training with less data |
| `--skip-collection` | off | Skip loading data, use what's already cached |
| `--models` | `all` | Which models to train: `record`, `severity`, `chain`, or `all` |

---

## Understanding Training Output

When you run training, you'll see something like this:

```
Training record classifier...
  RandomForest — CV F1 Score: 0.8234 (+/- 0.0312)
  CatBoost — CV F1 Score: 0.8456 (+/- 0.0287)
  GradientBoosting — CV F1 Score: 0.8189 (+/- 0.0345)
✓ Classifier trained (Best Accuracy: 85.0%)

Training priority predictor...
  CV F1 Score: 0.9312 (+/- 0.0198)
✓ Priority predictor trained (Accuracy: 92.0%)

Training pattern detector...
✓ Pattern detector trained
```

**What does this mean?**

- **Accuracy** — how often the model gets the right answer on data it hasn't seen before
- **CV F1 Score** — the model tested itself 5 different ways to make sure it's not just getting lucky. Higher = better. The `+/-` shows how much the score varies
- **Pattern detector** — doesn't have an accuracy score because it uses rules, not ML

### Why 3 Models?

The classifier trains 3 separate models (RandomForest, CatBoost, GradientBoosting). Each one learns differently, so together they're more accurate than any single model. You can see which one does best from the CV scores.

---

## Saved Model Files

After training, these files appear in `data/models/`:

| File | What's Inside |
|---|---|
| `classifier.pkl` | The 3-model classifier + a label encoder |
| `priority_predictor.pkl` | The priority/severity model + a label encoder |
| `pattern_detector.pkl` | The pattern chain rules |
| `feature_engineer.pkl` | The feature transformer (remembers how it turned data into numbers) |

You need all 4 files to make predictions.

---

## Data Fields

Every record uses the `DataRecord` format. Here's what each field means:

**Required fields:**

| Field | Type | What It Is |
|---|---|---|
| `report_id` | str | A unique ID for this record |
| `target_domain` | str | Stock ticker (e.g. "AAPL") |
| `target_company` | str | Company name (e.g. "Apple") |
| `record_type` | str | Event type (e.g. "Stock Goes Up") |
| `severity` | str | How serious: `critical`, `high`, `medium`, or `low` |
| `priority_score` | float | Impact score from 0 to 10 |

**Optional fields (help the model be more accurate):**

| Field | Type | What It Is |
|---|---|---|
| `technology_stack` | List[str] | Data sources used (e.g. Yahoo Finance, SEC Filings) |
| `description` | str | Plain-English description of what happened |
| `endpoint` | str | API endpoint where data was pulled from |
| `http_method` | str | How the data was fetched (GET, POST) |
| `reward_amount` | float | Estimated price impact in dollars |
| `source_quality` | int | How reliable the data source is (higher = better) |
| `authentication_required` | bool | Does the data source need a login? |
| `complexity` | str | How complex the event is: `low`, `medium`, or `high` |
| `category` | str | Sector: `Technology`, `Healthcare`, `Financials`, etc. |

---

## Accuracy vs. Data Size

Rough expectations when training on mock data:

| Records | Expected Accuracy | Training Time |
|---|---|---|
| 50–100 | 40–60% | ~5 seconds |
| 500 | 70–80% | ~20 seconds |
| 1000 | 80–90% | ~45 seconds |
| 5000+ | 85–95% | ~5 minutes |

Mock data gives lower accuracy than real data because event types are random. Real labeled data in a specific area will be more accurate.

---

## Tips

**Start small.** Train on 100 records first to make sure everything works, then go bigger.

**Back up your models.** Before retraining, save a copy:
```bash
cp -r data/models data/models_backup_$(date +%Y-%m-%d)
```

**Balance your data.** Make sure you have examples of all event types. If 90% of your data is "Stock Goes Up," the model will just guess that every time.

**Make it yours.** The 10 event types (Stock Goes Up, Stock Goes Down, Good Forecast, etc.) are examples. Change `RecordType` in `src/collectors/data_sources.py` to whatever categories fit your project.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Low accuracy (<60%) | Add more training data, or make sure all event types are represented |
| Training takes too long | Use `--quick` flag or reduce `--reports` |
| Out of memory | Reduce `--reports` to 500 or lower |
| Models not saving | Make sure `data/models/` folder exists |
| Import errors | Set `PYTHONPATH` to the project root folder |

---

## What To Do Next

After training:

1. **Start the API** — `python app.py` → predictions at `http://localhost:8000`
2. **Analyze a company** — `python scripts/analyze_target.py --domain AAPL`
3. **Check model quality** — `python scripts/evaluate_models.py --models-dir data/models`
