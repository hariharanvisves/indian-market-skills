# Sovereign gold bonds and debt mutual funds: detail

Purpose: edge-case rules for SGBs and debt mutual funds, moved out of SKILL.md section 7. Read when classifying an SGB or a debt fund, or writing the tax-year loop for debt-fund purchase dates.

## Contents

- [Sovereign gold bonds](#sovereign-gold-bonds)
- [Debt mutual funds](#debt-mutual-funds)

## Sovereign gold bonds

- **Redemption at RBI maturity is exempt only if an individual held the bond
  from the date of original issue till maturity** (§70(1)(x) of the 2025 Act as
  substituted by the Finance Act 2026, from 1 April 2026; §47(viic) in 1961
  numbering); earlier redemptions by any individual were exempt. A
  secondary-market buyer's redemption, or an early redemption, is a taxable
  capital gain. Omit exempt redemptions from the capital-gains rows
  upstream; do not emit a zero row. Fail loudly if one reaches the schedule writer.
- A **market sale** before maturity is an ordinary §112 long-term gain (§197
  under the 2025 Act): no §112A exemption. Check for an SGB **before** any
  gold-matching regex, or "gold" in the name routes it wrongly.
- Match tranche symbols tightly (`SGB` plus six digits), not `^SGB`, which
  catches unrelated tickers. An SGB *fund* is a mutual fund with no exemption.
- The 2.5% coupon accrues on the tranche's **nominal issue price**, not on your
  cost. A secondary-market buyer's cost overstates it; an online-discount buyer's
  understates it. Hold nominal prices in a sourced table and render "issue price
  unknown" for an unlisted tranche rather than falling back to cost.

## Debt mutual funds

A *specified mutual fund* under §50AA holds more than 65% in
debt and money-market instruments. Units bought **on or after 1 April 2023** are taxed at
slab, always, whatever the holding period; there is no long-term bucket. Units
bought before that date keep a long-term path. Route on the **purchase** date,
not the sale date, and verify the current thresholds against statute before
coding either.

The *specified mutual fund* definition (§76(5)(b) of the 2025 Act; §50AA in 1961
numbering) changed on **1 April 2026**. From then a fund is specified if it invests
**more than 65%** of its proceeds in debt and money-market instruments, or **65% or
more** in units of such a fund (the fund-of-funds limb), measured on the annual
average of the daily closing figures. A tax-year loop over 2023-24 to 2025-26 must
use the pre-2026 definition, not this one
([open claim](../../../docs/unverified-claims.md)). Test debt FoF, bond index,
target-maturity, gilt and money-market funds as specified **before** any generic
FoF, index or international rule; equity-oriented hybrids and arbitrage funds are
not specified. An unknown or missing MF sub-category must reject (fail closed),
never default to equity.
