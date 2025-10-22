import os, requests

API_URL = "https://api.perplexity.ai/chat/completions"

def pplx_summarize(host: dict, model: str|None=None, timeout: int|None=None) -> str:
    api_key = os.environ.get("PPLX_API_KEY")
    if not api_key:
        raise RuntimeError("PPLX_API_KEY non impostata")
    model = model or os.environ.get("PPLX_MODEL", "pplx-70b-online")
    timeout = int(timeout or os.environ.get("AI_TIMEOUT", "15"))
    prompt = (
        "Agisci come analista sicurezza. Dati host (porte/servizi/versioni):\n"
        f"{host}\n"
        "Fornisci elenco rischi prioritari e breve raccomandazione finale."
    )
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 400,
    }
    r = requests.post(API_URL, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()

