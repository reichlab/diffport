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

tpl_table_change = tpl("""## Tables changed

### Watched tables/schemas

{% if watched_schemas|length > 0 -%}
**Schemas**

{% for schema in watched_schemas %}- {{ schema }}
{% endfor -%}
{% endif %}
{% if watched_tables|length > 0 -%}
**Tables**

{% for table in watched_tables %}- {{ table }}
{% endfor -%}
{% endif %}
### Changed tables

{% if changed_tables|length > 0 -%}
  {% for table in changed_tables -%}
    - {{ table }}
  {% endfor -%}
{% else -%}
  *None*
{% endif %}""")
