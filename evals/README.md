# Evals

One file per skill: `evals/cases/<skill-name>.json`. Each file checks two things:
whether the skill **triggers** on the right prompts, and whether an agent that loads
it gives the **right answer**.

## Case format

```json
{
  "skill_name": "indian-capital-gains-tax",
  "trigger": {
    "positive": [{ "prompt": "Is a share held exactly 12 months long term in India?" }],
    "negative": [{ "prompt": "What is the brokerage on a ₹1L delivery buy?", "owner": "indian-equity-charges" }]
  },
  "evals": [
    {
      "id": 1,
      "prompt": "I bought listed shares on 2025-04-01 and sold on 2026-04-01. STCG or LTCG?",
      "expectations": ["Classifies the gain as short term, because LTCG needs more than 12 months"],
      "must_match": ["(?i)short[- ]term|STCG"],
      "must_not_match": ["(?i)\\bis (a )?long[- ]term\\b"]
    }
  ]
}
```

- `trigger.positive`: prompts where this skill should load. Give at least 3.
- `trigger.negative`: nearby prompts that belong to another skill. `owner` names that
  skill, or is `null` if no skill in this repo applies. Give at least 2.
- `evals`: 3 to 6 answer checks. Each one targets a rule in the skill that a generic,
  US-trained model gets wrong.
- `expectations`: plain-language criteria for a human or an LLM grader.
- `must_match` / `must_not_match`: Python regexes that `scripts/run_evals.py` checks
  against the answer. Keep them loose enough to accept any correct wording.
- Every fact an eval asserts must already be in the skill, with its source.

## Running

```bash
python3 scripts/validate.py                       # also checks the case files are well formed
python3 scripts/run_evals.py                      # every skill; calls `claude -p`, so it costs tokens
python3 scripts/run_evals.py indian-equity-charges
python3 scripts/run_evals.py --baseline           # same prompts without the plugin, for comparison
```

The runner prints pass or fail for each eval, then the overall pass rate. Its regex
checks are a floor. Use `expectations` for a full review.
