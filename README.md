# AI Security Scanner (MVP)

Scanner Nmap modulare con parsing XML, storage, AI locale (punteggio rischio) e report HTML/PDF. Include CLI e interfacce grafiche: Desktop (Tkinter) e Web locale (Flask).

## Architettura
Scanner → Parser → Data Storage (JSON/DB) → AI Engine → Reporter → HTML/PDF

## Requisiti
- Python 3.10+ (consigliato 3.12)
- Nmap nel PATH
- Opzionali per GUI:
  - Tkinter (Desktop GUI)
  - Flask (Web UI locale)

---

## Installazione

### Windows (PowerShell)
nella root del progetto
py -m venv .venv
..venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e .

Nmap: scarica da https://nmap.org/download.html e aggiungi al PATH se necessario

### Linux (Ubuntu/Debian)
sudo apt update
sudo apt install -y nmap python3.12-venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

GUI Tkinter opzionale
sudo apt install -y python3.12-tk

(sostituisci 3.12 con la tua versione se differente: controlla con python3 --version)

### macOS
brew install nmap
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

Tkinter è incluso nelle build ufficiali; in caso di problemi, usa Python.org installer.


---

## Uso CLI

Pipeline completa con parsing XML e report:

ai-scanner run --targets scanme.nmap.org --profile balanced --xml --out-dir reports

Alternativa senza entry point:
python -m ai_scanner.cli.ai_scanner run --targets scanme.nmap.org --profile balanced --xml --out-dir reports


Output:
- reports/report.html
- reports/summary.pdf
- Dati (default) in data/scans.jsonl

---

## GUI Desktop (Tkinter)

### Abilitazione
- Windows: già disponibile.
- Linux: installa Tkinter della tua versione (esempio 3.12):

sudo apt install -y python3.12-tk

- macOS: tipicamente incluso (se manca, usa installer Python.org).

### Avvio
python -m ai_scanner.gui.tk_app


Funzioni:
- Campo Targets (spazio separati), scelta Profile, checkbox XML, Output dir.
- Bottone “Run” → genera report HTML/PDF e apre il report nel browser.

---

## Web UI Locale (Flask)


### Avvio server

python -m ai_scanner.api_web.app

Browser → http://127.0.0.1:5000


Funzioni:
- Form per Targets, Profile, XML.
- Al submit genera reports/report.html e reports/summary.pdf scaricabili.

---

## Profili di scansione
- stealth (T1), polite (T2), balanced (T4, default), xml_full (T4, XML on, -Pn), insane (T5).
- Modifica in `src/ai_scanner/scanner/scanner_config.py` (porte, script NSE, extra, timeout, XML).

---

## Struttura progetto
src/ai_scanner/
cli/ai_scanner.py # Entry-point CLI
scanner/
scanner_config.py # Profili
nmap_wrapper.py # Subprocess Nmap
parser/
models.py
nmap_xml_parser.py
storage/
json_store.py
sqlite_store.py
ai_engine/
rules.py
risk_score.py # score_host()
reporter/
html_reporter.py
pdf_reporter.py
templates/
report.html.j2
gui/ e api_web/ sono sotto src/ai_scanner/ (tk_app.py, app.py)
tests/ con test_scanner.py, test_parser.py, test_ai_engine.py


---

## Test
python -m unittest discover -s tests -p "test_*.py"


---

## Troubleshooting

- `ai-scanner: comando non trovato`
  - Attiva il venv e reinstalla: `python -m pip install -e .`
  - Usa il modulo: `python -m ai_scanner.cli.ai_scanner ...`

- `ModuleNotFoundError` per moduli del progetto
  - Esegui dalla root o usa `python -m ...`
  - Verifica `__init__.py` nei package, poi reinstalla in editable

- `nmap: not found`
  - Installa Nmap e verifica PATH

- `tkinter` mancante
  - Linux: `sudo apt install python3.<ver>-tk`
  - macOS/Windows: usa distribuzione Python con Tk incluso

- `ensurepip/venv` mancante (Linux)
  - `sudo apt install python3.<ver>-venv` e ricrea `.venv`

---

## Sicurezza
Usa il tool solo su asset per cui hai autorizzazione esplicita. Le scansioni possono essere intrusive; rispetta leggi e policy di rete.

## Contributi
- Branch per feature → test → PR con descrizione chiara.
- Aggiorna README e test quando cambi opzioni/parametri.

##Licenza
