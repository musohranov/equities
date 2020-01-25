"""
Абстрактное понятие команды.
"""

from abc import ABC


class Cmd(ABC):
    """
    Команда.
    """

    def __init__(self, name, description, syntax):
        """
        :param str name: Имя.
        :param str description: Описание
        :param str syntax: Синтаксис

        :raise: ValueError
        """

        if not (isinstance(name, str) and name):
            raise ValueError('Некорректно задано название!')
        self._name = name

        if not (isinstance(description, str) and description):
            raise ValueError('Некорректно задано описание!')
        self._description = description

        if not isinstance(syntax, str):
            raise ValueError('Некорректно задан синтаксис!')
        self._syntax = syntax

        self._names = [name] + self._get_aliases()

    def get_name(self):
        """
        Получить название.
        :rtype: str
        """
        return self._name

    def get_description(self):
        """
        Получить описание.
        :rtype: str
        """
        return self._description

    def get_syntax(self):
        """
        Получить синтаксис.
        :rtype: str
        """
        return self._syntax

    def _get_aliases(self):
        """
        Получить список синонимов
        :rtype: list[str]
        """
        return []

    def get_names(self):
        """
        Получить список имен с учетом синонимов.
        :rtype: list[str]
        """
        return self._names

    def run(self, params):
        """
        Выполнить команду
        :param list[str] params: Параметры

        :raise: InvalidCmdParams

        :rtype: list[str]
        :return: Результат выполнения команды, или синтаксис команды если переданный параметр "?"
        """

        if len(params) == 1 and params[0] == CMD_PARAM_HELP and self._syntax:
            names = '|'.join(self._names)
            return [self._description, f'{names} {self._syntax}']
        else:
            return self._run(params)

    def _run(self, params):
        """
        Выполнить команду
        :param list[str] params: Параметры
        :raise: InvalidCmdParams
        :rtype: list[str]
        """
        raise NotImplementedError()


CMD_PARAM_HELP = '?'
"""
Параметр команды 'Получить детали'
"""


class InvalidCmdParams(Exception):
    """
    Исключение 'Не верные параметры команды'
    """
    def __init__(self):
        """
        """
        super().__init__(f'Параметры команды введены не верно!')
