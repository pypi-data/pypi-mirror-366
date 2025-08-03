import os
import platform
import subprocess
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def open_env_file_in_editor(filepath):
    try:
        if platform.system() == "Windows":
            os.startfile(filepath)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", filepath])
        else:  # Linux and others
            subprocess.run(["xdg-open", filepath])
    except Exception as e:
        print(f"⚠️ Failed to open the file: {e}")




from pathlib import Path
from pathlib import Path
import os

from pathlib import Path

def get_docoreai_env_path():
    """
    Reads the docoreai_cwd.txt file in the current working directory
    and returns the path to the .env file inside that directory.
    """
    cwd_file = Path.cwd() / "docoreai_cwd.txt"
    
    if not cwd_file.exists():
        print(f"⚠️ {cwd_file} not found.")
        return None

    try:
        base_path = Path(cwd_file.read_text(encoding="utf-8").strip()).expanduser().resolve()
        return str(Path(base_path) / ".env")
    except Exception as e:
        print(f"⚠️ Error reading {cwd_file}: {e}")
        return None

def get_retry_session(retries=3, backoff_factor=0.5, status_forcelist=(502, 503, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["POST"],  # Retry POST too
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

import socket

def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        try:
            s.connect((host, port))
            return True
        except (ConnectionRefusedError, OSError):
            return False
