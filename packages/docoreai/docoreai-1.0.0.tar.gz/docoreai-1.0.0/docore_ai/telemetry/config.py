import os
from dotenv import load_dotenv
from pathlib import Path

from docore_ai.init_engine import get_state

state=get_state()
dotenv_path = state.get("env_path")
load_dotenv(dotenv_path=dotenv_path, override=True)

# Configuration variables
DOCOREAI_API_URL = os.getenv("DOCOREAI_API_URL", "https://docoreai.com")
TELEMETRY_ENABLED = os.getenv("DOCOREAI_TELEMETRY", "True").strip().lower() in ("true", "1", "yes")
TELEMETRY_LOCAL_FILE = os.getenv("DOCOREAI_LOCAL_FILE", "telemetry_log.json") #TBD
DOCOREAI_TOKEN = os.getenv("DOCOREAI_TOKEN", "")  # Must be set by user
ALLOW_SYSTEM_MESSAGE_INJECTION=os.getenv("ALLOW_SYSTEM_MESSAGE_INJECTION")