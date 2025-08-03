import subprocess
from docore_ai.init_engine import get_state
import os
import time
from docore_ai.utils.logger import dprint
from docore_ai.init_engine import get_state
import sys

marker = "shutdown.marker"

# Get the directory of this script (utils)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHOW_APP = os.path.join(BASE_DIR, "show_app.py")

# Remove marker if it already exists
if os.path.exists(marker):
    os.remove(marker)

# Launch Streamlit as a subprocess with the absolute path to show_app.py
#proc = subprocess.Popen(["streamlit", "run", SHOW_APP], cwd=BASE_DIR)
# Forward the user's current directory so show_app.py knows where to look
USER_CWD = os.getcwd()
os.environ["DOCOREAI_USER_CWD"] = USER_CWD

state = get_state()
is_account_inactive = state.get("account_state") in ("activation_pending","inactive",)

# Run Streamlit and pass the environment
if is_account_inactive:
    dsys_exit('Please verify your email & upgrade access')
    os._exit(1)
else:
    proc = subprocess.Popen(["streamlit", "run", SHOW_APP], env=os.environ)

try:
    while True:
        if os.path.exists(marker):
            dprint("Shutdown marker detected. Killing Streamlit.")
            proc.terminate()
            break
        time.sleep(1)
except KeyboardInterrupt:
    proc.terminate()

# Cleanup
if os.path.exists(marker):
    os.remove(marker)
