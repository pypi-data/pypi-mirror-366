"""
EOAP CWLWrap (c) 2025

EOAP CWLWrap is licensed under
Creative Commons Attribution-ShareAlike 4.0 International.

You should have received a copy of the license along with this work.
If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
"""

import sys
from .types import Workflows
from cwl_utils.parser import load_document_by_yaml, save
from cwl_utils.parser.cwl_v1_2 import Workflow
from cwltool.load_tool import default_loader
from cwltool.update import update
from ruamel.yaml import YAML
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import gzip
import io
import requests
import os

__TARGET_CWL_VERSION__ = 'v1.2'

yaml = YAML()

def _clean_part(
    value: str,
    separator: str = '/'
) -> str:
    return value.split(separator)[-1]

def _clean_workflow(workflow: Any):
    workflow.id = _clean_part(workflow.id, '#')

    print(f"  Cleaning {workflow.class_} {workflow.id}...", file=sys.stderr)

    for parameters in [ workflow.inputs, workflow.outputs ]:
        for parameter in parameters:
            parameter.id = _clean_part(parameter.id)

            if hasattr(parameter, 'outputSource'):
                for i, output_source in enumerate(parameter.outputSource):
                    parameter.outputSource[i] = _clean_part(output_source, f"{workflow.id}/")

    for step in getattr(workflow, 'steps', []):
        step.id = _clean_part(step.id)

        for step_in in getattr(step, 'in_', []):
            step_in.id = _clean_part(step_in.id)
            step_in.source = _clean_part(step_in.source, f"{workflow.id}/")

        if step.out:
            if isinstance(step.out, list):
                step.out = [_clean_part(step_out) for step_out in step.out]
            else:
               step.out = _clean_part(step)

        if step.run:
            step.run = step.run[step.run.rfind('#'):]

        if step.scatter:
            if isinstance(step.scatter, list):
                step.scatter = [_clean_part(scatter, f"{workflow.id}/") for scatter in step.scatter]
            else:
                step.scatter = _clean_part(step.scatter, f"{workflow.id}/")

def _is_url(path_or_url: str) -> bool:
    try:
        result = urlparse(path_or_url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except Exception:
        return False

def load_workflow(path: str) -> Workflows:
    print(f"Loading CWL document from {path}...", file=sys.stderr)

    if _is_url(path):
        response = requests.get(path, stream=True)
        response.raise_for_status()

        # Read first 2 bytes to check for gzip
        magic = response.raw.read(2)
        remaining = response.raw.read()  # Read rest of the stream
        combined = io.BytesIO(magic + remaining)

        if magic == b'\x1f\x8b':
            decompressed = gzip.GzipFile(fileobj=combined)
            raw_workflow = yaml.load(io.TextIOWrapper(decompressed, encoding='utf-8'))
        else:
            raw_workflow = yaml.load(io.TextIOWrapper(combined, encoding='utf-8'))
    elif os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            raw_workflow = yaml.load(f)
    else:
        raise ValueError(f"Invalid source {path}: not a URL or existing file path")

    print(f"Raw CWL document successfully loaded from {path}! Now updating the model to v1.2...", file=sys.stderr)

    updated_workflow = update(
        doc=raw_workflow,
        loader=default_loader(),
        baseuri=path,
        enable_dev=False,
        metadata={'cwlVersion': __TARGET_CWL_VERSION__},
        update_to=__TARGET_CWL_VERSION__
    )

    print('Raw CWL document successfully updated! Now converting to the CWL model...', file=sys.stderr)

    workflow = load_document_by_yaml(
        yaml=updated_workflow,
        uri=path,
        load_all=True
    )

    print('Raw CWL document successfully updated! Now dereferencing the FQNs...', file=sys.stderr)

    if isinstance(workflow, list):
        for wf in workflow:
            _clean_workflow(wf)
    else:
        _clean_workflow(workflow)

    print(f"CWL document successfully dereferenced!", file=sys.stderr)

    return workflow

def dump_workflow(
    workflow: Workflows,
    stream: Any
):
    data = save(
        val=workflow,
        relative_uris=False
    )
    yaml.dump(data=data, stream=stream)
