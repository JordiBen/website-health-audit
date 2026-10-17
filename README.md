# SEO Audit & Domain Checker: Bulk DNS Lookup, SSL Checker, DMARC & Security Headers

[![Run on Apify](https://img.shields.io/badge/Run%20on-Apify-1f6feb?logo=apify)](https://apify.com/manageable_gully/website-health-audit) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Run it in the cloud with no setup:** [SEO Audit & Domain Checker: DNS Lookup, SSL, DMARC on the Apify Store](https://apify.com/manageable_gully/website-health-audit).  
> Pay only per result, export to JSON/CSV/Excel, schedule runs and call it from the API.
<!-- AFFILIATE_LINK_PLACEHOLDER: replace the Apify links above with the affiliate link when available -->

Paste a list of domains or URLs and get one row per site with a **0–100 health score** and a plain-English list of what to fix. One run replaces several single-purpose tools: a **technical SEO audit**, a **bulk DNS lookup** (A, AAAA, MX, NS, CAA, SPF, DMARC), an **SSL certificate checker** with days until expiry, a **security headers** check and a redirect checker.

## What you can use it for
- **SEO and web agencies:** run a technical **website audit** on 50 prospect domains before a pitch and paste the fix list into your proposal.
- **IT and DevOps:** schedule a weekly **SSL certificate checker** run and get alerted before a certificate expires (`ssl.daysUntilExpiry`).
- **Email deliverability:** bulk-check **SPF and DMARC records** across all your sending domains, or a client's, in one table.
- **Domain portfolio and due diligence:** a quick **domain checker** for DNS, HTTPS, redirects and basic SEO hygiene across an acquisition target's web estate.
- **Security reviews:** find sites missing HSTS, CSP or X-Frame-Options, and servers that leak `X-Powered-By` versions.

## How to use it
1. Paste your domains or URLs into **Targets** (one per line, up to 10,000).
2. Keep the SSL, DNS and SEO checks on, or turn off what you don't need.
3. Click **Start**. Each site takes about a second.
4. Sort by `score`, filter `issues` by severity, and export to CSV, Excel or Google Sheets.

## What it checks
| Area | Details |
|---|---|
| **SSL / TLS** | Certificate validity, issuer, TLS version, expiry date, **days until expiry**, SANs |
| **DNS & email security** | A, AAAA, MX, NS and CAA records, **SPF** and **DMARC** (via DNS-over-HTTPS) |
| **HTTP** | Final URL, full **redirect chain**, status code, response time, whether the site ends on HTTPS |
| **Security headers** | HSTS, Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and `X-Powered-By` leaks |
| **On-page SEO** | Title and meta description (with lengths), H1s, canonical, viewport, `lang`, Open Graph, images missing alt text, favicon, robots.txt, sitemap.xml |

## Input
```json
{ "targets": ["example.com", "https://shop.example.org/"], "checkSsl": true, "checkDns": true, "checkSeo": true }
```
- `targets`: domains or URLs. Duplicates are removed. Up to 10,000 per run.
- `checkSsl`, `checkDns`, `checkSeo`: turn sections on or off.
- `maxConcurrency` (default 10) and `timeoutSecs` (default 15).

## Output (one item per target)
```json
{
  "input": "example.com", "score": 62, "issueCount": 12,
  "http": {"finalUrl": "https://example.com/", "status": 200, "redirectChain": [{"url": "https://example.com/", "status": 200}], "responseTimeMs": 180},
  "ssl": {"valid": true, "issuer": "SSL Corporation", "tlsVersion": "TLSv1.3", "daysUntilExpiry": 69},
  "dns": {"domain": "example.com", "MX": [], "spf": "v=spf1 -all", "dmarc": "v=DMARC1;p=reject", "CAA": []},
  "securityHeaders": {"missing": ["HSTS", "Content-Security-Policy"]},
  "seo": {"title": "Example Domain", "metaDescription": null, "h1Count": 1},
  "issues": [{"severity": "high", "code": "MISSING_HEADER", "message": "Missing security header: HSTS"}]
}
```
You can download results as JSON, CSV, Excel or HTML, or fetch them through the Apify API, webhooks or integrations (Make, Zapier, n8n, Google Sheets).

**Score:** starts at 100. Each issue subtracts points by severity: critical 30, high 10, medium 5, low 2.

## Good to know
- The Actor only makes ordinary public requests: one page load, robots.txt and sitemap.xml per site, plus DNS and TLS lookups. It never logs in and never crawls deeper.
- Requests to private or internal IP addresses are refused.
- It collects no personal data. DNS records and headers are public technical information.

## Pricing
Pay per event, no monthly rent: **$0.005 per site** (**$5.00 per 1,000**).

| Example | Cost |
|---|---|
| 100 sites | $0.50 |
| 1,000 sites | $5.00 |
| 10,000 sites | $50.00 |

Targets that are invalid or fail to resolve are not charged.

You can set a **maximum cost per run** in the run options; the Actor stops cleanly when it is reached. New to Apify? The free plan includes $5 of platform credit every month, so you can try this Actor at no cost.

## API, integrations and AI agents (MCP)
Run it from your own code with the [Apify API](https://docs.apify.com/api/v2) and get the results in one call:
```bash
curl -X POST "https://api.apify.com/v2/acts/manageable_gully~website-health-audit/run-sync-get-dataset-items?token=<YOUR_APIFY_TOKEN>" \
  -H "Content-Type: application/json" -d @input.json
```
```python
from apify_client import ApifyClient
run = ApifyClient("<YOUR_APIFY_TOKEN>").actor("manageable_gully/website-health-audit").call(run_input={...})
```
- **No-code:** use the Apify app in **n8n, Make or Zapier** ("Run Actor", then "Get dataset items"), or send results to Google Sheets, Slack or a webhook.
- **AI agents (MCP):** add `https://mcp.apify.com?tools=manageable_gully/website-health-audit` to Claude, Cursor, VS Code or any MCP client and the agent can call this Actor as a tool.
- **Schedules:** run it hourly, daily or weekly from Apify Console.

## FAQ
**Can I run a bulk DNS lookup without the SEO checks?** Yes. Turn off `checkSeo` and `checkSsl` to focus on DNS records (A, AAAA, MX, NS, CAA, SPF, DMARC). The price per site stays the same.

**Does it do WHOIS or domain availability?** No. It checks live DNS, SSL, HTTP and on-page signals. It doesn't query WHOIS registries.

**How is this different from a Lighthouse audit?** This is a fast technical and configuration audit (DNS, TLS, headers, metadata). For page speed and Core Web Vitals, use the [Lighthouse & PageSpeed Bulk Audit](https://apify.com/manageable_gully/lighthouse-bulk-audit).

**Is this a full SEO crawler?** No. It checks the landing page of each target. For whole-site link problems, use the [Broken Link Checker](https://apify.com/manageable_gully/broken-link-checker) Actor.

**Why a "low" issue for CAA?** CAA is optional but recommended hardening. Filter on `severity` if you only care about high and critical issues.

**Can AI agents use it?** Yes. It is available as a tool through the Apify MCP server (`https://mcp.apify.com?tools=manageable_gully/website-health-audit`) and the Apify API, and it returns structured JSON that agents can read directly.

## More tools from WebIntel Tools
- [Broken Link Checker](https://apify.com/manageable_gully/broken-link-checker): crawl a site and find every 404, broken image and bad redirect
- [Lighthouse & PageSpeed Bulk Audit](https://apify.com/manageable_gully/lighthouse-bulk-audit): Lighthouse scores and Core Web Vitals for hundreds of URLs
- [Website Tech Stack Detector](https://apify.com/manageable_gully/website-tech-detector): BuiltWith/Wappalyzer-style tech stack lookup in bulk
- [Website Screenshot & URL to PDF](https://apify.com/manageable_gully/url-to-pdf-screenshot): full-page screenshots and PDFs of URLs or your own HTML

See [all WebIntel Tools Actors](https://apify.com/manageable_gully).

*Made by WebIntel Tools. This Actor was built and is maintained with AI assistance. Report issues on the Issues tab; they are monitored daily.*

## Run from source
This repository is the full source of the [SEO Audit & Domain Checker: DNS Lookup, SSL, DMARC](https://apify.com/manageable_gully/website-health-audit) Actor.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest
# run locally with the Apify CLI (https://docs.apify.com/cli):
apify run --input '{...}'
```

Deploy your own copy with `apify push`. The easiest way to use it is the hosted version on the [Apify Store](https://apify.com/manageable_gully/website-health-audit).

<!-- AFFILIATE_LINK_PLACEHOLDER: "New to Apify? Sign up here" link goes here -->

## License
MIT, see [LICENSE](LICENSE).
