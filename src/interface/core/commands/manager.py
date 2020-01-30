"""
Менеджер команд, предоставляет:
 * Декоратор для регистрации команды
 * Поиск и выполненеи команды по входным данным
 * Команду помощи
"""

from typing import List, Callable
from src.interface.core.commands.cmd import Cmd, InvalidCmdParams, CMD_PARAM_HELP


class UnknownCmd(Exception):
    """
    Исключение 'Неизвестная команда'
    """
    def __init__(self, name: str):
        """
        :param name: Название команды.
        """
        super().__init__(f'Команда "{name}" не найдена!')


class Manager:
    """
    Менеджер команд
    """

    _cmd_list = {}

    @classmethod
    def register(cls, name: str, aliases: List[str], description: str, syntax: str) -> Callable:
        """
        Декоратор регистрации команды

        :param name: Название команды
        :param aliases: Синонинмы
        :param description: Описание
        :param syntax: Синтаксис
        """

        def decorator(func: Callable):
            cmd = Cmd(name, aliases, description, syntax, func)
            for alias in [name] + aliases:
                cls._cmd_list[alias.lower()] = cmd
        return decorator

    @classmethod
    def run_cmd(cls, cmd_name: str, cmd_params: List[str]) -> List[str]:
        """
        Выполнить команду. Формат командной строки: <имя_команды> + [параметры]

        :param cmd_name: Имя команды
        :param cmd_params:  Параметры команды
        :raise: UnknownCmd
        :return: Результат выполнения команды
        """

        if cmd_name.lower() not in Manager._cmd_list:
            raise UnknownCmd(cmd_name)

        cmd = cls._cmd_list[cmd_name]

        try:
            return cmd.run(cmd_params)
        except InvalidCmdParams as err:
            return [f'Ошибка! {str(err)}', ''] + cmd.run(['?'])

    @classmethod
    def help(cls) -> List[str]:
        """
        Выполнить команду 'Помощь'
        """
        return cls._cmd_list['help'].run([])

    @classmethod
    def get_cmd_list(cls) -> List[Cmd]:
        """
        Получить список команд
        """
        return list(set(cls._cmd_list.values()))


@Manager.register('help', ['h', '?'], 'Получить список команд', '')
def _run_help(_: List[str]) -> List[str]:
    """
    Получить список поддерживаемых команд с описанием синтаксиса
    :param _: Параметры.
    """

    result = [f'Перечень команд (для детального описание выполните команду с параметром "{CMD_PARAM_HELP}"):']

    for cmd in Manager.get_cmd_list():
        cmd_name, cmd_description = cmd.get_name(), cmd.get_description()
        cmd_result = f'- {cmd_name}, {cmd_description}'

        result.append(cmd_result)

    return result
