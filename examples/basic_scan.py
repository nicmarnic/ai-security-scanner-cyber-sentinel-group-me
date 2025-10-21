# examples/basic_scan.py
#!/usr/bin/env python3
from src.ai_scanner.scanner import get_profile
from src.ai_scanner.scanner.nmap_wrapper import run_nmap
import sys, json

def main():
    if len(sys.argv) < 2:
        print("Uso: basic_scan.py <target> [profile]", file=sys.stderr); sys.exit(2)
    target = sys.argv[1]
    profile = get_profile(sys.argv[2] if len(sys.argv) > 2 else "balanced", xml=True)
    res = run_nmap(target, profile)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
