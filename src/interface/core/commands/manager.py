from src.interface.core.commands.cmd import Cmd, InvalidCmdParams, CMD_PARAM_HELP
from src.interface.core.commands.reference.find import Find
from src.interface.core.commands.reference.price import Price


class UnknownCmd(Exception):
    """
    Исключение 'Неизвестная команда'
    """
    pass


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
            except InvalidCmdParams:
                return ['Ошибка! Параметры команды введены не верно!', ''] + cmd.run(['?'])

    raise UnknownCmd()


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
            result = ['Список доступных команд:']
            for cmd in _CMD_LIST:
                cmd_name, cmd_description, cmd_syntax = cmd.get_name(), cmd.get_description(), cmd.get_syntax()

                cmd_result = f'- {cmd_name}, {cmd_description}'

                result.append(cmd_result)

            result.append(f'/// Для детального описания синтаксиса команды, выполните "имя_команды {CMD_PARAM_HELP}"')
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
