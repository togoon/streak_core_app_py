from django import template

register = template.Library()

@register.filter
def space_to_hyphen(value):
	# print value
	return value.replace(" ","_-_")
