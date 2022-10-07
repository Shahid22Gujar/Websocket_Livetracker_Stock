from django import template
register = template.Library()

@register.filter
def get(mapping,key): # mapping is dictionary
    return mapping.get(key, ' ')#if not found then it return Empty string