#token_auth.py
import requests
from .config import DOCOREAI_API_URL, DOCOREAI_TOKEN
from docore_ai.utils.logger import dprint

_token_validation_result = None

def validate_token():
    global _token_validation_result

    if _token_validation_result is not None:
        return _token_validation_result

    if not DOCOREAI_TOKEN:
        dprint("🔒 No token provided. Please set DOCOREAI_TOKEN in your .env file.")
        dprint("Create New Token at https://docoreai.com/generate-token - Needs app restart (fresh read from .env)")
        return {
            "valid": False,
            "user_id": None,
            "message": "No token provided. - mod:token_auth"
        }
        

    try:
        response = requests.post(f"{DOCOREAI_API_URL}/wp-json/docoreai/v1/validate-token", json={"token": DOCOREAI_TOKEN})
        if response.status_code == 200:
            result = response.json()
            if result.get("valid", False):
                _token_validation_result = result  # Only cache if token is valid
            return result

        else:
            return {
                "valid": False,
                "user_id": None,
                "message": f"Server error. Status code: {response.status_code}"
            }
    except Exception as e:
        dprint(f"Token validation failed: {e}")
        return {
            "valid": False,
            "user_id": None,
            "message": f"Exception during token validation: {str(e)}"
        }
