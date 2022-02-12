"""Лаунчер"""

import subprocess
import time

PROCESS = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESS.append(subprocess.Popen('python server.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        time.sleep(1)
        PROCESS.append(subprocess.Popen('python client.py -m send -n name1',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        time.sleep(2)
        PROCESS.append(subprocess.Popen('python client.py -m send -n name2',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        time.sleep(2)
        PROCESS.append(subprocess.Popen('python client.py -m listen -n name3',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        time.sleep(2)
        PROCESS.append(subprocess.Popen('python client.py -m listen -n name4',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
