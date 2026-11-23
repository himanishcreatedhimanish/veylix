import json, sys, os
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(__file__))
from risk_engine import evaluate
from url_analyzer import extract_url

CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload=None):
        self.send_response(status)
        for k, v in CORS.items():
            self.send_header(k, v)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if payload is not None:
            self.wfile.write(json.dumps(payload).encode())

    def do_OPTIONS(self):
        self._send(204)

    def do_GET(self):
        self._send(405, {"error": "Method not allowed"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._send(400, {"error": "Invalid JSON"})
        url = body.get("url")
        message = body.get("message")
        if message:
            url = extract_url(message)
            if not url:
                return self._send(200, {"error": "no_url", "message": "No URL found in the message."})
        if not url:
            return self._send(400, {"error": "Provide 'url' or 'message' in request body."})
        self._send(200, evaluate(url))
