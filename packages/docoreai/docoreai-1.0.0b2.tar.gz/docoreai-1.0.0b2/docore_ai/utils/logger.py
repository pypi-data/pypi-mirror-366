# docore_ai/utils/logger.py

import os
import sys

def docoreai_log():
    """
    Determines whether to log messages based on the environment variable.
    Set DOCOREAI_LOG_ONLY=true to enable logs.
    """
    return os.getenv("DOCOREAI_LOG_ONLY", "false").lower() == "true"


# def dprint(*args, **kwargs):
#     """
#     Print only if DoCoreAI logging is enabled.
#     Usage: replace print(...) with dprint(...)
#     """
#     if docoreai_log():
#         print(*args, **kwargs)

def dsys_exit(message=None, code=1):
    """
    Exits the app using SystemExit if DOCOREAI_LOG_ONLY is true.
    Otherwise, prints the message and continues (useful when used as a library).
    """
    if docoreai_log():
        raise SystemExit(message if message else code)
    else:
        if message:
            print(f"💡  {message}")
        else:
            print(f"💡  Exit code: {code}")

            # In auto_patch.py or logger module
import os
import socket

def dprint(*args, **kwargs):
    if not docoreai_log():  # skip if logging globally disabled
        return

    try:
        msg = " ".join(str(arg) for arg in args) + "\n"
        host = os.getenv("DOCOREAI_LOG_HOST", "127.0.0.1")
        port = int(os.getenv("DOCOREAI_LOG_PORT", "5678"))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(msg.encode("utf-8"))
    except Exception:
        # Optional: silently drop, or write to fallback file
        pass
