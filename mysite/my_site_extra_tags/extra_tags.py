
from django import template
register = template.Library()

@register.simple_tag
def total_value_item_cart(qty,price,*args, **kwargs):
    return qty*price