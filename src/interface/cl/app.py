"""
Реализация приложения в виде интерфейса командной строки.
"""

import sys
from os import linesep
from src.interface.core.commands.manager import run_cmd, run_help_cmd, UnknownCmd


def run():
    """
    Запустить приложение.
    """

    if len(sys.argv) <= 1:
        _print_result_cmd(run_help_cmd())
        return

    try:
        _print_result_cmd(run_cmd(sys.argv[1], sys.argv[2:]))

    except UnknownCmd as err:
        print(f'Ошибка! {str(err)}')
        _print_result_cmd(run_help_cmd())


def _print_result_cmd(str_list):
    """
    Вывести результат выполнения команды
    :param list[str] str_list: Список строк
    """
    print(linesep.join(str_list))


if __name__ == '__main__':
    run()
