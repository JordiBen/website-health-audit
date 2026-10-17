"""Apify entrypoint: bulk website & domain health audit (SSL, DNS, security headers, redirects, on-page SEO)."""
from __future__ import annotations

import asyncio
import os

import httpx
from apify import Actor

from .audit import USER_AGENT, AuditOptions, audit_target, normalize_target

EVENT = 'domain-audited'
MAX_TARGETS = 10_000


def parse_input(inp: dict) -> tuple[list[str], AuditOptions, int]:
    raw = list(inp.get('targets') or [])
    raw += [s.get('url') for s in (inp.get('startUrls') or []) if isinstance(s, dict) and s.get('url')]
    seen, targets = set(), []
    for t in raw:
        t = (t or '').strip()
        if not t:
            continue
        try:
            key = normalize_target(t)
        except ValueError:
            key = t
        if key not in seen:
            seen.add(key)
            targets.append(t)
    if not targets:
        raise ValueError('Provide at least one domain or URL in "targets".')
    if len(targets) > MAX_TARGETS:
        raise ValueError(f'At most {MAX_TARGETS} targets per run.')
    opts = AuditOptions(check_dns=bool(inp.get('checkDns', True)), check_ssl=bool(inp.get('checkSsl', True)),
                        check_seo=bool(inp.get('checkSeo', True)),
                        timeout_s=float(min(max(inp.get('timeoutSecs', 15), 3), 60)))
    concurrency = int(min(max(inp.get('maxConcurrency', 10), 1), 50))
    return targets, opts, concurrency


async def main() -> None:
    async with Actor:
        inp = await Actor.get_input() or {}
        try:
            targets, opts, concurrency = parse_input(inp)
        except ValueError as e:
            await Actor.fail(status_message=str(e))
            return
        # Local-dev escape hatch for sandboxes whose resolver returns proxy IPs. Ignored on the Apify platform.
        if os.environ.get('ALLOW_PRIVATE_NETWORK_FOR_LOCAL_DEV') == '1' and not Actor.is_at_home():
            opts.allow_private = True
        Actor.log.info(f'Auditing {len(targets)} target(s) with concurrency {concurrency}')
        sem = asyncio.Semaphore(concurrency)
        stop = asyncio.Event()
        done = 0

        async with httpx.AsyncClient(timeout=opts.timeout_s, headers={'User-Agent': USER_AGENT},
                                     verify=False, limits=httpx.Limits(max_connections=concurrency * 2)) as client:
            async def work(t: str) -> None:
                nonlocal done
                async with sem:
                    if stop.is_set():
                        return
                    try:
                        result = await audit_target(t, opts, client)
                    except Exception as e:  # noqa: BLE001 - one bad target must not kill the run
                        result = {'input': t, 'error': f'{type(e).__name__}: {e}'[:300], 'score': None}
                    # Only successfully produced reports are charged; invalid input rows are free.
                    charge = EVENT if 'error' not in result else None
                    if stop.is_set():
                        return
                    res = await Actor.push_data(result, charged_event_name=charge)
                    if not (charge and res.charged_count == 0 and res.event_charge_limit_reached):
                        done += 1
                    if res.event_charge_limit_reached:
                        stop.set()
                    if done % 25 == 0:
                        await Actor.set_status_message(f'Audited {done}/{len(targets)}')

            await asyncio.gather(*(work(t) for t in targets))
        msg = f'Done: {done}/{len(targets)} targets saved' + (' (stopped: max charge reached)' if stop.is_set() else '')
        await Actor.set_status_message(msg, is_terminal=True)
