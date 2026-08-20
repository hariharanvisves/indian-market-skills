# Indian Market Skills

[Agent Skills](https://agentskills.io) for Indian equity markets, tax and broker
data. Portable across Claude Code, Cursor, Codex, Gemini CLI and other
skills-compatible agents.

Most finance skills in circulation were written for US markets and crypto. Ported
to India they produce confident wrong answers — not because the rates differ, but
because the **rules** differ. These skills exist to close that gap.

## Skills

| Skill | What it covers |
|---|---|
| [`indian-equity-charges`](skills/indian-equity-charges/) | STT, exchange transaction charge, SEBI turnover fee, stamp duty, GST and DP charges — with the correct base and side for each, and why a blended bps figure cannot express them |
| [`indian-capital-gains-tax`](skills/indian-capital-gains-tax/) | §111A / §112A rates, the 12-month boundary, the ₹1.25L annual aggregate exemption, §112A grandfathering, set-off ordering and 8-year carry-forward |
| [`indian-market-data-pitfalls`](skills/indian-market-data-pitfalls/) | IST date shifts, survivorship bias, corporate-action price breaks, broker statement drift, cross-source duplicates, MF scheme-name matching, parser coverage checks |
| [`nse-options-mechanics`](skills/nse-options-mechanics/) | European-style exercise (so Black-Scholes throughout), IV non-convergence, expiry as an instant from the calendar, settlement price vs price-at-an-instant, one ATM definition, multi-leg payoff and leg ordering |

## Install

Copy a skill directory into your agent's skills folder:

```bash
git clone https://github.com/hariharanvisves/indian-market-skills.git
cp -R indian-market-skills/skills/indian-capital-gains-tax ~/.claude/skills/
```

Or place it in a project at `.claude/skills/` so it loads only for that repo.
Restart the agent session and the skill is available.

## Four rules that make US-authored tax code wrong in India

Called out here because they cause silent, wrong-direction errors:

1. **No wash-sale rule.** No window disallows a loss for re-entering a position.
   Porting a wash-sale check *suppresses legitimate loss harvesting*.
2. **No deduction against ordinary income.** There is no ₹ equivalent of the US
   $3,000 allowance. A capital loss offsets capital gains, or it waits.
3. **Set-off is asymmetric.** STCL offsets STCG *and* LTCG; **LTCL offsets LTCG
   only**. Pooling them wipes out STCG that is genuinely taxable.
4. **Carry-forward is 8 years and conditional** on filing by the §139(1) due
   date — not indefinite.

A fifth, for the boundary: LTCG requires **more than** 12 months, so a holding of
exactly 365 days is short term. `>= 365` flips a 20% rate to 12.5%.

## On the rates

Every rate in these skills carries an as-of date and is **verified against broker
charge schedules or statute, not secondary summaries**. While writing
`indian-equity-charges`, two secondary sources gave the NSE cash transaction
charge as 0.00297%; two brokers' live schedules agreed on 0.00307%. Prefer a
source that has to be correct because it bills people.

Rates change with each Finance Act and with exchange circulars. **Load them from a
dated table with a single owner** rather than inlining them at call sites, and
re-verify before relying on any figure here.

## Scope and disclaimer

Informational and engineering guidance only. **Not tax, legal or investment
advice.** Consult a qualified professional. Nothing here constitutes a
recommendation to buy or sell any security.

Coverage is the **NSE/BSE cash segment**. Derivatives have different charge bases
and sides. Virtual digital assets (crypto) are a separate regime under §115BBH —
flat 30%, no set-off, no carry-forward — so harvesting and offsetting concepts do
not apply to them at all.

## Contributing

Corrections welcome, especially on rates and effective dates. Please cite a
primary source (statute, exchange circular, or a broker's published schedule)
rather than a blog or search summary.

## License

MIT — see [LICENSE](LICENSE).
