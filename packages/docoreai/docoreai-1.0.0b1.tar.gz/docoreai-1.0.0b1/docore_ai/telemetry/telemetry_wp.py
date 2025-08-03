# telemetry_wp.py
import sys
import os
from docore_ai.utils.helpers import get_retry_session
from .config import DOCOREAI_API_URL
from .config import DOCOREAI_TOKEN, ALLOW_SYSTEM_MESSAGE_INJECTION
import threading
import requests
import time
import json
from datetime import datetime
import platform
from docore_ai.utils.logger import dprint
from docore_ai.init_engine import _ENGINE_STATE

from docore_ai.telemetry.tracker import get_version_info
from docore_ai.telemetry import usage_limits
from docore_ai.init_engine import get_state



#from token_utils import token_profiler  # your updated token_profiler
#from tracker import get_version_info    # your version tracker (docoreai_version, etc.)

def get_python_version():
    return platform.python_version()

def save_telemetry_to_wordpress(data: dict, messages=None, response=None):
    #dprint("Entered save_telemetry_to_wordpress")
    #enriched_data = enrich_telemetry_data(data, messages, response) #Not required delete it
    try:
        
        url = "https://docoreai.com/wp-json/docoreai/v1/telemetry?action=true"
        #dprint("Telemetry Payload being sent:", enriched_data) #delete  this later ToDO
        #response = requests.post(url, json=telemetry_data, timeout=10)
        # new change
        #dprint("attempting to sent success telemetry data...")
        headers = {
            "X-DocoreAI-Token": DOCOREAI_TOKEN 
        }
        #dprint(DOCOREAI_TOKEN)
        session = get_retry_session()
        response = session.post(
            url,
            json=data,
            timeout=10,
            headers=headers,
            proxies={"http": None, "https": None}  # ✅ Bypass system proxy
        )
        #dprint("response status code", response.status_code)
        if response.status_code in (200, 204):
            #dprint("📤 Telemetry sent. Evaluating response...")
            try:
                response_data = response.json()
                remaining = response_data.get("remaining_hits")

                if remaining == 0:
                    dprint("🚫 Daily telemetry limit reached. Please upgrade your plan.")
                    return

                # ✅ Only increment if server accepted it #29-Jul
                if response_data.get("status") == "success":
                    usage_limits.increment_usage(data.get("user_id"))

                dprint("📊 Telemetry recorded successfully.")

                if remaining is not None:
                    dprint(f"🧮 Remaining telemetry quota: {remaining}")
                    dprint("🟢 Ready for next request — OpenAI/Groq/HTTP calls will be logged here.")
            except ValueError:
                #  No JSON returned — still a success
                dprint("✅ Telemetry sent (non-JSON response)")                    
        else:
            dprint(f"⚠️ Telemetry logging failed: {response.status_code} - {response.text}")
    except Exception as e:
        dprint(f"⚠️ Telemetry transmission failed: {e}")

def save_failure_telemetry_to_wordpress(telemetry_data: dict, messages=None, response=None):
    dprint("Failure Telemetry")
    try:
        #telemetry_data = enrich_telemetry_data(telemetry_data, messages, response)

        url = "https://docoreai.com/wp-json/docoreai/v1/telemetry-failure?action=true"
        dprint("🧪 Failure telemetry payload:", telemetry_data)  # TODO: Remove this in production

        #"Authorization": f"Bearer {DOCOREAI_TOKEN}" REMOVED
        headers = {
            "X-DocoreAI-Token": DOCOREAI_TOKEN
        }
        session = get_retry_session()
        response = session.post(
            url,
            json=telemetry_data,
            headers=headers,
            timeout=10,
            proxies={"http": None, "https": None}  # ✅ Bypass system proxy
        )

        if response.status_code in (200, 204):
            dprint("🗂️ Failure telemetry saved.")
        else:
            dprint(f"⚠️ Failure telemetry error: {response.status_code} - {response.text}")
    except Exception as e:
        dprint(f"⚠️ Failed to log failed telemetry: {e}")




#New implementation 08-06-25
def prepare_telemetry_payload(
    user_id,
    user_content,
    role,
    model_name,
    execution_time,
    prompt_version,
    version_info,
    success,    
    response_content=None,
    usage=None,
    bloat_info=None,
    system_injected=0,  
):
    payload = {
        "user_id": int(user_id),
        "local_timestamp": datetime.now().astimezone().isoformat(),
        "prompt_length": len(user_content),
        "response_length": len(response_content["optimized_response"]) if success and response_content else 0,
        "model_name": model_name,
        "prompt_type": _ENGINE_STATE["prompt_type"],
        "role": role,
        "execution_time": float(execution_time),
        "success": int(success),
        "temperature_profile": (
            str(response_content.get("temperature", f"{role}::no_injection"))
        ),
        "docoreai_version": version_info.get("docoreai_version", "unknown"),
        "python_version": platform.python_version(),
        "prompt_version": prompt_version
    }
    payload["system_injected"] = int(os.getenv("ALLOW_SYSTEM_MESSAGE_INJECTION", "true").strip().lower() == "true")

    if success and usage and bloat_info:
        payload.update({
            "temperature": response_content.get("temperature", -1),  # -1 or None indicates unknown
            "bloated_prompt": int(bloat_info["bloat_flag"]),
            "bloated_score": bloat_info["bloat_score"],
            "cost_estimation": 1.12,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "total_tokens": usage.total_tokens,
        })
    
    return payload

import threading

def log_telemetry_to_wordpress(success: bool, telemetry_data: dict, failure: bool = False):
    #dprint("Entered log_telemetry_to_wordpress")
    try:
        #dprint(f"🚀 Logging telemetry. Success: {success}, Failure: {failure}")
        #telemetry_data = enrich_telemetry_data(telemetry_data)

        state1 = get_state()
        is_account_active = state1.get("account_state") in ("activation_pending","inactive","expired")
        if is_account_active:
            dprint("❌ Verify your email & Upgrade Access")
            dprint("Account Status: " . state1.get("account_state") )
            sys.exit(1)


        if success:
            telemetry_data = enrich_telemetry_data(telemetry_data)
            #thread = threading.Thread(target=save_telemetry_to_wordpress, args=(telemetry_data,))
            # 🛑 Add this limit check here
            user_id = telemetry_data.get("user_id")

            daily_limit = usage_limits.get_daily_limit_from_server()

            if daily_limit is None:
                dprint("❌ Daily limit could not be determined from server. Skipping telemetry to avoid mismatch.")
                return

            if usage_limits.has_hit_limit(user_id, daily_limit):
                dprint("🚫 Local usage limit reached. Skipping telemetry send. Please upgrade for higher limits")
                return
            save_telemetry_to_wordpress(telemetry_data)
        elif failure:
            telemetry_data = enrich_telemetry_data(telemetry_data)
            #thread = threading.Thread(target=save_failure_telemetry_to_wordpress, args=(telemetry_data,))
            save_failure_telemetry_to_wordpress(telemetry_data)
        else:
            dprint("⚠️ Invalid telemetry state — neither success nor failure")
            return
        #thread.daemon = True
        #thread.start()
        #dprint("✅ Telemetry logging thread started.")
    except Exception as e:
        dprint(f"Warning: Telemetry thread failed: {e}")




# telemetry_wp.py


from docore_ai.telemetry.token_utils import token_profiler
from docore_ai.telemetry.tracker import get_version_info
from docore_ai.prompt_updates.prompt_loader import get_current_bundle
state = get_state()
def enrich_telemetry_data(data: dict, messages=None, response=None) -> dict:
    #dprint("Entered enrich_telemetry_data")

    # 1. Safe fallback for user_id
    if not data.get("user_id") or state.get("user_id"):
        data["user_id"] = state.get("user_id")
        #dprint("🛠️ [enrich] Filled missing: user_id")

    # 2. Prompt version
    if not data.get("prompt_version"):
        try:
            data["prompt_version"] = get_current_bundle().get("prompt_version", "unknown")
            dprint("🛠️ [enrich] Filled missing: prompt_version")
        except Exception:
            data["prompt_version"] = "unknown"
            dprint("⚠️ [enrich] Failed to fetch prompt_version")

    # 3. Python version
    if not data.get("python_version"):
        data["python_version"] = platform.python_version()
        dprint("🛠️ [enrich] Filled missing: python_version")

    # 4. DoCoreAI version
    if not data.get("docoreai_version"):
        try:
            data["docoreai_version"] = get_version_info().get("docoreai_version", "unknown")
            dprint("🛠️ [enrich] Filled missing: docoreai_version")
        except Exception:
            data["docoreai_version"] = "unknown"
            dprint("⚠️ [enrich] Failed to fetch docoreai_version")

    # 5. model_name fallback
    if not data.get("model_name"):
        data["model_name"] = state.get("model_name", "unknown")
        dprint("🛠️ [enrich] Filled missing: model_name")

    # 6. Extract user_content and role from messages
    if messages:
        for msg in messages:
            if msg.get("role") == "user" and not data.get("user_content"):
                data["user_content"] = msg.get("content", "")
                dprint("🛠️ [enrich] Filled missing: user_content (from messages)")
            if msg.get("role") == "system" and not data.get("role"):
                data["role"] = "system"
                dprint("🛠️ [enrich] Filled missing: role (from messages)")

    # Fallback for role
    if not data.get("role"):
        data["role"] = "user"
        dprint("🛠️ [enrich] Filled missing: role (default user)")

    # 7. Prompt length
    if not data.get("prompt_length") and data.get("user_content"):
        data["prompt_length"] = len(data["user_content"])
        dprint("🛠️ [enrich] Filled missing: prompt_length")

    # 8. Bloat info
    if not data.get("bloat_info") and data.get("user_content") and data.get("model_name"):
        try:
            data["bloat_info"] = token_profiler(data["user_content"], data["model_name"])
            dprint("🛠️ [enrich] Filled missing: bloat_info")
        except Exception as e:
            data["bloat_info"] = {}
            dprint(f"⚠️ [enrich] Bloat info generation failed: {e}")

    # 9. Response length
    if not data.get("response_length") and response:
        try:
            content = response.choices[0].message.content
            data["response_length"] = len(content)
            dprint("🛠️ [enrich] Filled missing: response_length")
        except Exception as e:
            data["response_length"] = 0
            dprint(f"⚠️ [enrich] Failed to get response_length: {e}")

    return data
