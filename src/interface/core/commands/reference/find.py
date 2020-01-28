"""
Команда 'Поиск по ценным бумагам'
"""

from typing import List

from src.interface.core.commands.cmd import Cmd, InvalidCmdParams
from src.equities.finam import get_issuer_list


class Find(Cmd):
    """
    Команда
    """

    def __init__(self):
        super().__init__('find',
                         'Поиск эмитента по названию или идентификатору',
                         '<строка_поиска (миниму 3 символа)>')

    def _get_aliases(self) -> List[str]:
        """
        Получить список синонимов
        """
        return ['search']

    def _run(self, params: List[str]) -> List[str]:
        """
        Выполнить поиск. Поиск происходит в случае если кол-во параметров >= 3 либо один из параметров длинной >= 3

        :param params: Параметры
        :raise: InvalidCmdParams

        return: В случае успеха возвращаются строки вида 'Код ценной бумаги, Наименование', иначе строка с ошибкой об
        отсутствии результата
        """
        if len(params) >= 3 or any(len(p) >= 3 for p in params):
            issuer_list = get_issuer_list(params, 5)
            if issuer_list:
                return [f'{issuer[0]}, {issuer[1]}' for issuer in issuer_list]
            return ['Результат поиска отсутствует!']

        raise InvalidCmdParams()
