const test = require('node:test');
const assert = require('node:assert/strict');
const { toFloat, normalizeRecords, toCsv } = require('../api/lib/normalize');

test('toFloat parses Turkish decimal format', () => {
  assert.equal(toFloat('4.100,12'), 4100.12);
});

test('normalizeRecords maps harem-like fields', () => {
  const rows = normalizeRecords({
    HAS: { adi: 'Has Altın', alis: '4100,12', satis: '4115,34', degisim: '0,45' },
  });

  assert.equal(rows.length, 1);
  assert.equal(rows[0].symbol, 'HAS');
  assert.equal(rows[0].buy, 4100.12);
  assert.equal(rows[0].sell, 4115.34);
});

test('toCsv emits header and value rows', () => {
  const csv = toCsv({ fetched_at: '2026-04-03T00:00:00Z', prices: [{ symbol: 'HAS', name: 'Has', buy: 1, sell: 2, change: 0, unit: 'TRY' }] });
  assert.match(csv, /fetched_at,symbol,name,buy,sell,change,unit/);
  assert.match(csv, /HAS/);
});
