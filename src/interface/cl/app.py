"""
Реализация приложения в виде 'интерфейса командной строки'.
Для получения полного списка поддерживаемых команд, воспользуйтесь командой help.
"""

from src.interface.core.commands.manager import run_cmd, run_help_cmd, UnknownCmd


def run():
    """
    Запустить приложение.
    """

    while True:
        print('>> Введите команду: ', end='')

        input_str = input()
        _print_new_line()

        cmd_name = ''
        try:
            if input_str:
                cmd_name = input_str.split()[0]
                result_list = run_cmd(cmd_name, input_str.split()[1:])
            else:
                result_list = run_help_cmd()

        except UnknownCmd:
            print(f'Ошибка! Команда "{cmd_name}" не найдена!\n')
            result_list = run_help_cmd()

        for result in result_list:
            print(result)

        _print_new_line()


def _print_new_line():
    """
    Вывести пустую строку
    """
    print('')


if __name__ == '__main__':
    run()
