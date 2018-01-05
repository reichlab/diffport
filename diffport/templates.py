"""
Report templates
"""

from jinja2 import Template

def tpl(template_text):
    """
    Return a standard jinja2 template
    """

    return Template(template_text, lstrip_blocks=True)

tpl_number_of_rows_hash = tpl("""## Changes in number of rows (using hash)

{% for table in data -%}
### `{{ table[0] }}`

{{ table[1] }}
{% endfor -%}""")

tpl_number_of_rows = tpl("""## Changes in number of rows

{% for table in data -%}
### `{{ table[0] }}`

{{ table[1] }}
{% endfor -%}""")

tpl_schema_tables = tpl("""## Schema table changes

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

tpl_schema_columns = tpl("""## Schema column changes

{% if data|length > 0 -%}
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
  {% endfor -%}
{% else -%}
  *None*
{%- endif %}""")

tpl_table_change = tpl("""## Tables changes

{% if changed_tables|length > 0 -%}
  {% for table in changed_tables -%}
    - {{ table }}
  {% endfor -%}
{% else -%}
  *None*
{% endif %}""")
