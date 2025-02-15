import http.server
import socketserver
import base64
import configparser
import json

config = configparser.ConfigParser()
config.read("config.ini")


HOST = config["Client-server_app"]["host"]
PORT = int(config["Client-server_app"]["port"])
MAX_AGE = config["Client-server_app"]["max-age"]


class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def _send_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Cache-Control', f'max-age={MAX_AGE}')
        self.end_headers()
        self.wfile.write(json.dumps(message).encode())

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="TestRealm"')
        self.end_headers()

    def do_GET(self):
        if not self.is_authenticated():
            self.do_AUTHHEAD()
            self._send_response(401, {"error": "Unauthorized"})
            return

        response_message = {"message": f"GET request for {self.path}"}
        self._send_response(200, response_message)

    def do_POST(self):
        if not self.is_authenticated():
            self.do_AUTHHEAD()
            self._send_response(401, {"error": "Unauthorized"})
            return

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()
        response_message = {"message": f"POST request for {self.path} with data: {post_data}"}
        self._send_response(200, response_message)

    def do_PUT(self):
        if not self.is_authenticated():
            self.do_AUTHHEAD()
            self._send_response(401, {"error": "Unauthorized"})
            return

        content_length = int(self.headers['Content-Length'])
        put_data = self.rfile.read(content_length).decode()
        response_message = {"message": f"PUT request for {self.path} with data: {put_data}"}
        self._send_response(200, response_message)

    def do_DELETE(self):
        if not self.is_authenticated():
            self.do_AUTHHEAD()
            self._send_response(401, {"error": "Unauthorized"})
            return

        response_message = {"message": f"DELETE request for {self.path}"}
        self._send_response(200, response_message)

    def is_authenticated(self):
        auth_header = self.headers.get('Authorization')
        if auth_header is None:
            return False

        auth_type, credentials = auth_header.split(' ', 1)
        if auth_type.lower() != 'basic':
            return False

        decoded_credentials = base64.b64decode(credentials).decode()
        username, password = decoded_credentials.split(':', 1)

        return username == 'user' and password == 'password'


with socketserver.TCPServer((HOST, PORT), MyRequestHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
