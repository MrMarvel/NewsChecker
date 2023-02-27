from datetime import date


def get_date_from_str(date_str: str, delimiter=' ') -> date:
    day_str, month_str, year_str = date_str.split(delimiter)
    day = int(day_str)
    month = MONTHS.index(month_str.upper()) + 1
    if month < 1:
        raise Exception(f"Не найден месяц: \"{date_str}\"")
    year = int(year_str)
    if year < 100:
        today = date.today()
        year += today.year // 100 * 100
    return date(year, month, day)


def get_date_from_str_digital(date_str: str, delimiter='.') -> date:
    day_str, month_str, year_str = date_str.split(delimiter)
    day = int(day_str)
    month = int(month_str)
    year = int(year_str)
    return date(year, month, day)


MONTHS = [
    'ЯНВАРЯ',
    'ФЕВРАЛЯ',
    'МАРТА',
    'АПРЕЛЯ',
    'МАЯ',
    'ИЮНЯ',
    'ИЮЛЯ',
    'АВГУСТА',
    'СЕНТЯБРЯ',
    'ОКТЯБРЯ',
    'НОЯБРЯ',
    'ДЕКАБРЯ',
]
