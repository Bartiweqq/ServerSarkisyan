import socket
import sys
import urllib.parse
import msvcrt
import select
def http_client(url):
    # Парсинг URL для получения хоста, порта и пути
    parsed_url = urllib.parse.urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or 80
    path = parsed_url.path or "/"

    # Создание клиентского сокета и соединение с сервером
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Формирование HTTP-запроса
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    client_socket.sendall(request.encode())

    data_buffer = ""
    output_lines = 0

    while True:
        readable, _, _ = select.select([client_socket], [], [], 1)

        for s in readable:
            if s is client_socket:
                # Чтение данных от сервера
                data = s.recv(4096).decode()
                if data:
                    data_buffer += data
                    # Вывод данных построчно
                    while '\n' in data_buffer:
                        line, data_buffer = data_buffer.split('\n', 1)
                        print(line)
                        output_lines += 1
                        if output_lines >= 25:
                            print("Press space to scroll down.")
                            output_lines = 0
                            # Ожидание нажатия пробела для продолжения
                            while True:
                                if msvcrt.kbhit() and msvcrt.getch() == b' ':
                                    break
                else:
                    # Закрытие соединения при получении пустых данных
                    client_socket.close()
                    return

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <URL>")
        sys.exit(1)

    url = sys.argv[1]
    http_client(url)

#python 28.py http://example.com
