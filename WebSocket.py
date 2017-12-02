import http.server
import socketserver

# HTTP handler class
class WebSocketHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):

        message_parts = [
                "CLIENT VALUES:",
                "client_address=%s (%s)" % (self.client_address,
                                            self.address_string()),
                "command=%s" % self.command,
                "path=%s" % self.path,
                "request_version=%s" % self.request_version,
                "",
                "SERVER VALUES:",
                "server_version=%s" % self.server_version,
                "sys_version=%s" % self.sys_version,
                "protocol_version=%s" % self.protocol_version,
                "",
                "HEADERS RECEIVED:",
                ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')
        message = "\r\n".join(message_parts)
        self.send_response(200)
        self.end_headers()

        self.wfile.write(bytearray(message, encoding="utf-8"))
        return

# Main program
PORT = 8000

Handler = WebSocketHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
