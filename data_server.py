# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import manga_data
import json

HOSTNAME = "localhost"
SERVERPORT = 8080
webServer = None

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(manga_data.data_list).encode('utf-8'))

def start_server(address=None, port=None, thread=True):
    global webServer
    address = address or HOSTNAME
    port = port or SERVERPORT
    if webServer is not None:
        stop_server()

    if thread:
        t = threading.Thread(target=start_server, args=(address, port, False), name='Data server')
        t.start()
        return t

    webServer = HTTPServer((address, port), MyServer)
    print("Server started http://%s:%s" % (address, port))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f'ERROR on data server: {type(e)} - {str(e)}')

def stop_server():
    global webServer
    if webServer is not None:
        webServer.server_close()
    print("Server stopped.")
    webServer = None

if __name__ == "__main__":
    start_server()
    stop_server()