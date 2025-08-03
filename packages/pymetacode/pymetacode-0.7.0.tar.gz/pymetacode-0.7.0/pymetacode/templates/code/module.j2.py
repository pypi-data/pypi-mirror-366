"""
{{ module.name }} module of the {{ package.name }} package.
"""
{% if options.logging %}
import logging


logger = logging.getLogger(__name__)
{% endif %}

