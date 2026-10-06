"""Local storage/HPA lab server; /work deliberately consumes CPU."""
import hashlib
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import time

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status = 200
        if self.path == '/healthz':
            status = 503 if Path('/tmp/unhealthy').exists() else 200
            body = 'health check\n'
        elif self.path == '/readyz':
            status = 503 if Path('/tmp/unready').exists() else 200
            body = 'readiness check\n'
        elif self.path == '/work':
            hashlib.pbkdf2_hmac('sha256', b'assignment-load', b'local-lab', 50000)
            body = 'work complete\n'
        elif self.path == '/':
            saved = Path('/data/student.txt')
            student = saved.read_text() if saved.exists() else 'No record written yet'
            body = ('<!doctype html><title>Storage lab</title><h1>Session 13 storage lab</h1>'
                    '<p>' + html.escape(student) + '</p><p>Pod: ' + socket.gethostname() + '</p>')
        else:
            status, body = 404, 'not found\n'
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, fmt, *args):
        # Avoid filling the log with health checks and load-generator requests.
        if self.path not in ('/healthz', '/readyz', '/work'):
            super().log_message(fmt, *args)

time.sleep(8)  # Startup probe gives initialization time before other checks run.
print('Listening on 0.0.0.0:8080 after initialization', flush=True)
ThreadingHTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
