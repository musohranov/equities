from datetime import datetime

from src.interface.core.commands.cmd import Cmd, InvalidCmdParams
from src.equities.finam import get_price, NotFoundIssuer


class Price(Cmd):
    """
    Команда получения курса ценной бумаги
    """

    def __init__(self):
        super().__init__('price',
                         'Получить курс за отрезок, в формате <дата> <цена_открытия> <цена_закрытия>',
                         '<код> [<дата1> [<дата2>]], дата в формате dd.mm.yy, если не указана то за текущий день')

    def _run(self, params):
        """
        Выполнить команду
        :param list[str] params: Параметры
        :rtype: list[str]
        """

        if 1 <= len(params) <= 3:

            try:
                dt_left = datetime.strptime(params[1], '%d.%m.%y').date() \
                    if len(params) > 1 else datetime.today().date()

                dt_right = datetime.strptime(params[2], '%d.%m.%y').date() \
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
