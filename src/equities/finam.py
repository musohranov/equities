"""
API к данным акций российских эмитентов от finam.ru.

Обзор возможностей:

* Поиск по переченю ценных бумаг (акций).

* Курс на указанный период
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Tuple, NamedTuple
import urllib.request

from src.equities.issuer_list import ISSUER_LIST


def get_issuer_list(search_str_list: List[str], result_max: int) -> List[Tuple[str, str]]:
    """
    Получить список ценных бумаг по поисковой строке.
    Поиск проиходит по коду или названию без учета регистра.

    :param search_str_list: Список строк поиска. Если список пуст, соответствие щитается безуусловным.
    :param int result_max: Максимальный результат. Если 0, без ограничений.

    :return: Список кортежей (Код, Название)

    >>> get_issuer_list(['НорНик'], 0)
    [('GMKN', 'ГМКНорНик')]

    >>> get_issuer_list(['РогаИКопыта'], 0)
    []
    """

    result = []
    for code, data in ISSUER_LIST.items():
        name = data[0]
        if not search_str_list or all(search_str.upper() in code.upper() or search_str.upper() in name.upper()
                                      for search_str in search_str_list):
            result.append((code, name))

            if len(result) == result_max:
                break

    return result


class Price(NamedTuple):
    """
    Курс ценной бумаги
    """

    dt: datetime.date
    """
    Дата
    """

    open: Decimal
    """
    Цена на начало дня
    """

    close: Decimal
    """
    Цена на окончания дня
    """


class NotFoundIssuer(Exception):
    """
    Исключение 'Эмитент не найден'
    """
    pass


def get_price(issuer_code: str, dt_left: datetime, dt_right: datetime) -> List[Price]:
    """
    Получить курс за временной отрезок.

    :param issuer_code: Код эмитента
    :param dt_left: Дата конца отрезка
    :param dt_right: Дата начала отрезка

    :raise: NotFoundIssuer

    >>> get_price('XXX', datetime.today().date(), datetime.today().date())
    Traceback (most recent call last):
    ...
    finam.NotFoundIssuer
    """

    if issuer_code.upper() not in ISSUER_LIST:
        raise NotFoundIssuer()

    # Индекс эмитента
    index = ISSUER_LIST.get(issuer_code.upper())[1]

    # Отрезок
    df, mf, yf, from_ = dt_left.day, dt_left.month - 1, dt_left.year, dt_left.strftime('%d.%m.%Y')
    dt, mt, yt, to_ = dt_right.day, dt_right.month - 1, dt_right.year, dt_right.strftime('%d.%m.%Y')

    # Детализация отрезка. Варианты
    # '1' - тики,    '2' - 1 мин., '3' - 5 мин., '4' - 10 мин.,  '5' - 15 мин.,
    # '6' - 30 мин., '7' - 1 час,  '8' - 1 день, '9' - 1 неделя, '10' - 1 месяц
    period = 8

    # Формат результата. Варианты 'txt', 'csv'
    result_ff = 'txt'

    # Формат даты результата. Варианты '1' — ггггммдд, '2' — ггммдд, '3' — ддммгг, '4' — дд/мм/гг, '5' — мм/дд/гг
    result_df = 3

    # Формат времени результата. Варианты '1' — ччммсс, '2' — ччмм, '3' — чч: мм: сс, '4' — чч: мм
    result_tf = 2

    # Московское время результата. Варианты '0' - не московское
    result_tm = 0

    # Время свечи. Варианты '0' — начала свечи, '1' — окончания свечи
    result_tc = 0

    # Разделитель колонок. Варианты
    # '1' — запятая, '2' — точка, '3' — точка с запятой, '4' — табуляция, '5' — пробел
    result_column_sep = 3

    # Разделитель разрядов значений. Варианты '1' — нет, '2' — точка, '3' — запятая, '4' — пробел, '5' — кавычка
    result_value_sep = 1

    # Получаемые данные в результате. Варианты
    # '1' — TICKER, PER, DATE, TIME, OPEN, HIGH, LOW, CLOSE, VOL
    # '2' — TICKER, PER, DATE, TIME, OPEN, HIGH, LOW, CLOSE
    # '3' — TICKER, PER, DATE, TIME, CLOSE, VOL
    # '4' — TICKER, PER, DATE, TIME, CLOSE
    # '5' — DATE, TIME, OPEN, HIGH, LOW, CLOSE, VOL
    # '6' — DATE, TIME, LAST, VOL, ID, OPER
    result_data = 5

    # Наличие заголовка в результате. Варианты '0' - нет, '1' - да
    result_w_head = 0

    url = f'http://export.finam.ru/result.txt?market=1&em={index}&code={issuer_code}&apply=0' \
          f'&df={df}&mf={mf}&yf={yf}&from={from_}' \
          f'&dt={dt}&mt={mt}&yt={yt}&to={to_}' \
          f'&p={period}&f=result&e=.{result_ff}&cn={issuer_code}&dtf={result_df}&tmf={result_tf}' \
          f'&MSOR={result_tc}&mstimever={result_tm}&sep={result_column_sep}&sep2={result_value_sep}' \
          f'&datf={result_data}&at={result_w_head}'

    result = []
    with urllib.request.urlopen(url) as file:
        for result_str in file.readlines():
            result_values = result_str.decode().split(';')
            result.append(Price(datetime.strptime(result_values[0], "%d%m%y").date(),
                                Decimal(result_values[2]),
                                Decimal(result_values[5]))
                          )

    return result
