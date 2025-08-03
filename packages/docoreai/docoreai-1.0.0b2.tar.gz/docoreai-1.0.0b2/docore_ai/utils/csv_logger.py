# File: docore_ai/telemetry/csv_logger.py  - STREAMLIT
import csv
import time
import base64
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
from docore_ai.init_engine import get_state,initialize

# Debug print: import your project dprint, or fallback to print
try:
    from docore_ai.utils.logger import dprint
except ImportError:
    def dprint(*args, **kwargs):
        pass


# CSV header columns (fixed order)
HEADER = [
    "client_prompt_id",
    "user_id",
    "user_message",
    "role",
    "response",
    "local_timestamp",
    "prompt_length",
    #"response_length",
    "temperature",
    "model_name",
    #"prompt_type",
    "execution_time",
    "success",
    "bloated_prompt",
    "bloated_score",
    "cost_estimation",
    #"temperature_profile",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "docoreai_version",
    "python_version",
    #"prompt_version",
]

# Target CSV location: current working directory
#CSV_PATH = Path.cwd() / "docoreai_log.csv"
CSV_PATH = os.path.join(os.path.dirname(__file__), "docoreai_log.csv")
CSV_PATH=Path(CSV_PATH)

def _ensure_header():
    try:

        if not CSV_PATH.exists():
            with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(HEADER)
            dprint("[csv_logger] Created CSV with header.")
    except Exception as e:
        dprint(f"[csv_logger] Error ensuring header: {e}")

def append_telemetry(payload):
    try:
        _ensure_header()

        state = get_state()
        is_account_inactive = state.get("account_state") in ("activation_pending","inactive",)
        
        if is_account_inactive:
            dprint("❌ Please verify your email & upgrade access")
            return

        # Assign unique ID and timestamp
        client_id = str(int(time.time() * 1000))
        payload["client_prompt_id"] = client_id
        timestamp = datetime.utcnow().isoformat(sep=" ", timespec="seconds")
        payload["local_timestamp"] = timestamp

        new_row = pd.DataFrame([payload], columns=HEADER)

        try:
            existing = pd.read_csv(CSV_PATH)
        except FileNotFoundError:
            existing = pd.DataFrame(columns=HEADER)

        #combined = pd.concat([existing, new_row], ignore_index=True)
        
        combined = pd.concat([x for x in [existing, new_row] if not x.empty], ignore_index=True) #31-Jul
        
        # Filter to last 30 days only
        combined['local_timestamp'] = pd.to_datetime(combined['local_timestamp'], errors='coerce')
        invalid_rows = combined[combined['local_timestamp'].isna()]

        if not invalid_rows.empty:
            for _, row in invalid_rows.iterrows():
                dprint(f"[csv_logger] Warning: Invalid timestamp in row with client_prompt_id={row.get('client_prompt_id', 'N/A')}")

        combined = combined.dropna(subset=['local_timestamp'])
        cutoff = datetime.utcnow() - timedelta(days=30)

        combined = combined[combined['local_timestamp'] >= cutoff]
        
        if is_account_inactive:
            dprint("❌ Please verify your email & upgrade access")
        else:
            combined.to_csv(CSV_PATH, index=False, encoding='utf-8')
            #dprint(f"[csv_logger] Appended new telemetry row with client_prompt_id={client_id}")
    except Exception as e:
        dprint(f"[csv_logger] Failed to append telemetry: {e}")

