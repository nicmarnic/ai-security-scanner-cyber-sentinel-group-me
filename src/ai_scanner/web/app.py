from __future__ import annotations
import os, tempfile
from flask import Flask, request, redirect, url_for, send_file, render_template_string
from ai_scanner.cli.ai_scanner import do_scan
from ai_scanner.reporter import render_html, write_pdf_summary

app = Flask(__name__)

INDEX = """
<!doctype html>
<title>AI Security Scanner</title>
<h1>AI Security Scanner – GUI</h1>
<form method="post" action="{{ url_for('run_scan') }}">
  <label>Bersagli (separati da spazio):</label><br>
  <input name="targets" style="width:420px" placeholder="scanme.nmap.org 192.168.1.1"><br><br>
  <label>Profilo:</label>
  <input name="profile" value="balanced">
  <label>Ports:</label>
  <input name="ports" placeholder="80,443"><br><br>
  <label><input type="checkbox" name="xml" checked> Salva/usa XML</label><br>
  <label><input type="checkbox" name="ai_api"> Abilita Sintesi AI</label>
  <input name="ai_model" placeholder="sonar / pplx-70b-online" style="width:220px">
  <input name="ai_timeout" placeholder="15" style="width:60px"><br><br>
  <button type="submit">Esegui scan e genera report</button>
</form>
{% if report_ready %}
  <p>Report generato.</p>
  <p><a href="{{ url_for('view_report') }}" target="_blank">Apri report HTML</a> |
     <a href="{{ url_for('download_pdf') }}">Scarica PDF</a></p>
{% endif %}
"""

OUT_DIR = os.environ.get("SCANNER_WEB_OUT", os.path.join(tempfile.gettempdir(), "ai_scanner_web"))

@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX, report_ready=os.path.exists(os.path.join(OUT_DIR, "report.html")))

@app.route("/run", methods=["POST"])
def run_scan():
    targets = request.form.get("targets","").split()
    profile = request.form.get("profile","balanced")
    ports = request.form.get("ports") or None
    xml = bool(request.form.get("xml"))
    ai_api = bool(request.form.get("ai_api"))
    ai_model = request.form.get("ai_model") or None
    ai_timeout = int(request.form.get("ai_timeout") or 15)

    os.makedirs(OUT_DIR, exist_ok=True)
    doc = do_scan(targets, profile, ports, xml, timeout=None, extra=None,
                  ai_api=ai_api, ai_model=ai_model, ai_timeout=ai_timeout)
    html_path = os.path.join(OUT_DIR, "report.html")
    pdf_path  = os.path.join(OUT_DIR, "summary.pdf")
    render_html(doc, html_path)
    write_pdf_summary(doc, pdf_path)
    return redirect(url_for("index"))

@app.route("/report")
def view_report():
    return send_file(os.path.join(OUT_DIR, "report.html"), mimetype="text/html", as_attachment=False)  # noqa
@app.route("/report.pdf")
def download_pdf():
    return send_file(os.path.join(OUT_DIR, "summary.pdf"), mimetype="application/pdf", as_attachment=True)  # noqa

if __name__ == "__main__":
    app.run(debug=True)
