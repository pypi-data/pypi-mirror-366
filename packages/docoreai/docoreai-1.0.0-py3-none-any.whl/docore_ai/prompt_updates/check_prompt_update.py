# docore_ai/prompt_updates/check_prompt_update.py

import threading
import logging
import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from .prompt_loader import set_current_bundle
from docore_ai.utils.logger import dprint, dsys_exit

# Load environment variables
dotenv_path = Path.cwd() / ".env"
load_dotenv(dotenv_path)

# Configuration
DOCOREAI_API_URL = "https://docoreai.com"
DOCOREAI_TOKEN = os.getenv("DOCOREAI_TOKEN")

logger   = logging.getLogger(__name__)
_lock    = threading.Lock()
_checked = False
_result  = None
_raw_prompt = None

def check_prompt_update(user_id: int):
    """
    1. Call server with prompt_version and user_id.
    2. If server says update, cache new bundle in memory.
    3. Return dict: { updated, bundle, status, error }.
    """
    global _checked, _result, _raw_prompt

    with _lock:
        if _checked:
            return _result
        _checked = True

        current_version = None
        local_bundle = None

        if not DOCOREAI_API_URL or not DOCOREAI_TOKEN:
            dsys_exit("⚠️  DOCOREAI_API_URL and DOCOREAI_TOKEN must be set in .env")

        payload = {
            "token": DOCOREAI_TOKEN,
            "user_id": user_id,
            "prompt_version": current_version,
        }

        session = requests.Session()
        session.trust_env = False  # Prevent system proxies from interfering

        try:
            resp = session.post(
                f"{DOCOREAI_API_URL}/wp-json/docoreai/v1/prompts/check",
                json=payload,
                timeout=5
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            #import traceback
            dprint(f"❌ Prompt update check failed: {e}")
            #traceback.print_exc()
            data = {}  # Prevent crashes in later steps

        # Validate response
        status_flag = data.get("status") if isinstance(data, dict) else None
        if status_flag is None:
            dsys_exit("Malformed server response: missing status")

        # No update needed
        if not data.get("prompt_update_required", False):
            bundle = data.get("bundle", {})
            set_current_bundle(bundle)
            _result = {
                "updated": False,
                "bundle": bundle,
                "status": status_flag,
                "error": None
            }
            return _result

        # Update required
        try:
            new_bundle = data["bundle"]
            version_line = new_bundle["prompt_version"]
            raw_prompt   = new_bundle["system_message"]
            _raw_prompt = raw_prompt
        except KeyError as e:
            dsys_exit(f"Missing field in bundle: {e}")

        dprint("system message loaded...")
        set_current_bundle(new_bundle)

        _result = {
            "updated": True,
            "system_message": raw_prompt,
            "prompt_version": version_line,
            "status": status_flag,
            "error": None
        }
        return _result

def get_raw_prompt_new():
    return _raw_prompt
