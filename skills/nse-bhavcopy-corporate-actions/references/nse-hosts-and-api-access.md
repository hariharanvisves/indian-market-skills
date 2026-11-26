# NSE hosts and API access

Dated, observed notes on which NSE host serves which path. NSE changes these without notice; re-probe before depending on one. Read when a bhavcopy or corporate-actions fetch returns 403, a redirect or nothing.

- Use `nsearchives.nseindia.com`. `archives.nseindia.com` returned 403 for the same
  paths earlier but served them on 2026-11-11; do not depend on it. A plain browser
  User-Agent was enough; no cookies for these files.
- API host (fetch failures seen from about 2026-11-16, observed 2026-11-26, no NSE announcement found):
  `www.nseindia.com` pages and `/api/...` paths 301-redirect to the same path on
  `www.nseindia.in`. The `.com` homepage returns 403 (Akamai) to scripted clients,
  so a client that primes cookies on the `.com` homepage never gets cookies for
  `.in`. On 2026-11-26 `GET https://www.nseindia.in/api/corporates-corporateActions?index=equities`
  returned 200 JSON with no cookie priming. `nsearchives.nseindia.com` archive paths
  (bhavcopy zips, circular PDFs) still served 200 with no redirect. Keep the API
  host in one constant, call the `.in` host or follow redirects, and make a stalled
  export or last-date-lag check fail loudly: a nightly fetch failed silently and
  the export stalled for days when this changed.
- Corporate-actions endpoint: `nseindia.com/api/corporates-corporateActions?index=equities&from_date=DD-MM-YYYY&to_date=DD-MM-YYYY`
  needs `index=equities` (otherwise `Missing index`). It was earlier cookie-gated (GET
  the homepage first) and queried one year at a time; on 2026-11-11 it answered a bare
  curl and a 2000-2024 range in one call (39,046 rows), and serves back to at least
  2000. Keep cookie priming and year chunks as the safe default. NSE's official MCP
  exposes the same data as `get_corporate_actions`:
  [nse-official-mcp](../../nse-official-mcp/SKILL.md).
