from django import template

register = template.Library()

@register.filter
def mod7(value):
	# print value
	value = int(value)%7+1
	return value