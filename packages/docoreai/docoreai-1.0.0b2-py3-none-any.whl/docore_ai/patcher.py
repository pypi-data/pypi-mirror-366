#this files is not used as of now - will be used when developers need auto patching, also with the commented code in __init.py__
import threading
import inspect
import time
import os
from dotenv import load_dotenv
import openai
from pathlib import Path
from docore_ai.utils.logger import dprint
from docore_ai.init_engine import get_state

state=get_state()
dotenv_path = state.get("env_path")
load_dotenv(dotenv_path=dotenv_path, override=True)

# Thread-local flag to prevent recursive patching
_thread_local = threading.local()

# Optional: Environment toggle to allow chaining previous patch
ALLOW_CHAIN = os.getenv("DOCOREAI_CHAIN_PREVIOUS_PATCH", "true").lower() == "true"

def patch_openai_with_docoreai(force=False):
    existing = openai.ChatCompletion.create

    # Skip if already patched by DoCoreAI
    if getattr(existing, "__docoreai_patched__", False) and not force:
        return

    def docoreai_wrapper(*args, **kwargs):
        if getattr(_thread_local, "in_docoreai", False):
            # Re-entrant call from another wrapper
            return docoreai_wrapper.previous(*args, **kwargs)

        _thread_local.in_docoreai = True
        try:
            # ✅ Insert DoCoreAI logic here (telemetry, optimization, etc.)
            dprint("🧠 DoCoreAI patch active: Intercepted call to ChatCompletion.create")

            # Forward to previous patch if allowed
            if ALLOW_CHAIN and hasattr(docoreai_wrapper, "previous"):
                return docoreai_wrapper.previous(*args, **kwargs)

            # Fallback: call the existing OpenAI handler directly
            return docoreai_wrapper.previous(*args, **kwargs)

        finally:
            _thread_local.in_docoreai = False

    # Save reference to previous function
    docoreai_wrapper.previous = existing
    docoreai_wrapper.__docoreai_patched__ = True

    # Apply the patch
    openai.ChatCompletion.create = docoreai_wrapper
    dprint("✅ DoCoreAI monkey patch applied.")


def detect_override():
    current = openai.ChatCompletion.create
    return not getattr(current, "__docoreai_patched__", False)


def monitor_patch(interval_sec=2):
    def loop():
        while True:
            if detect_override():
                dprint("⚠️ DoCoreAI patch overridden. Reapplying...")
                patch_openai_with_docoreai(force=True)
            time.sleep(interval_sec)

    import threading
    threading.Thread(target=loop, daemon=True).start()


# Optional: manual usage
if __name__ == "__main__":
    patch_openai_with_docoreai(force=True)
    monitor_patch()
