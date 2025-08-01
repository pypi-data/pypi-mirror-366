"""
EOAP CWLWrap (c) 2025

EOAP CWLWrap is licensed under
Creative Commons Attribution-ShareAlike 4.0 International.

You should have received a copy of the license along with this work.
If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
"""

import sys
from .types import type_to_string
from cwl_utils.parser.cwl_v1_2 import Workflow
from jinja2 import Environment
from pathlib import Path

_COMPONENTS_TEMPLATE = """@startuml
skinparam linetype ortho

{% for workflow in workflows %}
node "{{ workflow.class_ }} '{{ workflow.id }}'" {
    component "{{ workflow.id }}" as {{ workflow.id | to_puml_name }} {
    {% for input in workflow.inputs %}
        portin "{{ input.id }}" as {{ workflow.id | to_puml_name }}_{{ input.id | to_puml_name }}
    {% endfor %}
    {% for output in workflow.outputs %}
        portout "{{ output.id }}" as {{ workflow.id | to_puml_name }}_{{ output.id | to_puml_name }}
    {% endfor %}
    }

{% for step in workflow.steps %}
    component "{{ step.id }}" as {{ workflow.id | to_puml_name }}_{{ step.id | to_puml_name }} {
    {% for input in step.in_ %}
        portin "{{ input.id }}" as {{ workflow.id | to_puml_name }}_{{ step.id | to_puml_name }}_{{ input.id | to_puml_name }}
        {{ workflow.id | to_puml_name }}_{{ input.source | replace('/', '_') | to_puml_name }} .down.> {{ workflow.id | to_puml_name }}_{{ step.id | to_puml_name }}_{{ input.id | to_puml_name }}
    {% endfor %}

    {% for output in step.out %}
        portout "{{ output }}" as {{ workflow.id | to_puml_name }}_{{ step.id | to_puml_name }}_{{ output | to_puml_name }}
    {% endfor %}
    }
{% endfor %}
}
{% endfor %}

{% for workflow in workflows %}
    {% for output in workflow.outputs %}
        {% for outputSource in output.outputSource %}
{{ workflow.id | to_puml_name }}_{{ outputSource | replace('/', '_') | to_puml_name }} .up.> {{ workflow.id | to_puml_name }}_{{ output.id | to_puml_name }}
        {% endfor %}
    {% endfor %}

    {% for step in workflow.steps %}
{{ workflow.id | to_puml_name }}_{{ step.id | to_puml_name }} .right.> {{ step.run[1:] | to_puml_name }}
    {% endfor %}
{% endfor %}
@enduml
"""

_CLASS_TEMPLATE = '''@startuml

{% for workflow in workflows %}
class "{{ workflow.id }}" as {{ workflow.id | to_puml_name }} extends {{ workflow.class_ }} {
    __ Inputs __
    {% for input in workflow.inputs %}
    + {{ input.id }}: {{ input.type_ | type_to_string }}{% if input.default %} = {{ input.default }}{% endif %}
    {% endfor %}

    __ Outputs __
    {% for output in workflow.outputs %}
    + {{ output.id }}: {{ output.type_ | type_to_string }}
    {% endfor %}

    {% if workflow.steps is defined %}
    __ Steps __
        {% for step in workflow.steps %}
    - {{ step.id }}: {{ step.run[1:] | to_puml_name }}
        {% endfor %}
    {% endif %}
}

    {% for requirement in workflow.requirements %}
        {% if requirement.class_ %}
{{ workflow.id | to_puml_name }} --> {{ requirement.class_ }}
        {% endif %}
    {% endfor %}
{% endfor %}

{% for workflow in workflows %}
    {% for step in workflow.steps %}
{{ workflow.id | to_puml_name }} --> {{ step.run[1:] | to_puml_name }}
    {% endfor %}

    {% for input in workflow.inputs %}
        {% if input.doc or input.label %}
note left of {{ workflow.id | to_puml_name }}::{{ input.id }}
    {% if input.doc %}{{ input.doc }}{% else %}{{ input.label }}{% endif %}
end note
        {% endif %}
    {% endfor %}
{% endfor %}
@enduml
'''

def to_puml_name(identifier: str) -> str:
    return identifier.replace('-', '_')

def to_puml(workflows: list[Workflow], output: str):
    env = Environment()
    env.filters['to_puml_name'] = to_puml_name
    env.filters['type_to_string'] = type_to_string

    for diagram_type, sring_template in { 'components': _COMPONENTS_TEMPLATE, 'class': _CLASS_TEMPLATE }.items():
        output_path = Path(output)
        output_path = Path(f"{output_path.parent}/{diagram_type}.puml")

        print(f"Saving the new PlantUML Workflow diagram to {output_path}...", file=sys.stderr)

        template = env.from_string(sring_template)

        with output_path.open("w") as f:
            f.write(template.render(workflows=workflows))

        print(f"PlantUML Workflow diagram successfully saved to {output_path}!", file=sys.stderr)
