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


## Do prices update when you click Refresh in Excel?

- **Yes**, if Excel points to a **running URL** (local server or hosted URL), clicking **Refresh** pulls fresh data.
- If you stop your local Python process, Excel cannot update.
- To avoid running Python on your machine, deploy the serverless version to Vercel and use that URL in Excel.

## Deploy on Vercel (no local Python needed)

This repo now includes Vercel serverless endpoints:

- `/api/prices` → JSON
- `/api/prices.csv` → CSV (best for Excel)
- `/api/healthz`

### Steps

1. Push this repo to GitHub.
2. Import repo in Vercel.
3. (Optional) Add env var `HAREM_SOURCE_URLS` (comma-separated URLs).
4. Deploy.
5. In Excel: **Data → From Web** and use:
   - `https://YOUR-VERCEL-DOMAIN/api/prices.csv`

Now Excel Refresh works without rerunning local scripts.

