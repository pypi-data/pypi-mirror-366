"""
EOAP CWLWrap (c) 2025

EOAP CWLWrap is licensed under
Creative Commons Attribution-ShareAlike 4.0 International.

You should have received a copy of the license along with this work.
If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
"""

import sys
from . import wrap
from .loader import (
    load_workflow,
    dump_workflow
)
from .pumler import to_puml
from datetime import datetime
from pathlib import Path
import click
import time

@click.command()
@click.option("--directory-stage-in", required=False, help="The CWL stage-in file for Directory derived types")
@click.option("--file-stage-in", required=False, help="The CWL stage-in file for File derived types")
@click.option("--workflow", required=True, help="The CWL workflow file")
@click.option("--workflow-id", required=True, help="ID of the workflow")
@click.option("--stage-out", required=True, help="The CWL stage-out file")
@click.option("--output", type=click.Path(), required=True, help="Output file path")
@click.option('--puml', is_flag=True, help="Serializes the workflow as PlantUML diagram.")
def main(
    directory_stage_in: str,
    file_stage_in: str,
    workflow: str,
    workflow_id: str,
    stage_out: str,
    output: str,
    puml: bool
):
    start_time = time.time()

    directory_stage_in_cwl = None
    if directory_stage_in:
        directory_stage_in_cwl = load_workflow(path=directory_stage_in)

        print('------------------------------------------------------------------------', file=sys.stderr)

    file_stage_in_cwl = None
    if file_stage_in:
        file_stage_in_cwl = load_workflow(path=file_stage_in)

        print('------------------------------------------------------------------------', file=sys.stderr)

    workflows_cwl = load_workflow(path=workflow)

    print('------------------------------------------------------------------------', file=sys.stderr)

    stage_out_cwl = load_workflow(path=stage_out)

    print('------------------------------------------------------------------------', file=sys.stderr)

    main_workflow = wrap(
        directory_stage_in=directory_stage_in_cwl,
        file_stage_in=file_stage_in_cwl,
        workflows=workflows_cwl,
        workflow_id=workflow_id,
        stage_out=stage_out_cwl
    )

    print('------------------------------------------------------------------------', file=sys.stderr)
    print('BUILD SUCCESS', file=sys.stderr)
    print('------------------------------------------------------------------------', file=sys.stderr)

    print(f"Saving the new Workflow to {output}...", file=sys.stderr)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        dump_workflow(main_workflow, output_path)

    print(f"New Workflow successfully saved to {output}!", file=sys.stderr)

    print('------------------------------------------------------------------------', file=sys.stderr)

    if puml:
        to_puml(
            workflows=main_workflow,
            output=output
        )

        print('--------------------------------------------------------------', file=sys.stderr)

    end_time = time.time()

    print(f"Total time: {end_time - start_time:.4f} seconds", file=sys.stderr)
    print(f"Finished at: {datetime.fromtimestamp(end_time).isoformat(timespec='milliseconds')}", file=sys.stderr)

if __name__ == "__main__":
    main()
