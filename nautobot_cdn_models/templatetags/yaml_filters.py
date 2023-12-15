from django import template
import yaml
import json

register = template.Library()  # Django's register module

@register.filter(name='jsonify_yaml')
def yamify(object):
    if isinstance(object, str):
        # Load the JSON string to a Python object.
        object = json.loads(object)
    # Convert the Python object to YAML.
    return yaml.safe_dump(object, allow_unicode=True, default_flow_style=False)
