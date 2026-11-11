# indian-market-skills

A Markdown-only repo of Agent Skills (`skills/<name>/SKILL.md`) and read-only
reviewer agents (`reviewers/<name>.md`). It ships as a Claude Code plugin and
marketplace through `.claude-plugin/`.

- Conventions, sourcing rule and fact-ownership map: [CONTRIBUTING.md](CONTRIBUTING.md)
- Eval case format: [evals/README.md](evals/README.md). Open claims: [docs/unverified-claims.md](docs/unverified-claims.md)
- User-facing overview and install steps: [README.md](README.md)

## Commands

```bash
python3 scripts/validate.py   # must exit 0 before you commit
claude plugin validate .      # checks the plugin and marketplace manifests
python3 scripts/run_evals.py [skill]   # answer evals through `claude -p`; costs tokens
```

## Quirks

- Tax content follows the Income-tax Act 2025, in force from 1 Apr 2026. CBDT ITR JSON
  field names keep the 1961 section numbers, so skills cite both.
- `.DS_Store` files are gitignored. `claude plugin validate` still warns about the
  ones on disk. Ignore that warning, because those files are never committed.
