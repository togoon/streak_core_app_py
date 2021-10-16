from django import template

register = template.Library()

@register.filter
def first_name(value):
	# print value
	or_value = value
	value = value.strip().split(' ')	
	if(len(value)>0):
		value = value[0]
	else:
		value = or_value
	return value