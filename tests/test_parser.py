# tests/test_parser.py
import unittest
from ai_scanner.parser.nmap_xml_parser import parse_scan_xml

class TestParser(unittest.TestCase):
    def test_parse_ok(self):
        xml = """<?xml version="1.0"?><nmaprun>
          <host><status state="up"/><address addr="10.0.0.1"/><ports>
            <port protocol="tcp" portid="80"><state state="open"/><service name="http"/></port>
          </ports></host></nmaprun>"""
        doc = parse_scan_xml(xml)
        self.assertIsNone(doc.error); self.assertEqual(len(doc.hosts), 1); self.assertEqual(doc.hosts[0].ports[0].port, 80)

    def test_parse_bad_xml(self):
        doc = parse_scan_xml("<bad")
        self.assertIsNotNone(doc.error)

if __name__ == "__main__":
    unittest.main()
