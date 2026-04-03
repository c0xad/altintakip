#!/usr/bin/env python3
"""Lightweight gold price bridge for Excel.

- Serves a tiny website with Excel import instructions.
- Exposes JSON and CSV endpoints suitable for Power Query / WEBSERVICE.
- Tries multiple Harem Altın-style JSON endpoints and normalizes records.
"""

from __future__ import annotations

import csv
import io
import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Iterable, List, Tuple
from urllib.error import URLError
from urllib.request import Request, urlopen

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "15"))

DEFAULT_SOURCE_URLS = [
    "https://www.haremaltin.com/tmp/altin.json",
    "https://www.haremaltin.com/ajax/json",
]
SOURCE_URLS = [u.strip() for u in os.getenv("HAREM_SOURCE_URLS", ",".join(DEFAULT_SOURCE_URLS)).split(",") if u.strip()]

_cache_lock = threading.Lock()
_cache: Dict[str, Any] = {
    "ts": 0.0,
    "payload": None,
    "error": None,
}


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace(".", "").replace(",", ".") if "," in str(value) else str(value).strip()
    try:
        return float(s)
    except ValueError:
        return None


def _normalize_records(raw: Any) -> List[Dict[str, Any]]:
    """Normalize known gold-price JSON formats to a common list schema."""
    rows: List[Dict[str, Any]] = []

    if isinstance(raw, dict):
        iterable: Iterable[Tuple[str, Any]] = raw.items()
    elif isinstance(raw, list):
        iterable = ((str(i), item) for i, item in enumerate(raw))
    else:
        return rows

    for key, item in iterable:
        if not isinstance(item, dict):
            continue

        name = item.get("adi") or item.get("name") or item.get("symbol") or key
        buy = _to_float(item.get("alis") or item.get("buy") or item.get("bid"))
        sell = _to_float(item.get("satis") or item.get("sell") or item.get("ask"))
        change = _to_float(item.get("degisim") or item.get("change"))
        unit = item.get("tur") or item.get("unit") or "TRY"

        if buy is None and sell is None:
            continue

        rows.append(
            {
                "symbol": str(key),
                "name": str(name),
                "buy": buy,
                "sell": sell,
                "change": change,
                "unit": str(unit),
            }
        )

    return rows


def _fetch_source() -> Dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Excel Gold Bridge)",
        "Accept": "application/json,text/plain,*/*",
    }

    last_error = "No data source configured"

    for source_url in SOURCE_URLS:
        req = Request(source_url, headers=headers)
        try:
            with urlopen(req, timeout=10) as response:
                body = response.read().decode("utf-8", errors="replace")
        except URLError as exc:
            last_error = f"{source_url}: {exc}"
            continue

        try:
            raw = json.loads(body)
        except json.JSONDecodeError as exc:
            last_error = f"{source_url}: invalid JSON ({exc})"
            continue

        rows = _normalize_records(raw)
        if not rows:
            last_error = f"{source_url}: JSON parsed but no gold rows found"
            continue

        now = datetime.now(timezone.utc).isoformat()
        return {
            "fetched_at": now,
            "source_url": source_url,
            "count": len(rows),
            "prices": rows,
        }

    raise RuntimeError(last_error)


def get_prices(force_refresh: bool = False) -> Dict[str, Any]:
    now = time.time()
    with _cache_lock:
        age = now - _cache["ts"]
        if not force_refresh and _cache["payload"] is not None and age < CACHE_TTL_SECONDS:
            return _cache["payload"]

    try:
        payload = _fetch_source()
        with _cache_lock:
            _cache.update({"ts": now, "payload": payload, "error": None})
        return payload
    except Exception as exc:  # pragma: no cover
        with _cache_lock:
            _cache["error"] = str(exc)
            if _cache["payload"] is not None:
                return {
                    **_cache["payload"],
                    "warning": f"Using cached data due to upstream error: {exc}",
                }
        raise


def _to_csv(payload: Dict[str, Any]) -> str:
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["fetched_at", "symbol", "name", "buy", "sell", "change", "unit"])
    for row in payload.get("prices", []):
        writer.writerow(
            [
                payload.get("fetched_at", ""),
                row.get("symbol", ""),
                row.get("name", ""),
                row.get("buy", ""),
                row.get("sell", ""),
                row.get("change", ""),
                row.get("unit", ""),
            ]
        )
    return out.getvalue()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, content_type: str, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/api/prices", "/api/prices?refresh=1"):
            force = self.path.endswith("refresh=1")
            try:
                payload = get_prices(force_refresh=force)
            except Exception as exc:
                self._send(502, "application/json", json.dumps({"error": str(exc)}))
                return
            self._send(200, "application/json", json.dumps(payload, ensure_ascii=False, indent=2))
            return

        if self.path == "/api/prices.csv":
            try:
                payload = get_prices()
            except Exception as exc:
                self._send(502, "text/plain", f"error,{exc}\n")
                return
            self._send(200, "text/csv", _to_csv(payload))
            return

        if self.path == "/healthz":
            self._send(200, "application/json", '{"ok":true}')
            return

        if self.path == "/":
            self._send(
                200,
                "text/html",
                f"""<!doctype html>
<html>
<head><meta charset='utf-8'><title>Gold Excel Bridge</title></head>
<body style="font-family:Arial,sans-serif;max-width:760px;margin:2rem auto;line-height:1.5">
  <h1>Gold Price Excel Bridge</h1>
  <p>This service normalizes live gold prices to JSON/CSV so Excel can refresh automatically.</p>
  <h2>Endpoints</h2>
  <ul>
    <li><code>/api/prices</code> (JSON)</li>
    <li><code>/api/prices.csv</code> (CSV - easiest for Excel)</li>
  </ul>
  <h2>Excel (Power Query) quick setup</h2>
  <ol>
    <li>Open Excel → <b>Data</b> → <b>From Web</b>.</li>
    <li>Enter: <code>http://YOUR_SERVER:{PORT}/api/prices.csv</code></li>
    <li>Load table and enable refresh every 1 minute in Query Properties.</li>
  </ol>
  <p><small>Current source candidates: {', '.join(SOURCE_URLS)}</small></p>
</body>
</html>""",
            )
            return

        self._send(404, "text/plain", "Not found")


def run() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Gold bridge listening at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
