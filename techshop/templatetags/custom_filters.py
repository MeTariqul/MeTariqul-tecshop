from django import template
from django.template import Context

register = template.Library()

@register.filter
def equals(value, arg):
    """Check if value equals arg"""
    return str(value) == str(arg)

@register.simple_tag
def select_if(value, arg):
    """Return 'selected' if value equals arg"""
    if str(value) == str(arg):
        return 'selected'
    return ''

@register.simple_tag
def currency(value):
    """Format price with currency short form from settings"""
    from admin_dashboard.models import SiteConfiguration
    try:
        config = SiteConfiguration.objects.first()
        currency_code = config.currency_short_form if config else 'USD'
    except:
        currency_code = 'USD'
    return f"{currency_code} {value}"
