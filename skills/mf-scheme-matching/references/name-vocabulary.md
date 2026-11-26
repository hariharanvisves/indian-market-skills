# Scheme-name vocabulary and parse edge cases

Purpose: the token vocabulary and tokenizer edge cases behind section 4 of
[SKILL.md](../SKILL.md). Extend these tables when a real name fails; never loosen the
equality rule. Each addition needs an anti-over-merge test (Direct vs Regular is the
standard probe).

## Vocabulary to handle explicitly

| Token or pattern | Handling |
|---|---|
| `DG`, `RG` | direct growth, regular growth (plan and option together) |
| `DP`, `Dir`, `Reg`, `Gr` | direct plan, direct, regular, growth |
| `(Non-Demat)` | custody suffix, not identity |
| `Direct` | whole-word match only; must not match inside another token of a Regular plan name |
| `(formerly ...)`, `(erstwhile ...)` | strip the annotation **before** tokenizing, so the old name is not parsed as part of the identity |
| "Direct Growth Plan Growth Option" | a repeated identical option is one option, not a conflict |
| a second, different option, or two plans | fails the parse |
| "Growth Opportunities Fund", "Dividend Yield Fund" | option words inside the scheme's own name; option words are not deletable noise |

## Identity boundary

Treat `fund` / `scheme` as identity boundaries and read the option only from the tail after
them. The last `fund` or `scheme` token is the boundary; a name without one ends its identity
at the first plan or option word. Neither boundary word joins the identity. A loosened rule applies to every name; a vocabulary entry applies only to the token it
defines, which is why the vocabulary grows and the rule does not.
