# Vendor format detail: Groww, CAMS, CAS PDF, encrypted PDF, INDmoney, ITD acknowledgement

Purpose: per-vendor layout traps behind sections 6, 7, 10, 15, 16 and 18 of
[SKILL.md](../SKILL.md). Layouts are as observed and change without notice; verify on a
current export.

Contents: [Groww](#groww-mf-exports-section-6) · [CAMS JSON and zip](#cams-json-and-zip-section-7) ·
[CAS PDF](#cas-pdf-text-layout-section-10) · [Encrypted PDF](#encrypted-pdf-error-chain-section-15) ·
[INDmoney](#indmoney-and-legacy-xls-section-16) · [ITD acknowledgement](#itd-acknowledgement-pdf-section-18)

## Groww MF exports (section 6)

The same statement exported twice can disagree on **scheme names** (renamed funds) and on
**dates by 1-3 days**, non-uniformly. That is order-date vs allotment-date, a real semantic
difference, not a timezone bug. The allotment date moves the 12-month boundary, so decide
the rule against the RTA statement and apply it in the parser, not by picking a file.

**Reversal twins (observed).** Groww MF exports can carry reversed entries:
- a same-scheme, same-day buy and sell pair with identical units;
- a capital-gains lot whose purchase date is after its redeem date;
- one redemption listed on consecutive days with identical units, NAV and amount.

Skip these with a warning, and diff against the store on `(date, type, units)` before
inserting.

**Wrong report uploaded.** A realised-gains or capital-gains report uploaded where a
transaction ledger is expected must be rejected by header signature. A generic alias scan
otherwise binds `Scheme Name` and `Purchase Date` and turns every row into a BUY.

**Tell.** Two exports of one FY with different row sets or names.

## CAMS JSON and zip (section 7)

CAMS delivers `.xls` (OLE2) and JSON whose rows sit under `dtTrxnResult`; some JSON
deliveries are wrapped in a `.zip`. Unzip, then read; the field names match the `.xls`. The
NAV column is named `PRICE`, not `NAV`.

A `scheme name + units` signature matches Groww's; without a `PRICE`-based signature CAMS
falls to `generic` (section 1 of SKILL.md). Test the CAMS signature before the Groww one.

**Tell.** CAMS rows detected as the Groww parser, or a `.json`/`.zip` upload rejected as
unsupported when the shape is already handled.

## CAS PDF text layout (section 10)

A CAS transaction often prints as one compact run (date, amount, NAV, units concatenated)
with the **unit balance on a following line**. A permissive regex also matches page
furniture; the balance line is a cheap structural check that rejects non-transaction lines.

Observed layout traps in CAS text:
- The `Folio No` line prints **before** the scheme header; clearing state at the header
  loses the folio.
- An inline stamp-duty line (`<date> *** Stamp Duty *** <amt>`) belongs to the preceding
  purchase, not a row of its own.
- Handle bare instalment rows, split SWP rows, additional-allotment rows (an undated line
  with the balance plus a dated line with units) and ISINs wrapped across lines.
- Reconcile every scheme block to its printed Closing Unit Balance and surface mismatches;
  a layout change can silently drop transactions (seen after a 2025 layout change).

**Tell.** Rows with no balance, or a running balance that does not reconcile.

## Encrypted PDF error chain (section 15)

In a fallback chain (library, then an external tool), the final error names the **primary**
failure, with the original attached as `cause` and a structured `code` for recoverable cases
(password required). Key password-retry logic on the code, never on the message wording. An
optional fallback's failure ("install tool X") once replaced the real "no password given"
and became a bug report that blamed a parser that was fine.

**Tell.** An install-this-package error when the package is demonstrably installed. Never
log or store password candidates.

## INDmoney and legacy xls (section 16)

INDmoney exports are legacy OLE2 `.xls`: use a reader that handles BIFF, filter junk rows,
and alias headers. Foreign-holding sheets use different headings (peak value, closing
balance, entity name) from domestic P&L. An OOXML-only reader fails; a CSV fallback
misclassifies the foreign asset sheet as a zero-value capital gain.

**Tell.** Zero-value gains from a foreign-assets sheet.

## ITD acknowledgement PDF (section 18)

A filing acknowledgement downloaded from the income-tax portal can be a **Java-serialized
wrapper** (stream magic `aced0005`) around the actual PDF. Find `%PDF` and the last `%%EOF`
and slice that byte range, then parse it. A PDF parser given the whole blob reports a
corrupt file, and the filing evidence looks missing.

**Tell.** Bytes that do not start with `%PDF` but contain it later.
