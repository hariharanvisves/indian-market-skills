# Ticker rename rules (continued)

Rename-map rules 1, 3, 4, 5 and 7-10 from SKILL.md §8, numbering unchanged. Rules 2 (ISIN wins conflicts) and 6 (compare issuers, not full ISINs) stay in SKILL.md. Read when generating or reviewing a rename map.

1. **ISIN reach depends on which files you load.** The legacy bhavcopy carries ISIN
   from about late 2011 to 5 Jul 2024 and UDiFF carries it after; only
   `sec_bhavdata_full` has none (formats in
   [nse-bhavcopy-corporate-actions](../../nse-bhavcopy-corporate-actions/SKILL.md) §1). A pipeline that
   switched to `sec_bhavdata_full` in 2019 loses ISIN for later renames. A rename is
   ISIN-derivable only if the old ticker traded in an ISIN-bearing window of the
   files you loaded.
3. **Do not chain hops.** Chaining assumes every intermediate is in the map; one
   missing hop silently yields a stale ticker. Flatten at generation. A map where
   several sources share one ISIN and point to one target is a legitimately
   flattened chain, not a collision.
4. **Date adjacency is not evidence.** In any 20-session window the exchange lists
   dozens of unrelated IPOs, ETFs and rights entitlements (46 candidates for one
   symbol). Suffixed lines (`-RE`, `-BE`) are never successors.
5. **Reject many-to-one folds.** Two different old symbols claiming one target
   means at least one is wrong. Co-trading on the same session proves distinct
   issuers (one pair overlapped on 4,168 sessions). Measure co-trading using the
   same series filter as the generator, or you get false overlaps from rights
   lines.
7. **Leave ambiguous unapplied.** More than one qualifying successor is a human
   decision from a source document. In one corpus 247 such cases were recorded and
   never applied.
8. **Uniqueness is not identity.** Promoting a candidate because it is the only
   survivor converts every killed rival into a confident rename with no evidence.
   Track a separate `identityConfirmed` flag; "applied" is not "confirmed".
9. **Series set for "is this listing alive".** Use the same-listing series
   ([nse-bhavcopy-corporate-actions](../../nse-bhavcopy-corporate-actions/SKILL.md) §2). Dropping them fabricates a termination date and opens a false
   successor window.
10. **Regeneration is a semantic change.** A wider price corpus reduced candidate
    counts without raising identity certainty and promoted ambiguous entries to
    confident ones. Diff the confirmed set before adopting a regenerated map.
