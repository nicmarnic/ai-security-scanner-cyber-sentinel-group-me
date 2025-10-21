# src/ai_scanner/gui/tk_app.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser, os
from ai_scanner.cli.ai_scanner import do_scan
from ai_scanner.reporter import render_html, write_pdf_summary

def run_scan(targets, profile, xml, out_dir):
    doc = do_scan(targets, profile, ports=None, xml=xml, timeout=None, extra=None)
    os.makedirs(out_dir, exist_ok=True)
    html = os.path.join(out_dir, "report.html")
    pdf = os.path.join(out_dir, "summary.pdf")
    render_html(doc, html)
    write_pdf_summary(doc, pdf)
    return html, pdf

def main():
    root = tk.Tk()
    root.title("AI Security Scanner")
    frm = ttk.Frame(root, padding=12); frm.grid(sticky="nsew")
    ttk.Label(frm, text="Targets (spazio separati):").grid(row=0, column=0, sticky="w")
    targets_var = tk.StringVar(value="scanme.nmap.org")
    ttk.Entry(frm, textvariable=targets_var, width=50).grid(row=0, column=1, sticky="ew")
    ttk.Label(frm, text="Profile:").grid(row=1, column=0, sticky="w")
    profile_var = tk.StringVar(value="balanced")
    ttk.Combobox(frm, textvariable=profile_var, values=["stealth","polite","balanced","xml_full","insane"], width=20).grid(row=1, column=1, sticky="w")
    xml_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(frm, text="Enable XML parsing", variable=xml_var).grid(row=2, column=1, sticky="w")
    outdir_var = tk.StringVar(value="reports")
    ttk.Label(frm, text="Output dir:").grid(row=3, column=0, sticky="w")
    ttk.Entry(frm, textvariable=outdir_var, width=50).grid(row=3, column=1, sticky="ew")

    def on_run():
        try:
            html, pdf = run_scan(targets_var.get().split(), profile_var.get(), xml_var.get(), outdir_var.get())
            messagebox.showinfo("Done", f"HTML: {html}\nPDF: {pdf}")
            webbrowser.open(f"file://{os.path.abspath(html)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(frm, text="Run", command=on_run).grid(row=4, column=1, sticky="e", pady=8)
    root.mainloop()

if __name__ == "__main__":
    main()
