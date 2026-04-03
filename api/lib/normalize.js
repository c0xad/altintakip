function toFloat(value) {
  if (value === null || value === undefined) return null;
  if (typeof value === 'number') return Number.isFinite(value) ? value : null;
  const raw = String(value).trim();
  if (!raw) return null;
  const normalized = raw.includes(',') ? raw.replace(/\./g, '').replace(',', '.') : raw;
  const n = Number.parseFloat(normalized);
  return Number.isFinite(n) ? n : null;
}

function normalizeRecords(raw) {
  const rows = [];
  if (!raw || typeof raw !== 'object') return rows;

  const entries = Array.isArray(raw)
    ? raw.map((v, i) => [String(i), v])
    : Object.entries(raw);

  for (const [key, item] of entries) {
    if (!item || typeof item !== 'object') continue;

    const name = item.adi || item.name || item.symbol || key;
    const buy = toFloat(item.alis ?? item.buy ?? item.bid);
    const sell = toFloat(item.satis ?? item.sell ?? item.ask);
    const change = toFloat(item.degisim ?? item.change);
    const unit = item.tur || item.unit || 'TRY';

    if (buy === null && sell === null) continue;

    rows.push({ symbol: String(key), name: String(name), buy, sell, change, unit: String(unit) });
  }

  return rows;
}

function toCsv(payload) {
  const header = 'fetched_at,symbol,name,buy,sell,change,unit';
  const rows = (payload.prices || []).map((r) =>
    [
      payload.fetched_at || '',
      r.symbol || '',
      r.name || '',
      r.buy ?? '',
      r.sell ?? '',
      r.change ?? '',
      r.unit || '',
    ].join(',')
  );
  return [header, ...rows].join('\n') + '\n';
}

module.exports = { toFloat, normalizeRecords, toCsv };
