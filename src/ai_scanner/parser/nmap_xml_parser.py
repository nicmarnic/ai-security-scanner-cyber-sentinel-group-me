# src/ai_scanner/parser/nmap_xml_parser.py
from __future__ import annotations
from typing import List
import xml.etree.ElementTree as ET
from .models import PortInfo, HostInfo, ScanDoc

def parse_scan_xml(xml_text: str) -> ScanDoc:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return ScanDoc(hosts=[], error="XML non valido")

    hosts: List[HostInfo] = []
    for host in root.findall("host"):
        status = host.find("status")
        addr_el = host.find("address")
        if addr_el is None:
            continue
        h = HostInfo(
            address=addr_el.get("addr", ""),
            state=(status.get("state") if status is not None else "unknown")
        )
        ports_el = host.find("ports")
        if ports_el is not None:
            for p in ports_el.findall("port"):
                portid = p.get("portid")
                proto = p.get("protocol") or "tcp"
                st = p.find("state")
                svc = p.find("service")
                h.ports.append(PortInfo(
                    port=int(portid) if portid and portid.isdigit() else -1,
                    proto=proto,
                    state=(st.get("state") if st is not None else "unknown"),
                    name=(svc.get("name") if svc is not None else None),
                    product=(svc.get("product") if svc is not None else None),
                    version=(svc.get("version") if svc is not None else None),
                ))
        hosts.append(h)
    return ScanDoc(hosts=hosts, error=None)
