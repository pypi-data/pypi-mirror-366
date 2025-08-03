# Load environment variables
import os
import platform
import subprocess
import sys
import signal
import atexit
import uvicorn
import threading

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from docore_ai.utils.helpers import is_port_in_use
from docore_ai.utils.logger import dprint, dsys_exit
from contextlib import asynccontextmanager
from docore_ai.model import intelligence_profiler
from docore_ai.init_engine import _ENGINE_STATE, get_state

from docore_ai.utils.logger import dprint

# -------- Configurations -------- #
PID_FILE = Path.home() / ".docoreai_server.pid"
server = None  # global reference for shutdown

# Load environment variables
state=get_state()
dotenv_path = state.get("env_path")
load_dotenv(dotenv_path=dotenv_path, override=True)

# -------- FastAPI Setup -------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        dprint("starting lifespan...")
    except SystemExit as e:
        dprint(f"❌ Initialization failed: {e}")
        sys.exit(str(e))
    yield
    try:
        dprint("🧼 Cleaning up DoCoreAI state...")
        shutdown_uvicorn()
        _ENGINE_STATE.clear()
    except Exception as e:
        dprint(f"⚠️ Failed to reset engine state: {e}")

    check_and_kill_port_all()
    dprint("ending lifespan...")

app = FastAPI(lifespan=lifespan)

@app.get("/healthz")
async def health_check():
    return {"status": "ok", "initialized": _ENGINE_STATE.get("initialized", False)}

class PromptRequest(BaseModel):
    user_content: str
    role: str

@app.post("/intelligence_profiler")
async def run_profiler(request: PromptRequest):
    try:
        result = intelligence_profiler(
            user_content=request.user_content,
            role=request.role
        )
        return {"optimal_response": result["response"]}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])

    if not messages:
        return JSONResponse(status_code=400, content={"error": "No messages provided"})

    user_message = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), None)
    role = next((m['role'] for m in reversed(messages) if m['role'] == 'user'), "user")

    try:
        profiled = intelligence_profiler(user_content=user_message, role=role)
        return {
            "id": "chatcmpl-proxy",
            "object": "chat.completion",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": profiled["response"]
                },
                "finish_reason": "stop"
            }],
            "usage": profiled.get("usage", {})
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal Server Error", "details": str(e)})

# -------- API Server Lifecycle -------- #
def shutdown_uvicorn():
    global server
    if server:
        dprint("🛑 Shutting down DoCoreAI API Server...")
        server.should_exit = True

atexit.register(shutdown_uvicorn)

def main():
    global server
    port = int(os.getenv("DOCOREAI_API_PORT", 8000))
    host = os.getenv("DOCOREAI_API_HOST", "127.0.0.1")
    dprint(f"🚀 Starting DoCoreAI API Server at http://{host}:{port}")
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    if is_port_in_use("127.0.0.1", 8000):
        dprint("⚠️ Port 8000 already in use. API server may already be running.")
    else:    
        server.run()

def is_server_running():
    system = platform.system()
    if system == "Windows":
        try:
            output = subprocess.check_output(
                ['tasklist', '/FI', 'WINDOWTITLE eq DoCoreAI API*'],
                creationflags=subprocess.CREATE_NO_WINDOW,
                text=True
            )
            if "DoCoreAI API" in output:
                return True
        except Exception:
            pass

    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            return True
        except Exception:
            return False
    return False

def launch_api_server():
    if is_server_running():
        dprint("✅ API server is already running.")
        return
    dprint(chr(0x1F680), " Launching DoCoreAI API server in a new window...")

    process = None
    os_platform = platform.system()
    if os_platform == "Windows":
        try:
            process_api = subprocess.Popen(["start", "DoCoreAI API Monitor", "cmd", "/k", f"{sys.executable} -m docore_ai.proxy"], shell=True)
            PID_FILE.write_text(str(process_api.pid))
        except Exception as e:
            dprint(f"Failed to launch API server: {e}")
            sys.exit(1)
    elif os_platform == "Darwin":
        try:
            subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "{sys.executable} -m docore_ai.proxy"'])
            dprint("🧭 API server launched in macOS Terminal.")
            PID_FILE.write_text("windowed_manual")
        except Exception as e:
            dprint(f"❌ Failed to launch Terminal on macOS: {e}")
    else:
        try:
            process = subprocess.Popen(["x-terminal-emulator", "-e", f"{sys.executable} -m docore_ai.proxy"])
            PID_FILE.write_text(str(process.pid))
            dprint(f"🐧 API server started in Linux terminal (PID {process.pid}).")
        except FileNotFoundError:
            dprint("❌ Could not find x-terminal-emulator. Please install a terminal or launch manually.")

    if not process and os_platform not in ("Windows", "Darwin"):
        dprint("Unable to capture process handle. Manual termination may be required.")

def stop_api_server():
    if not is_server_running():
        #dprint("ℹ️ API server is not running.")
        dprint("")
        dprint("DoCoreAI Command Reference:")
        dprint("  • `docoreai start` — Run DoCoreAI Fusion Engine.")
        dprint("  • `docoreai test`  — For Http calls & testing.")
        dprint("  • `docoreai show`  — Open the Local Prompts Viewer in your browser.")
        dprint("  • `docoreai dash`  — Go to your online Dashboard at https://docoreai.com/dashboard/")
        dprint("")
        return
    shutdown_uvicorn()
    try:
        os_platform = platform.system()
        if os_platform == "Windows":
            pid = int(PID_FILE.read_text()).strip()
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True, capture_output=True, text=True)
            dprint(f"Process with PID {pid} terminated successfully.")
            dprint("🛑 API server stopped (via window pid).")
        else:
            if not PID_FILE.exists():
                dprint("⚠️ No PID file found; skipping Unix kill.")
                return
            try:
                pid = int(PID_FILE.read_text().strip())
                os.kill(pid, signal.SIGTERM)
            except Exception as e:
                dprint(f"❌ Unexpected error: {e}")
            if PID_FILE.exists():
                PID_FILE.unlink()
            dprint(f"🛑 API server (PID {pid}) stopped.")
    except Exception as e:
        dprint(f"❌ Failed to stop API server: {e}")

def check_and_kill_port_all():
    stop_api_server()

if __name__ == "__main__":
    main()
