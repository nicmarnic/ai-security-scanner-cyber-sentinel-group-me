# src/ai_scanner/reporter/pdf_reporter.py
from __future__ import annotations
from typing import Any, Dict
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import os

def write_pdf_summary(data: Dict[str, Any], out_path: str) -> str:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    y = height - 2*cm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y, "AI Security Scanner - Executive Summary")
    y -= 1*cm
    c.setFont("Helvetica", 10)
    for host in data.get("hosts", []):
        if y < 3*cm:
            c.showPage(); y = height - 2*cm; c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, f"Host: {host.get('address','?')}  State: {host.get('state','?')}")
        y -= 0.5*cm
        rs = host.get("ai", {})
        c.drawString(2*cm, y, f"Score: {rs.get('score',0)}  Summary: {rs.get('summary','')}")
        y -= 0.5*cm
        for p in host.get("ports", [])[:8]:
            c.drawString(2.5*cm, y, f"- {p.get('proto','tcp')}/{p.get('port')} {p.get('state','?')} {p.get('name','')}")
            y -= 0.4*cm
        y -= 0.2*cm
    c.showPage()
    c.save()
    return out_path
