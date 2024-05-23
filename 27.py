import socket
import select
import sys

def main():
    # Проверка наличия всех необходимых аргументов командной строки
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <listening_port> <target_host> <target_port>")
        sys.exit(1)

    # Получение параметров из командной строки
    listening_port = int(sys.argv[1])
    target_host = sys.argv[2]
    target_port = int(sys.argv[3])

    # Создание серверного сокета для прослушивания входящих соединений
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', listening_port))
    server_socket.listen(5)
    server_socket.setblocking(False)

    print(f"Proxy server listening on port {listening_port}")

    # Списки для мониторинга сокетов
    inputs = [server_socket]
    outputs = []
    connections = {}

    while True:
        # Использование select для мониторинга сокетов
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        # Обработка входящих соединений
        for s in readable:
            if s is server_socket:
                # Принятие нового клиентского соединения
                client_socket, client_address = s.accept()
                client_socket.setblocking(False)
                inputs.append(client_socket)

                # Создание соединения с целевым сервером
                target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    target_socket.connect((target_host, target_port))
                    target_socket.setblocking(False)
                    inputs.append(target_socket)
                    connections[client_socket] = target_socket
                    connections[target_socket] = client_socket
                except Exception as e:
                    print(f"Could not connect to target server: {e}")
                    client_socket.close()

            else:
                # Чтение данных от клиента или сервера
                data = s.recv(4096)
                if data:
                    # Пересылка данных между клиентом и сервером
                    connections[s].sendall(data)
                else:
                    # Закрытие соединений при получении пустых данных
                    inputs.remove(s)
                    inputs.remove(connections[s])
                    connections[s].close()
                    s.close()
                    del connections[s]

        # Обработка исключительных состояний
        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            if s in connections:
                inputs.remove(connections[s])
                connections[s].close()
                del connections[s]

if __name__ == "__main__":
    main()

# Запуск: python 27.py 8888 example.com 80
# Пример использования: curl -x localhost:8888 http://example.com
