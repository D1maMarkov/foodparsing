from dataclasses import dataclass
from food.constants import ServicesEnum


@dataclass
class PageButton:
    type: ServicesEnum
    ref: str
    text: str