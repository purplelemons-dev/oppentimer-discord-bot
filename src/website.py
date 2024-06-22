from http.server import BaseHTTPRequestHandler, HTTPServer
from bot import Client

PORT = 10023


class Website(BaseHTTPRequestHandler):
    client: Client

    def _200(self, content: str):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def _500(self, content: str):
        self.send_response(500)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

    def do_GET(self):
        if self.client.has_loaded is False:
            self._500("Bot has not loaded yet")

        FINAL = "<h1>Users:</h1>"
        for user in self.client.GUILD.members:
            FINAL += f"<p><b>{user.name}</b>: is {user.status}</p>"

        self._200(FINAL)


def run_website(client: Client):
    server_address = ("0.0.0.0", PORT)
    Website.client = client
    httpd = HTTPServer(server_address, Website)
    httpd.serve_forever()
