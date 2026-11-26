# Press-release parser defects

Row-parsing traps in NSE index-change press releases (NSE CMS and niftyindices). Read when writing or debugging a parser for index-change releases (SKILL.md §5).

Rule: a row parser that takes "the last all-caps token" is wrong for at least two
layouts.

1. **Trailing token eats the Effective Date column.** Releases carrying a per-row
   date column print `Zuari Industries Limited  ZUARIAGRO  April 9, 2012`. The
   last `[A-Z0-9&-]{2,}` token is `2012`. This yields a wrong symbol rather than
   a failure, lands in both `included` and `excluded`, and loses the release's
   real changes. Strip a trailing `Month D, YYYY` first and reject all-digit
   tokens.
2. **G-Sec/SDL/bond releases share the channel.** They key on ISIN with a Maturity
   Date column and no Symbol column, so the parser scrapes a maturity year as a
   symbol. Screen fixed-income releases out in the shared parser, not in one
   caller: a caller reading PDFs off disk never sees the API summary that the
   other caller filtered on.
3. **Section nesting.** Releases nest a numbered prose heading (`1) Replacements
   on account of semi-annual review`), a lettered index heading (`a) Nifty 50`),
   then tables. Treating the numbered level as the index collapsed one release
   into five pseudo-indices. Use the lettered heading.
4. **Effective date placement.** It appears in the title (`w.e.f. April 02, 2018`)
   or the body (`shall become effective from March 27, 2020`), sometimes wrapped
   mid-date. Collapse whitespace first.
5. **Name-only releases.** Older releases list company names with no symbol
   column. "Last token of the row" returns `LTD`. Resolve names by **exact match
   or an explicit alias only**; fuzzy matching swaps Reliance Industries for
   Reliance Infrastructure.
6. **Same release, two hosts.** NSE CMS and niftyindices serve one document under
   different filenames with identical content. Dedupe on content
   `(effective, index, included, excluded)`, not filename; applying a change twice
   cannot be inverted.

Detector: enumerate every distinct symbol your parser ever emitted and reject
anything all-digit, a single character, or in the legal-suffix set. Repair
already-parsed events only where the defect signature is provable (an all-digit
symbol), never "re-parse everything", because re-parsing a de-duplicated sibling
refills it and doubles rows (88 duplicates against zero in one corpus). Abort the
write if the result contains any duplicate row.

