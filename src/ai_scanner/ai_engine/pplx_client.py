# src/ai_scanner/ai_engine/pplx_client.py
import os, requests
CHAT_URL = "https://api.perplexity.ai/chat/completions"
RESP_URL = "https://api.perplexity.ai/responses"

def _raise_with_body(r):
    try: err = r.json()
    except Exception: err = r.text
    raise RuntimeError(f"PPLX API {r.status_code}: {err}")

def _call_chat(model, prompt, key, timeout):
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    p = {"model": model, "messages":[
        {"role":"system","content":"Sei un analista di sicurezza conciso e preciso."},
        {"role":"user","content":prompt}],
        "temperature":0.2,"max_tokens":400,"top_p":0.9}
    r = requests.post(CHAT_URL, json=p, headers=h, timeout=timeout)
    if r.status_code >= 400: _raise_with_body(r)
    d = r.json()
    return d["choices"][0]["message"]["content"].strip()

def _call_responses(model, prompt, key, timeout):
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    p = {"model": model, "input": prompt, "temperature":0.2, "max_output_tokens":400}
    r = requests.post(RESP_URL, json=p, headers=h, timeout=timeout)
    if r.status_code >= 400: _raise_with_body(r)
    d = r.json()
    if "output_text" in d and d["output_text"]: return d["output_text"].strip()
    if "choices" in d and d["choices"]:
        msg = d["choices"][0].get("message",{}).get("content")
        if msg: return msg.strip()
    if "output" in d and d["output"]:
        first = d["output"][0].get("content",[{}])[0]
        txt = first.get("text")
        if txt: return txt.strip()
    return str(d)

def pplx_summarize(host, model=None, timeout=None, style=None):
    key = os.environ.get("PPLX_API_KEY")
    if not key: raise RuntimeError("PPLX_API_KEY non impostata")
    model = model or os.environ.get("PPLX_MODEL","sonar")
    timeout = int(timeout or os.environ.get("AI_TIMEOUT","15"))
    style = (style or os.environ.get("PPLX_API_STYLE","chat")).lower()
    prompt = ("Analizza i rischi dell'host (porte/servizi/versioni) e restituisci 3-5 bullet "
              "con priorità e una breve raccomandazione finale.\n"
              f"Dati: {host}")
    if style == "responses":
        return _call_responses(model, prompt, key, timeout)
    try:
        return _call_chat(model, prompt, key, timeout)
    except RuntimeError:
        return _call_responses(model, prompt, key, timeout)
