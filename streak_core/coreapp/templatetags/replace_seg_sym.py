from django import template

register = template.Library()

@register.filter
def replace_seg_sym(value,args):
	# print value,args
	return value.replace('_'+args,"")