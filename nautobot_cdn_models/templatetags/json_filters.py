from django import template
import json

register = template.Library()  # Django's register module

@register.filter(name='jsonify')
def jsonify(object):
    if isinstance(object, str):
        return json.loads(object)
    return json.dumps(object, indent=4)
