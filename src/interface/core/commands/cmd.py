"""
Команда предоставляет интерфейс:
 * Получения имени, описания, синтаксиса
 * Выполнение
"""

from typing import List, Callable


class Cmd:
    """
    Команда.
    """

    def __init__(self, name: str, aliases: List[str], description: str, syntax: str, run_func: Callable):
        """
        :param name: Имя
        :param description: Описание
        :param syntax: Синтаксис
        :param run_func: Функция выполнения
        :param syntax: Синонимы

        :raise: ValueError
        """

        if not (isinstance(name, str) and name):
            raise ValueError('Некорректно задано название!')
        self._name: str = name

        if not (isinstance(description, str) and description):
            raise ValueError('Некорректно задано описание!')
        self._description: str = description

        if not isinstance(syntax, str):
            raise ValueError('Некорректно задан синтаксис!')
        self._syntax: str = syntax

        self._names: List[str] = [name] + aliases

        self._run_func = run_func

    def get_name(self) -> str:
        """
        Получить название
        """
        return self._name

    def get_description(self) -> str:
        """
        Получить описание
        """
        return self._description

    def run(self, params) -> List[str]:
        """
        Выполнить команду

        :param list[str] params: Параметры
        :raise: InvalidCmdParams

        :return: Результат выполнения команды, или синтаксис команды если переданный параметр равен '?'
        """

        if len(params) == 1 and params[0] == CMD_PARAM_HELP and self._syntax:
            names = '|'.join(self._names)
            return [self._description, f'{names} {self._syntax}']

        return self._run_func(params)


CMD_PARAM_HELP = '?'
"""
Параметр команды 'Получить детали'
"""


class InvalidCmdParams(Exception):
    """
    Исключение 'Не верные параметры команды'
    """
    def __init__(self):
        super().__init__(f'Параметры команды введены не верно!')
