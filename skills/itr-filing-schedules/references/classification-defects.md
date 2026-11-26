# Classification and rebate defects seen in practice

Purpose: defects found while wiring capital-gains classification, residency and rebate into the schedule writer, moved out of SKILL.md section 4. Read when the writer needs the capital-gains classifier, a rebate or a surcharge cap.

- Fail-closed classification, the SGB branch (exemption conditions, checked
  before any `gold|silver` name regex), zero §112A exemption for gold, foreign
  shares and non-equity ETFs, and the grandfathering formula are owned by
  the capital-gains skill. Keep **one** implementation of each, and have the
  schedule writer read it.
- Holding-period cutoffs differ by asset class (listed equity vs gold/foreign vs
  debt funds by purchase date), and all are counted in **calendar months**,
  not days. The capital-gains skill states the listed-equity boundary and the
  debt-fund purchase-date rule; verify the threshold per other class. The same cutoff is often decided in a realized path
  and an unrealized path; change both or neither. A fix to one left gold/foreign
  under-stated in the realized path for 366-729 day holds.
- §112 and §112A rates may be equal yet are separate levers; never substitute.
- The rebate (§156; §87A in 1961) is for **resident** individuals only; the portal
  rejects it for a non-resident. A missing residential status must be a validation
  error, never a default to resident, which gives a non-resident zero tax. Use one
  shared residency predicate for the tax engine and for Schedule CG and foreign-income
  filtering.
- Rebate and surcharge: marginal relief must use the same rounded base as the
  tax; the 15% surcharge cap covers specified capital-gain and dividend income but
  **not** winnings or VDA income (which take the full band).
