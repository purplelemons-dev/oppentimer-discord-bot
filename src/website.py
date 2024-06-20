
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 10023

class Website(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Hello, world!')


def run_website():
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, Website)
    httpd.serve_forever()
