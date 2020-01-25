from src.interface.core.commands.cmd import Cmd, InvalidCmdParams, CMD_PARAM_HELP
from src.interface.core.commands.reference.find import Find
from src.interface.core.commands.reference.price import Price


class UnknownCmd(Exception):
    """
    Исключение 'Неизвестная команда'
    """
    def __init__(self, name):
        """
        :param str name: Название команды.
        """
        super().__init__(f'Команда "{name}" не найдена!')


def run_cmd(cmd_name, cmd_params):
    """
    Выполнить команду. Формат командной строки: <имя_команды> + [параметры]

    :param str cmd_name: Имя команды
    :param list[str] cmd_params:  Параметры команды
    :rtype: list[str]
    :raise: UnknownCmd

    :return: Результат выполнения команды
    """

    for cmd in _CMD_LIST:
        if cmd_name.lower() in ([c.lower() for c in cmd.get_names()]):
            try:
                return cmd.run(cmd_params)
            except InvalidCmdParams as err:
                return [f'Ошибка! {str(err)}', ''] + cmd.run(['?'])

    raise UnknownCmd(cmd_name)


class _Help(Cmd):
    """
    Команда 'Помощь'
    """

    def __init__(self):
        super().__init__('help',
                         'Получить список команд',
                         '')

        self._result = None

    def _get_aliases(self):
        """
        Получить список синонимов
        :rtype: list[str]
        """
        return ['h', '?']

    def _run(self, params):
        """
        Выполнить команду.
        :param list[str] params: Параметры
        :rtype: list[str]
        :return: Игнорируются переданные параметры и возвращается перечень возможных команд с описанием синтаксиса
        """

        if self._result is None:
            result = [f'Перечень команд (для детального описание выполните команду с параметром "{CMD_PARAM_HELP}"):']

            for cmd in _CMD_LIST:
                cmd_name, cmd_description, cmd_syntax = cmd.get_name(), cmd.get_description(), cmd.get_syntax()
                cmd_result = f'- {cmd_name}, {cmd_description}'

                result.append(cmd_result)

            self._result = result

        return self._result


_CMD_HELP = _Help()
_CMD_LIST = (_CMD_HELP, Find(), Price())


def run_help_cmd():
    """
    Выполнить команду 'Помощь'.
    :rtype: list[str]
    """
    return _CMD_HELP.run([])
