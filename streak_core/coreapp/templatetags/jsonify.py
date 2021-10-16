from django.core.serializers import serialize
from django.db.models.query import QuerySet
import ujson
from django.template import Library

register = Library()

@register.filter( is_safe=True )
def jsonify(object):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return ujson.dumps(object)