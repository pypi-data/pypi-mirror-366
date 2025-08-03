# NEW  safe_sender.py 07-06-25
# docore_ai/telemetry/safe_sender.py

import requests
from .config import DOCOREAI_TOKEN

DOCOREAI_TELEMETRY_URL = "https://docoreai.com/wp-json/docoreai/v1/telemetry?action=true"

def send_safe_telemetry(payload: dict):
    """
    Sends telemetry data to the DoCoreAI WordPress server bypassing any active proxy.
    """

    headers = {
        "Authorization": f"Bearer {DOCOREAI_TOKEN}"
    }    
    try:
        response = requests.post(
            DOCOREAI_TELEMETRY_URL,
            json=payload,
            headers=headers,
            timeout=10,
            proxies={"http": None, "https": None}  # ✅ Bypass system proxy
        )
        if response.status_code == 200:
            print("[✓] Proxy telemetry sent successfully.")
        else:
            print(f"[✘] Proxy telemetry failed ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[⚠️] Proxy telemetry exception: {e}")
