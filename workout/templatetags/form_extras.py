from django import template
register = template.Library()

@register.filter
def add_class(bound_field, css):
    return bound_field.as_widget(attrs={**bound_field.field.widget.attrs, "class": css})