from typing import Any

from django import template

register = template.Library()


@register.simple_tag
def url_replace(request, field, value) -> Any:
    """Replace new value for params in query url.

    Avoid having a long query params with the same field by updating that field
    with new value. Reference at: bit.ly/41pKoth

    Example:
        "localhost:8000/?page=3&page=2&page=1"

    Expected:
        "localhost:8000/?page=3"

    """
    data = request.GET.copy()
    data[field] = value
    return data.urlencode()
