# tracker.py
import json
import sys
#import pkg_resources # depricated

from datetime import datetime
from .config import TELEMETRY_ENABLED, TELEMETRY_LOCAL_FILE, DOCOREAI_API_URL, DOCOREAI_TOKEN
from .token_auth import validate_token
import requests
from docore_ai.utils.logger import dprint
try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # fallback for Python < 3.8

def get_version_info():
    return {
        "docoreai_version": version("docoreai"),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

def send_telemetry(notes: str = "Upgrade"):
    """Main telemetry logic"""
    if not TELEMETRY_ENABLED:
        return dprint("⚙️ Telemetry is disabled via .env")

    if not validate_token():
        return dprint("❌ Invalid or missing token. Telemetry skipped.")

    try:
        data = {
            "token": DOCOREAI_TOKEN,
            "event": "upgrade",
            "notes": notes,
            **get_version_info()
        }

        # Save locally
        with open(TELEMETRY_LOCAL_FILE, "a") as f:
            f.write(json.dumps(data) + "\n")

        # Send to remote server
        response = requests.post(f"{DOCOREAI_API_URL}/telemetry", json=data)
        if response.status_code == 200:
            dprint("✅ Telemetry successfully sent.")
        else:
            dprint(f"⚠️ Telemetry failed: {response.status_code} - {response.text}")
    except Exception as e:
        dprint(f"⚠️ Error sending telemetry: {e}")
