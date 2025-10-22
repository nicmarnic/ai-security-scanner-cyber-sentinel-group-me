# src/ai_scanner/gui/tk_app.py
from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser, os, threading, queue
from ai_scanner.cli.ai_scanner import do_scan
from ai_scanner.reporter import render_html, write_pdf_summary

def main():
    root = tk.Tk()
    root.title("AI Security Scanner")
    root.geometry("780x360")
    root.columnconfigure(0, weight=1)

    frm = ttk.Frame(root, padding=12)
    frm.grid(sticky="nsew")
    # colonna 1 (gli Entry principali) si espande orizzontalmente
    frm.grid_columnconfigure(1, weight=1)

    r = 0
    # Targets
    ttk.Label(frm, text="Targets (spazio separati):").grid(row=r, column=0, sticky="w", padx=8, pady=6)
    targets_var = tk.StringVar(value="scanme.nmap.org")
    ttk.Entry(frm, textvariable=targets_var).grid(row=r, column=1, columnspan=3, sticky="ew", padx=8, pady=6)

    r += 1
    # Profile + XML
    ttk.Label(frm, text="Profile:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
    profile_var = tk.StringVar(value="balanced")
    ttk.Combobox(frm, textvariable=profile_var,
                 values=["stealth","polite","balanced","xml_full","insane"], width=18)\
        .grid(row=r, column=1, sticky="w", padx=8, pady=6)
    xml_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(frm, text="Abilita XML parsing", variable=xml_var)\
        .grid(row=r, column=2, sticky="w", padx=8, pady=6)

    r += 1
    # Opzioni AI riga 1: modello + timeout su colonne 2-3
    ttk.Label(frm, text="AI Model:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
    ai_model_var = tk.StringVar(value="")
    ttk.Entry(frm, textvariable=ai_model_var).grid(row=r, column=1, sticky="ew", padx=8, pady=6)

    ttk.Label(frm, text="AI Timeout (s):").grid(row=r, column=2, sticky="e", padx=(8,4), pady=6)
    ai_timeout_var = tk.StringVar(value="15")
    ttk.Entry(frm, textvariable=ai_timeout_var, width=6).grid(row=r, column=3, sticky="w", padx=(4,8), pady=6)

    r += 1
    # Opzioni AI riga 2: toggle sintesi
    ai_api_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(frm, text="Abilita Sintesi AI", variable=ai_api_var)\
        .grid(row=r, column=1, sticky="w", padx=8, pady=(0,6))

    r += 1
    # Output dir + chooser
    ttk.Label(frm, text="Output dir:").grid(row=r, column=0, sticky="w", padx=8, pady=6)
    outdir_var = tk.StringVar(value="reports")
    ttk.Entry(frm, textvariable=outdir_var).grid(row=r, column=1, sticky="ew", padx=8, pady=6)

    def choose_dir():
        d = filedialog.askdirectory(initialdir=os.getcwd())
        if d:
            outdir_var.set(d)
    ttk.Button(frm, text="Scegli…", command=choose_dir)\
        .grid(row=r, column=2, sticky="w", padx=8, pady=6)

    r += 1
    # Progress + Run
    pb = ttk.Progressbar(frm, orient="horizontal", mode="indeterminate")
    pb.grid(row=r, column=1, columnspan=2, sticky="ew", padx=8, pady=(8,6))
    status_var = tk.StringVar(value="")
    ttk.Label(frm, textvariable=status_var)\
        .grid(row=r+1, column=1, columnspan=2, sticky="w", padx=8, pady=(0,6))

    run_btn = ttk.Button(frm, text="Run")
    run_btn.grid(row=r, column=3, sticky="e", padx=8, pady=(8,6))
    q: queue.Queue = queue.Queue()
    worker_thread: list[threading.Thread|None] = [None]

    # … lascia invariati queue/worker/poll_queue/on_run …


    def open_report(html_path: str):
        try:
            # Usa file:// path assoluto
            url = "file://" + os.path.abspath(html_path)
            webbrowser.open(url)
        except Exception as e:
            messagebox.showwarning("Browser", f"Impossibile aprire il report: {e}")

    def poll_queue():
        # Controlla completamento/errore dal worker
        try:
            msg = q.get_nowait()
        except queue.Empty:
            root.after(100, poll_queue)
            return
        finally:
            pass

        pb.stop()
        run_btn.config(state="normal")
        if msg["type"] == "ok":
            html_path, pdf_path = msg["html"], msg["pdf"]
            status_var.set(f"Fatto: {html_path}, {pdf_path}")
            open_report(html_path)
        else:
            status_var.set("Errore durante la scansione")
            messagebox.showerror("Errore", str(msg.get("error")))

    def worker(targets, profile, xml, ai_api, ai_model, ai_timeout, out_dir):
        try:
            doc = do_scan(
                targets, profile, ports=None, xml=xml, timeout=None, extra=None,
                ai_api=ai_api, ai_model=(ai_model or None),
                ai_timeout=(int(ai_timeout) if str(ai_timeout).strip() else None)
            )
            os.makedirs(out_dir, exist_ok=True)
            html_path = os.path.join(out_dir, "report.html")
            pdf_path  = os.path.join(out_dir, "summary.pdf")
            render_html(doc, html_path)
            write_pdf_summary(doc, pdf_path)
            q.put({"type":"ok","html":html_path,"pdf":pdf_path})
        except Exception as e:
            q.put({"type":"err","error":e})

    def on_run():
        if worker_thread[0] and worker_thread[0].is_alive():
            return
        targets = targets_var.get().split()
        if not targets:
            messagebox.showwarning("Input", "Inserisci almeno un target")
            return
        profile = profile_var.get()
        xml = xml_var.get()
        ai_api = ai_api_var.get()
        ai_model = ai_model_var.get().strip() or None
        ai_timeout = ai_timeout_var.get().strip() or None
        out_dir = outdir_var.get().strip() or "reports"

        status_var.set("In esecuzione…")
        run_btn.config(state="disabled")
        pb.start(50)

        t = threading.Thread(
            target=worker,
            args=(targets, profile, xml, ai_api, ai_model, ai_timeout, out_dir),
            daemon=True
        )
        worker_thread[0] = t
        t.start()
        root.after(100, poll_queue)

    run_btn.config(command=on_run)
    root.mainloop()

if __name__ == "__main__":
    main()
