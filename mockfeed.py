#!/usr/bin/env python3
"""Minimal NuGet v3 mock of a private feed: only a few packages, no upstream passthrough."""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
BASE = f"http://127.0.0.1:{PORT}"
LOG = open(sys.argv[2], "a") if len(sys.argv) > 2 else sys.stderr

# package id (lowercase) -> versions served by this "feed view"
PACKAGES = {
    "autofac": ["6.4.0"],  # what the user saw: only 6.4.0
    "contoso.internal.lib": ["1.2.0", "1.3.0"],
    # newtonsoft.json deliberately missing -> 404 like a package that is not in the view
}


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        LOG.write("%s %s\n" % (self.command, self.path))
        LOG.flush()

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/v3/index.json":
            return self._json(200, {
                "version": "3.0.0",
                "resources": [
                    {"@id": f"{BASE}/v3/registration/", "@type": "RegistrationsBaseUrl/3.6.0"},
                    {"@id": f"{BASE}/v3/flat/", "@type": "PackageBaseAddress/3.0.0"},
                ],
            })
        if p.startswith("/v3/registration/") and p.endswith("/index.json"):
            pid = p[len("/v3/registration/"):-len("/index.json")].lower()
            if pid not in PACKAGES:
                return self._json(404, {"error": "not found"})
            vs = PACKAGES[pid]
            items = [{"catalogEntry": {"version": v, "listed": True}} for v in vs]
            return self._json(200, {
                "count": 1,
                "items": [{
                    "@id": f"{BASE}/v3/registration/{pid}/index.json#page/{vs[0]}/{vs[-1]}",
                    "count": len(vs), "lower": vs[0], "upper": vs[-1], "items": items,
                }],
            })
        if p.startswith("/v3/flat/") and p.endswith("/index.json"):
            pid = p[len("/v3/flat/"):-len("/index.json")].lower()
            if pid not in PACKAGES:
                return self._json(404, {"error": "not found"})
            return self._json(200, {"versions": PACKAGES[pid]})
        return self._json(404, {"error": "not found"})


HTTPServer(("0.0.0.0", PORT), H).serve_forever()
