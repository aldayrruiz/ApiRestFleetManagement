from django import template

register = template.Library()


@register.filter(name='euros')
def euros(value):
    if value:
        return f'{value} €'
    else:
        return '-'


@register.filter(name='bool')
def bool(value):
    if value:
        return 'S'
    else:
        return 'N'
