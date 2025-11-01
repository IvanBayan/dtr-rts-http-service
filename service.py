#!/usr/bin/env python3
import json
import os
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import serial

# === Parse command line and environment variables ===
parser = argparse.ArgumentParser(description="Serial line HTTP server")
parser.add_argument("--port", help="Serial port device")
parser.add_argument("--http-port", type=int, help="HTTP server port")
args = parser.parse_args()

SERIAL_PORT = args.port or os.environ.get("PORT", "/dev/ttyS0")
HTTP_PORT = args.http_port or int(os.environ.get("HTTP_PORT", "8080"))
BAUDRATE = 9600  # Baudrate doesn’t matter for DTR/RTS

# === Initialize serial port ===
# script should keep port open to make it work.
ser = serial.Serial(SERIAL_PORT, BAUDRATE)
print(f"Opened serial port {SERIAL_PORT}")

# === HTTP Request Handler ===
class SerialRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _get_status(self, line_type):
        if line_type == "dtr":
            return "ON" if ser.dtr else "OFF"
        elif line_type == "rts":
            return "ON" if ser.rts else "OFF"

    def _handle_action(self, line_type, action):
        if line_type == "dtr":
            if action == "on":
                ser.setDTR(True)
            elif action == "off":
                ser.setDTR(False)
            status = self._get_status("dtr")
        elif line_type == "rts":
            if action == "on":
                ser.setRTS(True)
            elif action == "off":
                ser.setRTS(False)
            status = self._get_status("rts")
        else:
            self._send_json({"error": "Invalid endpoint"}, 404)
            return
        self._send_json({"result": status})

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        action = params.get("action", [None])[0]

        if action != "status":
            self._send_json({"error": "Invalid action"}, 400)
            return

        if parsed.path == "/dtr":
            status = self._get_status("dtr")
        elif parsed.path == "/rts":
            status = self._get_status("rts")
        else:
            self._send_json({"error": "Invalid endpoint"}, 404)
            return

        self._send_json({"result": status})

    def do_POST(self):
        parsed = urlparse(self.path)

        # Read body and query parameters
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        body_params = parse_qs(body)
        query_params = parse_qs(parsed.query)

        # Merge body and query params (body overrides)
        action = body_params.get("action", query_params.get("action", [None]))[0]

        if action not in ["on", "off"]:
            self._send_json({"error": f"Invalid or missing action {action}"}, 400)
            return

        if parsed.path == "/dtr":
            self._handle_action("dtr", action)
        elif parsed.path == "/rts":
            self._handle_action("rts", action)
        else:
            self._send_json({"error": f"Invalid endpoint {parsed.path}"}, 404)

# === Run HTTP server ===
def run_server():
    ser.setDTR(False)
    ser.setRTS(False)
    server = HTTPServer(("", HTTP_PORT), SerialRequestHandler)
    print(f"HTTP server running on port {HTTP_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        ser.setDTR(False)
        ser.setRTS(False)
        ser.close()
        server.server_close()
        print("Serial port closed, server stopped.")

if __name__ == "__main__":
    ser.setDTR(False)
    ser.setRTS(False)
    run_server()

