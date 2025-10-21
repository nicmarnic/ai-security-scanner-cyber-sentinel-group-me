# src/ai_scanner/ai_engine/risk_score.py
from __future__ import annotations
from typing import Dict, Any, List
from .rules import default_rules

def score_host(host: Dict[str, Any]) -> Dict[str, Any]:
    total = 0
    findings: List[str] = []
    rules = default_rules()
    for p in host.get("ports", []):
        if p.get("state") != "open":
            continue
        portnum = p.get("port")
        for r in rules:
            if r["port"] == portnum:
                total += r["weight"]
                findings.append(f"Porta {portnum}: {r['note']}")
    total = max(0, min(100, total))
    summary = "Rischio moderato" if total < 40 else ("Rischio alto" if total >= 70 else "Rischio medio")
    return {"score": total, "findings": findings, "summary": summary}
