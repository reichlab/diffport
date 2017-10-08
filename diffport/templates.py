"""
Report templates
"""

from jinja2 import Template

def tpl(template_text):
    """
    Return a standard jinja2 template
    """

    return Template(template_text, lstrip_blocks=True)

tpl_number_of_rows = tpl("""## Number of rows changes

### `{{ table_name }}`

{{ change }}""")

tpl_tables_in_schema = tpl("""## Schema table changes

{% for schema in data -%}
### `{{ schema[0] }}`

Added tables:

{% if schema[1]['added']|length > 0 -%}
  {% for table in schema[1]['added'] -%}
    - {{ table }}
  {% endfor -%}
{% else -%}
  *None*
{% endif %}
Removed tables:

{% if schema[1]['removed']|length > 0 -%}
  {% for table in schema[1]['removed'] -%}
    - {{ table }}
  {% endfor %}
{% else -%}
  *None*
{%- endif %}
{% endfor -%}""")

tpl_columns_in_schema = tpl("""## Schema column changes

{% for schema in data -%}
### `{{ schema[0] }}`

Added columns:

{% if schema[1]['added']|length > 0 -%}
  {% for column in schema[1]['added'] -%}
    - {{ column }}
  {% endfor -%}
{% else -%}
  *None*
{% endif %}
Removed columns:

{% if schema[1]['removed']|length > 0 -%}
  {% for column in schema[1]['removed'] -%}
    - {{ column }}
  {% endfor %}
{% else -%}
  *None*
{%- endif %}
{% endfor -%}""")

tpl_table_change = tpl("""## Tables changed

### Watched tables/schemas

### Changed tables

{% if changed_tables|length > 0 -%}
  {% for table in changed_tables -%}
    - {{ table }}
  {% endfor -%}
{% else -%}
  *None*
{% endif %}""")
