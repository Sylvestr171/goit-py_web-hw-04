"Модуля 4. Д/з Веб застосунок"

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, unquote_plus
from mimetypes import guess_type
from pathlib import Path
from logging import info, basicConfig, DEBUG
from socket import socket, AF_INET, SOCK_DGRAM
from threading import Thread
from json import dumps
from datetime import datetime
from typing import Self, Type
from colorama import Fore


class HttpHandler(BaseHTTPRequestHandler):

    """Клас обробника HTTP-запитів"""

    def do_get(self: Self) -> None:

        """Обробляє GET-запит HTTP-клієнта."""

        pr_url = urlparse(self.path)
        info("do_GET, pr_url: %s", pr_url)
        if pr_url.path == '/':
            self.send_html_file('./front-init/index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('./front-init/message.html')
        else:
            if Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('./front-init/error.html', 404)


    def do_post(self: Self) -> None:

        """Обробляє POST-запит HTTP-клієнта."""

        data = self.rfile.read(int(self.headers['Content-Length']))
        message_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        data_parse = unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        message_dict ={message_time: data_dict}
        print("do_POST -> message_dict", Fore.RED, message_dict, Fore.RESET)
        info("Message: %s", message_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
        run_client_socket(message_dict)

    def send_html_file(self: Self, filename: str, status: int=200) -> None:

        """Відправник HTML-файлів."""

        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self: Self) -> None:

        """Відправник статичних-файлів."""

        self.send_response(200)
        mt = guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
            info("Content-type %s", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
            info("Content-type, text/plain")
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

def run_server_socket() -> None:

    """
    Сервер сокет.
    Отримує дані та пише їх в файл
    """

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setblocking(False)
    server_socket_ip_port = ('localhost', 5000)
    sock.bind(server_socket_ip_port)
    info('Server_socket is active on: %s', server_socket_ip_port)
    while True:
        try:
            data, address = sock.recvfrom(1024)
            info('Received data: %s from: %s', data.decode(), address)
            print("run_server_socket -> data", Fore.RED, data, Fore.RESET)
            json_data = data.decode()
            print("run_server_socket -> json_data", Fore.RED, json_data, Fore.RESET)
            print(json_data)
            save_to_file(json_data)
        except BlockingIOError:
            continue

def save_to_file(data_for_save: str, path_to_save: str = './front-init/storage/data.json'):

    """Функція запису даних в файл"""

    print("save_to_file -> data_for_save", Fore.RED, data_for_save, Fore.RESET)
    file_for_saving = Path(path_to_save)
    with open (file_for_saving, "a", encoding='utf-8') as f:
        f.write(data_for_save + "\n")
        f.close()
    info('Save data: %s to file', data_for_save)


def run_client_socket(message: dict[str, dict[str, str]]):

    """
    Клієнтський сокет.
    Забирає данні з форми, формує JSON рядок та
    предає на сервер-сокет
    """

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setblocking(False)
    client_socket_ip_port = ('localhost', 5000)
    json_data = dumps(message, indent=4, ensure_ascii=False)
    print("run_client_socket -> message", Fore.RED, message, Fore.RESET)
    print("run_client_socket -> json_data", Fore.RED, json_data, Fore.RESET)
    data = json_data.encode()
    print("run_client_socket -> data", Fore.RED, data, Fore.RESET)
    try:
        sock.sendto(data, client_socket_ip_port)
        info('Send data: %s to server: %s', data.decode(), client_socket_ip_port)
        response, address = sock.recvfrom(1024)
        info('Response data: %s from address: %s', response.decode(), address)
    except BlockingIOError:
        info('BlockingIOError for run_client_socket')
    sock.close()


def run(server_class: Type[HTTPServer] =HTTPServer,
        handler_class: Type[HttpHandler]=HttpHandler
        ) -> None:

    """Запуск Веб-сервер"""

    info("Start Server")
    server_address = ('localhost', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
        info("Server close")


if __name__ == '__main__':
    basicConfig(level=DEBUG, format="%(asctime)s %(threadName)s %(message)s")
    web = Thread(target=run, args=())
    server = Thread(target=run_server_socket, args=())

    server.start()
    web.start()
    server.join()
    web.join()
