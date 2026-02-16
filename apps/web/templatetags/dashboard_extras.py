# Template filters for dashboard (safe dict/metadata access)
from django import template

register = template.Library()


@register.filter
def get_item(d, key):
    """Return d[key] or None if key missing. Safe for JSONField/metadata."""
    if d is None:
        return None
    if isinstance(d, dict):
        return d.get(key)
    return None
