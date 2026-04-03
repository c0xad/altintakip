import unittest

from server import _normalize_records


class ParserTests(unittest.TestCase):
    def test_normalizes_harem_like_payload(self):
        raw = {
            "HAS": {"adi": "Has Altın", "alis": "4100,12", "satis": "4115,34", "degisim": "0,45"},
            "USDTRY": {"alis": "39,01", "satis": "39,03"},
        }

        rows = _normalize_records(raw)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["symbol"], "HAS")
        self.assertAlmostEqual(rows[0]["buy"], 4100.12)
        self.assertAlmostEqual(rows[0]["sell"], 4115.34)


if __name__ == "__main__":
    unittest.main()
