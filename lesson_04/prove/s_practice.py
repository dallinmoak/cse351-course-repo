from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import time, json, random

class SlowHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        item_id = self.path.lstrip("/")
        time.sleep(0.1)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"item": item_id}).encode())

if __name__ == "__main__":
    server = ThreadingHTTPServer(("localhost", 8080), SlowHandler)
    print("Threaded server running on http://localhost:8080")
    server.serve_forever()
