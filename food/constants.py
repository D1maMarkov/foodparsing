from enum import StrEnum


FOOTER_CITY_NAMES = [
    "Москва",
    "Санкт-Петербург",
    "Нижний Новгород",
    "Екатеринбург",
    "Казань",
    "Краснодар",
    "Ростов-на-Дону",
    "Уфа",
    "Саратов",
    "Иркутск",
    "Красноярск",
    "Новосибирск",
]

BLOCK_CITIES = [
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Красноярск",
    "Нижний Новгород",
    "Челябинск",
]

MONTH_NAMES = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
]

class ServicesEnum(StrEnum):
    yandex = "Яндекс"
    delivery = "Деливери"
    
    @classmethod
    def list(cls) -> list[str]:
        return [e.value for e in cls]