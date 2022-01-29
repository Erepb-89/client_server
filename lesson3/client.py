"""Программа-клиент"""
import argparse
import sys
import json
import socket
import time
import logging
from log.config import client_log_config
from errors import ReqFieldMissingError
from common.variables import ACTION, PRESENCE, TIME, TYPE, STATUS, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, AUTHENTICATE, PASSWORD, PROBE
from common.utils import get_message, send_message

# Инициализация клиентского логера
CLIENT_LOGGER = logging.getLogger('client')


def create_arg_parser():
    """
    Создаём парсер аргументов коммандной строки
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    return parser


def authentication(account_name='erepb'):
    out = {
        ACTION: AUTHENTICATE,
        TIME: time.time(),
        TYPE: STATUS,
        USER: {
            ACCOUNT_NAME: account_name,
            PASSWORD: "123456"
        }
    }
    return out


def create_presence(account_name='Guest'):
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


def process_ans(message):
    '''
    Функция разбирает ответ сервера
    :param message:
    :return:
    '''
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


def main():
    '''Загружаем параметры коммандной строки'''
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    server_ip = namespace.addr
    server_port = namespace.port

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'{server_port} В качастве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    CLIENT_LOGGER.info(f'Запущен клиент с парамертами: '
                       f'адрес сервера: {server_ip}, порт: {server_port}')

    # Инициализация сокета и обмен
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    message_to_server = create_presence()
    send_message(sock, message_to_server)
    try:
        answer = process_ans(get_message(sock))
        CLIENT_LOGGER.info(f'Принят ответ от сервера {answer}')
        print(answer)
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Не удалось декодировать полученную Json строку.')
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'В ответе сервера отсутствует необходимое поле '
                            f'{missing_error.missing_field}')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_ip}:{server_port}, '
                               f'конечный компьютер отверг запрос на подключение.')


if __name__ == '__main__':
    main()
