"""
Report templates
"""

from jinja2 import Template

def tpl(template_text):
    """
    Return a standard jinja2 template
    """

    return Template(template_text, lstrip_blocks=True)

tpl_tables_in_schema = tpl("""## Schema table changes

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

tpl_columns_in_schema = tpl("""## Schema column changes

### `{{ schema_name }}`

Added columns:

{% if added_columns|length > 0 -%}
  {% for column in added_columns -%}
    - {{ column }}
  {% endfor -%}
{% else -%}
  *None*
{% endif %}
Removed columns:

{% if removed_columns|length > 0 %}
  {% for column in removed_columns -%}
    - {{ column }}
  {% endfor %}
{% else -%}
  *None*
{%- endif %}""")

