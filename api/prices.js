const { normalizeRecords, toCsv } = require('./lib/normalize');

const DEFAULT_SOURCES = [
  'https://www.haremaltin.com/tmp/altin.json',
  'https://www.haremaltin.com/ajax/json',
];

async function fetchFromSources(sources) {
  let lastError = 'No source configured';

  for (const source of sources) {
    try {
      const response = await fetch(source, {
        headers: {
          'user-agent': 'Excel-Gold-Bridge/1.0',
          accept: 'application/json,text/plain,*/*',
        },
      });

      if (!response.ok) {
        lastError = `${source}: HTTP ${response.status}`;
        continue;
      }

      const raw = await response.json();
      const prices = normalizeRecords(raw);
      if (!prices.length) {
        lastError = `${source}: parsed but no rows`;
        continue;
      }

      return {
        fetched_at: new Date().toISOString(),
        source_url: source,
        count: prices.length,
        prices,
      };
    } catch (err) {
      lastError = `${source}: ${err.message}`;
    }
  }

  throw new Error(lastError);
}

module.exports = async (req, res) => {
  try {
    const sources = (process.env.HAREM_SOURCE_URLS || DEFAULT_SOURCES.join(','))
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean);

    const payload = await fetchFromSources(sources);
    const asCsv = req.query.format === 'csv' || req.url.endsWith('/prices.csv');

    res.setHeader('Cache-Control', 's-maxage=20, stale-while-revalidate=40');

    if (asCsv) {
      res.setHeader('Content-Type', 'text/csv; charset=utf-8');
      res.status(200).send(toCsv(payload));
      return;
    }

    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.status(200).json(payload);
  } catch (error) {
    res.status(502).json({ error: error.message });
  }
};
