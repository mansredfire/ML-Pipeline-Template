# Installation Guide

How to install and set up ML Pipeline Template.

---

## What You Need

| What | Minimum | Recommended |
|------|---------|-------------|
| **Python** | 3.10+ | 3.11+ |
| **RAM** | 4GB | 8GB |
| **Disk Space** | 2GB free | 5GB free |
| **OS** | Windows 10+, Ubuntu 20.04+, macOS 10.15+ | Latest versions |

### Check if Python is Installed
```bash
python --version
# Should show Python 3.10.x or higher
```

If Python is not installed:

- **Windows**: Download from [python.org](https://www.python.org/downloads/) — check **Add Python to PATH** during install
- **Linux**: `sudo apt install python3.10 python3-pip python3-venv git -y`
- **macOS**: `brew install python@3.10`

---

## Installation

### Windows (PowerShell)

#### 1. Download the Project

**Option A — Download ZIP:** Go to the GitHub repo, click **Code → Download ZIP**, extract it.

**Option B — Clone with Git:**
```powershell
git clone https://github.com/mansredfire/ml-pipeline-template.git
cd ml-pipeline-template
```

#### 2. Allow Script Execution (one-time)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 3. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Your prompt should now show `(venv)` at the beginning.

#### 4. Set Python Path
```powershell
$env:PYTHONPATH = "$(Get-Location)"
```

#### 5. Install Everything
```powershell
pip install -r requirements.txt
```

#### 6. Make Sure It Works
```powershell
python -c "from src.collectors.data_sources import DataRecord; print('Installation successful')"
```

---

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.10 python3-pip python3-venv git -y

git clone https://github.com/mansredfire/ml-pipeline-template.git
cd ml-pipeline-template

python3 -m venv venv
source venv/bin/activate
export PYTHONPATH="$(pwd)"

pip install -r requirements.txt

python -c "from src.collectors.data_sources import DataRecord; print('Installation successful')"
```

---

### macOS

```bash
brew install python@3.10

git clone https://github.com/mansredfire/ml-pipeline-template.git
cd ml-pipeline-template

python3 -m venv venv
source venv/bin/activate
export PYTHONPATH="$(pwd)"

pip install -r requirements.txt

python -c "from src.collectors.data_sources import DataRecord; print('Installation successful')"
```

---

## Make Sure Everything Works

### Test That All Imports Work
```bash
python -c "
from src.collectors.data_sources import DataRecord, DataCollector
from src.training.pipeline import TrainingPipeline
from src.features.feature_engineer import FeatureEngineer
from src.inference.predictor import Predictor
print('All imports successful')
"
```

### Check That All Scripts Are There
```powershell
# Windows
dir scripts\

# Linux/Mac
ls scripts/
```

You should see: `train_model.py`, `train_with_mock_data.py`, `test_with_mock_data.py`, `analyze_target.py`, `batch_analyze.py`, `evaluate_models.py`

### Run a Quick Training Test
```bash
python scripts/train_with_mock_data.py --quick --reports 100
```

If this finishes without errors, you're good to go.

---

## Create the Models Folder

The pipeline saves trained models here. Create it if it doesn't exist:

```powershell
# Windows
New-Item -ItemType Directory -Path data\models -Force

# Linux/Mac
mkdir -p data/models
```

---

## Updating

### 1. Back Up Your Models (Optional)
```powershell
# Windows
Copy-Item -Path data -Destination data_backup -Recurse

# Linux/Mac
cp -r data data_backup
```

### 2. Pull Latest Code
```bash
git pull origin main
```

### 3. Update Packages
```bash
pip install --upgrade -r requirements.txt
```

### 4. Make Sure It Still Works
```bash
python -c "from src.collectors.data_sources import DataRecord; print('Update successful')"
```

---

## Uninstalling

### Remove Everything
```bash
deactivate
cd ..
```

```powershell
# Windows
Remove-Item -Recurse -Force ml-pipeline-template

# Linux/Mac
rm -rf ml-pipeline-template
```

### Keep Just Your Trained Models
```powershell
# Windows
Remove-Item -Recurse -Force venv, src, scripts, config, docker, docs

# Linux/Mac
rm -rf venv/ src/ scripts/ config/ docker/ docs/
```

Your `.pkl` model files in `data/models/` will still be there.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'src'` | Set `$env:PYTHONPATH = "$(Get-Location)"` (Windows) or `export PYTHONPATH="$(pwd)"` (Linux/Mac) |
| `pip install` fails | Run `python -m pip install --upgrade pip` first |
| Virtual environment won't activate (Windows) | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Missing package errors | Make sure `(venv)` is in your prompt, then `pip install -r requirements.txt` |
| Database driver errors | `pip install psycopg2-binary` (PostgreSQL) or `pip install pymysql` (MySQL) |
| Out of memory during training | Use `python scripts/train_with_mock_data.py --quick --reports 500` |
| Permission denied (Linux/Mac) | `chmod +x scripts/*.py` |

### Tips by Platform

**Windows**: Use PowerShell, not CMD. If antivirus flags ML libraries, add the project folder as an exception.

**Linux**: You might need `sudo apt install build-essential python3-dev`. Use `python3` instead of `python` if both Python 2 and 3 are installed.

**macOS**: You might need Xcode tools: `xcode-select --install`.

---

## Checklist

- [ ] Python 3.10+ installed
- [ ] Project downloaded or cloned
- [ ] Virtual environment created and activated (`(venv)` in prompt)
- [ ] `PYTHONPATH` set to project root
- [ ] Packages installed (`pip install -r requirements.txt`)
- [ ] Import test passed
- [ ] `data/models/` folder exists
- [ ] Quick training test completed successfully

---

## What's Next

1. **[Training.md](docs/Training.md)** — How to train the models
2. **[Databases.md](docs/Databases.md)** — How to use a database instead of mock data
3. **[Scripts.md](docs/Scripts.md)** — All scripts and what they do
