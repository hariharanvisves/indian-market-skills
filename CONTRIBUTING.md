# Contributing

Corrections and new skills are welcome. Rates and effective dates matter most.

## Sourcing rule

Every rate, threshold, date or format claim must cite a **primary source**:

- statute text or a Finance Act
- a CBDT notification or circular, or the e-filing portal
- an exchange, SEBI or AMFI circular
- a broker's published charge schedule

Blogs, news articles and search summaries do not count. If two sources disagree,
prefer the one that has to be correct because it bills people or binds them.
Put the citation in the pull request description.

## Editing a skill

- Each skill is `skills/<name>/SKILL.md`. Its frontmatter `name` must match the
  directory, using lowercase letters, digits and hyphens. Keep it to 64 characters or fewer.
- `description` says what the skill covers and when to use it, in 1024 characters or fewer.
- When you re-verify rates, update the as-of date in `compatibility`.
- Bump `metadata.version` when you make a substantive change.
- **One owner per fact.** Each rate or rule lives in exactly one skill. Other
  skills link to it with a relative path instead of restating it:
  - capital-gains rates and set-off: `indian-capital-gains-tax`
  - transaction charges: `indian-equity-charges`
  - survivorship: `nse-universe-survivorship`
  - corporate-action price adjustment (for returns, not tax): `nse-bhavcopy-corporate-actions`
  - mutual-fund matching: `mf-scheme-matching`
  - F&O and intraday tax, F&O charges: `fno-tax-and-charges`
  - tax effect of corporate actions (cost basis, buybacks): `corporate-action-taxation`
  - foreign shares, RSUs, LRS/TCS, Schedule FA: `foreign-equity-for-residents`
  - holidays, sessions, expiry-day shifts: `nse-trading-calendar`
  - general broker-API safety principles: `kite-connect-safety`
  - SEBI retail-algo rules and non-Kite broker deltas: `indian-broker-api-safety`
  - ITR forms, schedules, rounding, advance tax: `itr-filing-schedules`

## Editing an agent

Agents in `agents/` are read-only reviewers. Their `tools:` must not include
`Bash`, `Write` or `Edit`. Each agent names the skills it relies on and reports
findings as `path:line — severity — defect — evidence — fix`.

## Adding a skill or agent

Add a row to the matching table in `README.md`. When you release, bump `version`
in `.claude-plugin/plugin.json` and in the matching entry in
`.claude-plugin/marketplace.json`.

## Before opening a pull request

```bash
python3 scripts/validate.py   # frontmatter, links, README tables, manifests
claude plugin validate .      # if Claude Code is installed
```

CI runs `scripts/validate.py` on every pull request.

## Scope

The repo covers the NSE/BSE cash segment and resident-individual tax. Content is
informational and engineering guidance only. It is not tax, legal or investment advice.
