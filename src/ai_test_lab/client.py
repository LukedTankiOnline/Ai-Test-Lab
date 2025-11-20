import os
import time
import json
from typing import Tuple, Dict, Any

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

try:
    import openai
    openai.api_key = OPENAI_KEY
except Exception:
    openai = None

def send_to_openai(prompt: str, model: str = "gpt-3.5-turbo") -> Tuple[str, int, int, float, Dict[str, Any]]:
    if openai is None:
        # fallback: echo
        start = time.time()
        resp = f"[SIMULATED {model}] " + prompt[::-1]
        latency = (time.time() - start) * 1000.0
        return resp, len(prompt.split()), len(resp.split()), latency, {"simulated": True}

    start = time.time()
    # simple chat completion wrapper
    try:
        if model.startswith("gpt-"):
            completion = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512
            )
            text = completion.choices[0].message.content
            tokens_in = completion.usage.get("prompt_tokens", 0)
            tokens_out = completion.usage.get("completion_tokens", 0)
        else:
            # text completion fallback
            completion = openai.Completion.create(model=model, prompt=prompt, max_tokens=512)
            text = completion.choices[0].text
            tokens_in = 0
            tokens_out = 0
    except Exception as e:
        return f"[ERROR] {e}", 0, 0, 0.0, {"error": str(e)}

    latency = (time.time() - start) * 1000.0
    return text, tokens_in, tokens_out, latency, {"model": model}

def send_prompt(prompt: str, model: str = "simulated") -> Dict[str, Any]:
    if model == "simulated":
        resp, ti, to, lat, meta = send_to_openai(prompt, model="simulated")
    else:
        resp, ti, to, lat, meta = send_to_openai(prompt, model=model)
    return {
        "prompt": prompt,
        "response": resp,
        "tokens_in": ti,
        "tokens_out": to,
        "latency_ms": lat,
        "meta": meta,
    }
