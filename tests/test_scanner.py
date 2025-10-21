# tests/test_scanner.py
import unittest, types
from src.ai_scanner.scanner.scanner_config import ScanProfile
import src.ai_scanner.scanner.nmap_wrapper as nw

class TestNmapWrapper(unittest.TestCase):
    def test_build_command_full(self):
        profile = ScanProfile(ports="22,80", timing="T3", scripts="default", extra="-n -Pn", timeout=30, xml=True)
        cmd = nw.build_nmap_command("scanme.nmap.org", profile)
        self.assertIn("-T3", cmd); self.assertIn("-oX", cmd); self.assertIn("scanme.nmap.org", cmd)

    def test_missing_nmap(self):
        orig = nw._which
        nw._which = lambda _: None
        try:
            res = nw.run_nmap("127.0.0.1", ScanProfile())
            self.assertEqual(res["rc"], 127)
        finally:
            nw._which = orig

    def test_xml_parse(self):
        xml = """<?xml version="1.0"?><nmaprun>
          <host><status state="up"/><address addr="127.0.0.1" addrtype="ipv4"/>
            <ports><port protocol="tcp" portid="22"><state state="open"/>
              <service name="ssh" product="OpenSSH" version="9.0"/></port></ports>
          </host></nmaprun>"""
        def fake_run(cmd, timeout): return 0, xml, ""
        orig = nw._run
        try:
            nw._run = fake_run
            res = nw.run_nmap("127.0.0.1", ScanProfile(xml=True))
            self.assertEqual(res["rc"], 0); self.assertIn("parsed", res)
            self.assertEqual(res["parsed"]["hosts"][0]["address"], "127.0.0.1")
        finally:
            nw._run = orig

if __name__ == "__main__":
    unittest.main()
