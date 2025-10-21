# src/ai_scanner/scanner/scanner_config.py
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional, Dict

@dataclass(frozen=True)
class ScanProfile:
    name: str = "balanced"
    ports: Optional[str] = None
    timing: str = "T4"   # T0..T5
    scripts: Optional[str] = "default"
    extra: Optional[str] = "-n"
    timeout: int = 120
    xml: bool = False

PROFILES: Dict[str, ScanProfile] = {
    "stealth":   ScanProfile(name="stealth",   timing="T1", scripts=None,    extra="-n",      timeout=180, xml=True),
    "polite":    ScanProfile(name="polite",    timing="T2", scripts="default", extra="-n",    timeout=180, xml=False),
    "balanced":  ScanProfile(name="balanced",  timing="T4", scripts="default", extra="-n",    timeout=120, xml=False),
    "xml_full":  ScanProfile(name="xml_full",  timing="T4", scripts="default", extra="-n -Pn", timeout=180, xml=True),
    "insane":    ScanProfile(name="insane",    timing="T5", scripts=None,    extra="-n -Pn", timeout=90,  xml=False),
}
DEFAULT_PROFILE: ScanProfile = PROFILES["balanced"]

def get_profile(name: str, *, ports: Optional[str] = None, extra: Optional[str] = None,
                xml: Optional[bool] = None, timeout: Optional[int] = None) -> ScanProfile:
    base = PROFILES.get(name, DEFAULT_PROFILE)
    new = base
    if ports is not None:
        new = replace(new, ports=ports)
    if extra is not None:
        new = replace(new, extra=extra)
    if xml is not None:
        new = replace(new, xml=xml)
    if timeout is not None:
        new = replace(new, timeout=timeout)
    return new
