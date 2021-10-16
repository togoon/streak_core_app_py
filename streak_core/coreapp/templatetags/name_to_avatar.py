from django import template

register = template.Library()

@register.filter
def name_to_avatar(value):
	# print value
	value = value.strip().split(' ')	
	value = ''.join([v[0] for v in value][:2])
	return value