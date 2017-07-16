"""
Report templates
"""

from jinja2 import Template

def tpl(template_text):
    """
    Return a standard jinja2 template
    """

    return Template(template_text, lstrip_blocks=True)

tpl_tables_in_schema = tpl("""## Schema changes

### `{{ schema_name }}`

Added tables:

{% if added_tables|length > 0 -%}
  {% for table in added_tables -%}
    - {{ table }}
  {% endfor -%}
{% else -%}
  *None*
{% endif %}
Removed tables:

{% if removed_tables|length > 0 %}
  {% for table in removed_tables -%}
    - {{ table }}
  {% endfor %}
{% else -%}
  *None*
{%- endif %}""")
