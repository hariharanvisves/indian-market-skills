# Section and rule concordance: 1961 Act to 2025 Act

Purpose: lookup table of renumbered sections and rules for ITR work, moved out of SKILL.md. Read when labelling a section in a human-facing string or mapping a 1961 number to its 2025 number.

The Income-tax Act 2025 is in force from 1 April 2026 with renumbered sections;
Chapter VI-A becomes Chapter VIII and "assessment year" becomes "tax year". The
CBDT ITR JSON schema **keeps the 1961 literals in field names and enumerations**
regardless of year: translate section numbers only in human-facing labels, never
in JSON keys.

The table below was checked against the gazetted Act text and the Income-tax
Rules 2026 on 2026-11-11; confirm sub-section-level mappings against the CBDT
concordance utility:

| 1961 | 2025 | | 1961 | 2025 |
|---|---|---|---|---|
| §111A | §196 | | §87A rebate | §156 |
| §112 | §197 | | §89 relief | §157 |
| §112A | §198 | | §80C/80CCC/80CCE | §123 |
| §115BB, §115BBH | §194 | | §80CCD | §124 |
| §115JC (AMT) | §206 | | §80D | §126 |
| §234A / B / C | §423 / §424 / §425 | | §54 / §54EC / §54F | §82 / §85 / §86 |
| §194S (VDA TDS) | §393 | | §49 (cost by acquisition mode) | §73(1) |
| §44AD/ADA/AE | §58 | | Rule 128 (FTC) | Rule 76 (2026 Rules) |
| §115BAC (new regime) | §202 | | Rule 115 (FX conversion) | Rule 206 (2026 Rules) |
| Form 67 (FTC statement) | Form 44 | | §288A / §288B (rounding) | §516 |

Rule 76 and Form 44 apply from tax year 2026-27; returns for AY 2026-27 and
earlier still use Rule 128 and Form 67. Guard each label key with a parity test;
a missing key renders `undefined`.
