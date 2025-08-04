from types import ModuleType

from nema.workflow.workflow import Workflow
from nema.app.app import App
from nema.app.utils import map_workflow_arguments_to_app_arguments
from nema.run.utils import (
    convert_app_output_to_nema_data,
    convert_app_input_to_dict,
    call_function,
    extract_output_dict_from_function_output,
)


def run_wf_from_app(wf: Workflow, app: App, only_run_outdated: bool = False) -> bool:

    branch_name = "main"

    wf_details = wf.get_workflow_details()

    if only_run_outdated:
        local_status = wf_details["local_status"]["status"]
        if local_status == "UP_TO_DATE":
            print("Skipping workflow as it is up to date\n")
            return False

    # execute the application code
    user_module = ModuleType("user_module")

    # retrieve inputs for this workflow
    formatted_input_data = map_workflow_arguments_to_app_arguments(
        wf_details["input_data"], app.app_io.input_data
    )
    formatted_output_data = map_workflow_arguments_to_app_arguments(
        wf_details["output_data"], app.app_io.output_data
    )

    converted_input = convert_app_input_to_dict(
        formatted_input_data, branch=branch_name
    )

    # load code into module
    exec(app.code, user_module.__dict__)

    # execute code
    raw_output = call_function(user_module.run, converted_input)

    output = extract_output_dict_from_function_output(user_module.run, raw_output)

    # put output back into the right format
    converted_nema_data = convert_app_output_to_nema_data(output, formatted_output_data)

    # sync output to API
    wf.push_outputs_to_API(converted_nema_data, branch_name=branch_name, local=True)

    return True
