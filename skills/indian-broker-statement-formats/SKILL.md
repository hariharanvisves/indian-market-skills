---
name: indian-broker-statement-formats
description: Format facts and parse-safety rules for Indian broker and RTA statements — Zerodha Console tradebook and tax P&L, Groww stock and mutual-fund xlsx, CAMS xls/json/zip, KFintech vs CAMS servicing split, CAS PDFs (including encrypted ones), INDmoney xls, AIS, ITD acknowledgement PDFs. Use when writing or debugging a statement importer, upload parser or CAS/PDF regex, even if the user only says "import my holdings"; when openpyxl or xlrd says a .xls is not a zip file, a parse returns zero or suspiciously few rows, capital gains look doubled or tripled, SIP vs lumpsum labelling is wrong, an ETF shows as a mutual fund, or AIS and broker figures disagree (reconcile; never overwrite with AIS). Scheme-name matching belongs to mf-scheme-matching.
license: MIT
compatibility: Describes export formats as observed; vendors change layouts without notice, so detect by header signature and verify on a current file.
metadata:
  author: hariharanvisves
  version: "1.2"
  jurisdiction: India
  verified: "2026-11-11"
---

# Indian Broker Statement Formats

Each item is a defect class that yields plausible numbers: an importer that reads the wrong
sheet or binds the wrong column still returns rows. Date shifts, float parsing and precision
traps live in [indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md);
sections 12-14 add only the statement-specific angle. Scheme-name matching is in
[mf-scheme-matching](../mf-scheme-matching/SKILL.md).

## Core rules

1. Detect the format from magic bytes, then a header-row signature, never from the
   extension or filename; CAMS and INDmoney `.xls` are OLE2, not OOXML (§1, §2).
2. A file no parser matches is an error the user can act on, never a zero-row success
   (§1, §4, §11).
3. Zerodha capital gains come only from the per-lot tax P&L; summary sheets duplicate it (§4).
4. Resolve ETFs by symbol before the ISIN-prefix rule: ETFs carry `INF` too (§5).
5. Groww `PURCHASE` has no mode: label it "Not stated", never infer SIP from cadence (§6).
6. Map transaction-type strings exactly: `Purchase (Continuous Offer)` is lumpsum, not SIP (§9).
7. A CAS row counts only if its next-line balance parses, and every scheme block must
   reconcile to its Closing Unit Balance (§10).
8. Report coverage (emitted over candidate rows) and assert `units x price = amount` on
   every transaction (§12, §13).
9. AIS is a cross-check: reconcile and flag, never overwrite broker figures (§17).
10. Each source dedupes only against itself; the cross-source key is price-free (§19).

Read [references/vendor-formats.md](references/vendor-formats.md) when parsing Groww, CAMS
JSON, CAS text, encrypted PDFs, INDmoney or ITD acknowledgements.

## 1. Detect by content, never by extension or filename

**Rule.** Sniff magic bytes, then a header-row signature (all signature columns present,
first match wins, else `generic`). List the more specific signature first.

| Bytes | Format |
|---|---|
| `504b0304` | OOXML (`.xlsx`, also `.zip`) |
| `d0cf11e0a1b11ae1` | OLE2/BIFF (legacy `.xls`) |
| `%PDF` | PDF |

**Why.** CAMS and INDmoney `.xls` files are OLE2, not OOXML. An xlsx reader rejects them,
so do not ask the user to resave: route to a BIFF-capable reader. A reader that falls
through to "csv" decodes garbage into zero rows.

**Detector.** An "xlsx" upload that fails the ZIP signature, or yields 0 rows without error.

```python
MAGIC = {bytes.fromhex("504b0304"): "ooxml", bytes.fromhex("d0cf11e0a1b11ae1"): "ole2", b"%PDF": "pdf"}
# Placeholder columns; copy the real signature from a current export.
SIGNATURES = [("cams", {"scheme name", "units", "price"}),      # superset of Groww's: first
              ("groww_mf", {"scheme name", "units"})]

def detect(head: bytes, rows: list[list]) -> str:
    kind = next((k for m, k in MAGIC.items() if head.startswith(m)), None)
    if kind is None:
        raise UnsupportedFile("unknown file type")             # refuse, do not guess csv
    if kind == "pdf":
        return "pdf"                                           # section 11 decides by outcome
    header = max(rows[:25], key=lambda r: sum(bool(c) for c in r), default=[])  # section 2
    cols = {str(c).strip().lower() for c in header if c}
    if len(cols) < 2:
        raise UnsupportedFile("no header row in first 25 rows")
    return next((n for n, sig in SIGNATURES if sig <= cols), "generic")

# After parsing: generic must not turn "matched nothing" into "imported nothing".
if not records:
    raise UnsupportedFile(f"{fmt}: 0 rows parsed")
```

## 2. Header rows are scanned, not assumed

**Rule.** Scan the first ~25 rows; the most-populated row (>= 2 non-empty cells, earliest
wins ties) is the header.

**Why.** Real exports open with a title banner or a "Personal Details" block. Assuming
row 0 collapses the sheet into junk columns and the import becomes a silent no-op.
**Detector.** A genuine file parsing to 0 rows looks identical to a wrong-file upload;
surface zero-row parses to the user.

## 3. Pin columns the alias scan would resolve in file order

**Rule.** Alias scans resolve by file position, so a broker whose file carries two
plausible columns (an AMC column before the scheme column) needs its columns pinned
explicitly after the scan.

**Why.** CAMS-style files carry an AMC name and a scheme name; unpinned, `name` binds to
the AMC and every scheme of a fund house collapses into one instrument. **Detector.**
Instrument count equals the number of AMCs, not schemes.

## 4. Zerodha Console: tax P&L is authoritative, summary sheets duplicate

**Rule.** Take capital gains from the **tax P&L** workbook (per-lot rows with buy/sell
dates). Skip the P&L summary/aggregate sheets, and any row with no buy date whose quantity
and consideration equal the per-lot sum. Claim a file as Zerodha only when it carries the
tax P&L layout; an aggregate P&L summary must fall to "no parser matched", not parse to
zero rows.

**Why.** Ingesting summary sheets beside per-lot rows counts the same trades up to three
times: undated aggregate rows, plain and exchange-suffixed (`-E`) symbols. The inflation
equals the aggregate rows' sum, so it is plausible. A confident zero-row parse reads as a
successful empty import; no match is an error the user can act on.

**Detector.** Gains rise when a second file is added; rows with null buy date; a Zerodha
detection that yields 0 trades.

## 5. Zerodha tradebook: stock vs ETF vs mutual fund

**Rule.** Resolve asset type in this order: broker implies MF, explicit field, **ETF symbol
check**, ISIN prefix `INF`, default stock.

**Why.** An ETF is a mutual fund in law and carries the same `INF` ISIN prefix, but trades
and is taxed like equity. If the ISIN branch runs first, every ETF is classed as a mutual
fund and gets the wrong tax treatment. Non-equity ETFs (gold, silver, international) then
need their own bucket; see [indian-capital-gains-tax](../indian-capital-gains-tax/SKILL.md).

```python
ETF_SYMBOLS = {"NIFTYBEES", "..."}      # grown by hand; a gold ETF may lack BEES/ETF in its name
ETF_SUFFIX = re.compile(r"(BEES|ETF)$")  # backstop only

def asset_type(broker, explicit, symbol, isin):
    if broker == "mutual_fund_platform":
        return "mutual_fund"
    if explicit == "stock" and symbol in ETF_SYMBOLS:
        raise Conflict(symbol)                     # reject, do not silently override
    if explicit:
        return explicit
    if symbol in ETF_SYMBOLS or ETF_SUFFIX.search(symbol):
        return "etf"                               # before the INF test
    return "mutual_fund" if isin.startswith("INF") else "stock"
```

`NIFTYBEES` with an `INF...` ISIN returns `etf`; with the two lines swapped it returns
`mutual_fund`. Matching by scheme name belongs to
[mf-scheme-matching](../mf-scheme-matching/SKILL.md).

**Detector.** A `*BEES` or `*ETF` symbol with asset type `mutual_fund`. A new ETF must be
added to the symbol list; a suffix regex is only a backstop.

## 6. Groww: no SIP column, and names drift

**Rule.** Groww MF order history has no mode column; the transaction type is a bare
`PURCHASE`. Label such buys **"Not stated"**, never "Unclassified" and never inferred.
Reject a realised-gains report uploaded as a ledger by header signature.

**Why.** Inferring SIP from monthly cadence mislabels genuine repeated lumpsums, and the
dashboard then asserts a fact the data does not contain. "Not stated" means absent at
source; "Unclassified" implies a recoverable failure.

**Detector.** Two exports of one FY with different row sets or names. Export drift
(names, 1-3 day date shifts) and reversal twins: see the Groww section of
[references/vendor-formats.md](references/vendor-formats.md).

## 7. CAMS: JSON, zip, and the PRICE column

**Rule.** CAMS delivers `.xls` (OLE2) and JSON whose rows sit under `dtTrxnResult`,
sometimes inside a `.zip`; the NAV column is named `PRICE`, not `NAV`. Detect CAMS by a
`PRICE`-based signature, or it falls to `generic` (section 1).

**Detector.** CAMS rows detected as the Groww parser, or a `.json`/`.zip` upload rejected
as unsupported when the shape is already handled. See the CAMS section of
[references/vendor-formats.md](references/vendor-formats.md).

## 8. CAMS covers only its serviced AMCs

**Rule.** CAMS exports contain only AMCs CAMS services; KFintech-serviced AMCs appear in no
CAMS file. The all-AMC view is the consolidated CAS PDF. Reconcile across sources, do not
expect any single one to be complete.

**Why.** Missing funds look like missing holdings. Their SIP/lumpsum mode is also
unobtainable from the CAMS file: "Not stated" is correct, not a gap to chase.
**Detector.** Holdings in the broker app that no CAMS row explains.

## 9. Transaction-type strings: one word flips the meaning

**Rule.** Map exact strings:

| String | Meaning |
|---|---|
| `Purchase (Continuous Offer)` | **Lumpsum** (scheme is open-ended) |
| `Systematic Purchase (Continuous Offer)`, `SIP Purchase`, `Purchase Systematic` | **SIP** |
| `Switch-In` / `Switch In`, `STP`, `NFO` | their own classes |

**Why.** "Continuous offer" describes the scheme, not the purchase. Collapsing the two
mislabels every SIP instalment as lumpsum or the reverse.

**Detector.** SIP count equals total purchases, or zero.

## 10. CAS PDF: compact lines, validate with the next-line balance

**Rule.** A CAS transaction often prints as one compact run (date, amount, NAV, units
concatenated) with the **unit balance on a following line**. Parse the run, then require
the balance line; accept the row only if the balance parses. Scheme headers carry the ISIN:
read it, do not infer it. Reconcile every scheme block to its printed Closing Unit Balance.

**Why.** A permissive regex also matches page furniture, so a regex that picks up page
headers as transactions needs the balance check, not a tighter pattern.

**Detector.** Rows with no balance, or a running balance that does not reconcile. Folio
and stamp-duty line traps: see the CAS section of
[references/vendor-formats.md](references/vendor-formats.md).

## 11. Reject non-statement PDFs by outcome

**Rule.** A PDF that yields zero records is the detector (a clear 400), not a separate
signature regex that drifts out of sync. A destatementisation request form or an 80C
summary reading "no transactions found" must return zero rows and say so.

**Why.** A signature regex drifts from the parser it guards; the parser's own output
cannot. **Detector.** A "successful" import of a form that contains no trades.

## 12. Parse coverage: candidate rows vs emitted, as a warning

**Rule.** Count rows that look like records, divide emitted by candidates, warn below a
threshold (e.g. 0.5). A warning, not a throw: the denominator is a heuristic that must
never reject a good file. Attach the ratio as metadata, not a field that changes the
return type.

**Why.** A caller that only tests for an empty result accepts 3 records out of ~300 as
success. A new layout silently loses almost everything.

**Detector.** Record count tiny against page count; the ratio is the detector.

## 13. Arithmetic identity: units x price = amount

**Rule.** For every transaction assert `|units * price - amount| <= tolerance`, where the
tolerance covers rounding at the source's precision.

**Why.** A column transposition (NAV in the units slot) still produces well-formed numbers.
A record count rising from 3 to 301 proves rows were read, not read correctly; the identity
proves they were mapped correctly. **Detector.** Failing on all rows is a column map; on a
few rows, a stamp-duty or rounding rule.

## 14. Number and date normalisation at the statement boundary

**Rule.** Read every number and date through one shared helper each.
- `parseFloat("1,999")` is `1`, silently: strip digit-grouping commas and currency symbols
  in one `toNumber`, and accept Indian (`1,23,456.78`) and Western grouping.
- Keep **one** Excel-serial converter: two converters in one project disagreed by exactly
  one day on every date. Never convert via `toISOString()`; see
  [indian-market-data-pitfalls](../indian-market-data-pitfalls/SKILL.md) item 1.
- Default ambiguous `dd/mm/yyyy` to day-first, say so, and reject impossible dates.
- Count rejected rows by reason, and flag a parse that covers under about 90% of the
  file's data rows (see §12).

**Detector.** A uniform 1-day offset across a whole file. Full checklist (allow-listed
order status, ISO conversion before validation):
[references/normalisation.md](references/normalisation.md).

## 15. Encrypted PDF: the error must name the primary failure

**Rule.** In a fallback chain (library, then an external tool), the final error names the
**primary** failure, with the original attached as `cause` and a structured `code` for
recoverable cases (password required). Key password-retry logic on the code, never on the
message wording. Never log or store password candidates.

**Detector.** An install-this-package error when the package is demonstrably installed.
Background: [references/vendor-formats.md](references/vendor-formats.md).

## 16. INDmoney and other legacy `.xls`

**Rule.** INDmoney exports are legacy OLE2 `.xls`: use a reader that handles BIFF, filter
junk rows, and alias headers. Foreign-holding sheets use different headings (peak value,
closing balance, entity name) from domestic P&L; a CSV fallback misclassifies them as
zero-value capital gains.

**Detector.** Zero-value gains from a foreign-assets sheet.

## 17. AIS is a cross-check, not the source of truth

**Rule.** The Annual Information Statement **omits items** your broker has, and it
**includes non-income categories** (card spend, securities purchases). Treat it as evidence
of what third parties reported, not of what you traded. Reconcile broker gains and
dividends against it and flag differences; do not overwrite broker figures with it.

**Why.** Auto-filling from AIS imports its omissions and its non-income lines; a diff that
sums a non-income category reads as missing income. **Detector.** A mismatch concentrated
in an "other" bucket.

## 18. ITD acknowledgement PDFs wrap the real PDF

**Rule.** A filing acknowledgement downloaded from the income-tax portal can be a
**Java-serialized wrapper** (stream magic `aced0005`) around the actual PDF. Find `%PDF`
and the last `%%EOF`, slice that byte range, then parse it.

**Detector.** Bytes that do not start with `%PDF` but contain it later. A PDF parser given
the whole blob reports a corrupt file; see
[references/vendor-formats.md](references/vendor-formats.md).

## 19. Never merge two sources by trusting either one's dedupe

**Rule.** Equity dedupe may hash price; MF cross-source dedupe must not. The key and its
tolerances are owned by [mf-scheme-matching](../mf-scheme-matching/SKILL.md) section 8.

**Why.** Each source dedupes only against itself, and NAV differs between sources, so a
price-including key never sees the cross-source pair. **Detector.** Units of a fund double
after a second source is imported.

## Verifying an implementation

- Rename a CAMS `.xls` to `.xlsx`: it still routes to the CAMS parser (§1).
- A title banner above the header parses the same as a file without one (§2).
- Two schemes of one AMC yield two instruments, not one (§3).
- Adding the Zerodha P&L summary beside the tax P&L leaves gains unchanged (§4).
- An ETF with an `INF` ISIN is classed equity, not mutual fund (§5).
- A Groww `PURCHASE` is "Not stated"; each §9 string maps to its own class.
- Every parser reports the coverage ratio and asserts the amount identity (§12, §13).
- `"1,999"` reads as 1999; one Excel-serial converter exists (§14).
- A non-statement PDF yields zero rows and a clear error (§11); an encrypted PDF yields the
  password-required `code` (§15).

## Scope

Formats and column names change; re-verify on a current export. Statements contain
personal financial data: never commit real samples, and build test fixtures from synthetic
rows. Engineering guidance, not tax advice.
