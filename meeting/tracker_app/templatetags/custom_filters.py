from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='replace_underscore')
def replace_underscore(value):
    return value.replace('_', ' ').title()
