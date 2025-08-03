import os
import subprocess
import sys
import sysconfig
from pathlib import Path
#from docore_ai.init_engine import initialize

from docore_ai.utils.logger import dprint

# Try to load the site-packages path from site_path.txt
SITE_PACKAGES_PATH = None
# try:
#     with open("site_path.txt", "r") as f:
#         SITE_PACKAGES_PATH = f.read().strip()
#         dprint(f"📦 Loaded site-packages path: {SITE_PACKAGES_PATH}")
# except Exception as e:
#     dprint(f"⚠️ Could not load site-packages path: {e}")

SITE_PACKAGES_PATH=sysconfig.get_paths()["purelib"]

def install_pth_file():
    global SITE_PACKAGES_PATH
    #initialize()
    # env_path = os.environ.get("DOCOREAI_ENV_PATH")
    # if not env_path:
    #     print("❌ Cannot install .pth file — DOCOREAI_ENV_PATH not set.")
    #     return

    try:
        if not SITE_PACKAGES_PATH:
            raise ValueError("SITE_PACKAGES_PATH not set")

        pth_path = os.path.join(SITE_PACKAGES_PATH, "docoreai_autopatch.pth")
        #dprint("📄 Installing patch at:", pth_path)


        current_env_path = str(Path.cwd().resolve())
        #we are inserting the path here coz auto_patch runs in a different process and to give access to current path's env
        # pth_code = (
        #     f"import os; os.environ['DOCOREAI_ENV_PATH'] = r'{current_env_path}'; import docore_ai.auto_patch\n"
        # )
        pth_code = (
            f"import os; os.environ['DOCOREAI_ENV_PATH'] = {repr(current_env_path)}; import docore_ai.auto_patch\n"
        )



        with open(pth_path, "w", encoding="utf-8") as f:
            f.write(pth_code)

        #dprint(f"✅ .pth file created at: {pth_path}")
        
        # 🔁 Simulate immediate reactivation
        #subprocess.run(["python", "-c", "print('activating patch...')"], check=True)    
        subprocess.run([sys.executable, "-c", "print('activating dopatch...')"], check=True)    
        return True

    except Exception as e:
        dprint(f"❌ [ERROR] Failed to create .pth file: {e}")
        
        return False


def blank_pth_file():
    global SITE_PACKAGES_PATH
    try:
        if not SITE_PACKAGES_PATH:
            raise ValueError("SITE_PACKAGES_PATH not set")

        pth_path = os.path.join(SITE_PACKAGES_PATH, "docoreai_autopatch.pth")

        if os.path.exists(pth_path):
            with open(pth_path, "w", encoding="utf-8") as f:
                f.write("")  # Blank out the file instead of deleting
            #dprint(f"🧹 .pth file blanked (disabled) at: {pth_path}")
        else:
            dprint("[INFO] No .pth file found to blank out.")

        # 🔕 Simulate deactivation confirmation
        #subprocess.run(["python", "-c", "print('🔕 DoCoreAI patch is now disabled')"], check=True)
        subprocess.run([sys.executable, "-c", "print('🔕 dopatch is now disabled')"], check=True)


    except Exception as e:
        dprint(f"❌ [ERROR] Failed to blank out .pth file: {e}")
