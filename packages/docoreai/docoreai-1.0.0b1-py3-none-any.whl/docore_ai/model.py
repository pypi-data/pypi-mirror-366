import os
from pathlib import Path
from docore_ai.utils.csv_logger import append_telemetry
from docore_ai.utils.logger import dprint, dsys_exit
import sys

import tiktoken
from typing import Optional
from groq import Groq
import time
import json


from docore_ai.telemetry.token_utils import token_profiler
from docore_ai.telemetry.tracker import get_version_info
from docore_ai.telemetry.token_auth import validate_token
from .prompt_updates.prompt_loader  import get_current_bundle, PromptLoaderError, load_local_bundle
from docore_ai.prompt_updates import check_prompt_update
from docore_ai.init_engine import initialize, get_state
from docore_ai.telemetry.telemetry_wp import (
    save_telemetry_to_wordpress,
    save_failure_telemetry_to_wordpress,
    prepare_telemetry_payload,
    log_telemetry_to_wordpress
)

_USER_MESSAGE = None

try:
    import openai
except ImportError:
    dprint("⚠️ OpenAI not installed. DoCoreAI auto-patch skipped.")
    openai = None

try:
    import groq
except ImportError:
    dprint("⚠️ Groq not installed. DoCoreAI Groq auto-patch skipped.")
    groq = None

# OpenAI version logic (only if openai is available)
if openai:
    try:
        from importlib.metadata import version as get_version
    except ImportError:
        from importlib_metadata import version as get_version  # for Python <3.8

from packaging import version

try:
    openai_version = get_version("openai")
    if version.parse(openai_version) >= version.parse("1.0.0"):
        from openai import OpenAI as OpenAIClass
        OpenAI = OpenAIClass
    else:
        OpenAI = None  # fallback if needed
except Exception as e:
    dprint(f"⚠️ Could not determine OpenAI version: {e}")
    OpenAI = None
else:
    OpenAI = None

MIN_PYTHON = (3, 8)
if sys.version_info < MIN_PYTHON:
    dprint(f"❌ Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or higher is required for smooth functioning. You are using {sys.version.split()[0]}.")


_INITIALIZED = False
_USER_ID = None
_PROMPT_BUNDLE = None
OPENAI_API_KEY = None
GROQ_API_KEY = None
MODEL_PROVIDER = None
MODEL_NAME = None
DOCOREAI_API_URL = None
DOCOREAI_TOKEN = None


def intelligence_profiler(user_content: str, role: str, model_provider: Optional[str] = None, model_name: Optional[str] = None,
                          show_token_usage: Optional[bool] = False, estimated_cost: Optional[bool] = True) -> dict:
    #### LIVE -- LIVE---LIVE -- LIVE
    #initialize_docoreai()
    dprint("activating intelligence profiler...")
    initialize()  #initialize is called only from cli todo delete after docoreai start cmd
    state = get_state()
    #dprint(f"📦 From get_state(): model_provider = {state.get('model_provider')}")
    # Resolve model_provider and model_name from state if not passed explicitly
    model_provider = model_provider or state.get("model_provider")
    model_name = model_name or state.get("model_name")
    #OPENAI_API_KEY=state.get("model_name")

    # --- Load system prompt ---
    try:
        bundle = get_current_bundle()

        system_message = bundle["system_message"]
        dprint(f"system_message FROM PROMPT LOADER: {system_message}")
        prompt_version = bundle["prompt_version"]
        #dprint(f"prompt_version FROM PROMPT LOADER: {prompt_version}")
    except PromptLoaderError as e:
        # Fallback or fail-fast
        dsys_exit(f"Could not load system prompt: {e}")

    user_message = f"""
    User Request: "{user_content}"
    Role: "{role}"
    """
    
    dprint(user_content)
    dprint(role)
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message}
    ]
    dprint(messages)
    start_time = time.time()
    
    # Choose model provider
    try:
        if model_provider == "openai":
            openai.api_key = state.get("openai_api_key")
            dprint(openai.api_key)
            dprint("🔑 Using OpenAI API...")
            dprint(f"OPENAI_API_KEY loaded: {len(openai.api_key) if openai.api_key else '❌ Not Found'}")

            dprint(messages)
            dprint("----------")
            dprint(model_name)
            dprint("----------")
            try:
                sdk_version = version.parse(openai.__version__)
                if sdk_version >= version.parse("1.0.0"):
                    dprint(f"🔍 Detected OpenAI SDK version: {sdk_version}")
                    # Build args safely
                    chat_kwargs = {
                        "model": model_name,
                        "messages": messages,
                    }

                    # Inject skip_tracking temporarily
                    state["skip_tracking"] = True                        
                    if state.get("skip_tracking"):
                        chat_kwargs["skip_tracking"] = True

                    # Let auto_patch see it, then pop before calling OpenAI
                    
                    safe_kwargs = dict(chat_kwargs)  # copy for patch
                    skip_flag = safe_kwargs.pop("skip_tracking", None)

                    client = openai.Client()
                    response = client.chat.completions.create(**safe_kwargs)                
                else:
                    dprint(f"🔍 Detected OpenAI SDK version: {sdk_version}")
                    chat_kwargs = {
                        "model": model_name,
                        "messages": messages,
                    }
                    state["skip_tracking"] = True                        
                    if state.get("skip_tracking"):
                        chat_kwargs["skip_tracking"] = True

                    safe_kwargs = dict(chat_kwargs)
                    skip_flag = safe_kwargs.pop("skip_tracking", None)

                    response = openai.ChatCompletion.create(**safe_kwargs)
                    state["skip_tracking"] = False                        
            except ImportError:
                dprint("❌ OpenAI SDK is not installed. Please run: pip install openai")
                state["skip_tracking"] = False
                sys.exit("Missing OpenAI SDK. Cannot proceed with LLM call.")

            except AttributeError as e:
                dprint(f"❌ SDK AttributeError: {e}")
                state["skip_tracking"] = False
                sys.exit("Installed OpenAI SDK is incompatible or corrupted.")
            state["skip_tracking"] = False
            dprint("✅ OpenAI API call successful - Dynamic Temp Set Internally")
            
        elif model_provider == "groq":
            groq_api_key = state.get("groq_api_key")
            client = Groq(api_key=groq_api_key) 
            dprint("🔑 Using Groq API...")

            dprint(messages)
            dprint("----------")
            dprint(model_name)
            dprint("----------")

            chat_kwargs = {
                "model": model_name,
                "messages": messages,
            }

            # Inject skip_tracking so that patch_groq skips telemetry (e.g., internal optimizer use)
            state["skip_tracking"] = True
            if state.get("skip_tracking"):
                chat_kwargs["skip_tracking"] = True

            safe_kwargs = dict(chat_kwargs)
            skip_flag = safe_kwargs.pop("skip_tracking", None)

            response = client.chat.completions.create(**safe_kwargs)
            state["skip_tracking"] = False

            dprint("✅ Groq API call successful - Dynamic Temp Set Internally")

        else:
            dprint(f"Unsupported model provider - {model_provider} :Report to info@docoreai.com")
            raise ValueError(f"Unsupported model provider: {model_provider}")
                      
        content = response.choices[0].message.content  
        usage = response.usage  # Extract token usage
        

        result = {"response": content}

        if show_token_usage:
            result["usage"] = usage
        if estimated_cost:
            result["token_estimation"] = token_profiler(user_content, model_name)

        execution_time = round(time.time() - start_time, 2)
        version_info = get_version_info()
        bloat_info = token_profiler(user_content, model_name)
        try:
            response_content = json.loads(content)
            if not isinstance(response_content, dict):
                dprint("Response from LLM is not in json format")
                response_content = {"raw": content}
        except Exception as e:
            dprint(f"❌ Failed to decode JSON from LLM response: {e}")
            response_content = {"raw": content}
        is_token_valid = state.get("token_valid")
        is_account_active = state.get("account_state") in ("active", "activation_required") 
        current_user_id = state.get("user_id")

        if is_token_valid and is_account_active:
            dprint("--------------------------") 
            #dprint("is_token_valid : ", is_token_valid ,"is_account_active", is_account_active) 
            dprint("--------------------------") 
            #dprint("current_user_id ",current_user_id)
            payload = prepare_telemetry_payload(
                user_id=current_user_id,
                user_content=user_content,
                role=role,
                model_name=model_name,
                execution_time=execution_time,
                prompt_version=prompt_version,
                version_info=version_info,
                success=True,
                response_content=response_content,
                usage=usage,
                bloat_info=bloat_info
            )
            
            log_telemetry_to_wordpress(success=True, telemetry_data=payload)
            
            payload['user_message'] = user_message
            payload['response'] = response.choices[0].message.content
            append_telemetry(payload)

        return result      
     
    except Exception as e:
        dprint("❌ Exception during API call - intelligence_profiler:", e)
        state["skip_tracking"] = False
        execution_time = round(time.time() - start_time, 2)
        # Save a failed telemetry entry
        if state.get("token_valid"):
            payload = prepare_telemetry_payload(
                user_id=state.get("user_id"),
                user_content=user_content,
                role=role,
                model_name=model_name,
                execution_time=execution_time,
                prompt_version=prompt_version,
                version_info=get_version_info(),
                success=False
            )
            
            log_telemetry_to_wordpress(success=False, failure=True, telemetry_data=payload)
            payload['user_message'] = user_message
            #payload['response'] = response.choices[0].message.content on failure there is no response
            append_telemetry(payload)
            
        else:
            dprint(f"❌ Token invalid:")

        return {"response": None, "error": str(e)}
    
#Added only for tetsting

# def normal_prompt(user_content: str, role: str, model_provider: str = MODEL_PROVIDER, model_name: str = MODEL_NAME,
#                           show_token_usage: Optional[bool] = False, estimated_cost: Optional[bool] = True) -> dict: 
#     """  Sends a normal prompt to the selected LLM (OpenAI or Groq) without intelligence parameters.
#     """
#     system_message = f"""
#     You are an AI assistant. Generate response for the user content.

#     Return **ONLY** the following JSON format:  
#     {{
#         "optimized_response": "<AI-generated response>"
#     }}
#     """
#     user_message = f"""
#     User Request: "{user_content}"
#     """

#     messages = [
#         {"role": "system", "content": system_message},
#         {"role": "user", "content": user_message}
#     ]

#     try:
#         # Choose model provider
#         if model_provider == "openai":
#             openai.api_key = OPENAI_API_KEY
#             response = openai.Client().chat.completions.create(
#                 model=model_name,
#                 messages=messages,
#                 temperature=0.8 # Default - TEMPERATURE SETTING - for Normal Prompt

#             )
#             dprint("✅ OpenAI API call successful - Temperature is passed in the API call. 0.8 Fixed Temp Set Internally")       
#             content = response.choices[0].message.content
#             usage = response.usage  # Extract token usage

#             # Append AI response to message history -MEMORY WIP ToDO
#             #messages.append({"role": "assistant", "content": content})

#             result = {"response": content}

#             if show_token_usage:
#                 result["usage"] = usage
#             if estimated_cost:
#                 result["token_estimation"] = token_profiler(user_content, model_name)
#             return result       

#         elif model_provider == "groq":
#             client = Groq(api_key=GROQ_API_KEY) 

#             # Append new user query to message history -MEMORY WIP ToDO
#             #messages.append({"role": "user", "content": user_input})

#             response = client.chat.completions.create(
#                 messages=messages,
#                 model=model_name,
#                 #temperature=0.8 #Check Groq default temp
#             )
#             dprint("✅ Groq API call successful - No temperature is passed in the API call. 0.8 Fixed Temp Set Internally")       
#             content = response.choices[0].message.content  
#             usage = response.usage  # Extract token usage

#             if show_token_usage:
#                 result["usage"] = usage
#             if estimated_cost:
#                 result["token_estimation"] = token_profiler(user_content, model_name)
#             return result       
#     except Exception as e:
#         dprint("❌ Exception during API call - normal_prompt:", e)
#         return {"response": None, "error": str(e)}


def token_profiler(prompt: str, model_name) -> dict:
    # --- 1. Estimate token count ---
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # fallback

    token_count = len(encoding.encode(prompt))

    # --- 2. Estimate cost (simplified) ---
    # Source: https://openai.com/pricing
    price_per_1k = {
        "gpt-3.5-turbo": 0.0015,
        "gpt-4": 0.03,
        "gpt-4-turbo": 0.01,
        "gemma-2b": 0.0005,
        "gemma-9b": 0.001,
    }
    
    cost_per_token = price_per_1k.get(model_name, 0.0015) / 1000
    estimated_cost = round(token_count * cost_per_token, 6)

    # --- 3. Heuristic Bloat Score ---
    word_count = len(prompt.split())
    avg_tokens_per_word = token_count / word_count if word_count else 0

    bloat_score_raw = avg_tokens_per_word / 1.2  # 1.2 is healthy average
    bloat_score = round(bloat_score_raw, 2)
    bloat_flag = bloat_score_raw > 1.1  # Only flag if noticeably bloated

    # --- 4. Estimate potential savings if optimized ---
    savings_ratio = 0.3 if bloat_flag else 0.0
    estimated_savings = round(estimated_cost * savings_ratio, 6)
    savings_percent = f"{int(savings_ratio * 100)}%"
    
    return {
        "token_count": token_count,
        "estimated_cost": f"${estimated_cost:.6f}",
        "bloat_score": round(bloat_score, 2),
        "bloat_flag": bloat_flag,
        "estimated_savings_if_optimized": f"${estimated_savings:.6f}",
        "estimated_savings%_if_optimized": savings_percent
    }
