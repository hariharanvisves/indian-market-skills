# Constituent lists: NSE CSVs, strategy indices, BSE

Where to fetch index constituent lists and what each source gets wrong. Read when fetching a constituents CSV or API response for an index (SKILL.md §7).

- NSE archive CSVs under `nsearchives.nseindia.com/content/indices/` work with a
  browser User-Agent and no cookies, but filenames are **inconsistent per index**
  (`ind_nifty50list.csv` versus `ind_nifty200Momentum30_list.csv`). Pin each
  explicitly. A derived name returns an HTML error page; reject a body that starts
  with `<`.
- **Strategy/factor indices** (Alpha 50, Value 20, High Beta 50) are not in those
  CSVs (404 under every filename tried). Use the live-site market-data API after
  loading a page for cookies. Response data sat one level deeper than expected,
  the first row is the index itself, and some index names have two spellings where
  only one returns rows.
- Old third-party GitHub mirrors of constituents lists are years stale.
- **BSE has no plain-HTTP source.** It needs browser automation: constituents come
  from one host keyed on scrip code with no ticker, the scrip master from a second
  host, and the two block cross-origin reads. Join on scrip code. BSE sector
  indices are classifications (hundreds of names), not curated baskets. Some
  endpoints return only the top 30 for every index, which looks plausible and
  silently truncates.

Detector: reject a body that starts with `<`, and a list shorter than the index's
member count.

