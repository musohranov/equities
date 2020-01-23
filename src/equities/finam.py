"""
API к данным акций российских эмитентов от finam.ru.

Обзор возможностей:

* Перечень ценных бумаг (акций).
Взят со страницы https://www.finam.ru/profile/moex-akcii/tatneft-pref из файла icharts.js

* Курс на указанную дату
"""
from datetime import datetime
from collections import namedtuple
from decimal import Decimal
import urllib.request


def get_issuer_list(search_str_list, result_max):
    """
    Получить список эмитентов по поисковой строке. Поиск проиходит по коду или названию без учета регистра.

    :param list[str]|None search_str_list: Строки поиска.
    :param int result_max: Максимальный результат. Если 0, без ограничений.

    :rtype: list[tuple(str, str)]
    :return: Список кортежей (Код, Название)
    """

    result = []
    for code, data in _ISSUER_LIST.items():
        name = data[0]
        if all(search_str.upper() in code.upper() or search_str.upper() in name.upper()
               for search_str in search_str_list):
            result.append((code, name))

            if len(result) == result_max:
                break

    return result


Price = namedtuple('Price', 'dt open close')
Price.__doc__ = """
Курс ценной бумаги.

:param date dt: Дата
:param decimal open: Курс на начало дня
:param decimal open: Курс на окончания дня
"""


class NotFoundIssuer(Exception):
    """
    Исключение 'Эмитент не найден'
    """
    pass


def get_price(issuer_code, dt_left, dt_right):
    """
    Получить курс за отрезок.

    :param str issuer_code: Код эмитента
    :param date dt_left: Дата конца отрезка
    :param date dt_right: Дата начала отрезка

    :raise: NotFoundIssuer

    :rtype: list[Price]
    :return: Курсы за отрезок дат, если эмитент не найден исключение
    """

    if issuer_code.upper() not in _ISSUER_LIST:
        raise NotFoundIssuer()

    # Индекс эмитента
    index = _ISSUER_LIST.get(issuer_code.upper())[1]

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


# Список эмитентов
_ISSUER_LIST = {
    'MSNG': ('+МосЭнерго', 6, 'moex-akcii/mosenrg'),
    'AGRO': ('AGRO-гдр', 399716, 'moex-akcii/gdr-ros-agro-plc-ord-shs'),
    'ENPL': ('ENPL-гдр', 489354, 'moex-akcii/gdr-enplus-group-plc-ord-shs'),
    'FIVE': ('FIVE-гдр', 491944, 'moex-akcii/gdr-x5-retailgroup-n-v-ord-shs'),
    'POLY': ('Polymetal', 175924, 'moex-akcii/polymetal-international-plc'),
    'RUAL': ('RUSAL plc', 414279, 'moex-akcii/united-company-rusal-plc'),
    'RAVN': ('Raven', 498713, 'moex-akcii/raven-property-group-limited'),
    'TCSG': ('TCS-гдр', 913710, 'moex-akcii/gdr-tcs-group-holding-ord-shs_tcsg'),
    'YNDX': ('Yandex clA', 388383, 'moex-akcii/pllc-yandex-n-v'),
    'QIWI': ('iQIWI', 181610, 'moex-akcii/qiwi-plc'),
    'UNAC': ('iАвиастКао', 22843, 'moex-akcii/ob-aviastroitelnaya-korp'),
    'DZRD': ('iДонскЗР', 74744, 'moex-akcii/dzrd-ao'),
    'DZRDP': ('iДонскЗР п', 74745, 'moex-akcii/dzrd-pref'),
    'ISKJ': ('iИСКЧ ао', 17137, 'moex-akcii/hsci-ao'),
    'GEMA': ('iММЦБ ао', 901174, 'moex-akcii/imcb-pjsc_gema'),
    'NAUK': ('iНПОНаука', 81992, 'moex-akcii/npo-nauka-ao'),
    'LIFE': ('iФармсинтз', 74584, 'moex-akcii/farmsintez-ao'),
    'ALRS': ('АЛРОСА ао', 81820, 'moex-akcii/alrosa-ao'),
    'ALNU': ('АЛРОСА-Нюр', 81882, 'moex-akcii/alrosa-nurba-ao'),
    'ACKO': ('АСКО ао', 484229, 'moex-akcii/sk-yuzhural-asko-ao'),
    'ABRD': ('АбрауДюрсо', 82460, 'moex-akcii/abrau-durso-ao'),
    'AVAN': ('Авангрд-ао', 82843, 'moex-akcii/avangard'),
    'AKRN': ('Акрон', 17564, 'moex-akcii/akron'), 'APTK': ('Аптеки36и6', 13855, 'moex-akcii/apteki-36-6'),
    'ARSA': ('Арсагера', 19915, 'moex-akcii/uk-arsagera'),
    'ASSB': ('АстрЭнСб', 16452, 'moex-akcii/astrakhan-energo-sbyt'),
    'AMEZ': ('АшинскийМЗ', 20702, 'moex-akcii/ashinckiy-metzavod-oao'), 'AFLT': ('Аэрофлот', 29, 'moex-akcii/aeroflot'),
    'BSPB': ('БСП ао', 20066, 'moex-akcii/bsp'), 'FTRE': ('БУДУЩЕЕ ао', 462599, 'moex-akcii/fg-future-ao'),
    'BISV': ('БашИнСв ао', 35242, 'moex-akcii/bashinformsvyaz-ao'),
    'BISVP': ('БашИнСв ап', 35243, 'moex-akcii/bashinformsvyaz-ap'),
    'BANE': ('Башнефт ао', 81757, 'moex-akcii/bashneft-ank-ao'),
    'BANEP': ('Башнефт ап', 81758, 'moex-akcii/bashneft-ank-ap'), 'BLNG': ('Белон ао', 21078, 'moex-akcii/belon-ao'),
    'BELU': ('Белуга ао', 19651, 'moex-akcii/synergy-ao'),
    'ALBK': ('БестЭфБ ао', 82616, 'moex-akcii/best-efforts-bank-ao'),
    'BRZL': ('БурЗолото', 81901, 'moex-akcii/buryatzoloto-ao'),
    'VSMO': ('ВСМПО-АВСМ', 15965, 'moex-akcii/verhnesald-mpo'), 'VTBR': ('ВТБ ао', 19043, 'moex-akcii/vtb'),
    'VLHZ': ('ВХЗ-ао', 17257, 'moex-akcii/vhz'), 'VDSB': ('ВЭК 01 ао', 16352, 'moex-akcii/vek-ao'),
    'VJGZ': ('Варьеган', 81954, 'moex-akcii/var-eganneftegaz-ao'),
    'VJGZP': ('Варьеган-п', 81955, 'moex-akcii/var-eganneftegaz-ap'),
    'VZRZ': ('Возрожд-ао', 17068, 'moex-akcii/vozrojdenie'),
    'VZRZP': ('Возрожд-п', 17067, 'moex-akcii/vozrojdenie-pref'),
    'VGSB': ('ВолгЭнСб', 16456, 'moex-akcii/volgograd-energo-sbyt'),
    'VGSBP': ('ВолгЭнСб-п', 16457, 'moex-akcii/volgograd-energo-sbyt-pref'),
    'VSYD': ('ВыбСудЗ ао', 83251, 'moex-akcii/viborgskii-sudostr-zavod-ao'),
    'VSYDP': ('ВыбСудЗ ап', 83252, 'moex-akcii/viborgskii-sudostr-zavod-ap'),
    'GAZA': ('ГАЗ ао', 81997, 'moex-akcii/gaz-ao'), 'GAZAP': ('ГАЗ ап', 81998, 'moex-akcii/gaz-pref'),
    'GAZT': ('ГАЗ-Тек ао', 82115, 'moex-akcii/gaz-tek-oao-ao'),
    'GAZS': ('ГАЗ-сервис', 81399, 'moex-akcii/gaz-servis-ao'), 'GAZC': ('ГАЗКОН-ао', 81398, 'moex-akcii/gazkon-ao'),
    'GAZP': ('ГАЗПРОМ ао', 16842, 'moex-akcii/gazprom'),
    'GTSS': ('ГЕОТЕК ао', 436120, 'moex-akcii/geotech-seismic-services-ao'),
    'GRNT': ('ГИТ ао', 449114, 'moex-akcii/cityinnovativetechnologies-ao'),
    'GMKN': ('ГМКНорНик', 795, 'moex-akcii/nornickel-gmk'), 'GTRK': ('ГТМ ао', 488918, 'moex-akcii/gtm'),
    'RTGZ': ('ГазпРнД ао', 152397, 'moex-akcii/gazprom-gazorasp-rostov-ao'),
    'SIBN': ('Газпрнефть', 2, 'moex-akcii/gazprom-neft'),
    'HALS': ('Галс-Девел', 17698, 'moex-akcii/gals-development-ao'), 'FESH': ('ДВМП ао', 20708, 'moex-akcii/dvmp-ao'),
    'DVEC': ('ДЭК ао', 19724, 'moex-akcii/dec'), 'DASB': ('ДагСб ао', 16825, 'moex-akcii/dagestan-energosbyt-company'),
    'DSKY': ('ДетскийМир', 473181, 'moex-akcii/detsky-mir'),
    'EELT': ('ЕвроЭлтех', 487432, 'moex-akcii/european-eltech'), 'ZVEZ': ('ЗВЕЗДА ао', 82001, 'moex-akcii/zvezda-ao'),
    'ZILL': ('ЗИЛ ао', 81918, 'moex-akcii/zil-ao'), 'DIOD': ('ЗаводДИОД', 35363, 'moex-akcii/zavod-diod-ao'),
    'RUSI': ('ИКРУСС-ИНВ', 81786, 'moex-akcii/russ-invest-ic-ao'),
    'OPIN': ('ИНГРАД ао', 20711, 'moex-akcii/otkrytye-investicii-opin'),
    'IRKT': ('ИРКУТ-3', 15547, 'moex-akcii/irkut-3'), 'IGSTP': ('Ижсталь ап', 81887, 'moex-akcii/izhstal-ap'),
    'IGST': ('Ижсталь2ао', 81885, 'moex-akcii/izhstal-2ao'),
    'IDVP': ('Инв-Девел', 409486, 'moex-akcii/pao-invest-development'),
    'IRAO': ('ИнтерРАОао', 20516, 'moex-akcii/inter-rao-ao'), 'IRGZ': ('ИркЭнерго', 9, 'moex-akcii/irkutskenrg'),
    'KMAZ': ('КАМАЗ', 15544, 'moex-akcii/kamaz'), 'KZMS': ('КЗМС ао', 17359, 'moex-akcii/kzms-01'),
    'KMEZ': ('КМЗ', 22525, 'moex-akcii/kovrov-mech-zavod'), 'KTSB': ('КСБ ао', 16284, 'moex-akcii/ksb'),
    'KTSBP': ('КСБ ап', 16285, 'moex-akcii/ksb-ap'), 'KUNF': ('КУЗОЦМ ао', 81943, 'moex-akcii/kuzocm-ao'),
    'KLSB': ('КалужскСК', 16329, 'moex-akcii/kalugsk-sbyt-company-ao'),
    'KCHE': ('КамчатЭ ао', 20030, 'moex-akcii/kamchatskenergo'),
    'KCHEP': ('КамчатЭ ап', 20498, 'moex-akcii/kamchatskenergo-pref'), 'TGKD': ('Квадра', 18310, 'moex-akcii/kvadra'),
    'TGKDP': ('Квадра-п', 18391, 'moex-akcii/kvadra-pref'), 'KSGR': ('Кокс ао', 75094, 'moex-akcii/koks-ao'),
    'KOGK': ('КоршГОК ао', 20710, 'moex-akcii/korshunovskii-gok'), 'KMTZ': ('КосогМЗ ао', 81903, 'moex-akcii/kgiw-ao'),
    'KROTP': ('КрасОкт-1п', 511, 'moex-akcii/krasnyioctabr-1-pr'),
    'KROT': ('КрасОкт-ао', 510, 'moex-akcii/krasnyioctyabr'),
    'KRSB': ('Красэсб ао', 20912, 'moex-akcii/krashojarskenergosbyt'),
    'KRSBP': ('Красэсб ап', 20913, 'moex-akcii/krashojarskenergosbyt-pref'),
    'KUBE': ('Кубанэнр', 522, 'moex-akcii/kubanenrg'),
    'KBTK': ('КузбТК ао', 35285, 'moex-akcii/kuzbas-topl-kompaniya-ao'),
    'KUZB': ('КузнецкийБ', 83165, 'moex-akcii/bank-kuzneckiy'), 'KAZT': ('Куйбазот', 81941, 'moex-akcii/kuib-azot-ao'),
    'KAZTP': ('Куйбазот-п', 81942, 'moex-akcii/kuibishevazot-ap'),
    'KGKC': ('КурганГКао', 83261, 'moex-akcii/kurganskaja-gener-kompanija'),
    'KGKCP': ('КурганГКап', 152350, 'moex-akcii/kurganskaja-gener-kompanija-ap'),
    'LSRG': ('ЛСР ао', 19736, 'moex-akcii/lsr'), 'LKOH': ('ЛУКОЙЛ', 8, 'moex-akcii/lukoil'),
    'LPSB': ('ЛЭСК ао', 16276, 'moex-akcii/lesk-ao'), 'LVHK': ('Левенгук', 152517, 'moex-akcii/levenguk-ao'),
    'LNZLP': ('Лензол. ап', 22094, 'moex-akcii/lenzoloto-pref'), 'LNZL': ('Лензолото', 21004, 'moex-akcii/lenzoloto'),
    'LNTA': ('Лента др', 385792, 'moex-akcii/lenta-ltd-dr'), 'LSNGP': ('Ленэнерг-п', 542, 'moex-akcii/lenenrg-pref'),
    'LSNG': ('Ленэнерго', 31, 'moex-akcii/lenenrg'), 'MVID': ('М.видео', 19737, 'moex-akcii/m-video'),
    'MGTSP': ('МГТС-4ап', 12983, 'moex-akcii/mgts-4'), 'MGTS': ('МГТС-5ао', 12984, 'moex-akcii/mgts-5'),
    'MERF': ('МЕРИДИАН', 20947, 'moex-akcii/meridian-ao'), 'CBOM': ('МКБ ао', 420694, 'moex-akcii/oao-mkb-ao'),
    'MAGN': ('ММК', 16782, 'moex-akcii/mmk'), 'MSRS': ('МОЭСК', 16917, 'moex-akcii/moesk'),
    'MRKZ': ('МРСК СЗ', 20309, 'moex-akcii/mrsk-severo-zapada'),
    'MRKK': ('МРСК СК', 20412, 'moex-akcii/mrsk-severnogo-kavkaza-ao'),
    'MRKU': ('МРСК Ур', 20402, 'moex-akcii/mrsk-urala-ao'), 'MRKP': ('МРСК ЦП', 20107, 'moex-akcii/mrsk-cip'),
    'MRKC': ('МРСК Центр', 20235, 'moex-akcii/mrsk-centra'), 'MRKV': ('МРСКВол', 20286, 'moex-akcii/mrsk-volgi'),
    'MRKS': ('МРСКСиб', 20346, 'moex-akcii/mrsk-sibiri'), 'MRKY': ('МРСКЮга ао', 20681, 'moex-akcii/mrsk-yuga'),
    'MTSS': ('МТС-ао', 15523, 'moex-akcii/mts'), 'MAGE': ('МагадЭн ао', 74562, 'moex-akcii/magadanenergo-ao'),
    'MAGEP': ('МагадЭн ап', 74563, 'moex-akcii/magadanenergo-ap'), 'MGNT': ('Магнит ао', 17086, 'moex-akcii/magnit'),
    'MFON': ('МегаФон ао', 152516, 'moex-akcii/megafon-ao'), 'MFGS': ('Мегион-ао', 30, 'moex-akcii/megion'),
    'MFGSP': ('Мегион-ап', 51, 'moex-akcii/megion-pref'), 'ODVA': ('Медиахолд', 20737, 'moex-akcii/mediaholding'),
    'MTLR': ('Мечел ао', 21018, 'moex-akcii/mechel'), 'MTLRP': ('Мечел ап', 80745, 'moex-akcii/mechel-pref'),
    'MRSB': ('МордЭнСб', 16359, 'moex-akcii/mordovskaya-energosbyt-comp'),
    'MORI': ('Морион ао', 81944, 'moex-akcii/morion-ao'), 'MOEX': ('МосБиржа', 152798, 'moex-akcii/moscowexchange'),
    'MOBB': ('МосОблБанк', 82890, 'moex-akcii/akb-moskovskii-oblastnoi-bank'),
    'MSTT': ('Мостотрест', 74549, 'moex-akcii/mostotrest'),
    'MSST': ('МультиСис', 152676, 'moex-akcii/mul-tisistema-ao'),
    'NKNC': ('НКНХ ао', 20100, 'moex-akcii/niznekamskneftekhim-ao'),
    'NKNCP': ('НКНХ ап', 20101, 'moex-akcii/niznekamskneftekhim-pref'),
    'NKHP': ('НКХП ао', 450432, 'moex-akcii/nkhp-ao'), 'NLMK': ('НЛМК ао', 17046, 'moex-akcii/nlmk-ao'),
    'NMTP': ('НМТП ао', 19629, 'moex-akcii/nmtp'), 'NSVZ': ('НаукаСвяз', 81929, 'moex-akcii/nauka-svyaz-oao-ao'),
    'NFAZ': ('Нефтекамск', 81287, 'moex-akcii/neftekamskiy-avtozavod-oao-ao'),
    'NKSH': ('Нижкамшина', 81947, 'moex-akcii/nizhnekamskshina-ao'),
    'NVTK': ('Новатэк ао', 17370, 'moex-akcii/novatek'), 'UWGN': ('ОВК ао', 414560, 'moex-akcii/ovk-ao'),
    'OGKB': ('ОГК-2 ао', 18684, 'moex-akcii/ogk-2'), 'UCSS': ('ОКС ао', 175781, 'moex-akcii/pao-oks-ao'),
    'OMZZP': ('ОМЗ-ап', 15844, 'moex-akcii/omz-pref'), 'OBUV': ('ОР ао', 488674, 'moex-akcii/or'),
    'KZOS': ('ОргСинт ао', 81856, 'moex-akcii/oao-organicheskiy-sintez-ao'),
    'KZOSP': ('ОргСинт ап', 81857, 'moex-akcii/oao-organicheskiy-sintez-ap'),
    'GTLC': ('ПАОДжиТиЭл', 152876, 'moex-akcii/oao-gtl-ao'), 'PIKK': ('ПИК ао', 18654, 'moex-akcii/pik'),
    'PRTK': ('ПРОТЕК ао', 35247, 'moex-akcii/protek-ao'), 'PAZA': ('ПавлАвт ао', 81896, 'moex-akcii/pavlovo-bus-ao'),
    'PMSBP': ('ПермьЭнС-п', 16909, 'moex-akcii/perm-energosbyt-pref'),
    'PMSB': ('ПермьЭнСб', 16908, 'moex-akcii/perm-energosbyt'), 'PLSM': ('Плазмек', 81241, 'moex-akcii/plazmek-ao'),
    'PLZL': ('Полюс', 17123, 'moex-akcii/polus-zoloto'), 'PRMB': ('Приморье', 80818, 'moex-akcii/akb-primorye'),
    'RBCM': ('РБК ао', 74779, 'moex-akcii/rbk-ao'), 'RGSS': ('РГС СК ао', 181934, 'moex-akcii/jsc-rosgosstrakh-ao'),
    'RDRB': ('РДБанк ао', 181755, 'moex-akcii/rosdor-bank-ao'),
    'CHGZ': ('РН-ЗапСиб', 81933, 'moex-akcii/chernogorneft-ao'),
    'ROST': ('РОСИНТЕРао', 20637, 'moex-akcii/rosinter-restaurants-ao'),
    'RASP': ('Распадская', 17713, 'moex-akcii/raspadskaya'), 'RLMN': ('Роллман', 152677, 'moex-akcii/rollman-gk-ao'),
    'RLMNP': ('Роллман-п', 388313, 'moex-akcii/rollman-gk-ap'), 'ROSB': ('Росбанк ао', 16866, 'moex-akcii/rosbank'),
    'ROSN': ('Роснефть', 17273, 'moex-akcii/rosneft'), 'RSTI': ('Россети ао', 20971, 'moex-akcii/rosseti-ao'),
    'RSTIP': ('Россети ап', 20972, 'moex-akcii/rosseti-ap'), 'RTKM': ('Ростел -ао', 7, 'moex-akcii/rostelecom'),
    'RTKMP': ('Ростел -ап', 15, 'moex-akcii/rostelecom-pref'),
    'AQUA': ('РусАква ао', 35238, 'moex-akcii/russkaya-akvakul-tura'),
    'HYDR': ('РусГидро', 20266, 'moex-akcii/rusgidro'), 'RUGR': ('Русгрэйн', 66893, 'moex-akcii/rusgrain-holding-ao'),
    'ROLO': ('Русолово', 181316, 'moex-akcii/rusolovo-oao-ao'),
    'RUSP': ('Русполимет', 20712, 'moex-akcii/ruspolimet-ao'), 'RNFT': ('РуссНфт ао', 465236, 'moex-akcii/russneft-nk'),
    'RZSB': ('РязЭнСб', 16455, 'moex-akcii/ryazan-energo-sbyt'),
    'SFIN': ('САФМАР ао', 491359, 'moex-akcii/safmar-fin-invest-ao'),
    'SZPR': ('СЗПароход', 22401, 'moex-akcii/severo-zapadnoe-parokhodstvo'),
    'MGNZ': ('СМЗ-ао', 20892, 'moex-akcii/smz'), 'SVAV': ('СОЛЛЕРС', 16080, 'moex-akcii/sollers'),
    'SAGO': ('СамарЭн-ао', 445, 'moex-akcii/samaraenergo-ao'),
    'SAGOP': ('СамарЭн-ап', 70, 'moex-akcii/samaraenergo-pref'),
    'KRKN': ('СаратНПЗ', 81891, 'moex-akcii/saratovskiy-npz-ao'),
    'KRKNP': ('СаратНПЗ-п', 81892, 'moex-akcii/saratovskiy-npz-ap'),
    'SARE': ('СаратЭн-ао', 11, 'moex-akcii/saratovenergo-ao'),
    'SAREP': ('СаратЭн-ап', 24, 'moex-akcii/saratovenergo-pref'),
    'SLEN': ('Сахэнер ао', 473000, 'moex-akcii/sakhalinenergo-ao'), 'SBER': ('Сбербанк', 3, 'moex-akcii/sberbank'),
    'SBERP': ('Сбербанк-п', 23, 'moex-akcii/sberbank-pref'), 'CHMF': ('СевСт-ао', 16136, 'moex-akcii/severstal-ao'),
    'SELG': ('Селигдар', 81360, 'moex-akcii/seligdar'), 'SELGP': ('Селигдар-п', 82610, 'moex-akcii/seligdar-ap'),
    'SIBG': ('СибГост ао', 436091, 'moex-akcii/pao-sibirskiy-gostinec-ao'),
    'AFKS': ('Система ао', 19715, 'moex-akcii/afk-sistema'),
    'JNOSP': ('Слав-ЯНОСп', 15723, 'moex-akcii/slavneft-janos-pref'),
    'JNOS': ('Славн-ЯНОС', 15722, 'moex-akcii/slavneft-janos'),
    'STSB': ('СтаврЭнСб', 20087, 'moex-akcii/stavropolenergosbyt'),
    'STSBP': ('СтаврЭнСбп', 20088, 'moex-akcii/stavropolenergosbyt-pref'), 'SNGS': ('Сургнфгз', 4, 'moex-akcii/surgut'),
    'SNGSP': ('Сургнфгз-п', 13, 'moex-akcii/surgut-pref'), 'TANL': ('ТАНТАЛ ао', 81914, 'moex-akcii/tantal-ao'),
    'TANLP': ('ТАНТАЛ ап', 81915, 'moex-akcii/tantal-ap'), 'TGKA': ('ТГК-1', 18382, 'moex-akcii/tgk-1'),
    'TGKN': ('ТГК-14', 18176, 'moex-akcii/tgk-14'), 'TGKB': ('ТГК-2', 17597, 'moex-akcii/tgk-2'),
    'TGKBP': ('ТГК-2 ап', 18189, 'moex-akcii/tgk-2-pref'),
    'TUZA': ('ТЗА ао', 20716, 'moex-akcii/tuimaz-zavod-avtobetonovozov'),
    'KRKO': ('ТКЗКК ао', 81905, 'moex-akcii/tkz-krasny-kotelshchik-ao'),
    'KRKOP': ('ТКЗКК ап', 81906, 'moex-akcii/tkz-krasny-kotelshchik-ap'),
    'TUCH': ('ТКСМ ао', 74746, 'moex-akcii/tuchkovsk-csm'), 'TRMK': ('ТМК ао', 18441, 'moex-akcii/tmk-ao'),
    'KBSB': ('ТНСэКубань', 19916, 'moex-akcii/kuban-energosbyt-company'),
    'MISBP': ('ТНСэМаЭл-п', 16331, 'moex-akcii/marienergosbyt-pref'),
    'VRSBP': ('ТНСэнВор-п', 16547, 'moex-akcii/voronezh-energosbyt-comp-pref'),
    'VRSB': ('ТНСэнВорон', 16546, 'moex-akcii/voronezh-energosbyt-comp'),
    'MISB': ('ТНСэнМарЭл', 16330, 'moex-akcii/marienergosbyt-ao'),
    'NNSB': ('ТНСэнНН ао', 16615, 'moex-akcii/nizhegorodskaya-sbyt-comp'),
    'NNSBP': ('ТНСэнНН ап', 16616, 'moex-akcii/nizhegorodskaya-sbyt-comp-pref'),
    'RTSB': ('ТНСэнРст', 16783, 'moex-akcii/rostovenergosbyt-ao'),
    'RTSBP': ('ТНСэнРст-п', 16784, 'moex-akcii/rostovenergosbyt-pref'),
    'YRSB': ('ТНСэнЯр', 16342, 'moex-akcii/yaroslav-sbyt-company-ao'),
    'YRSBP': ('ТНСэнЯр-п', 16343, 'moex-akcii/yaroslav-sbyt-company-pref'),
    'TNSE': ('ТНСэнрг ао', 420644, 'moex-akcii/pao-gk-tns-energo-ao'),
    'TORS': ('ТРК ао', 16797, 'moex-akcii/tomsk-raspredelit-komp-ao'),
    'TORSP': ('ТРК ап', 16798, 'moex-akcii/tomsk-raspredelit-komp-ap'),
    'TASB': ('ТамбЭнСб', 16265, 'moex-akcii/tambov-energosbyt-company'),
    'TASBP': ('ТамбЭнСб-п', 16266, 'moex-akcii/tambov-energosbyt-comp-pref'),
    'TATN': ('Татнфт 3ао', 825, 'moex-akcii/tatneft-3'), 'TATNP': ('Татнфт 3ап', 826, 'moex-akcii/tatneft-pref'),
    'TTLK': ('Таттел. ао', 18371, 'moex-akcii/tattelekom'),
    'CNTL': ('Телеграф', 21002, 'moex-akcii/centrlnyi-telegraf'),
    'CNTLP': ('Телеграф-п', 81575, 'moex-akcii/centrlnyi-telegraf-ap'),
    'TRCN': ('ТрансК ао', 74561, 'moex-akcii/transkonteiner-ao'),
    'TRFM': ('ТрансФ ао', 497210, 'moex-akcii/transfin-m'), 'TRNFP': ('Транснф ап', 1012, 'moex-akcii/transneft-pref'),
    'URKZ': ('УрКузница', 82611, 'moex-akcii/uralskaya-kuznica-ao'),
    'USBN': ('УралСиб ао', 81953, 'moex-akcii/bank-uralsib-ao'), 'URKA': ('Уркалий-ао', 19623, 'moex-akcii/uralkaliy'),
    'FEES': ('ФСК ЕЭС ао', 20509, 'moex-akcii/fsk-ees'), 'NPOF': ('Физика ао', 81858, 'moex-akcii/npo-fizika-ao'),
    'PHOR': ('ФосАгро ао', 81114, 'moex-akcii/phosagro-ao'), 'HIMC': ('Химпром ао', 81939, 'moex-akcii/himprom-ao'),
    'HIMCP': ('Химпром ап', 81940, 'moex-akcii/himprom-ap'), 'WTCM': ('ЦМТ ао', 19095, 'moex-akcii/cmt'),
    'WTCMP': ('ЦМТ ап', 19096, 'moex-akcii/cmt-pref'), 'PRFN': ('ЧЗПСН ао', 83121, 'moex-akcii/czpsn-profnasteel'),
    'CHKZ': ('ЧКПЗ ао', 21000, 'moex-akcii/ckpz'), 'CHMK': ('ЧМК ао', 21001, 'moex-akcii/cmk'),
    'CHEP': ('ЧТПЗ ао', 20999, 'moex-akcii/chtpz'), 'GCHE': ('ЧеркизГ-ао', 20125, 'moex-akcii/gruppa-cherkizovo-ao'),
    'ELTZ': ('Электрцинк', 81934, 'moex-akcii/elektrotsink-ao'),
    'ENRU': ('ЭнелРос ао', 16440, 'moex-akcii/enel-russia'), 'RKKE': ('ЭнергияРКК', 20321, 'moex-akcii/rkk-energia'),
    'UTAR': ('ЮТэйр ао', 15522, 'moex-akcii/utair-aviacompany'),
    'UNKL': ('ЮУНК ао', 82493, 'moex-akcii/uzhno-uralskiy-nikel-komb-ao'),
    'UKUZ': ('ЮжКузб. ао', 20717, 'moex-akcii/uzhnyi-kuzbass'), 'UPRO': ('Юнипро ао', 18584, 'moex-akcii/e-on-russia'),
    'YAKG': ('ЯТЭК ао', 81917, 'moex-akcii/yatek-ao'), 'YKENP': ('Якутскэн-п', 81769, 'moex-akcii/yakutskenergo-ap'),
    'YKEN': ('Якутскэнрг', 81766, 'moex-akcii/yakutskenergo'),
}
