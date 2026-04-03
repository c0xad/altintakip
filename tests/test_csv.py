import unittest

from server import _to_csv


class CsvTests(unittest.TestCase):
    def test_csv_contains_headers_and_rows(self):
        payload = {
            "fetched_at": "2026-04-03T00:00:00+00:00",
            "prices": [
                {"symbol": "HAS", "name": "Has Altın", "buy": 4100.12, "sell": 4115.34, "change": 0.45, "unit": "TRY"}
            ],
        }
        csv_data = _to_csv(payload)
        self.assertIn("fetched_at,symbol,name,buy,sell,change,unit", csv_data)
        self.assertIn("HAS", csv_data)


if __name__ == "__main__":
    unittest.main()
