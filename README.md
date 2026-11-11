<p align="center">
  <img src="assets/icon.png" width="140" alt="Indian Market Skills">
</p>

<h1 align="center">Indian Market Skills</h1>

<p align="center">
  <em>Your coding agent knows US tax law. This teaches it India's.</em>
</p>

<p align="center">
  <a href="https://github.com/hariharanvisves/indian-market-skills/stargazers"><img src="https://img.shields.io/github/stars/hariharanvisves/indian-market-skills?style=flat-square&color=ff9933&label=stars" alt="Stars"></a>
  <a href="https://github.com/hariharanvisves/indian-market-skills/releases"><img src="https://img.shields.io/github/v/release/hariharanvisves/indian-market-skills?style=flat-square&color=0f2a4a&label=release" alt="Release"></a>
  <a href="https://github.com/hariharanvisves/indian-market-skills/actions/workflows/validate.yml"><img src="https://img.shields.io/github/actions/workflow/status/hariharanvisves/indian-market-skills/validate.yml?style=flat-square&label=validate" alt="Validate"></a>
  <img src="https://img.shields.io/badge/skills-18-2fbf71?style=flat-square" alt="18 skills">
  <a href="#install"><img src="https://img.shields.io/badge/works_with-Claude_Code_·_Codex_·_Cursor_·_Gemini-0f2a4a?style=flat-square" alt="Works with Claude Code, Codex, Cursor and Gemini"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT license"></a>
</p>

<p align="center">
  <b><a href="#install">Install</a> · <a href="#skills">Skills</a> · <a href="#reviewers-and-commands">Reviewers</a> · <a href="#five-rules-that-make-us-authored-code-wrong-in-india">India ≠ US</a> · <a href="#how-the-facts-are-kept-honest">How it stays correct</a> · <a href="CONTRIBUTING.md">Contributing</a></b>
</p>

<table>
<tr>
<td align="center" width="33%"><h3>18 skills</h3>tax, charges, NSE data, statements, backtests, options, broker APIs</td>
<td align="center" width="33%"><h3>4 reviewers</h3>read-only agents that audit your diff, with a slash command each</td>
<td align="center" width="33%"><h3>Every rate dated</h3>checked against a statute, circular or broker schedule, with its source</td>
</tr>
</table>

---

Most finance skills were written for US markets and crypto. Ported to India, they
give confident wrong answers. The rates differ, but the bigger problem is that the
**rules** differ: no wash-sale rule, asymmetric loss set-off, calendar-month holding
periods, STT with its own base and side for each charge, F&O taxed as business
income, and holidays that pandas has never heard of.

These are [Agent Skills](https://agentskills.io). Your agent loads the right one
when the task calls for it, and you don't need to change how you prompt.

| You ask your agent to… | Skill that loads | A rule it enforces |
|---|---|---|
| "Classify this sale as STCG or LTCG" | `indian-capital-gains-tax` | Long term needs **more than 12 calendar months**, so a `days_held > 365` check is wrong across 29 February |
| "Build a brokerage calculator" | `indian-equity-charges` | GST is charged on brokerage + exchange charge + SEBI fee, never on STT or stamp duty |
| "Compute F&O tax for ITR" | `fno-tax-and-charges` | F&O is non-speculative business income, and options STT is on **premium**, not notional |
| "Generate trading days for the backtest" | `nse-trading-calendar` | Use NSE's dated holiday circulars, not `bdate_range`; Muhurat is a real session whose trades settle |
| "Add order placement via Upstox" | `indian-broker-api-safety` | Every API order is an algo order under SEBI's 2025 framework: algo ID, static IP, 10 orders/second limit |
| "Import my CAS and Groww statements" | `mf-scheme-matching` | No fuzzy name matching; match by ISIN, and keep folio in the FIFO key |

## Install

**Any agent, one command.** The [skills CLI](https://github.com/vercel-labs/skills)
installs into Claude Code, Codex, Cursor, Gemini CLI and many other agents:

```bash
npx skills add hariharanvisves/indian-market-skills                  # all 18 skills
npx skills add hariharanvisves/indian-market-skills --list           # browse first
npx skills add hariharanvisves/indian-market-skills --skill indian-capital-gains-tax
```

That installs skills only. Use a native plugin below to get the reviewer agents
and the `/review-*` commands too.

<details>
<summary><b>Claude Code (recommended)</b></summary>

```
/plugin marketplace add hariharanvisves/indian-market-skills
/plugin install indian-market-skills@indian-market-skills
```

On Claude Code 2.1.275 or later, one step:

```
/plugin install indian-market-skills --marketplace hariharanvisves/indian-market-skills
```

Plugin skills, agents and commands are namespaced:
`/indian-market-skills:review-tax`, `@agent-indian-market-skills:indian-tax-reviewer`.

If cloning over SSH fails, add the marketplace by its HTTPS URL instead:
`/plugin marketplace add https://github.com/hariharanvisves/indian-market-skills.git`.

For local development, run `claude --plugin-dir /path/to/indian-market-skills`.

</details>

<details>
<summary><b>Codex</b></summary>

```bash
codex plugin marketplace add hariharanvisves/indian-market-skills
codex plugin add indian-market-skills@indian-market-skills
```

</details>

<details>
<summary><b>Gemini CLI</b></summary>

```bash
gemini extensions install https://github.com/hariharanvisves/indian-market-skills
```

</details>

<details>
<summary><b>Cursor</b></summary>

```bash
npx skills add hariharanvisves/indian-market-skills -a cursor
```

</details>

<details>
<summary><b>Manual copy</b></summary>

Copy a skill directory into your agent's skills folder, and an agent file into its agents folder:

```bash
git clone https://github.com/hariharanvisves/indian-market-skills.git
cp -R indian-market-skills/skills/indian-capital-gains-tax ~/.claude/skills/
cp indian-market-skills/agents/indian-tax-reviewer.md ~/.claude/agents/
```

Or place it in a project at `.claude/skills/` so it loads only for that repo.
Restart the agent session and the skill is available.

</details>

## Skills

### Tax

| Skill | What it covers |
|---|---|
| [`indian-capital-gains-tax`](skills/indian-capital-gains-tax/) | §111A / §112A rates (§196 / §198 of the 2025 Act), the calendar-month boundary, the ₹1.25L aggregate exemption, grandfathering, set-off ordering and 8-year carry-forward |
| [`itr-filing-schedules`](skills/itr-filing-schedules/) | Choosing ITR-1 to ITR-4, the schedule map, cross-schedule identities, foreign tax credit (Form 67, Form 44 from 2026), TDS dedupe, advance tax, §288A/B rounding, JSON emit |
| [`fno-tax-and-charges`](skills/fno-tax-and-charges/) | F&O and intraday as business income (non-speculative vs speculative), ITR-3, tax-audit turnover, dated F&O STT, stamp duty and exchange charges |
| [`corporate-action-taxation`](skills/corporate-action-taxation/) | Cost basis and holding period across bonus, split, rights, demerger and merger; buybacks in three dated regimes; dividend and bonus stripping |
| [`foreign-equity-for-residents`](skills/foreign-equity-for-residents/) | US stocks and RSUs for resident Indians: 24-month threshold, SBI TT rate conversion, LRS and TCS, DTAA withholding, Schedule FA on a calendar year |

### Costs and valuation

| Skill | What it covers |
|---|---|
| [`indian-equity-charges`](skills/indian-equity-charges/) | STT, exchange charge, SEBI fee, stamp duty, GST and DP charge, each with its own base and side, and why a blended bps figure can't express them |
| [`indian-equity-valuation`](skills/indian-equity-valuation/) | India-specific DCF and comps inputs: corporate tax regimes, FBIL risk-free rate, Ind AS 116, consolidated accounts, results lag, promoter pledges |

### Market data

| Skill | What it covers |
|---|---|
| [`indian-market-data-pitfalls`](skills/indian-market-data-pitfalls/) | Start here. IST date shifts, survivorship, corporate-action breaks, format drift, duplicates, money precision, sanity gates |
| [`nse-bhavcopy-corporate-actions`](skills/nse-bhavcopy-corporate-actions/) | Bhavcopy formats and their date ranges, the UDiFF switch, the corporate-actions API, banded rebasing, price-sanity guards |
| [`nse-universe-survivorship`](skills/nse-universe-survivorship/) | Point-in-time index membership from NSE change releases, ever-member unions, renames via ISIN |
| [`nse-trading-calendar`](skills/nse-trading-calendar/) | Trading and clearing holidays by segment, Muhurat and special sessions, T+1 dates, expiry shifts, the dated weekly-expiry history |

### Statements and mutual funds

| Skill | What it covers |
|---|---|
| [`indian-broker-statement-formats`](skills/indian-broker-statement-formats/) | Zerodha, Groww, CAMS, KFintech, CAS PDF, INDmoney and AIS formats and their traps; parse-coverage and arithmetic checks |
| [`mf-scheme-matching`](skills/mf-scheme-matching/) | Matching schemes across sources without false merges; AMFI NAVAll lookup by ISIN; folio-aware FIFO; price-free dedupe |

### Backtests and options

| Skill | What it covers |
|---|---|
| [`backtest-engine-correctness`](skills/backtest-engine-correctness/) | 24 defect classes: look-ahead, annualisation, phantom trades, cost sizing, metrics, engine versioning, NSE fill realism |
| [`momentum-factor-research`](skills/momentum-factor-research/) | Lookback ladder, volatility estimator choice, parameter sensitivity, factor vs portfolio validation, safe formula engines |
| [`nse-options-mechanics`](skills/nse-options-mechanics/) | European exercise, IV non-convergence, expiry as an instant, dated settlement-price rules, one ATM definition, multi-leg payoff |

### Broker APIs

| Skill | What it covers |
|---|---|
| [`kite-connect-safety`](skills/kite-connect-safety/) | Kite Connect login and tokens, authorization, live-path gating, order ceilings, idempotency, the UNKNOWN state, static IP |
| [`indian-broker-api-safety`](skills/indian-broker-api-safety/) | SEBI's retail algo framework, plus auth, token, idempotency and order-state differences across Upstox, Dhan, Angel One, ICICI Breeze and Fyers |

## Reviewers and commands

Four read-only reviewer agents (`Read, Glob, Grep` only). They never edit, run
or place orders. Each one loads its skills and reports findings as
`path:line — severity — defect — evidence — fix`.

| Command | Agent | Reviews |
|---|---|---|
| `/review-tax` | [`indian-tax-reviewer`](agents/indian-tax-reviewer.md) | Classification, boundaries, set-off ordering, rounding, schedule identities |
| `/review-ingestion` | [`statement-ingestion-reviewer`](agents/statement-ingestion-reviewer.md) | Parsers and importers: false merges, duplicates, coverage, unit and date shifts, PII in tracked files |
| `/review-backtest` | [`backtest-reviewer`](agents/backtest-reviewer.md) | Look-ahead, survivorship, costs, metrics, engine versioning, tests that can't fail |
| `/review-broker` | [`broker-safety-reviewer`](agents/broker-safety-reviewer.md) | Fail-open guards, secret leakage, live-path gating, idempotency, rebalance safety |

Pass a path or git range (`/review-tax src/tax/`). With no target, a command reviews the current diff.

## Five rules that make US-authored code wrong in India

They cause silent errors that push results the wrong way:

1. **No wash-sale rule.** No window disallows a loss for re-entering a position.
   Porting a wash-sale check *suppresses legitimate loss harvesting*.
2. **No deduction against ordinary income.** India has no equivalent of the US
   $3,000 allowance. A capital loss offsets capital gains, or it waits.
3. **Set-off is asymmetric.** STCL offsets STCG *and* LTCG; **LTCL offsets LTCG
   only**. Pooling them wipes out STCG that is genuinely taxable.
4. **Carry-forward is 8 years, and only if you file on time** (by the original
   due date). It is not indefinite.
5. **The boundary is calendar months.** LTCG needs **more than** 12 months. A
   holding of exactly 12 months is short term, so `>=` flips a 20% rate to 12.5%,
   and `days_held > 365` is wrong whenever the window spans 29 February.

## How the facts are kept honest

- **Primary sources only.** Every rate and rule cites a statute, gazette, CBDT,
  SEBI, NSE or AMFI circular, or a broker's published charge schedule. Secondary
  sources do get it wrong: while `indian-equity-charges` was being written, two of
  them gave the NSE cash charge as 0.00297%, but two brokers' live schedules
  agreed on 0.00307%.
- **Dated.** Each skill carries `metadata.verified`, and CI warns once it is more than
  180 days old. Rates keyed to a date (STT, buybacks, settlement rules) list each
  regime with its date range.
- **One owner per fact.** Each rate lives in one skill; the others link to it.
  [`data/rates.json`](data/rates.json) is a machine-readable copy, and CI fails
  if it drifts from the owning skill.
- **Unknowns are listed, not guessed.** [`docs/unverified-claims.md`](docs/unverified-claims.md)
  tracks every claim still waiting on a primary source.
- **Evals.** [`evals/`](evals/) has trigger and answer cases for every skill.
  Run them with `python3 scripts/run_evals.py`, or add `--baseline` to compare against the same agent without the plugin.
  On the first full run (2026-11-11, Sonnet), 97 of 103 passed. The six misses were
  five over-strict checks and one skill description that missed a common phrasing.
  All six were fixed and re-checked.

Rates change with each Finance Act and exchange circular. Load them from a dated
table in your own code, and re-check before relying on any figure here.

## Project structure

```
skills/<name>/SKILL.md      18 skills (Agent Skills format)
agents/<name>.md            4 read-only reviewer agents
commands/review-*.md        slash commands that run the reviewers
evals/cases/<name>.json     trigger and answer evals, one file per skill
data/rates.json             dated rate table, checked against the skills
docs/unverified-claims.md   claims waiting on a primary source
scripts/validate.py         frontmatter, links, evals, rates, manifests (runs in CI)
scripts/run_evals.py        runs the evals through `claude -p`
.claude-plugin/  .codex-plugin/  .cursor-plugin/  gemini-extension.json
```

## Related skills (not in this repo)

Generic methods worth pairing with these skills. Others wrote them, mostly for
US markets. Use them for the method, and take every India rule (tax, charges,
settlement, data) from this repo.

| Skill / agent | Source | Licence | Adapt for India |
|---|---|---|---|
| `backtest-expert` | [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/backtest-expert) | MIT | Cost model from `indian-equity-charges`; fills from `backtest-engine-correctness` |
| `residual-edge-analyzer` | [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/residual-edge-analyzer) | MIT | Baseline is a total-return Indian index (Nifty 50 TRI), not SPY |
| `technical-analyst` | [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills/tree/main/skills/technical-analyst) | MIT | Chart method is market-neutral; its script fallback fetches US data from FMP |
| `dcf-model` | [ginlix-ai/LangAlpha](https://github.com/ginlix-ai/LangAlpha/tree/main/plugins/langalpha_research/skills/dcf-model) | Apache-2.0 | Inputs from `indian-equity-valuation` |
| `comps-analysis` | [ginlix-ai/LangAlpha](https://github.com/ginlix-ai/LangAlpha/tree/main/plugins/langalpha_research/skills/comps-analysis) | Apache-2.0 | Peer and accounting rules from `indian-equity-valuation` |
| `quant-analyst` (subagent) | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/07-specialized-domains/quant-analyst.md) | MIT | Point it at this repo's skills |
| `risk-manager` (subagent) | [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/07-specialized-domains/risk-manager.md) | MIT | Framed for enterprise risk; keep the market and portfolio sections |

## Scope and disclaimer

Informational and engineering guidance only. **Not tax, legal or investment
advice.** Consult a qualified professional. Nothing here is a recommendation to
buy or sell any security.

Coverage is NSE/BSE equity, equity and index derivatives, and mutual funds, for
**resident individuals**. NRIs are out of scope, apart from pointers in
`foreign-equity-for-residents`. Crypto (virtual digital assets) is a separate
regime: a flat 30% with no set-off and no carry-forward, so harvesting and
offsetting concepts don't apply to it at all.

## Contributing

Corrections are welcome, especially on rates and effective dates. Open a
[correction issue](https://github.com/hariharanvisves/indian-market-skills/issues/new?template=correction.yml)
with a primary-source link, or pick up a claim from
[`docs/unverified-claims.md`](docs/unverified-claims.md). See
[CONTRIBUTING.md](CONTRIBUTING.md) for the sourcing rule, file format and
validation steps.

## License

[MIT](LICENSE) © hariharanvisves
