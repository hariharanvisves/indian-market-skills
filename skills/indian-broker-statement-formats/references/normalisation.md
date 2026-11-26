# Number and date normalisation at the statement boundary

Purpose: the full checklist behind section 14 of [SKILL.md](../SKILL.md). Date-shift and
float traps are owned by
[indian-market-data-pitfalls](../../indian-market-data-pitfalls/SKILL.md).

- `parseFloat("1,999")` is `1`, silently. Strip digit-grouping commas and currency symbols
  in one `toNumber` helper and use it for every numeric read.
- Excel serial dates arrive as numbers (cell values stay `string | number | boolean | null`).
  Keep **one** serial converter in the codebase: two converters in one project disagreed by
  exactly one day on every date.
- Convert serials and date strings from parts, never via `toISOString()`; see
  [indian-market-data-pitfalls](../../indian-market-data-pitfalls/SKILL.md) item 1.
- Default ambiguous `dd/mm/yyyy` to day-first and say so.
- Use one shared number reader for Indian (`1,23,456.78`) and Western grouping, and one
  calendar-checked date parser. Convert day-first CSV dates to ISO before validation and
  reject impossible dates (`31/02`).
- Count rejected rows by reason, and flag a parse that covers under about 90% of the file's
  data rows (see §12 of SKILL.md).
- Validate order status against an allow-list, not a deny-list of bad states.
