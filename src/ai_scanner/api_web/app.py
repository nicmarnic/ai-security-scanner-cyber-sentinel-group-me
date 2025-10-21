# src/ai_scanner/api_web/app.py
from flask import Flask, render_template_string, request, send_from_directory, redirect, url_for
import os
from ai_scanner.cli.ai_scanner import do_scan
from ai_scanner.reporter import render_html, write_pdf_summary

TPL = """
<form method="post">
  <label>Targets</label><input name="targets" value="scanme.nmap.org" size="50"><br>
  <label>Profile</label>
  <select name="profile">
    {% for p in ["stealth","polite","balanced","xml_full","insane"] %}
      <option value="{{p}}">{{p}}</option>
    {% endfor %}
  </select>
  <label><input type="checkbox" name="xml" checked> XML</label>
  <button type="submit">Run</button>
</form>
{% if html %}
  <p>HTML: <a href="{{ url_for('report', filename='report.html') }}">report.html</a></p>
  <p>PDF: <a href="{{ url_for('report', filename='summary.pdf') }}">summary.pdf</a></p>
{% endif %}
"""

def create_app():
    app = Flask(__name__)
    out_dir = os.path.abspath("reports")
    os.makedirs(out_dir, exist_ok=True)

    @app.route("/", methods=["GET","POST"])
    def index():
        html = None
        if request.method == "POST":
            targets = request.form.get("targets","").split()
            profile = request.form.get("profile","balanced")
            xml = request.form.get("xml") == "on"
            doc = do_scan(targets, profile, ports=None, xml=xml, timeout=None, extra=None)
            html_path = os.path.join(out_dir, "report.html")
            pdf_path = os.path.join(out_dir, "summary.pdf")
            render_html(doc, html_path)
            write_pdf_summary(doc, pdf_path)
            html = True
        return render_template_string(TPL, html=html)

    @app.route("/reports/<path:filename>")
    def report(filename):
        return send_from_directory(out_dir, filename)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
