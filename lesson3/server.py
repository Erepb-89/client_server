"""Программа-сервер"""
import argparse
import socket
import sys
import json
import time
import select
import logging
from decorators import log
from log.config import server_log_config
from errors import IncorrectDataRecivedError
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, AUTHENTICATE, MESSAGE, MESSAGE_TEXT, SENDER, EXIT, TARGET
from common.utils import get_message, send_message

# Инициализация логирования сервера.
SERVER_LOGGER = logging.getLogger('server')


@log
def handle(message, messages_list, client, clients, names):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клинта,
    проверяет корректность, отправляет словарь-ответ для клиента с результатом приёма.
    :param names:
    :param clients:
    :param message:
    :param messages_list:
    :param client:
    :return:
    """
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    # Если это сообщение о присутствии, принимаем и отвечаем
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        # Если это новый пользователь, регистрируем
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: 200})
        # Иначе отправляем ошибку и закрываем соединение
        else:
            response = {RESPONSE: 400, ERROR: 'Имя пользователя уже занято'}
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TARGET in message and TIME in message and MESSAGE_TEXT in message:
        # print(message[ACCOUNT_NAME], message[MESSAGE_TEXT])
        messages_list.append(message)
        return
    # Если клиент вышел
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    # Иначе отдаём Bad request
    else:
        response = {RESPONSE: 400, ERROR: 'Некорректный запрос'}
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
    :param message:
    :param names:
    :param listen_socks:
    :return:
    """
    if message[TARGET] in names and names[message[TARGET]] in listen_socks:
        send_message(names[message[TARGET]], message)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[TARGET]} от пользователя {message[SENDER]}.')
    elif message[TARGET] in names and names[message[TARGET]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(f'Пользователь {message[TARGET]} не зарегистрирован на сервере, отправка сообщения невозможна.')


@log
def create_arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(
            f'Попытка запуска сервера с указанием неподходящего порта '
            f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port


def main():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Сначала обрабатываем порт:
    server.py -p 8888 -a 127.0.0.1
    :return:
    '''
    listen_address, listen_port = create_arg_parser()

    SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}')

    # Готовим сокет
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((listen_address, listen_port))
    sock.settimeout(1.5)

    # список клиентов , очередь сообщений
    clients = []
    messages = []
    names = dict()

    # Слушаем порт
    sock.listen(MAX_CONNECTIONS)
    # Основной цикл программы сервера

    while True:
        # Ждём подключения, если таймаут вышел, ловим исключение.
        try:
            client, client_address = sock.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соединение с ПК {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    handle(get_message(client_with_message),
                           messages, client_with_message, clients, names)
                    SERVER_LOGGER.debug(
                        f'Получено сообщение от клиента {client_with_message}: {messages[client_with_message]}')
                except:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and send_data_lst:
            for mess in messages:
                try:
                    process_message(mess, names, send_data_lst)
                except Exception:
                    SERVER_LOGGER.info(f'Связь с клиентом с именем {mess[TARGET]} была потеряна')
                    clients.remove(names[mess[TARGET]])
                    del names[mess[TARGET]]
            messages.clear()


if __name__ == "__main__":
    main()
