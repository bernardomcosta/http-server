import base64
import json
import hashlib
import http.server
import socketserver

# HTTP handler class
# Promotes the connection to WebSocket if endpoint is "/ws"
class WebSocketHandler(http.server.BaseHTTPRequestHandler):
    WEBSOCKET_KEY = "Sec-WebSocket-Key"
    
    # Generates a WebSocketAccept header value
    # Returns: A base64 encoded WebSocketAccept value, based on the given key
    def _generateWebSocketAccept(self, key):
        hash = hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode('utf-8'))
        return base64.b64encode(hash.digest())

    # Generates headers for WebSocket handshake response
    # Arguments: Dictonary with the request headers
    # Response: Headers for the response of the WebSocket handshake
    def _generateHeaders(self, requestHeaders):
        if self.WEBSOCKET_KEY not in requestHeaders:
            raise

        headers = {"Upgrade" : "websocket",
                    "Connection" : "Upgrade",
                    "Sec-WebSocket-Accept" : self._generateWebSocketAccept(requestHeaders[self.WEBSOCKET_KEY])}

        return headers

    # Override of the GET handler
    def do_GET(self):

        if self.path == "/ws":
            try:
                headers = self._generateHeaders(self.headers)
            except Exception as ex:
                self.send_response(400)
                self.end_headers()
            else:
                for k, v in headers.items():
                    self.send_header(k, v)
            
                self.send_response(101)
                self.end_headers()

                message = json.dumps({"status" : "success"})

                self.wfile.write(bytearray(message, encoding="utf-8")) 
       
        else:
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
