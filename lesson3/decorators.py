"""Декораторы"""

import sys
import logging
import log.config.server_log_config
import log.config.client_log_config
import traceback
import inspect

print(sys.argv[0].split('/')[-1])
if sys.argv[0].split('/')[-1].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func):
    """Функция-Декоратор"""

    def save_logger(*args, **kwargs):
        """Обертка"""
        res = func(*args, **kwargs)
        LOGGER.debug(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
                     f'Вызов из модуля {func.__module__}. Вызов из'
                     f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
                     f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
        return res

    return save_logger


class Log:
    """Класс-декоратор"""

    def __call__(self, func):
        def save_logger(*args, **kwargs):
            """Обертка"""
            res = func(*args, **kwargs)
            LOGGER.debug(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
                         f'Вызов из модуля {func.__module__}. Вызов из'
                         f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
                         f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
            return res

        return save_logger
