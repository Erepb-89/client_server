"""Программа-сервер"""

import socket
import sys
import time
import json
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, AUTHENTICATE, PASSWORD, RESPONSE_402, PROBE, IP_ADDRESS, PORT
from common.utils import get_message, send_message


def handle(message):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клиента, проверяет корректность,
    возвращает словарь-ответ для клиента

    :param message:
    :return:
    '''
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }
    # elif ACTION in message and message[ACTION] == AUTHENTICATE and USER in message and \
    #         (message[USER][ACCOUNT_NAME] != 'erepb' or message[USER][PASSWORD] != "123456"):
    #     return {
    #         RESPONSE: 402,
    #         ERROR: RESPONSE_402
    #     }


def main():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Сначала обрабатываем порт:
    server.py -p 8888 -a 127.0.0.1
    :return:
    '''

    try:
        listen_port = int(sys.argv[sys.argv.index(PORT) + 1]) if PORT in sys.argv else DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        print('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        print('В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Затем загружаем какой адрес слушать

    try:
        listen_address = sys.argv[sys.argv.index(IP_ADDRESS) + 1] if IP_ADDRESS in sys.argv else ''

    except IndexError:
        print('После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    # создаем сокет AF_INET - IPv4, AF_INET6 - IPv6, SOCK_STREAM - сокет TCP, SOCK_DGRAM - сокет UDP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # биндим адрес и порт
        sock.bind((listen_address, listen_port))
        # Слушаем порт, указываем максимальное количество соединений (очередь, пока не обработает первое соединение
        # - до закрытия)
        sock.listen(MAX_CONNECTIONS)
        # Устанавливаем неблокирующий режим
        sock.setblocking(False)
        # Устанавливаем SO_REUSEADDR в 1 для переиспользования того же порта
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        while True:
            # accept - принимает клиента из очереди (кортеж из сокета клиента и его адреса/порта) - при его наличии,
            # если очередь пуста - ожидает клиента
            try:
                client, client_ip = sock.accept()
                print(client_ip)
            except socket.error:
                # print('No clients')
                pass
            except KeyboardInterrupt:
                sock.close()
                break
            else:
                try:
                    client.setblocking(True)
                    message_from_client = get_message(client)
                    print(message_from_client)
                    response = handle(message_from_client)
                    send_message(client, response)
                except (ValueError, json.JSONDecodeError):
                    print('Принято некорретное сообщение от клиента.')


if __name__ == '__main__':
    main()
