# Corporate-action subject traps (continued)

Parsing traps 3-6, 8 and 9 for the free-text `subject` field of the NSE corporate-actions API; traps 1, 2 and 7 (the ones that change a price factor) are in SKILL.md §5. Read when writing or fixing a subject parser. Numbering matches SKILL.md §5.

3. **Bonus debentures and preference shares are not equity bonuses.** `Bonus Deb1:1`
   issues debt; share count is unchanged. Exclude with
   `/debenture|\bdeb\d|preference\s+share/i`, not the full word alone.
4. **Multiple dividend figures in one subject.** `Final Dividend Rs.4/- And Special
   Dividend Rs.10/-` pays Rs.14 on one ex-date. First-match understates; **sum every
   stated figure** (300 rows checked to sum exactly).
5. **Separator variants.** `Rs.5`, `Rs 5`, `Rs:- 5.50`, `Rs - 3.50`; singular `Re` for
   sub-rupee amounts. Allowing `r[se][.:\s-]*` took amount coverage from 99.5% to
   99.8%. Open the unparsed remainder instead of accepting a percentage.
6. **Leave ambiguous forms empty.** `Interim Dividend 3 Per Share` has no currency
   word; a bare-number rule would also swallow the ordinal in `2nd Interim Dividend`.
8. **Rights with two simultaneous tranches** (4:25 fully paid plus 2:25 partly paid)
   have no single ratio. Leave blank.
9. **The API files nothing for ETFs.** Zero rows for several large ETFs, so a
   widened scope did not recover a known 1:100 split. Query the source for the
   missing instrument class before widening a filter. Fix with a small hand-verified
   table, each entry citing the two closes its ratio was derived from, and never let
   it override a fetched action (a stale hardcoded factor would double-adjust).
