from http.server import BaseHTTPRequestHandler, HTTPServer
from bot import Client
from http.cookies import SimpleCookie

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
            return

        if self.path == "/":
            # check for cookies
            cookie = SimpleCookie(self.headers.get("Cookie"))
            if "user" not in cookie:
                self._200("<h1>Welcome to the website!</h1>")
                return

            FINAL = "<h1>Users:</h1>"
            for user in self.client.GUILD.members:
                if user.bot:
                    continue
                color = "000"
                status = user.status.name
                if status == "online":
                    color = "0f0"
                elif status == "idle":
                    color = "ff0"
                elif status == "dnd":
                    color = "f00"
                FINAL += f"<p><b>{user.display_name}</b>: is <font color='#{color}'>{status}</font></p>"

            self._200(FINAL)


def run_website(client: Client):
    server_address = ("0.0.0.0", PORT)
    Website.client = client
    httpd = HTTPServer(server_address, Website)
    httpd.serve_forever()
