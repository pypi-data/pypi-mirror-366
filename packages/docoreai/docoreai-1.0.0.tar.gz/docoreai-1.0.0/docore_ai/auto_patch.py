# auto_patch.py
import os
import sys
import time
from dotenv import load_dotenv 
from pathlib import Path
from docore_ai.utils.csv_logger import append_telemetry
from docore_ai.utils.logger import dprint, dsys_exit
from docore_ai.init_engine import _ENGINE_STATE, get_state, initialize



env_path = os.environ.get("DOCOREAI_ENV_PATH")
dotenv_path = Path(env_path) / ".env"

if env_path:
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=True)
        #dprint(f"✅ .env loaded from {dotenv_path}")
    else:
        dprint(f"⚠️ .env file not found at {dotenv_path}")
else:
    dprint("⚠️ DOCOREAI_ENV_PATH not set")


# ✅ Step 1: Early exit if not enabled (safe for .pth context) #SystemExit also happens when .env file is missing
if os.getenv("DOCOREAI_LOG_ONLY", "false").lower() != "true":
    dsys_exit("Check if .env file exists or restart app to auto-create a new file\n\n"
                     "run `docoreai start`\n\n")  # or simply return if you wrap this in a function

if os.getenv("DOCOREAI_ENABLE", "true").lower() != "true":
    dsys_exit(
        "\n🔒 DoCoreAI is currently DISABLED.\n\n"
        "👉 To enable it:\n"
        "1. Open your .env file and add or update:\n"
        "   DOCOREAI_ENABLE=true\n\n"
        "2. Save the file.\n"
        "3. Run the following command in your terminal:\n"
        "   docoreai start\n\n"
        "ℹ️ This will activate the dopatch engine for your Python environment.\n"
    )    
    

import dotenv
from packaging import version

from docore_ai.telemetry.safe_sender import send_telemetry_async
from pathlib import Path


from docore_ai.telemetry.telemetry_wp import log_telemetry_to_wordpress, prepare_telemetry_payload
from docore_ai.telemetry.token_utils import token_profiler
from docore_ai.telemetry.tracker import get_version_info
from docore_ai.prompt_updates.prompt_loader import get_current_bundle, PromptLoaderError
import json

#dprint("✅ [TEST] DoCoreAI logging is working!")


_already_patched = False  # 🛡️ Module-level flag to prevent double patching



#dprint("✅ [TEST] DoCoreAI logging is working!")
try:
    #initialize()
    model_provider = os.getenv("MODEL_PROVIDER").strip().lower()    
except:
    dsys_exit("❌ MODEL_PROVIDER not set in .env, please update MODEL_PROVIDER")



# ✅ Call this early in your script
#find_dotenv_flexible()

dprint("initiating dopatch...")


try:
    import openai
except ImportError:
    dprint("⚠️ OpenAI not installed. dopatch skipped.")
    openai = None

try:
    import groq
except ImportError:
    dprint("⚠️ Groq not installed. DoCoreAI Groq dopatch skipped.")
    groq = None


DEBUG_PRINT = os.getenv("DOC_DEBUG_PRINT", "False").lower() == "true"


#INJECT_SYS_MSG = os.getenv("ALLOW_SYSTEM_MESSAGE_INJECTION", "true").lower() == "true"
try:
    SYS_MSG = _ENGINE_STATE["prompt_bundle"]["system_message"]
except Exception:
    SYS_MSG = (
    "You are an AI system prompt profiler. Analyze the user request and role to guess "
    "what AI-generated temperature setting would best match the {role}.\n"
    "Return the estimated temperature value only, between 0.0 and 1.0, based on the following:\n"
    "- Low temperature (~0.0–0.3): Precise, factual, deterministic answers.\n"
    "- Medium temperature (~0.4–0.6): Balanced creativity and reasoning.\n"
    "- High temperature (~0.7–1.0): Creative, open-ended or speculative.\n"
    "You MUST generate responses using the estimated temperature.\n"
    "The response must be coherent and informative.\n"
    "Return **ONLY** the following JSON format:\n"
    "{ \"optimized_response\": \"<AI-generated response>\", \"temperature\": <value> }"
)


def patch_openai():
    #dprint("starting dopatch...")
    global _already_patched
    if _already_patched:
        dprint("⚠️ DoCoreAI dopatch already applied. Skipping...")
        return
    _already_patched=True
    initialize()
            
    try:
        model_provider = os.getenv("MODEL_PROVIDER").strip().lower()
    except:
        dsys_exit("❌ MODEL_PROVIDER incorrect in .env file, please update MODEL_PROVIDER")

    
    dprint(f"current model provider: {model_provider}") 

    if model_provider == "groq" and groq:
        if groq is None:
            dprint("⚠️ Groq SDK not installed. Skipping dopatch.")
            return              
        patch_groq()
    elif model_provider == "openai" and openai:
        if openai is None:
            dprint("⚠️ OpenAI SDK not installed. Skipping dopatch.")
            return        
        sdk_version = version.parse(openai.__version__)
        if sdk_version < version.parse("1.0.0"):
            apply_legacy_patch()
        else:
            apply_modern_patch()
    else:
        dsys_exit("Supported model provider not found!")

def str2bool(value: str) -> bool:
    return str(value).strip().lower() in ("yes", "true", "1")

def inject_system_message_if_needed(messages: list[dict]) -> list[dict]:
    
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=True)
    
    inject_enabled = os.getenv("ALLOW_SYSTEM_MESSAGE_INJECTION", "true").strip().lower()
    #dprint(f"🚩 ALLOW_SYSTEM_MESSAGE_INJECTION = {inject_enabled}")
    #dprint(f"🚩 dotenv_path = {dotenv_path}")
    

    #dprint("ALLOW_SYSTEM_MESSAGE_INJECTION =", os.getenv("ALLOW_SYSTEM_MESSAGE_INJECTION"))
    already_has_system = any(msg.get("role") == "system" for msg in messages)

    if inject_enabled == "false":
        if already_has_system:
            dprint("⚠️ System message detected and injection is disabled — skipping injection.")
        else:
            dprint("- Injection is disabled and no system message found — continuing without injection.")
        return messages

    dprint("- System message injection is enabled.")

    if already_has_system:
        dprint("🧹 Removing existing system messages before injection.")
        messages = [m for m in messages if m.get("role") != "system"]

    new_messages = [{"role": "system", "content": SYS_MSG}] + messages

    #dprint("🧠 System message injected into prompt.")
    #dprint(new_messages)
    return new_messages


def apply_legacy_patch():
    try:
        original_create = openai.ChatCompletion.create

        def patched_create(*args, **kwargs):
            dprint("intercepted: legacy...")

            if kwargs.get("skip_tracking") is True:
                dprint("🚫 Telemetry skipped (skip_tracking=True)")
                return original_create(*args, **kwargs)
    
            # Inject system message if enabled
            if "messages" in kwargs:
                kwargs["messages"] = inject_system_message_if_needed(kwargs["messages"])
                #dprint(kwargs["messages"])
                # ✅ dprint the final message list with roles
            
                #dprint("final messages sent to llm openai legacy...")
                # for msg in kwargs.get("messages", []):
                #     dprint(f"  ->>> {msg.get('role')}: {msg.get('content')}")
            else:

                messages = []
            try:    
                start_time = time.time()    
                response = original_create(*args, **kwargs) #This is where the prompt is actually sent to the LLM.
                kwargs["execution_time"] = round(time.time() - start_time, 2)
                state = get_state()
                if not kwargs.get("skip_tracking") and not state.get("skip_tracking"):
                    prepare_and_log_telemetry_from_args_kwargs_response(args, kwargs, response, success=True)
                return response
            except Exception as e:
                dprint(f"❌ LLM call failed (legacy dopatch): {e}")
                prepare_and_log_failure_telemetry(args, kwargs, success=False)
                #raise 

            

        openai.ChatCompletion.create = patched_create #replaces the actual OpenAI SDK method with your modified one
        dprint("..legacy dopatch applied")

    except Exception as e:
        dprint(f"⚠️ DoCoreAI legacy dopatch failed: {e}")


def apply_modern_patch():
    try:
        from openai import Client
        original_client_init = Client.__init__

        def patched_client_init(self, *args, **kwargs):
            #dprint("🔧 Patched Client.__init__ triggered.")
            original_client_init(self, *args, **kwargs)

            try:
                original_create = self.chat.completions.create

                def patched_create(*args2, **kwargs2):
                    dprint("intercepted: modern...")


                    if kwargs2.get("skip_tracking") is True:
                        dprint("🚫 Telemetry skipped (skip_tracking=True)")
                        return original_create(*args2, **kwargs2)

                    # Inject system message
                    #dprint("Before: ", kwargs2["messages"] )
                    if "messages" in kwargs2:
                        kwargs2["messages"] = inject_system_message_if_needed(kwargs2["messages"])
                        #dprint(kwargs2["messages"] )
                        # ✅ dprint the final message list with roles
                        #dprint("final messages sent to llm openai modern...")
                        for msg in kwargs2.get("messages", []):
                            dprint(f"->>>->>>")
                             #dprint(f"  ->>> {msg.get('role')}: {msg.get('content')}")
                    #dprint("After if : ", kwargs2["messages"] )
                    try:
                        start_time = time.time()    
                        response = original_create(*args2, **kwargs2)
                        kwargs2["execution_time"] = round(time.time() - start_time, 2)
                        state = get_state()
                        if not kwargs2.get("skip_tracking") and not state.get("skip_tracking"):
                            prepare_and_log_telemetry_from_args_kwargs_response(args2, kwargs2, response, success=True)
                            #send_telemetry_async(args2, kwargs2, response)
                        return response    
                    except Exception as e:
                        dprint(f"❌ LLM call failed (mordern dopatch): {e}")
                        prepare_and_log_failure_telemetry(args2, kwargs2, success=False)
                        #raise 
                    

                self.chat.completions.create = patched_create
                dprint("modern dopatch applied...")

            except Exception as e:
                dprint(f"⚠️ Client dopatch failed: {e}")

        Client.__init__ = patched_client_init

    except Exception as e:
        dprint(f"⚠️ DoCoreAI modern dopatch failed: {e}")
def patch_groq():
    try:
        from groq import Client
        original_client_init = Client.__init__

        def patched_client_init(self, *args, **kwargs):
            #dprint("🔧 Patched Groq Client.__init__ triggered.")
            original_client_init(self, *args, **kwargs)

            try:
                original_create = self.chat.completions.create

                def patched_create(*args3, **kwargs3):
                    dprint("intercepted: groq")

                    #if kwargs3.get("skip_tracking") is True:
                    #    dprint("🚫 Telemetry skipped (skip_tracking=True)")
                    #    return original_create(*args2, **kwargs3)
                    skip_tracking = kwargs3.pop("skip_tracking", None)
                    if skip_tracking is True:
                        dprint("🚫 Telemetry skipped (skip_tracking=True)")
                        return original_create(*args3, **kwargs3)

                    if "messages" in kwargs3:
                        kwargs3["messages"] = inject_system_message_if_needed(kwargs3["messages"])
                        #dprint("final messages sent to llm (Groq)...")
                        # for msg in kwargs3.get("messages", []):
                        #     dprint(f"  ->>> {msg.get('role')}: {msg.get('content')}")
                    
                    try:
                        start_time = time.time() 
                        response = original_create(*args3, **kwargs3)
                        kwargs3["execution_time"] = round(time.time() - start_time, 2)
                        state = get_state()
                        if not skip_tracking and not state.get("skip_tracking"):
                            prepare_and_log_telemetry_from_args_kwargs_response(args3, kwargs3, response, success=True)
                            #send_telemetry_async(args3, kwargs3, response)    
                        return response                                                
                    except Exception as e:
                        dprint(f"❌ LLM call failed (groq dopatch): {e}")
                        prepare_and_log_failure_telemetry(args3, kwargs3, success=False)
                        #raise 

                self.chat.completions.create = patched_create
                #dprint("✅ Groq dopatch applied (Client.chat.completions.create)")

            except Exception as e:
                dprint(f"⚠️ Groq client dopatch failed: {e}")

        Client.__init__ = patched_client_init

    except Exception as e:
        dprint(f"⚠️ DoCoreAI Groq modern dopatch failed: {e}")

if not _already_patched:
     patch_openai()


def prepare_and_log_telemetry_from_args_kwargs_response(args, kwargs, response, success=True):

    try:
        state = get_state()
        model_name = kwargs.get("model", state.get("model_name"))
        execution_time = kwargs.get("execution_time", 0)
        current_user_id = state.get("user_id")
        is_token_valid = state.get("token_valid")
        is_account_active = state.get("account_state") in ("active",)
                
        #dprint(f"🧪 Token valid: {is_token_valid}, Account active: {is_account_active}, user_id: {current_user_id}")

        user_content = ""
        role = ""
        for msg in kwargs.get("messages", []):
            if msg.get("role") == "user":
                user_content = msg.get("content", "")
                import re
                match = re.search(r'role:\s*"?([^"\n]+)"?', user_content, re.IGNORECASE)
                if match:
                    role = match.group(1).strip()  # 🎯 Extracted semantic role
                else:
                    role = msg.get("role")  # fallback to "user" or similar
            elif msg.get("role") == "system" and not role:
                role = msg.get("role")


        #response_content = json.loads(response.choices[0].message.content)
        try:
            raw = response.choices[0].message.content
            dprint(f"- Raw LLM response content: {raw[:50]}...")

            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                #dprint("✅ LLM response parsed as JSON dictionary.")
                response_content = parsed
            else:
                #dprint("ℹ️ LLM response is valid JSON but not a dictionary — using raw.")
                response_content = { "optimized_response": raw }  # 👈 keep original string
        except Exception as e:
            raw_fallback = response.choices[0].message.content
            #dprint(f"⚠️ LLM response is not JSON — using raw content. Error: {e}")
            response_content = { "optimized_response": response.choices[0].message.content }  # 👈 return raw fallback



        usage = getattr(response, "usage", {})
        dprint(f"- Usage info: {usage[:50]}...")

        try:
            prompt_bundle = get_current_bundle()
            prompt_version = prompt_bundle.get("prompt_version", "v1")
        except PromptLoaderError:
            prompt_version = "unknown"
        dprint(f"🧬 Prompt version: {prompt_version}")

        version_info = get_version_info()
        bloat_info = token_profiler(user_content, model_name)

        if is_token_valid and is_account_active:
            #dprint("🛠️ Constructing telemetry payload...")
            payload = prepare_telemetry_payload(
                user_id=current_user_id,
                user_content=user_content,
                role=role,
                model_name=model_name,
                execution_time=execution_time,
                prompt_version=prompt_version,
                version_info=version_info,
                success=success,
                response_content=response_content,
                usage=usage,
                bloat_info=bloat_info
            )
            #dprint("📦 Payload constructed. Sending to telemetry logger...")
            
            log_telemetry_to_wordpress(success=success, telemetry_data=payload)
            payload['user_message'] = user_content 
            payload['response'] = response_content
            append_telemetry(payload)
            
        else:
            dprint("⚠️  Skipping telemetry — Email Verification / Account state invalid.")
            sys.exit(1)
    except Exception as e:
        dprint(f"⚠️ Failed to log telemetry: {e}")

def prepare_and_log_failure_telemetry(args, kwargs, success=False):

    try:
        state = get_state()
        model_name = kwargs.get("model", state.get("model_name"))
        execution_time = kwargs.get("execution_time", 0)
        user_id = state.get("user_id")
        is_token_valid = state.get("token_valid")
        is_account_active = state.get("account_state") in ("active",)

        # Extract user_content and role
        user_content = ""
        role = ""
        for msg in kwargs.get("messages", []):
            if msg.get("role") == "user":
                user_content = msg.get("content", "")
                import re
                match = re.search(r'role:\s*"?([^"\n]+)"?', user_content, re.IGNORECASE)
                if match:
                    role = match.group(1).strip()  # 🎯 Extracted semantic role
                else:
                    role = msg.get("role")  # fallback to "user" or similar

            elif msg.get("role") == "system" and not role:
                role = msg.get("role")

        # Get prompt version
        try:
            prompt_bundle = get_current_bundle()
            prompt_version = prompt_bundle.get("prompt_version", "v1")
        except PromptLoaderError:
            prompt_version = "unknown"

        version_info = get_version_info()

        if is_token_valid and is_account_active:
            payload = prepare_telemetry_payload(
                user_id=user_id,
                user_content=user_content,
                role=role,
                model_name=model_name,
                execution_time=execution_time,
                prompt_version=prompt_version,
                version_info=version_info,
                success=success
            )
            
            log_telemetry_to_wordpress(success=False, failure=True, telemetry_data=payload)
            payload['user_message'] = user_content 
            append_telemetry(payload)

            
    except Exception as e:
        dprint(f"⚠️ Failed to log failure telemetry: {e}")
