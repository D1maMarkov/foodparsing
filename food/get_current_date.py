import datetime

from food.constants import MONTH_NAMES


def get_formatted_date() -> str:
    now = datetime.datetime.now()
    day = now.day
    month = MONTH_NAMES[now.month - 1]
    year = now.year
    return f"{day} {month} {year}"
