from food.interfaces import PageButton

from food.constants import ServicesEnum
from food.models import Ref


def get_buttons(refs: list[Ref], default_buttons: list[PageButton]) -> list[PageButton]:
    buttons = []
    default_texts = {}
    for b in default_buttons:
        default_texts[b.type] = b.text

    for ref in refs:
        if "market-delivery.yandex.ru" in ref.ref:
            buttons.append(
                PageButton(
                    ref=ref.ref,
                    text=ref.text if ref.text else default_texts.get(ServicesEnum.delivery),
                    type=ServicesEnum.delivery
                )
            )
        elif "eda.yandex.ru" in ref.ref:
            buttons.append(
                PageButton(
                    ref=ref.ref,
                    text=ref.text if ref.text else default_texts.get(ServicesEnum.yandex),
                    type=ServicesEnum.yandex
                )
            )
    
    for service in ServicesEnum.list():
        butt_exists = False
        for button in buttons:
            if button.type == service:
                butt_exists = True
        
        if not butt_exists:
            for default_button in default_buttons:
                if default_button.type == service:
                    buttons.append(default_button)

    return buttons