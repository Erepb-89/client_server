"""Программа-клиент"""

import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, TYPE, STATUS, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, AUTHENTICATE, PASSWORD, PROBE
from common.utils import get_message, send_message


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
    # elif ACTION in message:
    #     if message[ACTION] == PROBE:
    #         create_presence()
    raise ValueError


def main():
    '''Загружаем параметры коммандной строки'''
    # client.py 127.0.0.1 8888
    try:
        server_ip = sys.argv[2]
        server_port = int(sys.argv[3])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_ip = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Инициализация сокета и обмен
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))
    message_to_server = create_presence()
    send_message(sock, message_to_server)
    try:
        answer = process_ans(get_message(sock))
        print(answer)
    except (ValueError, json.JSONDecodeError):
        print('Не удалось декодировать сообщение сервера.')


def test_presence():
    """тест 1"""
    test1 = create_presence(account_name='Guest')
    assert test1 == {
        ACTION: PRESENCE,
        TIME: time.time(),
        TYPE: STATUS,
        USER: {
            ACCOUNT_NAME: 'Guest',
            STATUS: "Yep, I am here!"
        }
    }


def test_process_ans_200():
    """тест 2"""
    test2 = process_ans({'response': 200})
    assert test2 == '200 : OK'


def test_process_ans_400():
    """тест 3"""
    test3 = process_ans({
        RESPONSE: 400,
        ERROR: 'Bad Request'
    })
    assert test3 == '400 : Bad Request'


if __name__ == '__main__':
    test_presence()
    test_process_ans_200()
    test_process_ans_400()
    main()
