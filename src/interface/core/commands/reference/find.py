from src.interface.core.commands.cmd import Cmd, InvalidCmdParams
from src.equities.finam import get_issuer_list


class Find(Cmd):
    """
    Команда поиска по ценным бумагам
    """

    def __init__(self):
        super().__init__('find',
                         'Поиск эмитента по названию или идентификатору',
                         '<строка_поиска (миниму 3 символа)>')

    def _get_aliases(self):
        """
        Получить список синонимов
        :rtype: list[str]
        """
        return ['search']

    def _run(self, params):
        """
        Выполнить команду
        :param list[str] params: Параметры
        :rtype: list[str]
        """
        if len(params) >= 3 or any(len(p) >= 3 for p in params):
            issuer_list = get_issuer_list(params, 5)
            if issuer_list:
                return [f'{issuer[0]}, {issuer[1]}' for issuer in issuer_list]
            else:
                return ['Результат поиска отсутствует!']
        else:
            raise InvalidCmdParams()
