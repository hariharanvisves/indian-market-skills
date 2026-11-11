---
name: indian-broker-statement-formats
description: Format facts and parse-safety rules for Indian broker and RTA statements — Zerodha Console tradebook and tax P&L, Groww stock and mutual-fund xlsx, CAMS xls/json, KFintech vs CAMS servicing split, CAS PDFs, INDmoney xls, AIS, ITD acknowledgement PDFs. Use when writing or debugging a statement importer or upload parser, when a broker .xls will not open or a parse returns suspiciously few rows, when SIP vs lumpsum labelling is wrong, or when imported capital gains are double-counted.
license: MIT
compatibility: Describes export formats as observed; vendors change layouts without notice, so detect by header signature and verify on a current file.
metadata:
  author: hariharanvisves
  version: "1.1"
  jurisdiction: India
  verified: "2026-11-11"
---

# Indian Broker Statement Formats

Each item is a defect class that yields plausible numbers. Date shifts, float
parsing and precision traps live in
[indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md) and are
not repeated; sections 12-14 only add the statement-specific angle. Scheme-name
matching is in [mf-scheme-matching](../mf-scheme-matching/SKILL.md).

## 1. Detect by content, never by extension or filename

**Rule.** Sniff magic bytes, then a header-row signature (all signature columns
present, first match wins, else `generic`).

| Bytes | Format |
|---|---|
| `504b0304` | OOXML (`.xlsx`, also `.zip`) |
| `d0cf11e0a1b11ae1` | OLE2/BIFF (legacy `.xls`) |
| `%PDF` | PDF |

**Why.** CAMS and INDmoney `.xls` files are OLE2, not OOXML. An xlsx reader
rejects them; a reader that falls through to "csv" decodes garbage into zero
rows.

**Tell.** An "xlsx" upload that fails the ZIP signature, or yields 0 rows
without error.

## 2. Header rows are scanned, not assumed

**Rule.** Scan the first ~25 rows; the most-populated row (>= 2 non-empty cells,
earliest wins ties) is the header.

**Why.** Real exports open with a title banner or a "Personal Details" block.
Assuming row 0 collapses the sheet into junk columns and the import becomes a
silent no-op.

**Tell.** A genuine broker file parsing to 0 rows looks identical to a
wrong-file upload. Surface zero-row parses to the user.

## 3. Pin columns the alias scan would resolve in file order

**Rule.** Alias scans resolve by file position, so a broker whose file carries
two plausible columns (an AMC column before the scheme column) needs its
columns pinned explicitly after the scan.

**Why.** CAMS-style files carry both an AMC name and a scheme name. Without a
pin, `name` binds to the AMC and every scheme of a fund house collapses into one
instrument.

**Tell.** Instrument count equals the number of AMCs, not schemes.

## 4. Zerodha Console: tax P&L is authoritative, summary sheets duplicate

**Rule.** Take capital gains from the **tax P&L** workbook (per-lot rows with
buy/sell dates). Skip the P&L summary/aggregate sheets, and any row with no buy
date whose quantity and consideration equal the per-lot sum.

**Why.** Ingesting summary sheets beside per-lot rows counts the same trades up
to three times: undated aggregate rows, plain and exchange-suffixed (`-E`)
symbols. The inflation equals the aggregate rows' sum, so it is plausible.

**Tell.** Gains rise when a second file is added; rows with null buy date.

## 5. Zerodha tradebook: stock vs ETF vs mutual fund

**Rule.** Resolve asset type in this order: broker implies MF, explicit field,
**ETF symbol check**, ISIN prefix `INF`, default stock.

**Why.** An ETF is a mutual fund in law and carries the same `INF` ISIN prefix,
but trades and is taxed like equity. If the ISIN branch runs first, every ETF is
classed as a mutual fund and gets the wrong tax treatment. Non-equity ETFs
(gold, silver, international) then need their own bucket; see
[indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md).

**Tell.** A `*BEES` or `*ETF` symbol with asset type `mutual_fund`. A new ETF
must be added to the symbol list; a suffix regex is only a backstop.

## 6. Groww: no SIP column, and names drift

**Rule.** Groww MF order history has no mode column; the transaction type is a
bare `PURCHASE`. Label such buys **"Not stated"**, never "Unclassified" and never
inferred.

**Why.** Inferring SIP from monthly cadence mislabels genuine repeated lumpsums,
and the dashboard then asserts a fact the data does not contain. "Not stated"
means absent at source; "Unclassified" implies a recoverable failure.

**Also.** The same statement exported twice can disagree on **scheme names**
(renamed funds) and on **dates by 1-3 days**, non-uniformly. That is
order-date vs allotment-date, a real semantic difference, not a timezone bug.
The allotment date moves the 12-month boundary, so decide the rule against the
RTA statement and apply it in the parser, not by picking a file.

**Tell.** Two exports of one FY with different row sets or names.

## 7. CAMS: JSON, zip, and the PRICE column

**Rule.** CAMS delivers `.xls` (OLE2) and JSON whose rows sit under
`dtTrxnResult`; some JSON deliveries are wrapped in a `.zip`. Unzip, then read;
the field names match the `.xls`. The NAV column is named `PRICE`, not `NAV`.

**Why.** A `scheme name + units` signature matches Groww's; without a `PRICE`
based signature CAMS falls to `generic` (section 1).

**Tell.** CAMS rows detected as the Groww parser, or a `.json`/`.zip` upload
rejected as unsupported when the shape is already handled.

## 8. CAMS covers only its serviced AMCs

**Rule.** CAMS exports contain only AMCs CAMS services; KFintech-serviced AMCs
appear in no CAMS file. The all-AMC view is the consolidated CAS PDF.
Reconcile across sources, do not expect any single one to be complete.

**Why.** Missing funds look like missing holdings or a smaller portfolio.
Their SIP/lumpsum mode is also unobtainable from the CAMS file: "Not stated"
is correct, not a gap to chase.

**Tell.** Holdings in the broker app that no CAMS row explains.

## 9. Transaction-type strings: one word flips the meaning

**Rule.** Map exact strings:

| String | Meaning |
|---|---|
| `Purchase (Continuous Offer)` | **Lumpsum** (scheme is open-ended) |
| `Systematic Purchase (Continuous Offer)`, `SIP Purchase`, `Purchase Systematic` | **SIP** |
| `Switch-In` / `Switch In`, `STP`, `NFO` | their own classes |

**Why.** "Continuous offer" describes the scheme, not the purchase. Collapsing
the two mislabels every SIP instalment as lumpsum or the reverse.

**Tell.** SIP count equals total purchases, or zero.

## 10. CAS PDF: compact lines, validate with the next-line balance

**Rule.** A CAS transaction often prints as one compact run (date, amount, NAV,
units concatenated) with the **unit balance on a following line**. Parse the
run, then require the balance line; accept the row only if the balance parses.
Scheme headers carry the ISIN: read it, do not infer it.

**Why.** A permissive regex also matches page furniture. The balance line is a
cheap structural check that rejects non-transaction lines.

**Tell.** Rows with no balance, or a running balance that does not reconcile.

## 11. Reject non-statement PDFs by outcome

**Rule.** A PDF that yields zero records is the detector (a clear 400), not a
separate signature regex that drifts out of sync. A destatementisation request
form or an 80C summary reading "no transactions found" must return zero rows
and say so.

**Why.** A signature regex drifts from the parser it guards; the parser's own
output cannot.

**Tell.** A "successful" import of a form that contains no trades.

## 12. Parse coverage: candidate rows vs emitted, as a warning

**Rule.** Count rows that look like records, divide emitted by candidates, warn
below a threshold (e.g. 0.5). A warning, not a throw: the denominator is a
heuristic that must never reject a good file. Attach the ratio as metadata,
not a field that changes the return type.

**Why.** A caller that only tests for an empty result accepts 3 records out of
~300 as success. A new layout silently loses almost everything.

**Tell.** Record count tiny against page count; the ratio is the detector.

## 13. Arithmetic identity: units x price = amount

**Rule.** For every transaction assert `|units * price - amount| <= tolerance`,
where the tolerance covers rounding at the source's precision.

**Why.** A column transposition (NAV in the units slot) still produces
well-formed numbers. A record count rising from 3 to 301 proves rows were read,
not read correctly; the identity proves they were mapped correctly.

**Tell.** The identity failing on all rows is a column map; on a few rows, a
stamp-duty or rounding rule.

## 14. Number and date normalisation at the statement boundary

- `parseFloat("1,999")` is `1`, silently. Strip digit-grouping commas and
  currency symbols in one `toNumber` helper and use it for every numeric read.
- Excel serial dates arrive as numbers (cell values stay `string | number |
  boolean | null`). Keep **one** serial converter in the codebase: two
  converters in one project disagreed by exactly one day on every date.
- Convert serials and date strings from parts, never via `toISOString()`; see
  [indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md) item 1.
- Default ambiguous `dd/mm/yyyy` to day-first and say so.

**Tell.** A uniform 1-day offset across a whole file.

## 15. Encrypted PDF: the error must name the primary failure

**Rule.** In a fallback chain (library, then an external tool), the final error
names the **primary** failure, with the original attached as `cause` and a
structured `code` for recoverable cases (password required). Key password-retry
logic on the code, never on the message wording.

**Why.** An optional fallback's failure ("install tool X") replaced the real
"no password given", and became the content of a bug report that blamed a
parser that was fine.

**Tell.** An install-this-package error when the package is demonstrably
installed. Never log or store password candidates.

## 16. INDmoney and other legacy `.xls`

**Rule.** INDmoney exports are legacy OLE2 `.xls`: use a reader that handles
BIFF, filter junk rows, and alias headers. Foreign-holding sheets use
different headings (peak value, closing balance, entity name) from domestic P&L.

**Why.** An OOXML-only reader fails; a CSV fallback misclassifies the foreign
asset sheet as a zero-value capital gain.

**Tell.** Zero-value gains from a foreign-assets sheet.

## 17. AIS is a cross-check, not the source of truth

**Rule.** Treat the Annual Information Statement as evidence of what third
parties reported, not of what you traded. Reconcile broker gains and dividends
against it and flag differences; do not overwrite broker figures with it.
Expect it to omit items the portal or your broker has, and to include categories
(card spend, securities purchases) that are not income.

**Why.** Auto-filling from AIS imports its omissions and its non-income lines;
a diff track that sums a non-income category reads as missing income.

**Tell.** A mismatch concentrated in an "other" bucket.

## 18. ITD acknowledgement PDFs wrap the real PDF

**Rule.** A filing acknowledgement downloaded from the income-tax portal can be a
**Java-serialized wrapper** (stream magic `aced0005`) around the actual PDF.
Find `%PDF` and the last `%%EOF` and slice that byte range, then parse it.

**Why.** A PDF parser given the whole blob reports a corrupt file, and the
filing evidence looks missing.

**Tell.** Bytes that do not start with `%PDF` but contain it later.

## 19. Never merge two sources by trusting either one's dedupe

**Rule.** Equity dedupe may hash price; MF cross-source dedupe must not. The
key and its tolerances are owned by
[mf-scheme-matching](../mf-scheme-matching/SKILL.md) section 8.

**Why.** Each source dedupes only against itself, and NAV differs between
sources, so a price-including key never sees the cross-source pair.

**Tell.** Units of a fund double after a second source is imported.

## Verifying an implementation

- Rename a CAMS `.xls` to `.xlsx`: it still routes to the CAMS parser (§1).
- A title banner above the header parses the same as a file without one (§2).
- Two schemes of one AMC yield two instruments, not one (§3).
- Adding the Zerodha P&L summary beside the tax P&L leaves gains unchanged (§4).
- An ETF with an `INF` ISIN is classed equity, not mutual fund (§5).
- A Groww `PURCHASE` is "Not stated"; each §9 string maps to its own class.
- Every parser reports the coverage ratio and asserts the amount identity
  (§12, §13).
- `"1,999"` reads as 1999; one Excel-serial converter exists (§14).
- A non-statement PDF yields zero rows and a clear error (§11); an encrypted PDF
  yields the password-required `code` (§15).

## Scope

Formats and column names change; re-verify on a current export. Statements
contain personal financial data: never commit real samples, and build test
fixtures from synthetic rows.
