# src/ai_scanner/ai_engine/rules.py
from typing import Dict, Any, List

def default_rules() -> List[Dict[str, Any]]:
    return [
        {"port": 23,   "weight": 30, "note": "Telnet esposto"},
        {"port": 21,   "weight": 20, "note": "FTP potenzialmente in chiaro"},
        {"port": 22,   "weight": 10, "note": "SSH: verifica policy e versioni"},
        {"port": 445,  "weight": 25, "note": "SMB esposto"},
        {"port": 3389, "weight": 30, "note": "RDP esposto"},
        {"port": 80,   "weight": 5,  "note": "HTTP senza TLS"},
        {"port": 5900, "weight": 15, "note": "VNC esposto"},
    ]
