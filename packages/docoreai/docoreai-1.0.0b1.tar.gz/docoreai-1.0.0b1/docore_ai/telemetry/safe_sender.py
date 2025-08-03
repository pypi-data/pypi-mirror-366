# docore_ai/telemetry/safe_sender.py

from datetime import datetime
import requests
import threading
import platform
from docore_ai.init_engine import _ENGINE_STATE, get_state
from docore_ai.prompt_updates.prompt_loader import get_current_bundle
from docore_ai.telemetry.tracker import get_version_info
from docore_ai.utils.logger import dprint
from .config import DOCOREAI_TOKEN

#from docore_ai.telemetry.token_utils import token_profiler
state = get_state()

DOCOREAI_TELEMETRY_URL = "https://docoreai.com/wp-json/docoreai/v1/telemetry?action=true"

def send_safe_telemetry(payload: dict):
    """
    Sends telemetry data to the DoCoreAI WordPress server bypassing any active proxy.
    """
    dprint("PAYLOAD ***********",payload)

    headers = {
        "X-DocoreAI-Token": DOCOREAI_TOKEN
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
            dprint("[✓] Proxy telemetry sent successfully.")
        else:
            dprint(f"[✘] Proxy telemetry failed ({response.status_code}): {response.text}")
    except Exception as e:
        dprint(f"[⚠️] Proxy telemetry exception: {e}")

def send_telemetry_async(args, kwargs, response):

    payload = construct_telemetry_payload(args, kwargs, response)
    dprint("PAYLOAD",payload)
    thread = threading.Thread(target=send_safe_telemetry, args=(payload,))
    thread.daemon = True
    thread.start()

def construct_telemetry_payload(args, kwargs, response) -> dict:
    """
    Reconstructs telemetry data from intercepted OpenAI call.
    Only works for patch-based interception (auto_patch).
    """
    try:
        messages = kwargs.get("messages", [])
        dprint("messages ************: ", messages)
        role = "unknown"
        prompt_length = 0

        for msg in messages:
            if msg.get("role") == "user":
                #prompt_length = len(msg.get("content", ""))
                prompt_length = sum(len(msg.get("content", "")) for msg in messages if msg.get("role") == "user")
            elif msg.get("role") == "system":
                continue
            else:
                role = next((msg.get("role") for msg in messages if msg.get("role") not in ("user", "system")), "unknown")

        response_text = ""
        if hasattr(response, "choices"):
            response_text = response.choices[0].message.content
        elif isinstance(response, dict):
            # Fallback for legacy SDK or mock
            response_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            #bloat_info = token_profiler(msg.get("content", ""), state.get("model_name"))


        payload = {
            "user_id": _ENGINE_STATE["user_id"],
            "local_timestamp": datetime.now().astimezone().isoformat(),
            "prompt_length": prompt_length,
            "response_length": len(response_text),
            "model_name": state.get("model_name"), #kwargs.get("model", "unknown"),
            "prompt_type": _ENGINE_STATE["prompt_type"] ,
            "role": role,
            "execution_time": 0,
            "success": 1,
            "temperature_profile": kwargs.get("temperature", "NA"),
            "docoreai_version":get_version_info().get("docoreai_version", "unknown"),
            "python_version": platform.python_version(),
            "prompt_version": get_current_bundle().get("prompt_version", "unknown"),
            "temperature": kwargs.get("temperature", None), #(str(response_content["temperature"]) if success and response_content else f"{role}::error"        ),
            "bloated_prompt": 0, # int(bloat_info["bloat_flag"]),
            "bloated_score": 0, # bloat_info["bloat_score"],
            "cost_estimation": 1.12,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return payload

    except Exception as e:
        dprint(f"[⚠️] Failed to construct telemetry payload: {e}")
        return {}
