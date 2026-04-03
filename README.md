# Gold Excel Bridge (Harem-style)

This project creates a tiny website/API so you can import live-ish gold prices into Excel and refresh automatically.

## Run

```bash
python server.py
```

Server starts at `http://localhost:8080`.

## Excel integration

Use **Data → From Web** with:

- `http://localhost:8080/api/prices.csv` (recommended)
- or `http://localhost:8080/api/prices` (JSON)

Then set query refresh interval from Query Properties.


## Export files to share (JSON/CSV)

If you want generated files to send/import manually:

```bash
python export_snapshot.py --out-dir exports --refresh
```

This writes:

- `exports/prices.json`
- `exports/prices.csv`

## Notes

- The app tries Harem-style JSON endpoints and normalizes fields (`alis/satis`, `buy/sell`, etc.).
- Configure sources with `HAREM_SOURCE_URLS` (comma-separated).
- If upstream blocks requests, deploy this service on a server/IP that can access your source.

## Test

```bash
python -m unittest discover -s tests
```
