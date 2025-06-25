from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
from datetime import datetime
import logging


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        logging.info("do_GET, pr_url: %s", pr_url)
        if pr_url.path == '/':
            self.send_html_file('./front-init/index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('./front-init/message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('./front-init/error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
            logging.info("Content-type %s", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
            logging.info("Content-type ", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        message_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        message_dict ={message_time: data_dict}
        logging.info("Message: %s", message_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    logging.info("Start Server")
    server_address = ('localhost', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
        logging.info("Server close")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(message)s")
    run()
