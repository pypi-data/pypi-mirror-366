# token_utils.py

import tiktoken

def token_profiler(prompt: str, model_name: str) -> dict:
    # --- 1. Estimate token count ---
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # fallback

    token_count = len(encoding.encode(prompt))

    # --- 2. Estimate cost ---
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

    bloat_score_raw = avg_tokens_per_word / 1.2
    bloat_score = round(bloat_score_raw, 2)
    bloat_flag = bloat_score_raw > 1.1

    # --- 4. Savings Estimation ---
    savings_ratio = 0.3 if bloat_flag else 0.0
    estimated_savings = round(estimated_cost * savings_ratio, 6)
    savings_percent = f"{int(savings_ratio * 100)}%"

    return {
        "token_count": token_count,
        "estimated_cost": estimated_cost,
        "bloat_score": bloat_score,
        "bloat_flag": bloat_flag,
        "estimated_savings_if_optimized": estimated_savings,
        "estimated_savings%_if_optimized": savings_percent
    }
