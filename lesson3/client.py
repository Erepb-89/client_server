"""Программа-клиент"""
import argparse
import sys
import json
import socket
import time
import logging
from decorators import log
from log.config import client_log_config
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from common.variables import ACTION, PRESENCE, TIME, TYPE, STATUS, USER, ACCOUNT_NAME, EXIT, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, AUTHENTICATE, PASSWORD, PROBE, MESSAGE, MESSAGE_TEXT, SENDER, \
    TARGET
from common.utils import get_message, send_message

# Инициализация клиентского логера
CLIENT_LOGGER = logging.getLogger('client')


@log
def message_from_users(sock, account_name):
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and TARGET in message \
                    and MESSAGE_TEXT in message and message[TARGET] == account_name:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                   f'\n{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            CLIENT_LOGGER.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
            break


@log
def create_arg_parser():
    """
    Создаём парсер аргументов коммандной строки
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')

    namespace = parser.parse_args(sys.argv[1:])
    server_ip = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    client_mode = namespace.mode

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'{server_port} В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(
            f'{server_port} Указан недопустимый режим работы {client_mode}.'
            f'Допустимые режимы: listen, send')
        sys.exit(1)

    return server_ip, server_port, client_mode, client_name


@log
def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def create_presence(account_name):
    '''
    Функция генерирует запрос о присутствии клиента
    :param account_name:
    :return:
    '''
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        TYPE: STATUS,
        USER: {
            ACCOUNT_NAME: account_name,
            STATUS: "Yep, I am here!"
        }
    }
    CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def message_from_server(message):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                           f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')


@log
def create_message(sock, account_name):
    """Функция запрашивает текст сообщения и возвращает его.
    Так же завершает работу при вводе подобной комманды
    """
    mes_target = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки или \'exit\' для завершения работы: ')
    if message == 'exit':
        send_message(sock, create_exit_message(account_name))
        CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
        sock.close()
        print('Спасибо за использование нашего сервиса!')
        time.sleep(1)
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        TARGET: mes_target,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        CLIENT_LOGGER.debug(f'Отправлено сообщение для пользователя {mes_target}')
    except:
        CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)
    # return message_dict


@log
def process_ans(message):
    """
    Функция разбирает ответ сервера на сообщение о присутствии,
    возращает 200 если все ОК или генерирует исключение при ошибке
    :return:
    """
    CLIENT_LOGGER.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            CLIENT_LOGGER.debug('Клиент не подключился к серверу')
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


def main():
    """Загружаем параметры коммандной строки"""
    server_ip, server_port, client_mode, client_name = create_arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    print('client_name: ', client_name)

    CLIENT_LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_ip}, '
        f'порт: {server_port}, режим работы: {client_mode}, имя пользователя: {client_name}')

    # Инициализация сокета и сообщение серверу о нашем появлении
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_ip, server_port))
        send_message(sock, create_presence(account_name=client_name))
        answer = process_ans(get_message(sock))
        # time.sleep(1)
        CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(
            f'Не удалось подключиться к серверу {server_ip}:{server_port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        # Если соединение с сервером установлено корректно,
        # начинаем обмен с ним, согласно требуемому режиму.
        # основной цикл прогрммы:
        if client_mode == 'send':
            print('Режим работы - отправка сообщений.')
        else:
            print('Режим работы - приём сообщений.')
        while True:
            # time.sleep(1)
            # режим работы - отправка сообщений
            if client_mode == 'send':
                try:
                    create_message(sock, client_name)
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_ip} было потеряно.')
                    sys.exit(1)

            # Режим работы приём:
            if client_mode == 'listen':
                try:
                    message_from_server(get_message(sock))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Соединение с сервером {server_ip} было потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
