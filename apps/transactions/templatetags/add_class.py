from typing import Any

from django import template

register = template.Library()


@register.filter
def add_class(field, css) -> Any:
    """Add css class inside a html tag."""
    definition = field.as_widget(attrs={"class": css})
    return definition
