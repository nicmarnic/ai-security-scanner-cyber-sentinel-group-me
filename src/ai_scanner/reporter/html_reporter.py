# src/ai_scanner/reporter/html_reporter.py
from __future__ import annotations
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

def render_html(data: Dict[str, Any], out_path: str, templates_dir: str = None) -> str:
    if templates_dir is None:
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=select_autoescape(["html"]))
    tpl = env.get_template("report.html.j2")
    html = tpl.render(doc=data)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
