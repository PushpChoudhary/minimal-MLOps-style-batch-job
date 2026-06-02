# MLOps Batch Job: Signal Generation

This repository contains a minimal, production-ready MLOps batch job that reads OHLCV data, calculates a rolling mean on the `close` column, and generates a binary trading signal. It ensures high reproducibility, robust validation, and extensive observability through structured logging and JSON metrics.

## Features
- **Deterministic:** Ensures reproducibility using a configurable seed.
- **Robust Error Handling:** Writes structured JSON error outputs on failures (e.g., missing files, missing columns).
- **Dockerized:** Runs cleanly in an isolated container.

## Local Run Instructions

1. **Create a virtual environment (optional but recommended):**
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
```
Install dependencies:

```bash
   pip install -r requirements.txt
```
Run the script:
```bash
   python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```