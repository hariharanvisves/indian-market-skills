# Banded rebasing: an action that takes several sessions to show

Detail for SKILL.md §7: how a correct corporate-action factor can still show as a multi-session raw price walk. Read when a price-continuity check fails on a bonus or split whose ratio and factor are correct.

**Rule:** do not assume a corporate action re-bases the raw price in one bar.

**Why:** a 5:7 bonus (factor 0.5833) on one small-cap walked raw close 163.00 to 93.50
over ten sessions, five of them locked (`Open == High == Low == Close`), each move
pinned at about -4.97% to -5.00%. The action, ratio and factor were all correct; the
check's one-bar assumption was wrong, and three claims in its failure message were
false ("raw closes are continuous", and others). The ex-date factor
(`date < exDate`) was right, which is why hundreds of other symbols adjusted flat.

Rules:
- Detect the signature (several locked bars at the band, cumulative move reconciling
  to the factor within tolerance), not a market rule. This repo's bhavcopy carried no
  price-band column, so the band regime is an inference from the path. Say so and
  flag it unresolved rather than asserting a band.
- Population was 1 of 87 covered-era events. With n=1, loosening any gate leaves
  the live suite green. Use synthetic fixtures for each gate and mutate each.
- Distinguish from crashes: several-session falls with zero locked bars are
  crashes, not band walks.
