# Portal quirks and measured defects

Purpose: real-portal behaviours and defects that support SKILL.md sections 3, 7 and 9. Read when reconciling Schedule CG against the portal's quarterly table, debugging a TDS double count, or emitting JSON.

## Contents

- [Portal reconciliation identities](#portal-reconciliation-identities)
- [TDS and capital-gain row duplicates](#tds-and-capital-gain-row-duplicates)
- [JSON emit quirks](#json-emit-quirks)

## Portal reconciliation identities

Continuing the list in SKILL.md section 3:

8. Portal CG quarterly-accrual table row totals equal the matching BFLA items
   (per project notes from a real portal filing): the long-term special-rate row
   equals the BFLA long-term item and **includes §112A gains covered by the
   exemption**, not only taxable gain. Negative quarterly cells are rejected, so
   fold a negative quarter into an adjacent one; only the sum is validated.
9. Foreign dividend appears in OS (added on top of the portal prefill, which
   knows nothing of foreign brokers) and the **same rupee amount** in FSI.

Measured defect: brought-forward losses were reported twice (CFL and BFLA) once
BFLA landed. Add the identity test in the same change as any new schedule.

## TDS and capital-gain row duplicates

Measured defect: a real 26AS (TAN present) and the stub auto-created from an AIS
upload (no TAN) held the same salary credit; concatenation doubled the TDS and
turned a small genuine demand into a large false refund. Mirror defect: salary TDS
present only in AIS and excluded from the AIS side of a TDS reconciliation shows a
false mismatch.

Similarly for capital-gain rows: broker P&L summary sheets and per-lot sheets
exported together count the same trades up to three times. A natural key that
includes sale date and amounts never matches an undated aggregate row against its
dated per-lot rows, so the duplicate check reports zero. Skip aggregate rows whose
quantity and consideration equal the per-lot sum.

## JSON emit quirks

- Real defect: a missing divide at one emit point produced a 100x capital-gain
  figure; builder-level tests pinned the builder's own scale and could not see it.
- Portal quirks (per project notes): prefill reads the live AIS at filing time and
  supersedes an earlier AIS PDF (including interest on a prior-year refund); if
  prefill exceeds your estimate, trust it. Filing with tax payable unpaid yields an
  intimation demand. Schedule 112A has a consolidated two-total mode for post-2018
  acquisitions and scrip rows for pre-2018 holdings. CYLA/BFLA/CFL are portal views.
