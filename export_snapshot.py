#!/usr/bin/env python3
"""Create shareable snapshot files (JSON + CSV) from the live bridge feed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from server import _to_csv, get_prices


def main() -> None:
    parser = argparse.ArgumentParser(description="Export current prices to files.")
    parser.add_argument("--out-dir", default="exports", help="Output folder (default: exports)")
    parser.add_argument("--refresh", action="store_true", help="Force refresh from source")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = get_prices(force_refresh=args.refresh)

    json_path = out_dir / "prices.json"
    csv_path = out_dir / "prices.csv"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_path.write_text(_to_csv(payload), encoding="utf-8")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {csv_path}")


if __name__ == "__main__":
    main()
