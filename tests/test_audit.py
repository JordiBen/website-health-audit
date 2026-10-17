import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from src.audit import (AuditOptions, analyze_security_headers, analyze_seo, audit_target, normalize_target,
                       registrable_domain, score_and_issues)
from src.main import parse_input
from src.netguard import BlockedAddressError, assert_public_url

GOOD_HTML = """<!doctype html><html lang="en"><head><title>Acme Widgets - Fast reliable widgets</title>
<meta name="description" content="Acme sells fast, reliable widgets for small businesses, shipped worldwide within two days.">
<meta name="viewport" content="width=device-width"><link rel="canonical" href="/home">
<meta property="og:title" content="Acme"><link rel="icon" href="/f.ico"></head>
<body><h1>Widgets</h1><img src="a.png" alt="a"><img src="b.png"></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path == '/':
            self.send_response(301); self.send_header('Location', '/home'); self.end_headers(); return
        if self.path == '/home':
            body = GOOD_HTML.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Powered-By', 'PHP/7.4')
            self.end_headers(); self.wfile.write(body); return
        if self.path == '/robots.txt':
            self.send_response(200); self.end_headers(); self.wfile.write(b'User-agent: *\nSitemap: http://x/sitemap.xml\n'); return
        self.send_response(404); self.end_headers()


@pytest.fixture(scope='module')
def server():
    srv = ThreadingHTTPServer(('127.0.0.1', 0), H)
    t = threading.Thread(target=srv.serve_forever, daemon=True); t.start()
    yield f'http://127.0.0.1:{srv.server_address[1]}'
    srv.shutdown()


def test_normalize_target():
    assert normalize_target('Example.com') == 'https://example.com/'
    assert normalize_target('http://a.bc/x?y=1') == 'http://a.bc/x?y=1'
    with pytest.raises(ValueError):
        normalize_target('ftp://x')
    with pytest.raises(ValueError):
        normalize_target('   ')
    with pytest.raises(ValueError):
        normalize_target('not a domain!!')
    assert normalize_target('http://127.0.0.1:8080/') == 'http://127.0.0.1:8080/'


def test_registrable_domain():
    assert registrable_domain('www.example.co.il') == 'example.co.il'
    assert registrable_domain('shop.example.com') == 'example.com'
    assert registrable_domain('example.co.uk') == 'example.co.uk'


def test_seo_parse():
    s = analyze_seo(GOOD_HTML, 'https://acme.test/')
    assert s['title'].startswith('Acme') and s['h1Count'] == 1 and s['lang'] == 'en'
    assert s['canonical'] == 'https://acme.test/home'
    assert s['imagesMissingAlt'] == 1 and s['openGraph']['title'] == 'Acme' and s['favicon']


def test_security_headers():
    r = analyze_security_headers({'Strict-Transport-Security': 'max-age=1', 'X-Powered-By': 'Express'})
    assert 'HSTS' in r['present'] and 'Content-Security-Policy' in r['missing'] and r['xPoweredBy'] == 'Express'


def test_scoring_flags_critical():
    score, issues = score_and_issues({'http': {'error': 'ConnectError'}, 'ssl': {'valid': False, 'error': 'x'}})
    codes = {i['code'] for i in issues}
    assert {'UNREACHABLE', 'SSL_INVALID'} <= codes and score == 40


def test_scoring_email_security():
    _, issues = score_and_issues({'dns': {'MX': ['10 mx.x'], 'spf': None, 'dmarc': None, 'CAA': []}})
    codes = {i['code'] for i in issues}
    assert {'NO_SPF', 'NO_DMARC', 'NO_CAA'} <= codes


def test_ssrf_guard_blocks_private():
    for u in ('http://127.0.0.1/', 'http://10.0.0.5/', 'http://169.254.169.254/latest/meta-data', 'file:///etc/passwd'):
        with pytest.raises(BlockedAddressError):
            asyncio.run(assert_public_url(u))


def test_audit_local_server(server):
    opts = AuditOptions(check_dns=False, check_ssl=False, allow_private=True, timeout_s=5)
    r = asyncio.run(audit_target(server, opts))
    assert r['http']['status'] == 200 and r['http']['finalUrl'].endswith('/home')
    assert len(r['http']['redirectChain']) == 2
    assert r['robotsTxt']['found'] and r['robotsTxt']['sitemaps'] == ['http://x/sitemap.xml']
    assert not r['sitemap']['found']
    codes = {i['code'] for i in r['issues']}
    assert 'NO_HTTPS_REDIRECT' in codes and 'TECH_DISCLOSURE' in codes and 'IMG_ALT' in codes
    assert 'NO_SITEMAP' not in codes  # declared in robots.txt
    assert 0 <= r['score'] < 100


def test_audit_refuses_private_by_default(server):
    r = asyncio.run(audit_target(server, AuditOptions(check_dns=False, check_ssl=False)))
    assert 'non-public' in r['http']['error'] and r['issues'][0]['code'] == 'UNREACHABLE'


def test_parse_input_dedup_and_limits():
    t, o, c = parse_input({'targets': ['a.com', 'https://a.com/', ' ', 'b.com'], 'maxConcurrency': 999})
    assert t == ['a.com', 'b.com'] and c == 50
    with pytest.raises(ValueError):
        parse_input({'targets': []})


@pytest.mark.skipif(os.environ.get('SKIP_NETWORK') == '1', reason='network disabled')
def test_live_example_com():
    # allow_private only because this sandbox's resolver returns 198.18.x proxy IPs; on Apify it's real DNS
    r = asyncio.run(audit_target('example.com', AuditOptions(timeout_s=15, allow_private=True)))
    assert r['http']['status'] == 200
    assert r['ssl']['valid'] and r['ssl']['daysUntilExpiry'] > 0
    assert r['dns']['A'] and r['dns']['NS']


@pytest.mark.skipif(os.environ.get('SKIP_NETWORK') == '1', reason='network disabled')
def test_live_doh_email_records():
    from src.audit import check_dns
    d = asyncio.run(check_dns('google.com'))
    assert d['MX'] and d['spf'].startswith('v=spf1') and d['dmarc'].startswith('v=DMARC1')


@pytest.mark.skipif(os.environ.get('SKIP_NETWORK') == '1', reason='network disabled')
def test_live_expired_cert():
    from src.audit import check_ssl
    r = asyncio.run(check_ssl('expired.badssl.com'))
    assert r['valid'] is False and 'expired' in r['error']
