# Website SEO Audit & DNS Lookup: SSL, DMARC, Security Headers

[![Run on Apify](https://img.shields.io/badge/Run%20on-Apify-1f6feb?logo=apify)](https://apify.com/manageable_gully/website-health-audit) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Run it in the cloud with no setup:** [Website SEO Audit & DNS Lookup: SSL, DMARC, Headers on the Apify Store](https://apify.com/manageable_gully/website-health-audit).  
> Pay only per result, export to JSON/CSV/Excel, schedule runs and call it from the API.
<!-- Note: the Apify Store page goes live once the Actor is published. -->
<!-- AFFILIATE_LINK_PLACEHOLDER: replace the Apify links above with the affiliate link when available -->

Paste a list of domains or URLs and get one row per site with a **0–100 health score** and a plain-English list of what to fix. One run replaces several single-purpose tools: a **technical SEO audit**, a **bulk DNS lookup** (A, AAAA, MX, NS, CAA, SPF, DMARC), an **SSL certificate checker** with days until expiry, a **security headers** check and a redirect checker.

## What it checks
| Area | Details |
|---|---|
| **SSL / TLS** | Certificate validity, issuer, TLS version, expiry date, **days until expiry**, SANs |
| **DNS & email security** | A, AAAA, MX, NS and CAA records, **SPF** and **DMARC** (via DNS-over-HTTPS) |
| **HTTP** | Final URL, full **redirect chain**, status code, response time, whether the site ends on HTTPS |
| **Security headers** | HSTS, Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, and `X-Powered-By` leaks |
| **On-page SEO** | Title and meta description (with lengths), H1s, canonical, viewport, `lang`, Open Graph, images missing alt text, favicon, robots.txt, sitemap.xml |

## Use cases
- **Agencies:** audit a prospect's or client's sites in bulk and paste the issues into a report.
- **IT / DevOps:** run on a schedule to catch **SSL certificates about to expire** and missing DMARC records.
- **SEO:** a quick technical first pass across many domains.
- **Due diligence:** check the basic hygiene of a vendor's or acquisition target's web estate.

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

## Pricing
Pay per event: **$0.005 per audited target** ($5 per 1,000 sites) for SEO, DNS, SSL and header checks together. Targets that are invalid or fail to resolve are not charged. Set a maximum cost per run in the run options, and the Actor stops cleanly when it reaches it.

## Good to know
- The Actor only makes ordinary public requests: one page load, robots.txt and sitemap.xml per site, plus DNS and TLS lookups. It never logs in and never crawls deeper.
- Requests to private or internal IP addresses are refused.
- It collects no personal data. DNS records and headers are public technical information.

## FAQ
**Is this a full SEO crawler?** No. It checks the landing page of each target. For whole-site link problems, use the companion **Broken Link Checker** Actor.
**Why a "low" issue for CAA?** CAA is optional but recommended hardening. Filter on `severity` if you only care about high and critical issues.

*This Actor was built and is maintained with AI assistance. Report issues on the Issues tab; they are monitored daily.*

## Run from source
This repository is the full source of the [Website SEO Audit & DNS Lookup: SSL, DMARC, Headers](https://apify.com/manageable_gully/website-health-audit) Actor.

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
