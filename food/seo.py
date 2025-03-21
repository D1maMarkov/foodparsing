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
    print(wildcard_variables)
    if seo.title:
        seo.title = replace_wildcard_templates(seo.title, wildcard_variables)

    if seo.h1:
        seo.h1 = replace_wildcard_templates(seo.h1, wildcard_variables)

    if seo.text:
        seo.text = seo.text.replace("[current_date]", get_formatted_date())
        buttons = wildcard_variables.get("buttons")
        if buttons:
            for button in buttons:
                if button.type == ServicesEnum.delivery:
                    button_html = render_template(app_name="food", template_name="components/link-button", context={"button": button})
                    seo.text = seo.text.replace("[button.delivery]", button_html)
                    seo.text = seo.text.replace("[link_mobile.delivery]", button.ref + "/apps")
                    
                if button.type == ServicesEnum.yandex:
                    button_html = render_template(app_name="food", template_name="components/link-button", context={"button": button})
                    seo.text = seo.text.replace("[button.yandex]", button_html)
                    seo.text = seo.text.replace("[link_mobile.yandex]", button.ref + "/apps")

        seo.text = replace_wildcard_templates(seo.text, wildcard_variables)
    
    if seo.description:
        seo.description = replace_wildcard_templates(seo.description, wildcard_variables)
    
    return seo