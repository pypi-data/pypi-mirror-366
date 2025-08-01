'''
EOAP CWLWrap (c) 2025

EOAP CWLWrap is licensed under
Creative Commons Attribution-ShareAlike 4.0 International.

You should have received a copy of the license along with this work.
If not, see <https://creativecommons.org/licenses/by-sa/4.0/>.
'''

import sys
from .types import (
    Directory_or_File,
    get_assignable_type,
    is_array_type,
    is_directory_compatible_type,
    is_type_assignable_to,
    is_uri_compatible_type,
    is_nullable,
    replace_directory_with_url,
    replace_type_with_url,
    type_to_string,
    URL_SCHEMA,
    validate_directory_stage_in,
    validate_file_stage_in,
    validate_stage_out,
    Workflows
)
from cwl_utils.parser.cwl_v1_2 import (
    InlineJavascriptRequirement,
    ProcessRequirement,
    ScatterFeatureRequirement,
    SchemaDefRequirement,
    SubworkflowFeatureRequirement,
    Workflow,
    WorkflowInputParameter,
    WorkflowOutputParameter,
    WorkflowStep,
    WorkflowStepInput
)
from typing import (
    Any,
    Optional
)
import sys
import time

def _to_workflow_input_parameter(
    source: str,
    parameter: Any,
    target_type: Optional[Any] = None
) -> WorkflowInputParameter:
    return WorkflowInputParameter(
        type_=target_type if target_type else parameter.type_,
        label=f"{parameter.label} - {source}/{parameter.id}" if parameter.label else f"{source}/{parameter.id}",
        secondaryFiles=parameter.secondaryFiles,
        streamable=parameter.streamable,
        doc=f"{parameter.doc} - This parameter is derived from {source}/{parameter.id}" if parameter.label else f"This parameter is derived from: {source}/{parameter.id}",
        id=parameter.id,
        format=parameter.format,
        loadContents=parameter.loadContents,
        loadListing=parameter.loadListing,
        default=parameter.default,
        inputBinding=parameter.inputBinding,
        extension_fields=parameter.extension_fields,
        loadingOptions=parameter.loadingOptions,
    )

def _add_feature_requirement(
    requirement: ProcessRequirement,
    workflow: Workflow
):
    if any(requirement.class_ == current_requirement.class_ for current_requirement in workflow.requirements):
        return;

    workflow.requirements.append(requirement)

def _build_orchestrator_workflow(
    directory_stage_in: Workflow,
    file_stage_in: Workflow,
    workflow: Workflow,
    stage_out: Workflow
) -> Workflow:
    start_time = time.time()
    print(f"Building the CWL Orchestrator Workflow...", file=sys.stderr)

    imports = { URL_SCHEMA }

    def _ad_import(type_string: str):
        if '#' in type_string:
            imports.add(type_string.split('#')[0])

    orchestrator = Workflow(
        id='main',
        label=f"{workflow.class_} {workflow.id} orchestrator",
        doc=f"This Workflow is used to orchestrate the {workflow.class_} {workflow.id}",
        requirements=[SubworkflowFeatureRequirement()],
        inputs=[],
        outputs=[],
        steps=[]
    )

    main_workflow = [ orchestrator ]

    app = WorkflowStep(
        id='app',
        in_=[],
        out=[],
        run=f"#{workflow.id}"
    )

    # inputs

    print(f"Analyzing {workflow.id} inputs...", file=sys.stderr)

    stage_in_counters = {
        'Directory': 0,
        'File': 0
    }

    stage_in_cwl = {
        'Directory': directory_stage_in,
        'File': file_stage_in
    }

    for input in workflow.inputs:
        type_string = type_to_string(input.type_)
        _ad_import(type_string)

        print(f"* {workflow.id}/{input.id}: {type_string}", file=sys.stderr)

        assignable_type = get_assignable_type(actual=input.type_, expected=Directory_or_File)

        target_type = input.type_

        if assignable_type:
            stage_in = stage_in_cwl[type_to_string(assignable_type)]
            if not stage_in:
                sys.exit(f"  input requires a {type_to_string(assignable_type)} stage-in, that was not specified")

            stage_in_id = f"{type_to_string(assignable_type).lower()}_stage_in_{stage_in_counters[type_to_string(assignable_type)]}"

            print(f"  {type_to_string(assignable_type)} type detected, creating a related '{stage_in_id}'...", file=sys.stderr)

            print(f"  Converting {type_to_string(input.type_)} to URL-compatible type...", file=sys.stderr)

            target_type = replace_type_with_url(source=input.type_, to_be_replaced=Directory_or_File)

            print(f"  {type_to_string(input.type_)} converted to {type_to_string(target_type)}", file=sys.stderr)

            workflow_step = WorkflowStep(
                id=stage_in_id,
                in_=[],
                out=list(map(lambda out: out.id, stage_in.outputs)),
                run=f"#{stage_in.id}"
            )

            orchestrator.steps.append(workflow_step)

            for stage_in_input in stage_in.inputs:
                workflow_step.in_.append(
                    WorkflowStepInput(
                        id=stage_in_input.id,
                        source=input.id if is_uri_compatible_type(stage_in_input.type_) else stage_in_input.id
                    )
                )

                if is_uri_compatible_type(stage_in_input.type_):
                    if is_array_type(input.type_):
                        print(f"  Array detected, 'scatter' required for {stage_in_input.id}:{input.id}", file=sys.stderr)

                        workflow_step.scatter = stage_in_input.id
                        workflow_step.scatterMethod = 'dotproduct'

                        _add_feature_requirement(
                            requirement=ScatterFeatureRequirement(),
                            workflow=orchestrator
                        )

                    if is_nullable(input.type_):
                        print(f"  Nullable detected, 'when' required for {stage_in_input.id}:{input.id}", file=sys.stderr)

                        workflow_step.when = f"$(inputs.{stage_in_input.id} !== null)"

                        _add_feature_requirement(
                            requirement=InlineJavascriptRequirement(),
                            workflow=orchestrator
                        )

            print(f"  Connecting 'app/{input.id}' to '{stage_in_id}' output...", file=sys.stderr)

            app.in_.append(
                WorkflowStepInput(
                    id=input.id,
                    source=f"{stage_in_id}/{next(filter(lambda out: is_type_assignable_to(out.type_, Directory_or_File), stage_in.outputs), None).id}"
                )
            )

            if 0 == stage_in_counters[type_to_string(assignable_type)]:
                main_workflow.append(stage_in)

                orchestrator.inputs.extend(
                    list(
                        map(
                            lambda parameter: _to_workflow_input_parameter(stage_in.id, parameter),
                            list(
                                filter(
                                    lambda workflow_input: not is_uri_compatible_type(workflow_input.type_),
                                    stage_in.inputs
                                )
                            )
                        )
                    )
                )

            stage_in_counters[type_to_string(assignable_type)] += 1
        else:
            app.in_.append(
                WorkflowStepInput(
                    id=input.id,
                    source=input.id
                )
            )

        orchestrator.inputs.append(
            _to_workflow_input_parameter(
                source=workflow.id,
                parameter=input,
                target_type=target_type
            )
        )

    # once all '{type}_stage_in_{index}' are defined, we can now append the 'app' step

    main_workflow.append(workflow)

    orchestrator.steps.append(app)

    # outputs

    print(f"Analyzing {workflow.id} outputs...", file=sys.stderr)

    stage_out_counter = 0
    for output in workflow.outputs:
        type_string = type_to_string(output.type_)
        _ad_import(type_string)
        print(f"* {workflow.id}/{output.id}: {type_string}", file=sys.stderr)

        app.out.append(output.id)

        if is_directory_compatible_type(output.type_):
            print(f"  Directory type detected, creating a related 'stage_out_{stage_out_counter}'...", file=sys.stderr)

            print(f"  Converting {type_to_string(output.type_)} to URL-compatible type...", file=sys.stderr)

            url_type = replace_directory_with_url(output.type_)

            print(f"  {type_to_string(output.type_)} converted to {type_to_string(url_type)}", file=sys.stderr)

            workflow_step = WorkflowStep(
                id=f"stage_out_{stage_out_counter}",
                in_=[],
                out=list(map(lambda out: out.id, stage_out.outputs)),
                run=f"#{stage_out.id}"
            )

            orchestrator.steps.append(workflow_step)

            for stage_out_input in stage_out.inputs:
                workflow_step.in_.append(
                    WorkflowStepInput(
                        id=stage_out_input.id,
                        source=f"app/{output.id}" if is_directory_compatible_type(stage_out_input.type_) else stage_out_input.id,
                    )
                )

                if is_directory_compatible_type(stage_out_input.type_):
                    if is_array_type(url_type):
                        print(f"  Array detected, scatter required for {stage_out_input.id}:app/{output.id}", file=sys.stderr)

                        workflow_step.scatter = stage_out_input.id
                        workflow_step.scatterMethod = 'dotproduct'

                        _add_feature_requirement(
                            requirement=ScatterFeatureRequirement(),
                            workflow=orchestrator
                        )

                    if is_nullable(url_type):
                        print(f"  Nullable detected, 'when' required for {stage_out_input.id}:app/{output.id}", file=sys.stderr)

                        workflow_step.when = f"$(inputs.{stage_out_input.id} !== null)"

                        _add_feature_requirement(
                            requirement=InlineJavascriptRequirement(),
                            workflow=orchestrator
                        )

            print(f"  Connecting 'app/{output.id}' to 'stage_out_{stage_out_counter}' output...", file=sys.stderr)

            orchestrator.outputs.append(
                next(
                    map(
                        lambda mapping_output: WorkflowOutputParameter(
                            id=output.id,
                            type_=url_type,
                            outputSource=[f"stage_out_{stage_out_counter}/{mapping_output.id}"],
                            label=output.label,
                            secondaryFiles=output.secondaryFiles,
                            streamable=output.streamable,
                            doc=output.doc,
                            format=output.format,
                            extension_fields=output.extension_fields,
                            loadingOptions=output.loadingOptions
                        ),
                        filter(
                            lambda stage_out_cwl_output: is_uri_compatible_type(stage_out_cwl_output.type_),
                            stage_out.outputs
                        )
                    ),
                    None
                )
            )

            stage_out_counter += 1
        else:
            orchestrator.outputs.append(
                WorkflowOutputParameter(
                    type_=output.type_,
                    label=f"{output.label} - app/{output.id}" if output.label else f"app/{output.id}",
                    secondaryFiles=output.secondaryFiles,
                    streamable=output.streamable,
                    doc=f"{output.doc} - This output is derived from app/{output.id}" if output.label else f"This output is derived from: app/{output.id}",
                    id=output.id,
                    format=output.format,
                    outputSource=[ f"app/{output.id}" ],
                    linkMerge=output.linkMerge,
                    pickValue=output.pickValue,
                    extension_fields=output.extension_fields,
                    loadingOptions=output.loadingOptions
                )
            )

    if stage_out_counter > 0:
        main_workflow.append(stage_out)

        orchestrator.inputs.extend(
            list(
                map(
                    lambda parameter: _to_workflow_input_parameter(stage_out.id, parameter),
                    list(
                        filter(
                            lambda workflow_input: not is_directory_compatible_type(workflow_input.type_),
                            stage_out.inputs
                        )
                    )
                )
            )
        )

    _add_feature_requirement(
        requirement=SchemaDefRequirement(
            types=list(
                map(
                    lambda import_: { '$import': import_ },
                    imports
                )
            )
        ),
        workflow=orchestrator
    )

    end_time = time.time()
    print(f"Orchestrator Workflow built in {end_time - start_time:.4f} seconds", file=sys.stderr)

    return main_workflow

def _search_workflow(workflow_id: str, workflow: Workflows) -> Workflows:
    if isinstance(workflow, list):
        for wf in workflow:
            if workflow_id in wf.id:
                return wf
    elif workflow_id in workflow.id:
        return wf

    sys.exit(f"Sorry, '{workflow_id}' not found in the workflow input file, only {list(map(lambda wf: wf.id, workflow)) if isinstance(workflow, list) else [workflow.id]} available.")

def wrap(
    workflows: Workflow,
    workflow_id: str,
    stage_out: Workflow,
    directory_stage_in: Optional[Workflow] = None,
    file_stage_in: Optional[Workflow] = None
) -> Workflow:
    if directory_stage_in:
        validate_directory_stage_in(directory_stage_in=directory_stage_in)

    if file_stage_in:
        validate_file_stage_in(file_stage_in=file_stage_in)

    workflow = _search_workflow(workflow_id=workflow_id, workflow=workflows)
    validate_stage_out(stage_out=stage_out)

    orchestrator = _build_orchestrator_workflow(
        directory_stage_in=directory_stage_in,
        file_stage_in=file_stage_in,
        workflow=workflow,
        stage_out=stage_out
    )

    if isinstance(workflows, list):
        for wf in workflows:
            if workflow_id not in wf.id:
                orchestrator.append(wf)

    return orchestrator
