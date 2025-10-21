# src/ai_scanner/scanner/nmap_wrapper.py
from __future__ import annotations
import shutil, subprocess
from typing import Optional, Dict, Any, List, Tuple
import xml.etree.ElementTree as ET

class ScanProfileLike:
    ports: Optional[str]
    timing: str
    scripts: Optional[str]
    extra: Optional[str]
    timeout: int
    xml: bool

def _which(exe: str) -> Optional[str]:
    return shutil.which(exe)

def build_nmap_command(target: str, profile: ScanProfileLike) -> List[str]:
    cmd = ["nmap", "-sV", f"-{profile.timing}"]
    if profile.ports:   cmd += ["-p", profile.ports]
    if profile.scripts: cmd += ["--script", profile.scripts]
    if profile.extra:   cmd += profile.extra.split()
    if profile.xml:     cmd += ["-oX", "-"]
    cmd.append(target)
    return cmd

def _run(command: List[str], timeout: int) -> Tuple[int, str, str]:
    try:
        res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, timeout=timeout, check=False)
        return res.returncode, res.stdout, res.stderr
    except subprocess.TimeoutExpired as e:
        return 124, e.stdout or "", e.stderr or "Operazione terminata per timeout."
    except FileNotFoundError as e:
        return 127, "", f"Eseguibile non trovato: {e}"
    except Exception as e:
        return 1, "", f"Errore imprevisto: {e}"

def parse_nmap_xml(xml_text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"hosts": []}
    try:
        root = ET.fromstring(xml_text)
        for host in root.findall("host"):
            status = host.find("status")
            addr_el = host.find("address")
            ports_el = host.find("ports")
            host_d: Dict[str, Any] = {
                "state": status.get("state") if status is not None else None,
                "address": addr_el.get("addr") if addr_el is not None else None,
                "ports": [],
            }
            if ports_el is not None:
                for p in ports_el.findall("port"):
                    portid = p.get("portid")
                    proto = p.get("protocol")
                    state_el = p.find("state")
                    svc_el = p.find("service")
                    host_d["ports"].append({
                        "port": int(portid) if portid and portid.isdigit() else portid,
                        "proto": proto,
                        "state": state_el.get("state") if state_el is not None else None,
                        "name": svc_el.get("name") if svc_el is not None else None,
                        "product": svc_el.get("product") if svc_el is not None else None,
                        "version": svc_el.get("version") if svc_el is not None else None,
                    })
            out["hosts"].append(host_d)
    except ET.ParseError:
        out["error"] = "XML non valido"
    return out

def run_nmap(target: str, profile: ScanProfileLike) -> Dict[str, Any]:
    if _which("nmap") is None:
        return {"rc": 127, "stdout": "", "stderr": "Errore: 'nmap' non è nel PATH.", "cmd": ["nmap"]}
    cmd = build_nmap_command(target, profile)
    rc, out, err = _run(cmd, timeout=profile.timeout)
    result: Dict[str, Any] = {"rc": rc, "stdout": out, "stderr": err, "cmd": cmd}
    if profile.xml and out:
        result["parsed"] = parse_nmap_xml(out)
    return result
