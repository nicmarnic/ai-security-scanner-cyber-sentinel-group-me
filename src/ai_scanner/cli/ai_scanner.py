# src/ai_scanner/cli/ai_scanner.py
from __future__ import annotations
import argparse, json, os
from typing import List, Dict, Any
from ai_scanner.scanner import get_profile
from ai_scanner.scanner.nmap_wrapper import run_nmap
from ai_scanner.parser.nmap_xml_parser import parse_scan_xml
from ai_scanner.reporter import render_html, write_pdf_summary
from ai_scanner.ai_engine import score_host
from ai_scanner.storage.json_store import JSONStore

def do_scan(targets: List[str], profile_name: str, ports: str|None, xml: bool,
            timeout: int|None, extra: str|None) -> Dict[str, Any]:
    profile = get_profile(profile_name, ports=ports, xml=xml if xml else None, timeout=timeout, extra=extra)
    doc: Dict[str, Any] = {"hosts": []}
    raw_map: Dict[str, Any] = {}
    for tgt in targets:
        res = run_nmap(tgt, profile)
        raw_map[tgt] = res
        if xml and res.get("stdout"):
            parsed = parse_scan_xml(res["stdout"])
            if parsed.error is None:
                hlist = []
                for h in parsed.hosts:
                    hlist.append({
                        "address": h.address,
                        "state": h.state,
                        "ports": [vars(p) for p in h.ports],
                    })
                for h in hlist:
                    h["ai"] = score_host(h)
                doc["hosts"].extend(hlist)
        else:
            doc["hosts"].append({"address": tgt, "state": "unknown", "ports": [], "ai": {"score":0,"findings":[],"summary":"N/D"}})
    doc["_raw"] = raw_map
    return doc

def main() -> None:
    ap = argparse.ArgumentParser(description="AI Security Scanner CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="Esegui scansione e stampa JSON")
    p_scan.add_argument("--targets", nargs="+", required=True)
    p_scan.add_argument("--profile", default="balanced")
    p_scan.add_argument("--ports", default=None)
    p_scan.add_argument("--xml", action="store_true")
    p_scan.add_argument("--timeout", type=int, default=None)
    p_scan.add_argument("--extra", default=None)

    p_report = sub.add_parser("report", help="Genera report da JSON")
    p_report.add_argument("--json", required=True)
    p_report.add_argument("--out-dir", default="reports")

    p_run = sub.add_parser("run", help="Pipeline completa scan→store→report")
    p_run.add_argument("--targets", nargs="+", required=True)
    p_run.add_argument("--profile", default="balanced")
    p_run.add_argument("--ports", default=None)
    p_run.add_argument("--xml", action="store_true")
    p_run.add_argument("--timeout", type=int, default=None)
    p_run.add_argument("--extra", default=None)
    p_run.add_argument("--out-dir", default="reports")

    args = ap.parse_args()
    if args.cmd == "scan":
        doc = do_scan(args.targets, args.profile, args.ports, args.xml, args.timeout, args.extra)
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return

    if args.cmd == "report":
        with open(args.json, "r", encoding="utf-8") as f:
            doc = json.load(f)
        os.makedirs(args.out_dir, exist_ok=True)
        html_path = os.path.join(args.out_dir, "report.html")
        pdf_path = os.path.join(args.out_dir, "summary.pdf")
        render_html(doc, html_path)
        write_pdf_summary(doc, pdf_path)
        print(f"HTML: {html_path}\nPDF: {pdf_path}")
        return

    if args.cmd == "run":
        os.makedirs(args.out_dir, exist_ok=True)
        doc = do_scan(args.targets, args.profile, args.ports, args.xml, args.timeout, args.extra)
        # store jsonl
        store = JSONStore()
        for tgt, raw in doc.get("_raw", {}).items():
            parsed = None
            for h in doc["hosts"]:
                if h.get("address") == tgt:
                    parsed = h
                    break
            store.save(tgt, raw, parsed)
        # report
        html_path = os.path.join(args.out_dir, "report.html")
        pdf_path = os.path.join(args.out_dir, "summary.pdf")
        render_html(doc, html_path)
        write_pdf_summary(doc, pdf_path)
        print(f"HTML: {html_path}\nPDF: {pdf_path}")
        return

if __name__ == "__main__":
    main()
