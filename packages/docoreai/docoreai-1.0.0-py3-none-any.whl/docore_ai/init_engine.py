# init_engine.py
import os
from multiprocessing import Process
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from docore_ai.prompt_updates.check_prompt_update import check_prompt_update
from docore_ai.pth_installer import install_pth_file
from docore_ai.utils.helpers import open_env_file_in_editor
from docore_ai.utils.logger import dprint, dsys_exit

dotenv_path = Path.cwd() / ".env"

global _ENGINE_STATE

_ENGINE_STATE = {
    "initialized": False,
    "user_id": None,
    "prompt_bundle": None,
    "openai_api_key": None,
    "groq_api_key": None,
    "model_provider": None,
    "model_name": None,
    "docoreai_api_url": None,
    "docoreai_token": None,
    "token_valid": None,
    "account_state": None, #'active','inactive','activation_required','expired','pending','unsubscribed'
    "level_id": None,
    "level_name": None,
    "email":None,
    "skip_tracking": False, 
    "prompt_type":None,
    "env_path": None,
}

def initialize():
    #dprint(">>> ENTER initialize()")
    global _ENGINE_STATE
    if _ENGINE_STATE["initialized"]:
        dprint("refreshing state info...)")
        _ENGINE_STATE["model_provider"] = (os.getenv("MODEL_PROVIDER") or "").strip().lower()
        _ENGINE_STATE["model_name"] = (os.getenv("MODEL_NAME") or "").strip()        
        return
    
    dprint("🛠️  Initializing DoCoreAI...")
    #dotenv_path = Path(__file__).resolve().parents[1] / ".env"
    dotenv_path = Path.cwd() / ".env"
    #dprint(f"📂 Looking for .env at: {dotenv_path}")
    ensure_env_file_exists_and_valid()

    load_dotenv(dotenv_path=dotenv_path, override=True)
    dprint(f"📂 .env loaded from: {dotenv_path}")
    
    _ENGINE_STATE["env_path"] = dotenv_path


    command = sys.argv[1].strip().lower() if len(sys.argv) > 1 else None
    #print(command)
    if command == "test":
        _ENGINE_STATE["prompt_type"] = "test"
    elif command == "start":
        _ENGINE_STATE["prompt_type"] = "prod"
    elif command == "show":
        _ENGINE_STATE["prompt_type"] = "show"
    elif command == "dash":
        _ENGINE_STATE["prompt_type"] = "dash"
    else:
        _ENGINE_STATE["prompt_type"] = "import"
    
    

    _ENGINE_STATE.update({
        "openai_api_key": (os.getenv("OPENAI_API_KEY") or "").strip(),
        "groq_api_key": (os.getenv("GROQ_API_KEY") or "").strip(),
        "model_provider": (os.getenv("MODEL_PROVIDER") or "").strip(),
        "model_name": (os.getenv("MODEL_NAME") or "").strip(),
        "docoreai_api_url": (os.getenv("DOCOREAI_API_URL") or "https://docoreai.com").strip(),
        "docoreai_token": (os.getenv("DOCOREAI_TOKEN") or "").strip()
    })


    if not _ENGINE_STATE["docoreai_token"]:
        dprint("❌ No DOCOREAI_TOKEN found in .env.")
        sys.exit("⚠️  Your DOCOREAI_TOKEN variable is missing in .env file. Please generate a new token here: 👉 https://docoreai.com/generate-token ,\nadd line `DOCOREAI_TOKEN=new_token` in .env file and try again")
    
    session = requests.Session()
    session.trust_env = False  # 💡 Ensure no system proxy interferes
    data = {}
    try:
        resp = session.post(
            f"https://docoreai.com/wp-json/docoreai/v1/validate-token?action=true",
            json={"token": _ENGINE_STATE["docoreai_token"]},
            timeout=6
        )
        if resp.status_code == 403 and 'blocked' in resp.text.lower():#this if condition can be used later if blocking is required
            dprint("Your API token will be deactivated due to excessive use. Please check your email for more info or contact support.")

            #exit(1) CAN BE USED FOR BLOCKING/DEACTIVATION
        # 🛑 Avoid breaking the code with raw traceback on token validation failure
        if resp.status_code >= 400:
            dprint(f"❌ Token validation failed: {resp.status_code} {resp.reason}")
            dprint(f"🔗 {resp.url}")
            sys.exit("⚠️ Looks like your DOCOREAI_TOKEN is invalid. Please generate a new token from https://docoreai.com/generate-token")
        data = resp.json()
        _ENGINE_STATE["user_id"] = data["user_id"]
        _ENGINE_STATE["token_valid"] = data["valid"]
        dprint(f"🎟️  Token validation successful")

        headers = {
            "X-DocoreAI-Token": _ENGINE_STATE["docoreai_token"]
        }

        resp2 = session.post(
            f"https://docoreai.com/wp-json/docoreai/v1/get_member_info?action=true", #telemetry.php
            json={"user_id": _ENGINE_STATE["user_id"]},
            timeout=2,
            headers=headers
        )
        
        
        #resp2.raise_for_status()
        data2 = resp2.json()
        if "account_state" not in data2:
            dprint("❌ Failed to retrieve membership info. Invalid response.")

        _ENGINE_STATE["account_state"] = data2.get("account_state")
        _ENGINE_STATE["level_id"] = data2.get("level_id")
        _ENGINE_STATE["level_name"] = data2.get("level_name")
        _ENGINE_STATE["email"] = data2.get("email")
        dprint(f"🎟️  Membership Status: {_ENGINE_STATE['account_state']} | Level: {_ENGINE_STATE['level_name']}")    
        #dprint(f"{_ENGINE_STATE['email']}")

        account_state = _ENGINE_STATE.get("account_state", "").lower()

        if account_state == "activation required":
            dprint(
                "\n🚫  Email Verification Required\n"
                "To use DoCoreAI Dashboard, you need to verify your email address.\n"
                "📨 Please check your inbox (or spam folder) for the activation email from DoCoreAI.\n"
                "✅ Once verified, restart the app.\n"
                "💡 If you didn't receive an email, please re-register or contact support at info@docoreai.com.\n")
            

        elif account_state in ["pending", "inactive", "unsubscribed"]:
            dprint(
                "\n🚫 Access Restricted\n"
                f"Your membership status is currently set to: '{account_state}'.\n"
                "🔒 Unfortunately, this prevents you from using DoCoreAI at the moment.\n"
                "📞 Please contact the DoCoreAI support team at info@docoreai.com or your system administrator to resolve this issue.\n"
                "We'll help you reactivate your membership promptly.\n")
            

        elif account_state == "expired":
            dprint(
                "\n⚠️  Membership Expired\n"
                "Your membership has expired, which means access to premium features like Dashboard Reports is restricted.\n"
                "✅ However, you can still use DoCoreAI to optimize prompts and improve performance — Completely Free.\n"
                "🚀 To unlock full analytics and advanced tracking, please upgrade your membership.\n"
                "🔗 Visit https://docoreai.com/pricing or go to the 'Upgrade Plan' section inside your account.\n"
                "📞 Please contact the DoCoreAI support team at info@docoreai.com")
            # Allow engine to continue running for prompt optimization use only
            
        else:
            #dprint(f"✅ Membership state '{account_state}' validated. Full access granted.")
            dprint("--------------------------------------------------")
    

    except Exception as e:
        dprint(f"❌ Token validation failed due to network or server issue: {str(e)}")
        #dprint("📡 Please check your internet connection or try again later.")
        # You can log full traceback to a file if needed instead of printing - remove traceback on PROD
        # import traceback
        # traceback.print_exc(file=open("error.log", "a")) todo later
        data = {"valid": False}

    if not data.get("valid"):
        dprint("❌ Invalid token. Continuing without setting initialized flag.")
        return
   
    try:
        prompt_info = check_prompt_update(_ENGINE_STATE["user_id"])
        _ENGINE_STATE["prompt_bundle"] = prompt_info
        #dprint(_ENGINE_STATE["prompt_bundle"]["system_message"])
    except Exception as e:
        dprint(f"⚠️ Prompt update failed: {e}")
    
    if data.get("valid"):
        _ENGINE_STATE["initialized"] = True
    if not _ENGINE_STATE.get("prompt_bundle"):
        dprint("⚠️ Prompt bundle missing — using defaults.")
    #dprint(">>> EXIT initialize()")
    
def get_state():
    return _ENGINE_STATE

# try:
#     from docore_ai.auto_patch import patch_openai
#     patch_openai() # called only from cli when docoreai is called
# except Exception as e:
#     dprint(f"⚠️ DoCoreAI auto-patch failed: {e}")

from dotenv import dotenv_values

REQUIRED_ENV_KEYS = [
    "DOCOREAI_TOKEN",
    "MODEL_PROVIDER",
    "MODEL_NAME",
    
]

def ensure_env_file_exists_and_valid():
    #if os.path.exists(".env"):
        #return  # ✅ .env exists, skip all prompting    
    if not os.path.exists(".env"):
        resp = input("\n🚀  Launching DoCoreAI Fusion Engine...\n"
                     "searching .env file...\n"
                     "⚙️  DoCoreAI: Setting up environment...\n" 
                     "⚠️  No .env file found. Auto-create one with default settings? (Y/n): ").strip().lower()
        if resp in ("y", "yes","Y"):
            with open(".env", "w", encoding="utf-8") as f:
                f.write(
        """
        # ==============================================================
        # DoCoreAI Configuration File
        # --------------------------------------------------------------
        # This file contains required settings to run DoCoreAI.
        # Please update the missing keys below and save the file.

        # ================================================================
        # Required: API Keys - Enter your keys here to enable AI access.
        # Provide OPENAI_API_KEY or GROQ_API_KEY — at least one is required.
        # ------------------------------------------------------------------
        OPENAI_API_KEY=
        GROQ_API_KEY=

        # =============================================================================
        # Model Configuration - Specify the AI provider and model name you want to run 
        # e.g:- MODEL_PROVIDER=openai, MODEL_NAME=gpt-4
        # e.g:- MODEL_NAME=gpt-4 or gpt-3.5-turbo
        # -----------------------------------------------------------------------------
        MODEL_PROVIDER=openai
        MODEL_NAME=gpt-3.5-turbo

        # ==================================================================================
        # DoCoreAI Token – Required to run the app. Get your token from https://docoreai.com
        # ----------------------------------------------------------------------------------
        DOCOREAI_TOKEN=

        # ==============================================================
        # Advanced Settings - Only change if you know what you're doing.
        # --------------------------------------------------------------
        DOCOREAI_API_URL=https://docoreai.com
        EXTERNAL_NETWORK_ACCESS=False  
        ALLOW_SYSTEM_MESSAGE_INJECTION=true
        DOC_SYSTEM_MESSAGE=You are a helpful assistant.
        DOCOREAI_LOG_ONLY=true
        DOCOREAI_ENABLE=true
        DOC_DEBUG_PRINT=false
        DOCOREAI_LOG_HOST=127.0.0.1
        DOCOREAI_LOG_PORT=5678
        """)
            #dprint("✅ .env file created. Please fill in your keys before continuing.\n")
            #dprint("ℹ️ Restart the app after updating your .env file.\n")
            dsys_exit("✅ .env file created.\nUpdate your keys in the .env file, then run:\n`docoreai start`\n")
            time.sleep(1.5)
            #open_env_file_in_editor(".env") 
            #sys.exit("ℹ️ Run: `docoreai start` again.")
        
        # Check other required keys
        # env_data = dotenv_values(".env")
        # missing_keys = [k for k in REQUIRED_ENV_KEYS if not env_data.get(k, "").strip()]
        # if missing_keys:
        #     #dprint("\n⚠️ The following required environment variable values are missing or empty in .env:\n")
        #     for key in missing_keys:
        #         value = env_data.get(key, "")
        #         #dprint(f"  {key} = {value}")
        #     dprint("\n🔍 Some required keys are missing in your .env file.\n")
        # #time.sleep(1.5)
        # #open_env_file_in_editor(".env") 
        # dsys_exit("ℹ️ Update, Save & Restart app with: `docoreai start` \n")
        elif resp in ("n", "no","N"):
            dprint("⚠️ DoCoreAI requires a `.env` file to work properly.")
            print("📌 If you already have a `.env`, please add the following DoCoreAI-specific variables:\n")

            docoreai_env = {
                "OPENAI_API_KEY": "",
                "GROQ_API_KEY": "",
                "MODEL_PROVIDER": "",
                "MODEL_NAME": "",
                "DOCOREAI_TOKEN": "",
                "DOCOREAI_API_URL": "https://docoreai.com",
                "DOCOREAI_ENABLE": "true",
                "DOC_DEBUG_PRINT": "false",
                "ALLOW_SYSTEM_MESSAGE_INJECTION": "true",
                "DOCOREAI_LOG_ONLY": "true",
                "EXTERNAL_NETWORK_ACCESS": "false",
                "DOC_SYSTEM_MESSAGE": "You are a helpful assistant.",
                "DOCOREAI_LOG_HOST": "127.0.0.1",
                "DOCOREAI_LOG_PORT": "5678",
            }
            for key, val in docoreai_env.items():
                #dprint(f"{key}={val}")
                print(f"{key}={val}")
            dsys_exit("\n📄 After adding these to your `.env`, restart the app with: `docoreai start`\n")

        else:
            dsys_exit("❌ Invalid input. Please enter 'y' or 'n'.\nRun: `docoreai start` again")


def get_env_settings(path=Path.cwd() / ".env" ):
    # List of variables to look for
    required_vars = [
        "MODEL_PROVIDER",
        "MODEL_NAME",
        "EXTERNAL_NETWORK_ACCESS",
        "DOC_DEBUG_PRINT",
        "ALLOW_SYSTEM_MESSAGE_INJECTION",
        "DOCOREAI_LOG_ONLY",
        "DOCOREAI_ENABLE",
    ]

    # Load .env content into dictionary
    env_vars = {}
    env_file = Path(path)
    if env_file.exists():
        with env_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    env_vars[key.strip()] = val.strip()

    # Build result string with abbreviations
    def abbreviate(var_name):
        return "_".join([word[0].upper() for word in var_name.split("_")])

    parts = []
    for var in required_vars:
        abbrev = abbreviate(var)
        value = env_vars.get(var, "")
        parts.append(f"{abbrev}={value}")

    return ",".join(parts)