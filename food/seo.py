import re

from food.constants import ServicesEnum
from food.models import Seo
from typing import Any

from django.template import loader
from food.get_current_date import get_formatted_date


def render_template(app_name: str, template_name: str, context: dict[str, Any] | None = None) -> str:
    return loader.render_to_string(f"{app_name}/{template_name}.html", context, None)


def replace_wildcard_templates(string: str, wildcard_variables: dict[str, Any]) -> str:
    wildcard_templates = re.findall(r"\[(.*?)\]", string)
    for wildcard_template in wildcard_templates:
        obj, attr = wildcard_template.split(".")
        try:
            if not (replace_value := getattr(wildcard_variables[obj], attr)):
               replace_value = ""
        except KeyError:
            replace_value = ""
            
        string = string.replace("[" + wildcard_template + "]", str(replace_value))

    return string


def get_wildcard_seo(seo: Seo, wildcard_variables: dict[str, Any]) -> Seo:
    buttons = wildcard_variables.get("buttons")

    for attr_name, attr_type in Seo.__annotations__.items():
        seo_text = getattr(seo, attr_name)
        if attr_type == str and seo_text:
            seo_text = seo_text.replace("[current_date]", get_formatted_date())
            if buttons:
                for button in buttons:
                    if button.type == ServicesEnum.delivery:
                        button_html = render_template(app_name="food", template_name="components/link-button", context={"button": button})
                        seo_text = seo_text.replace("[button.delivery]", button_html)
                        seo_text = seo_text.replace("[link_mobile.delivery]", button.ref + "/apps")
                        
                    if button.type == ServicesEnum.yandex:
                        button_html = render_template(app_name="food", template_name="components/link-button", context={"button": button})
                        seo_text = seo_text.replace("[button.yandex]", button_html)
                        seo_text = seo_text.replace("[link_mobile.yandex]", button.ref + "/apps")

            seo_text = replace_wildcard_templates(seo_text, wildcard_variables)
                        
            setattr(seo, attr_name, seo_text)

    return seo