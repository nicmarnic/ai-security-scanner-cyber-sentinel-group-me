# src/ai_scanner/parser/models.py
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class PortInfo:
    port: int
    proto: str
    state: str
    name: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None

@dataclass
class HostInfo:
    address: str
    state: str
    ports: List[PortInfo] = field(default_factory=list)

@dataclass
class ScanDoc:
    hosts: List[HostInfo] = field(default_factory=list)
    error: Optional[str] = None
