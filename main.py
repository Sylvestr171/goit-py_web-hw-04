from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        print(">>>>> ", pr_url.path)
        if pr_url.path == '/':
            self.send_html_file('./front-init/index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('./front-init/message.html')
        else:
            self.send_html_file('./front-init/error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('localhost', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run()
