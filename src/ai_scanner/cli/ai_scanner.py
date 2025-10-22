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
            timeout: int|None, extra: str|None,
            ai_api: bool=False, ai_model: str|None=None, ai_timeout: int|None=None) -> Dict[str, Any]:
    profile = get_profile(profile_name, ports=ports, xml=xml if xml else None, timeout=timeout, extra=extra)
    doc: Dict[str, Any] = {"hosts": []}
    raw_map: Dict[str, Any] = {}
    for tgt in targets:
        res = run_nmap(tgt, profile)
        raw_map[tgt] = res
        if xml and res.get("stdout"):
            parsed = parse_scan_xml(res["stdout"])
            if parsed.error is None:
                for host_info in parsed.hosts:
                    h: Dict[str, Any] = {
                        "address": host_info.address,
                        "state": host_info.state,
                        "ports": [vars(p) for p in host_info.ports],
                    }
                    # punteggio locale sempre
                    h["ai"] = score_host(h)
                    # opzionale: sintesi AI via API
                    if ai_api:
                        try:
                            from ai_scanner.ai_engine.pplx_client import pplx_summarize
                            h["ai_api_summary"] = pplx_summarize(h, model=ai_model, timeout=ai_timeout)
                        except Exception as e:
                            h["ai_api_summary"] = f"AI API errore: {e}"
                    doc["hosts"].append(h)
        else:
            h = {
                "address": tgt,
                "state": "unknown",
                "ports": [],
                "ai": {"score": 0, "findings": [], "summary": "N/D"},
            }
            if ai_api:
                h["ai_api_summary"] = "AI API non eseguita: nessun dato porte disponibile"
            doc["hosts"].append(h)
    doc["_raw"] = raw_map
    return doc

def main() -> None:
    ap = argparse.ArgumentParser(description="AI Security Scanner CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # scan
    p_scan = sub.add_parser("scan", help="Esegui scansione e stampa JSON")
    p_scan.add_argument("--targets", nargs="+", required=True)
    p_scan.add_argument("--profile", default="balanced")
    p_scan.add_argument("--ports", default=None)
    p_scan.add_argument("--xml", action="store_true")
    p_scan.add_argument("--timeout", type=int, default=None)
    p_scan.add_argument("--extra", default=None)
    # flag AI
    p_scan.add_argument("--ai-api", action="store_true")
    p_scan.add_argument("--ai-model", default=None)
    p_scan.add_argument("--ai-timeout", type=int, default=None)

    # report
    p_report = sub.add_parser("report", help="Genera report da JSON")
    p_report.add_argument("--json", required=True)
    p_report.add_argument("--out-dir", default="reports")

        # run
    p_run = sub.add_parser("run", help="Pipeline completa scan→store→report")
    p_run.add_argument("--targets", nargs="+", required=True)
    p_run.add_argument("--profile", default="balanced")
    p_run.add_argument("--ports", default=None)
    p_run.add_argument("--xml", action="store_true")
    p_run.add_argument("--timeout", type=int, default=None)
    p_run.add_argument("--extra", default=None)
    p_run.add_argument("--out-dir", default="reports")
    # flag AI
    p_run.add_argument("--ai-api", action="store_true")
    p_run.add_argument("--ai-model", default=None)
    p_run.add_argument("--ai-timeout", type=int, default=None)

    args = ap.parse_args()

    if args.cmd == "scan":
        doc = do_scan(
            args.targets, args.profile, args.ports, args.xml, args.timeout, args.extra,
            ai_api=args.ai_api, ai_model=args.ai_model, ai_timeout=args.ai_timeout
        )
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
        doc = do_scan(
            args.targets, args.profile, args.ports, args.xml, args.timeout, args.extra,
            ai_api=args.ai_api, ai_model=args.ai_model, ai_timeout=args.ai_timeout
        )
        # store jsonl
        store = JSONStore()
        for tgt, raw in doc.get("_raw", {}).items():
            parsed = next((h for h in doc["hosts"] if h.get("address") == tgt), None)
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

