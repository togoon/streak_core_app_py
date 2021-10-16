from django import template

register = template.Library()

@register.filter
def name_to_one_avatar(value):
	# print value
	# value = value.strip().split(' ')	
	# value = ''.join([v[0] for v in value][:1])
	return value[0][0]