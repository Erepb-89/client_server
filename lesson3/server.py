"""Программа-сервер"""
import argparse
import socket
import sys
import json
import logging
from log.config import server_log_config
from errors import IncorrectDataRecivedError
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, AUTHENTICATE
from common.utils import get_message, send_message

# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server')


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


def create_arg_parser():
    """
    Парсер аргументов коммандной строки
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    return parser


def main():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Сначала обрабатываем порт:
    server.py -p 8888 -a 127.0.0.1
    :return:
    '''
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(
            f'{listen_port} В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}. '
                       f'Если адрес не указан, принимаются соединения с любых адресов.')

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
                SERVER_LOGGER.info(f'Установлено соедение с ПК {client_ip}')
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
                    SERVER_LOGGER.debug(f'Получено сообщение {message_from_client}')
                    response = handle(message_from_client)
                    SERVER_LOGGER.info(f'Cформирован ответ клиенту {response}')
                    send_message(client, response)
                    SERVER_LOGGER.debug(f'Соединение с клиентом {client_ip} закрывается.')
                except json.JSONDecodeError:
                    SERVER_LOGGER.error(f'Не удалось декодировать JSON строку, полученную от '
                                        f'клиента {client_ip}. Соединение закрывается.')
                    client.close()
                except IncorrectDataRecivedError:
                    SERVER_LOGGER.error(f'От клиента {client_ip} приняты некорректные данные. '
                                        f'Соединение закрывается.')
                    client.close()


if __name__ == "__main__":
    main()
