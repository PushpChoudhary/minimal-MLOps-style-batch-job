import argparse
import json
import logging
import time
import os
import sys
import yaml
import pandas as pd
import numpy as np

def setup_logger(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def write_error(output_file, version, message):
    output = {
        "version": version,
        "status": "error",
        "error_message": message
    }
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    # Print to stdout per Docker requirements
    print(json.dumps(output, indent=2))

def main():
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description="MLOps Batch Job: Rolling Mean Signal Generator")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--config", required=True, help="Path to config YAML file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument("--log-file", required=True, help="Path to log file")
    args = parser.parse_args()

    # Initialize logger
    logger = setup_logger(args.log_file)
    logger.info("Job started")

    # Default version for fallback in early-stage error handling
    version = "unknown"

    try:
        # --- 1. Load + validate config ---
        if not os.path.exists(args.config):
            raise FileNotFoundError(f"Config file not found: {args.config}")
        
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
            
        if not isinstance(config, dict):
            raise ValueError("Invalid config format. Expected a YAML dictionary.")

        required_keys = ['seed', 'window', 'version']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required config key: {key}")

        seed = config['seed']
        window = config['window']
        version = config['version']

        # Set determinism
        np.random.seed(seed)
        logger.info(f"Config loaded & validated. Version: {version}, Seed: {seed}, Window: {window}")

        # --- 2. Load + validate dataset ---
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file not found: {args.input}")

        try:
            df = pd.read_csv(args.input)
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")

        if df.empty:
            raise ValueError("Input CSV is empty")

        if 'close' not in df.columns:
            raise KeyError("Missing required column: 'close'")

        rows_processed = len(df)
        logger.info(f"Dataset loaded successfully. Rows: {rows_processed}")

        # --- 3. Rolling mean ---
        logger.info(f"Computing rolling mean with window {window}")
        df['rolling_mean'] = df['close'].rolling(window=window).mean()

        # --- 4. Signal ---
        logger.info("Generating signals")
        # Handling the first window-1 rows: 
        # The rolling mean is NaN for the first window-1 rows. We will explicitly drop these NaNs 
        # before computing the signal and signal rate to maintain statistical consistency.
        valid_data = df.dropna(subset=['rolling_mean']).copy()
        valid_data['signal'] = np.where(valid_data['close'] > valid_data['rolling_mean'], 1, 0)
        
        # --- 5. Metrics + timing ---
        signal_rate = valid_data['signal'].mean() if not valid_data.empty else 0.0
        latency_ms = int((time.time() - start_time) * 1000)

        output_metrics = {
            "version": version,
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(float(signal_rate), 4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status": "success"
        }

        with open(args.output, 'w') as f:
            json.dump(output_metrics, f, indent=2)

        logger.info(f"Metrics summary: signal_rate={output_metrics['value']}, latency_ms={latency_ms}")
        logger.info("Job ended with status: success")
        
        # Print final metrics JSON to stdout
        print(json.dumps(output_metrics, indent=2))
        sys.exit(0)

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Job failed: {error_msg}")
        logger.info("Job ended with status: error")
        
        write_error(args.output, version, error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()