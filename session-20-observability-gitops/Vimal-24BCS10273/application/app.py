#!/usr/bin/env python3
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,os,threading,time,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path

counts=Counter();lock=threading.Lock()
def version():return Path('/config/version').read_text().strip()
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        started=time.monotonic();path=self.path.split('?')[0]
        trace=uuid.uuid4().hex
        status=200;kind='application/json'
        if path=='/metrics':
            kind='text/plain; version=0.0.4'
            with lock:samples=list(counts.items())
            rss=int(Path('/proc/self/statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')
            lines=['# TYPE lab_http_requests_total counter']
            lines += [f'lab_http_requests_total{{path="{p}",status="{s}"}} {n}' for (p,s),n in samples]
            lines += ['# TYPE lab_process_cpu_seconds_total counter',f'lab_process_cpu_seconds_total {time.process_time()}',
                      '# TYPE lab_process_resident_memory_bytes gauge',f'lab_process_resident_memory_bytes {rss}',
                      '# TYPE lab_application_up gauge','lab_application_up 1',
                      '# TYPE lab_build_info gauge',f'lab_build_info{{version="{version()}"}} 1']
            body=('\n'.join(lines)+'\n').encode()
        else:
            if path=='/work':hashlib.pbkdf2_hmac('sha256',b'assignment',b'load',100000)
            elif path=='/fail':status=503
            elif path not in ['/','/healthz']:status=404
            body=json.dumps({'application':'Release Monitor','student':'Vimal Kumar Yadav','version':version(),'status':status,'request_id':trace}).encode()
        self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)));self.send_header('X-Request-ID',trace);self.end_headers();self.wfile.write(body)
        with lock:counts[(path if path in ['/','/healthz','/metrics','/work','/fail'] else '/unknown',str(status))]+=1
        if path!='/healthz':print(json.dumps({'timestamp':datetime.now(timezone.utc).isoformat(),'request_id':trace,'path':path,'status':status,'duration_seconds':round(time.monotonic()-started,6)}),flush=True)
    def log_message(self,*args):pass
ThreadingHTTPServer(('0.0.0.0',8000),Handler).serve_forever()
