from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse, mimetypes, pathlib, logging, socket, threading, json, colorama
from datetime import datetime

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
    
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        message_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        message_dict ={message_time: data_dict}
        print("do_POST -> message_dict", colorama.Fore.RED, message_dict, colorama.Fore.RESET)
        logging.info("Message: %s", message_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
        run_client_socket(message_dict)

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
            logging.info("Content-type, text/plain")
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

def run_server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    server = ('localhost', 5000)
    sock.bind(server)
    logging.info('Server_socket is active on: %s', server)
    while True:
        try:
            data, address = sock.recvfrom(1024)
            logging.info('Received data: %s from: %s', data.decode(), address)
            print("run_server_socket -> data", colorama.Fore.RED, data, colorama.Fore.RESET)
            json_data = data.decode()
            print("run_server_socket -> json_data", colorama.Fore.RED, json_data, colorama.Fore.RESET)
            print(json_data)
            save_to_file(json_data)
        except BlockingIOError:
            continue

def save_to_file(data_for_save, path_to_save = './front-init/storage/data.json'):
    print("save_to_file -> data_for_save", colorama.Fore.RED, data_for_save, colorama.Fore.RESET)
    file_for_saving = pathlib.Path(path_to_save)
    with open (file_for_saving, "a", encoding='utf-8') as f:
        f.write(data_for_save + "\n")
        f.close()
    logging.info('Save data: %s to file', data_for_save)


def run_client_socket(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    server = ('localhost', 5000)
    json_data = json.dumps(message, indent=4, ensure_ascii=False)
    print("run_client_socket -> message", colorama.Fore.RED, message, colorama.Fore.RESET)
    print("run_client_socket -> json_data", colorama.Fore.RED, json_data, colorama.Fore.RESET)
    data = json_data.encode()
    print("run_client_socket -> data", colorama.Fore.RED, data, colorama.Fore.RESET)
    try:
        sock.sendto(data, server)
        logging.info('Send data: %s to server: %s', data.decode(), server)
        response, address = sock.recvfrom(1024)
        logging.info('Response data: %s from address: %s', response.decode(), address)
    except BlockingIOError:
            logging.info('BlockingIOError for run_client_socket')
    sock.close()


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
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(threadName)s %(message)s")
    web = threading.Thread(target=run, args=())
    server = threading.Thread(target=run_server_socket, args=())

    server.start()
    web.start()
    
    server.join()
    web.join()