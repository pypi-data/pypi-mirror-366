import os
import json
from datetime import datetime
from docore_ai.utils.helpers import get_retry_session
from docore_ai.utils.logger import dprint
from docore_ai.init_engine import _ENGINE_STATE
from .config import DOCOREAI_TOKEN, DOCOREAI_API_URL

USAGE_FILE = os.path.join(os.path.dirname(__file__), ".docoreai_usage.json")

def _load_usage_data():
    if not os.path.exists(USAGE_FILE):
        return {}
    try:
        with open(USAGE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_usage_data(data):
    try:
        with open(USAGE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        dprint(f"⚠️ Failed to save usage file: {e}")

def get_usage_today(user_id):
    """Returns count of prompts used today by user_id"""
    today = datetime.now().strftime("%Y-%m-%d")
    data = _load_usage_data()
    entry = data.get(str(user_id))
    if not entry or entry.get("date") != today:
        return 0
    return entry.get("count", 0)

def increment_usage(user_id):
    """Increments count for today for the given user"""
    today = datetime.now().strftime("%Y-%m-%d")
    data = _load_usage_data()
    key = str(user_id)

    if key not in data or data[key].get("date") != today:
        data[key] = {"date": today, "count": 1}
    else:
        data[key]["count"] += 1

    _save_usage_data(data)
    #dprint(f"📈 Local usage updated: {data[key]}")

def reset_usage(user_id):
    data = _load_usage_data()
    if str(user_id) in data:
        data.pop(str(user_id))
        _save_usage_data(data)
        dprint(f"🧹 Cleared usage record for user {user_id}")

def get_daily_limit_from_server():
    """Contact the server to get the user's actual allowed daily limit."""
    try:
        url = f"{DOCOREAI_API_URL}/wp-json/docoreai/v1/get_member_info"
        headers = {
            "X-DocoreAI-Token": DOCOREAI_TOKEN
        }
        session = get_retry_session()
        resp = session.post(url, headers=headers, timeout=8)

        if resp.status_code != 200:
            dprint(f"❌ Failed to fetch plan info. Status: {resp.status_code}")
            return None

        data = resp.json()
        level_id = int(data.get("level_id", 2))
        dprint(f"📦 Server reported Level: {level_id}")
        return {
            2: 10,
            3: 300,
            4: 1000
        }.get(level_id, 10)

    except Exception as e:
        dprint(f"❌ Error getting daily limit: {e}")
        return None

def has_hit_limit(user_id, limit):
    """Helper: checks if local usage has reached the provided limit"""
    if limit is None:
        return False
    return get_usage_today(user_id) >= limit
