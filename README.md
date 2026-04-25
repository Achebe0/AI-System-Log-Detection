# AI System Log Detection

## Problem

System failures cost companies thousands to millions of dollars in downtime. Detecting anomalies quickly requires:
- **Labeled training data** (hard to get from production)
- **Understanding failure patterns** (DB latency vs auth failures vs traffic spikes)
- **Real-time detection** (manual log analysis is too slow)

## Solution

A controlled synthetic log generator that simulates realistic microservices failures with labeled ground truth, enabling:
1. **Fast ML model training** on diverse, reproducible failure scenarios
2. **Accurate anomaly detection** across multiple services
3. **Interpretable explanations** of detected failures

---

## Features

### Log Simulation
- **3 Microservices**: Auth, Database, API (with realistic latencies)
- **5 Anomaly Scenarios**:
  - `NORMAL` — Baseline healthy state
  - `DB_LATENCY` — Database performance degradation (+200/500/2000ms)
  - `AUTH_FAILURE` — Authentication rejection spikes (5%/20%/50%)
  - `TRAFFIC_SPIKE` — Request volume surges (3x/10x/50x)
  - `DEGRADATION` — Gradual system resource exhaustion
- **Structured Output**: JSONL format with full metadata (timestamp, service, latency, status_code, severity, scenario)
- **Reproducible**: Seeded randomness for consistent training data

### Example Log
```json
{"timestamp": "2026-04-25T10:00:01.261000", "service": "database_service", 
 "latency_ms": 607, "status_code": 200, "severity": "WARNING", 
 "message": "High database latency", "scenario": "DB_LATENCY"}
```

---

## Project Structure

```
.
├── constants.py          # Enums and scenario definitions
├── log_entry.py         # Log data model with JSONL export
├── simulator.py         # Core log generation engine
├── main.py              # Example usage and demo
├── logs.jsonl           # Generated training data (150 logs)
└── README.md            # This file
```

---

## Quick Start

### Prerequisites
```bash
pip install pandas torch numpy
```

### Run Log Generation
```bash
python main.py
```

**Output:**
- Prints sample logs from each scenario to console
- Exports 150 labeled logs to `logs.jsonl`

### Example Output
```
[2026-04-25T10:00:00] auth_service    | Status: 200 | Latency:   80ms | INFO     | Normal operation
[2026-04-25T10:00:01.261000] database_service | Status: 200 | Latency:  607ms | WARNING  | High database latency
[2026-04-25T10:00:01.903000] auth_service    | Status: 401 | Latency:   73ms | ERROR    | Authentication failed
```

---

## Usage Examples

### Generate Logs for a Specific Scenario
```python
from simulator import LogSimulator
from constants import Scenario, Intensity

sim = LogSimulator(seed=42)

# Generate DB latency scenario
sim.generate_logs(100, Scenario.DB_LATENCY, Intensity.HIGH)
sim.export_jsonl("db_latency_logs.jsonl")
```

### Analyze Generated Logs
```python
import pandas as pd

logs = pd.read_json("logs.jsonl", lines=True)
print(logs[logs['scenario'] == 'AUTH_FAILURE'].head())
print(f"Average latency by scenario:\n{logs.groupby('scenario')['latency_ms'].mean()}")
```

---

## Roadmap

### Phase 1: ✅ Complete
- [x] Log simulator with 5 scenarios
- [x] JSONL export format
- [x] Reproducible generation

### Phase 2: 🔄 In Progress
- [ ] PyTorch neural network classifier (90%+ accuracy)
- [ ] Train/test split evaluation with metrics
- [ ] Confusion matrix and F1-score analysis

### Phase 3: 📋 Future
- [ ] Cohere LLM integration for incident summaries
- [ ] REST API for real-time predictions
- [ ] Web dashboard for visualization
- [ ] Extended scenarios (cascading failures, retry storms)

---

## How It Works

```
1. LOG GENERATION
   Simulator creates N logs per scenario
   Each log includes: timestamp, service, latency, status, severity, scenario label

2. FEATURE EXTRACTION (upcoming)
   Extract features: [latency_ms, status_code, service_id, severity_id]
   
3. MODEL TRAINING (upcoming)
   PyTorch neural network learns scenario classification
   
4. EVALUATION (upcoming)
   Test on unseen logs, measure accuracy and F1-score
   
5. DEPLOYMENT (future)
   Use trained model to classify real-world logs in production
```

---

## Technical Details

- **Language**: Python 3.8+
- **Framework**: PyTorch (upcoming)
- **Data Format**: JSONL (newline-delimited JSON)
- **Reproducibility**: Seeded RNG for deterministic generation
- **Scenarios**: Parameterized by intensity level (LOW/MEDIUM/HIGH)

---

## Contributing

Extend scenarios by modifying `LogSimulator._apply_scenario_effects()` in `simulator.py`:

```python
elif scenario == Scenario.YOUR_SCENARIO:
    latency_mod = {
        Intensity.LOW: 100,
        Intensity.MEDIUM: 300,
        Intensity.HIGH: 800
    }[intensity]
    return (latency_mod, None, Severity.WARNING, "Your scenario message")
```

---

## License

MIT License

---

## Author

Built for Cohere AI SWE application | April 2026 
