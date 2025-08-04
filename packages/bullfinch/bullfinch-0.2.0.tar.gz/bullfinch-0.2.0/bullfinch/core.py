import http.server
import socketserver
import urllib.parse
import os

_routes = {}

class Bullfinch:
    def __init__(self, name):
        self.name = name
        self.login = "admin"
        self.password = "1234"
        self.port = 8000
        self.debug = True
        self.host = "0.0.0.0"

    def run(self, debug=True, host="0.0.0.0", port=8000):
        self.debug = debug
        self.host = host
        self.port = port
        Handler = self.make_handler()
        with socketserver.TCPServer((host, port), Handler) as httpd:
            print(f"Serving on http://{host}:{port}")
            httpd.serve_forever()

    def make_handler(self):
        login = self.login
        password = self.password

        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/login":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<form method='post'>"
                                     b"Username: <input name='username'><br>"
                                     b"Password: <input name='password' type='password'><br>"
                                     b"<input type='submit'>"
                                     b"</form>")
                    return

                handler = _routes.get(self.path)
                if handler:
                    response = handler()
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(response.encode())
                else:
                    self.send_error(404, "Not Found")

            def do_POST(self):
                if self.path == "/login":
                    content_length = int(self.headers['Content-Length'])
                    body = self.rfile.read(content_length).decode()
                    data = urllib.parse.parse_qs(body)
                    user = data.get("username", [""])[0]
                    pwd = data.get("password", [""])[0]

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    if user == login and pwd == password:
                        self.wfile.write(b"Login successful!")
                    else:
                        self.wfile.write(b"Access Denied")
        return CustomHandler

def file_template(name):
    try:
        with open(f"bullfinch_lite/templates/{name}", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Template not found</h1>"

def password(obj):
    class Setter:
        def __eq__(self, value):
            obj.password = value
    return Setter()

def name(obj):
    class Setter:
        def __eq__(self, value):
            obj.login = value
    return Setter()
