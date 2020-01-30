"""
Команда 'Получить курс ценной бумаги'
"""

from datetime import datetime
from typing import List

from src.interface.core.commands.cmd import InvalidCmdParams
from src.equities.finam import get_price, NotFoundIssuer
from src.interface.core.commands.manager import Manager


@Manager.register('price',
                  [],
                  'Получить курс за отрезок, в формате <дата> <цена_открытия> <цена_закрытия>',
                  '<код> [<дата1> [<дата2>]], дата в формате dd.mm.yy, если не указана то за текущий день')
def _run(params: List[str]) -> List[str]:
    """
    Получить цену. Если дата не передана считаем текущей

    :param list[str] params: Параметры <Код> [<Дата1> [<Дата2>]]
    :raise: InvalidCmdParams

    :return: Строки вида 'Дата ЦенаОткрытия ЦенаЗакрытия'. Если ценная бумага не найдена, возвращается
    строка с ошибкой
    """

    if 1 <= len(params) <= 3:

        try:
            dt_left: datetime.date = datetime.strptime(params[1], '%d.%m.%y').date() \
                if len(params) > 1 else datetime.today().date()

            dt_right: datetime.date = datetime.strptime(params[2], '%d.%m.%y').date() \
                if len(params) > 2 else dt_left
        except:
            raise InvalidCmdParams()

        try:
            price_list = get_price(params[0], dt_left, dt_right)
            return [f'{price.dt.strftime("%d.%m.%y")} {price.open:.2f} {price.close:.2f}' for price in price_list]
        except NotFoundIssuer:
            return ['Эмитент не найден!']
    else:
        raise InvalidCmdParams()
