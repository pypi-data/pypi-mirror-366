
import datetime
import os
import platform
import shutil
import time
import typer
import importlib.util # for ensure_openai_installed
import subprocess # for ensure_openai_installed
import sys
from docore_ai.init_engine import _ENGINE_STATE, ensure_env_file_exists_and_valid, initialize, get_state
from docore_ai.utils.csv_logger import _ensure_header
from docore_ai.utils.logger import dprint
from packaging import version
from docore_ai.proxy import launch_api_server, stop_api_server # for ensure_openai_installed

from importlib.metadata import version as get_version, PackageNotFoundError
from docore_ai.pth_installer import install_pth_file, blank_pth_file
from docore_ai.utils.helpers import get_docoreai_env_path, is_port_in_use

from pathlib import Path
from api.main import app as docoreai_api_app
from docore_ai.fusion_log_server import start_log_server

import logging
from rich.logging import RichHandler
import threading
import requests

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from dotenv import load_dotenv
load_dotenv()  # Loads .env into os.environ    

## 20-06-25 Start  Inprocess Server 
from docore_ai.proxy import app as proxy_app
import uvicorn
def run_api_server_in_process():
    config = uvicorn.Config(proxy_app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    if is_port_in_use("127.0.0.1", 8000):
        dprint("⚠️ Port 8000 already in use. API server may already be running.")
    else:
        server.run()
## End Inprocess Server

console = Console()
def custom_help(ctx: typer.Context, param: typer.CallbackParam, value: bool):
    if value:
        console.print("[bold orange1]🚀 Welcome to DoCoreAI CLI[/]\n")
        console.print("[cyan]DoCoreAI helps you optimize prompts, reduce token usage, and view powerful analytics.[/]\n")
        console.print("[bold]Available Commands:[/]")
        console.print("  [green]start[/]       Launch the DoCoreAI proxy")
        console.print("  [green]stop[/]        Stop the running proxy and clean up")
        console.print("  [green]version[/]     Show installed version info")
        #console.print("  [green]report[/]      View analytics dashboard")
        console.print("\n📊 Dashboard: https://docoreai.com/dashboard/")
        console.print("💬 Help & Issues: https://github.com/SajiJohnMiranda/DoCoreAI/discussions\n")
        raise typer.Exit()

#IMPORTANT DO NOT IGNORE OR REMOVE THIS BLOCK Option 3: Forced Override + Optional Chaining (Best of Both)
#Make DoCoreAI’s patch forcefully apply, but allow it to optionally call the previous version — only if you want.
#refer https://chatgpt.com/share/684631bc-f880-8008-b7ee-5a8e6d5a126e
#from docore_ai import patcher
#patcher.monitor_patch()  # Optional: Keep DoCoreAI patch active even if overridden

#from docore_ai.proxy import start_proxy

app = typer.Typer(
    help="Run DoCoreAI to optimize your LLM prompts efficiently.",
    add_completion=False,
    no_args_is_help=True
)
@app.callback()
def main(
    help: bool = typer.Option(
        None,
        "--help",
        "-h",
        is_eager=True,
        is_flag=True,
        callback=custom_help,
        help="Show this message and exit.",
    )
):
    pass

# def run_uvicorn():
#     uvicorn.run("docore_ai.proxy:app", host="127.0.0.1", port=8000, log_level="info")  # 👈 Ensure log level
    


ENV_FILE = Path.cwd() / ".env"

# ✅ Check if API Server is Running (via PID file)
@app.command()
def start():
    dprint("🟢 DoCoreAI CLI start initiated")

    # --- Initialization Phase ---
    try:
        dprint("🔧 Running initialize()...")
        initialize()
        dprint("✅ initialize() complete")
    except Exception as e:
        dprint(f"❌ initialize() failed: {e}")
        return


    #os.environ["DOCOREAI_ENV_PATH"] = get_docoreai_env_path()
    dprint("Starting DoCoreAI - setting .env path to:", Path.cwd() / ".env")

    
    try:
        
        ensure_openai_installed()
        dprint("📦 Checking latest DoCoreAI version...")
        check_latest_docoreai_version()
        dprint("✅ Version check complete")
    except Exception as e:
        dprint(f"⚠️ Version check failed: {e}")

    # --- Logging & Background API ---
    set_env_flag(True)     
    try:
        start_log_server()
        dprint("✅ Fusion Log Server started")
    except Exception as e:
        dprint(f"⚠️ Log server failed: {e}")
    
    #launch_api_server()
    dprint("🚀 Starting DoCoreAI Proxy-Server...")

    #thread = threading.Thread(target=run_api_server_in_process, daemon=True)
    #thread.start()
    
    # --- CLI Banner ---
    show_start_banner()

    # 🔴 FINAL STEP: Trigger autopatch via .pth
    try:
        #dprint("🧩 Installing .pth file for autopatch...")
        install_pth_file()
        #dprint("✅ .pth installation complete (autopatch active)")
    except Exception as e:
        dprint(f"❌ Failed to install .pth file: {e}")
    
    #dprint("🚀 Starting DoCoreAI Proxy Server...")
    
    

    #dprint("📊 View your reports at: https://docoreai.com/dashboard/")
    #dprint("📂 Ensure your .env file is configured properly.")
    #dprint("🛑 Press Ctrl+C to stop the server.\n")

    # 👇 Start Uvicorn in a background thread
    #server_thread = threading.Thread(target=run_uvicorn, daemon=True)
    #server_thread.start()

    
    #subprocess.Popen(["uvicorn", "docore_ai.proxy:app", "--port", "8000"]) As PID TBD todo
    #Start as new process (same as `python -m docore_ai.api_server`)

    # process = subprocess.Popen(
    #     [sys.executable, "-m", "docore_ai.api_server"],
    #     stdout=subprocess.DEVNULL,
    #     stderr=subprocess.DEVNULL,)    
    # PID_FILE.write_text(str(process.pid))
    # dprint(f"🔢 API server started with PID {process.pid}")

    #✅ Now terminal stays alive and logs from patching will show!
    dprint("🌐 HTTP server running in background.")
    dprint("🧠 Listening for OpenAI/Groq calls...LLM script activity will be logged here.\n")
    dprint("🛑 Press Ctrl+C to stop the server. — Start LLM prompting now!\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        dprint("\n🛑 Shutting down DoCoreAI...")
        stop()
  

# Run the FastAPI app from proxy.py
@app.command()
def show():
    """Open the local telemetry CSV in a browser using Streamlit."""
    # ✅ Validate token before launching the test server
    if not validate_token():
        dprint("❌ Missing or invalid DOCOREAI_TOKEN. Please sign up at https://docoreai.com and set the token in your .env file.")
        dprint("Support: info@docoreai.com")
        return
   
    # Build absolute path to wrapper script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    utils_dir = os.path.join(base_dir, "utils")
    #dprint(f"[docoreai show] Prompts Viewer launched at {datetime.datetime.now().isoformat()}") does not work
    dprint("🛑 Press Ctrl+C to exit")
    wrapper_script = os.path.join(utils_dir, "run_streamlit_with_shutdown.py")

    subprocess.run([sys.executable, wrapper_script])


@app.command()
def stop():
    """Stop any running DoCoreAI background services and clean up state."""
    dprint("🧼 Cleaning up DoCoreAI state...")
    
    # Reset engine state
    try:
        #set_env_flag(False) # set DOCOREAI_ENABLE as false
        blank_pth_file()
        _ENGINE_STATE.clear()
        dprint("engine state reset.")
    except Exception as e:
        dprint(f"⚠️ Failed to reset engine state: {e}")

    # Clean up commonly used ports
    
    #check_and_kill_port()

    # Remove temporary files
    temp_files = [".env.cache"]
    for file in temp_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                dprint(f"✅ Removed temp file: {file}")
            except Exception:
                dprint(f"⚠️ Could not remove temp file: {file}")
    
    
    
    dprint("                            ")
    stop_api_server()
    dprint("                            ")
    show_stop_banner()
    time.sleep(1)
    dprint("👋 Take a break or come back anytime to optimize smarter!")
    

    #dprint("When you're ready, just run: `docoreai start`")

@app.command()
def show_version():
    dprint("------------------------------------------------------------")
    try:
        current_version = get_version("docoreai")
        console.dprint(f"[bold blue]DoCoreAI version:[/] [white]{current_version}[/]")
    except PackageNotFoundError:
        console.dprint("[red]❌ DoCoreAI is not installed.[/]")
        return
    except Exception as e:
        console.dprint(f"[bold yellow]⚠️ Could not retrieve version: {e}[/]")
        return
    dprint("------------------------------------------------------------")
    console.print("[bold rgb(244,90,42)]Optimize your prompts, save your tokens![/]")
    dprint("📊 Dashboard: https://docoreai.com/dashboard/")
    dprint("Report issues: https://github.com/SajiJohnMiranda/DoCoreAI/discussions")

@app.command()
def reset():
    dprint("♻️ Resetting DoCoreAI configuration...")
    # Reset logic can go here

@app.command()
def dash():
    """Open the online DoCoreAI Dashboard."""
    # ✅ Validate token before launching the test server
    if not validate_token():
        dprint("❌ Missing or invalid DOCOREAI_TOKEN. Please sign up at https://docoreai.com and set the token in your .env file.")
        dprint("Support: info@docoreai.com")

    import webbrowser
    url = "https://docoreai.com/dashboard/"
    #dprint(f"[docoreai dash] Opening dashboard: {url}") does not work
    webbrowser.open(url)

@app.command()
def test():
    """Run DoCoreAI test server with extra tools (e.g., Postman testing, manual inspection)"""
    # ✅ Validate token before launching the test server
    if not validate_token():
        dprint("❌  Missing or invalid DOCOREAI_TOKEN. Please sign up at https://docoreai.com and set the token in your .env file.")
        dprint("Support: info@docoreai.com")
        return
        if  _ENGINE_STATE["account_state"] == "activation_pending": dsys_exit('❌ Verify your email & Upgrade Access')
    from docore_ai.test_server import app as test_app
    dprint("🛑 Press Ctrl+C to exit")
    uvicorn.run("docore_ai.test_server:app", host="127.0.0.1", port=8001, reload=True)


if __name__ == "__main__":
    app()


def ensure_openai_installed(min_version="0.28.1", max_version="2.0.0"):
    """
    Checks if OpenAI SDK is installed and compatible.
    Prompts the user to install or upgrade if not found or version is invalid.
    """

    MIN_PYTHON = (3, 8)
    if sys.version_info < MIN_PYTHON:
        dprint(f"\n⚠️ WARNING: Your Python version is {sys.version.split()[0]}.")
        dprint("   DoCoreAI recommends Python 3.8 or higher for best compatibility.")
    
    spec = importlib.util.find_spec("openai")
    if spec is not None:
        import openai
        current_version = version.parse(openai.__version__)
        if version.parse(min_version) <= current_version < version.parse(max_version):
            return  # ✅ Compatible
        else:
            dprint(f"\n⚠️ Incompatible OpenAI SDK version detected: {current_version}")
            dprint("   DoCoreAI supports versions between 0.28.1 and 2.0.0.")
    else:
        dprint("\n⚠️ OpenAI SDK not found.")
    #version_input = input("Press Enter to install the latest OpenAI SDK, or type a version number to install a specific one: ").strip()
    #package = f"openai=={version_input}" if version_input else " openai"

    # try:
    #     dprint(f"\n📦 Installing {package} ...")
    #     subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    #     dprint("✅ OpenAI SDK installed successfully.\n")
    # except subprocess.CalledProcessError as e:
    #     error_output = str(e)
    #     if platform.system() == "Linux" and "externally-managed-environment" in error_output:
    #         dprint("⚠️ Detected externally-managed environment. Retrying with --break-system-packages...")
    #         try:
    #             subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", package])
    #             dprint("✅ OpenAI SDK installed successfully (with override).\n")
    #         except subprocess.CalledProcessError:
    #             dprint(f"❌ Even with override, failed to install {package}.")
    #             dprint(f"   Try manually: pip install {package} --break-system-packages")
    # else:
    #     dprint(f"❌ Failed to install {package}.")
    #     dprint(f"   Try manually: pip install {package}")

    #     dprint(f"   pip install {package}")
    #     sys.exit(1)


#----------------------


def check_latest_docoreai_version():
    try:
        current_version = get_version("docoreai")
    except PackageNotFoundError:
        return  # DoCoreAI is not yet installed — skip version check

    # Start background thread to avoid blocking CLI
    thread = threading.Thread(
        target=check_upgrade_latest_docoreai_version,
        args=(current_version,),
        daemon=True
    )
    thread.start()

def check_upgrade_latest_docoreai_version(current_version):
    try:
        response = requests.get("https://pypi.org/pypi/docoreai/json", timeout=5)
        latest_version = response.json()["info"]["version"]
        if version.parse(current_version) < version.parse(latest_version):
            dprint(f"\n⚠️ DoCoreAI version {current_version} is outdated.")
            dprint(f"   Latest version is {latest_version}. To upgrade:")
            dprint("   pip install --upgrade docoreai\n")
    except Exception:
        pass  # Fail silently

import psutil

# def check_and_kill_port():
#     """
#     Checks for any process using the given port and attempts to terminate it.
#     """
#     stop_api_server()

def show_start_banner():
    start_text = Text("⚪  Launching DoCoreAI Fusion Engine...", justify="left") 
    start_text.stylize("bold rgb(255,255,255) on rgb(0,76,186)")  # #2F373D (dark gray/black-blue)
    console.print(Panel(start_text, border_style="rgb(47,55,61)"))


def show_stop_banner():
    stop_text = Text("⚪  Shutting down DoCoreAI Fusion Engine.", justify="left")
    stop_text.stylize("bold rgb(255,255,255) on rgb(244,90,42)")  # #2F373D (dark gray/black-blue)
    console.print(Panel(stop_text, border_style="rgb(47,55,61)"))

def set_env_flag(active: bool):
    #ensure_env_file_exists_and_valid()
    lines = ENV_FILE.read_text().splitlines()
    updated = []
    found = False
    for line in lines:
        if line.startswith("DOCOREAI_ENABLE"):
            updated.append(f"DOCOREAI_ENABLE={'true' if active else 'false'}")
            found = True
        else:
            updated.append(line)
    if not found:
        updated.append(f"DOCOREAI_ENABLE={'true' if active else 'false'}")
    ENV_FILE.write_text("\n".join(updated))


def validate_token():
    TOKEN = os.getenv("DOCOREAI_TOKEN")
    if not TOKEN or not TOKEN.strip():
        dprint("\n❌ Environment variable DOCOREAI_TOKEN is missing.")
        return False
    session = requests.Session()
    try:
        response = session.post(
            "https://docoreai.com/wp-json/docoreai/v1/validate-token?action=true",
            json={"token": TOKEN},
            timeout=6
        )
        if response.status_code == 200 and response.json().get("valid") is True:
            dprint("✅ Token validated successfully.")
            return True
        else:
            dprint("❌ Invalid or expired token. Please reissue from https://docoreai.com/generate-token")
            return False
    except Exception as e:
        dprint(f"⚠️ Error validating token: {e}")
        return False

def quick_account_check():
    dprint("🔍 Starting quick account check...")
    token = (os.getenv("DOCOREAI_TOKEN") or "").strip()
    if not token:
        dprint("❌ Missing environment variable: DOCOREAI_TOKEN")
        dprint("💡 Please update your token before using DoCoreAI.")
        return False

    session = requests.Session()
    session.trust_env = False  # 💡 Avoid system proxy

    user_id = None

    try:
        # Step 1: Validate token and get user_id
        resp = session.post(
            "https://docoreai.com/wp-json/docoreai/v1/validate-token?action=true",
            json={"token": token},
            timeout=5
        )

        if resp.status_code != 200:
            dprint(f"❌ Token validation failed. HTTP {resp.status_code}")
            return False

        data = resp.json()
        if not data.get("valid") or "user_id" not in data:
            dprint("❌ Invalid token or missing user ID.")
            return False

        user_id = data["user_id"]
        #print(user_id)
    except Exception as e:
        dprint(f"⚠️  Error validating token: {e}")
        return False

    try:
        # Step 2: Get membership info using user_id
        session = requests.Session()
        session.trust_env = False  # 💡 Avoid system proxy

        headers = {
            "X-DocoreAI-Token": _ENGINE_STATE["docoreai_token"]
        }
        resp2 = session.post(
            "https://docoreai.com/wp-json/docoreai/v1/get_member_info?action=true",
            json={"user_id": user_id},
            timeout=2,
            headers=headers
        )
        dprint("Step 2:Get membership info using user_id")

        if resp2.status_code != 200:
            dprint(f"❌ Failed to retrieve membership info. HTTP {resp2.status_code}")
            return False

        data2 = resp2.json()
        account_state = data2.get("account_state", "").lower()

        if account_state == "activation_required":
            dprint(
                "\n🚫  Email Verification Required\n"
                "To use DoCoreAI Dashboard, you need to verify your email address.\n"
                "📨 Please check your inbox (or spam folder) for the activation email from DoCoreAI.\n"
                "✅ Once verified, restart the app.\n"
                "💡 If you didn't receive an email, please re-register or contact support at info@docoreai.com.\n"
            )

        return account_state
    except Exception as e:
        dprint(f"❌ Failed to fetch membership info: {str(e)}")


   #Retention when added to stop: was throwing error messages in Ctrl+c - To DO Later
    # session = requests.Session()
    # session.trust_env = False  # 💡 Ensure no system proxy interferes
    # try:
    #     token = os.getenv("DOCOREAI_TOKEN")
    #     if not token:
    #         dprint("[server-message] Error: Missing environment variable DOCOREAI_TOKEN")
    #     else:        
    #         headers = {
    #             "X-DocoreAI-Token": token
    #         }        
    #     resp = session.get(
    #         "https://docoreai.com/wp-json/docoreai/v1/server-message",
    #         params={
    #             "event": 'exit',         # 'start', 'stop', or 'exit'
    #             "level_id": 4, #_ENGINE_STATE["level_id"],    # 2=Free, 3=Plus, 4=Pro
    #             "user_id": 29 #_ENGINE_STATE["user_id"]
    #         },
    #         timeout=4,
    #         headers=headers
    #     )

    #     if resp.status_code == 200 and resp.json().get("status") == "ok":
    #         dprint('----')
    #         #dprint(resp.json()["message"]) Messaging is commented for now as
    #         # we need to understnd the start time & no of prompts processed to provide messages / or we can provide only tips msgd / TBD
    #     elif resp.status_code == 204:
    #         pass  # No message to show
    #     else:
    #         pass #dprint(f"[server-message] Warning: {resp.json().get('message', 'No message')}")
    #         #dprint(os.getenv("DOCOREAI_TOKEN"))
    # except Exception as e:
    #    dprint(f"[server-message] Error: {e}")