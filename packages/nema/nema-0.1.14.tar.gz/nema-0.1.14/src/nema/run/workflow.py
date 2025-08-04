from typing import Callable
from functools import wraps
from dataclasses import dataclass
import uuid
from typing import Dict, Any
from types import ModuleType

from nema.run.utils import (
    convert_app_input_to_dict,
    convert_app_output_to_nema_data,
    add_code_directory_to_sys_path,
    call_function,
    extract_output_dict_from_function_output,
)
from nema.workflow.workflow import Workflow


@dataclass
class InternalWorkflowOutput:
    input_data: Any
    output_data: Any
    input_global_id_mapping: Dict[str, int]
    output_global_id_mapping: Dict[str, int]


def workflow(
    input_global_id_mapping: Dict[str, int],
    output_global_id_mapping: Dict[str, int],
    job_id=None,
):
    # create random string if not provided
    actual_job_id = job_id if job_id else str(uuid.uuid4())

    def decorator(func: Callable):

        # Attach the mappings and job ID as attributes to the function
        func.__workflow_attributes__ = {
            "input_global_id_mapping": input_global_id_mapping,
            "output_global_id_mapping": output_global_id_mapping,
            "job_id": actual_job_id,
        }

        @wraps(func)
        def wrapper(*args, **kwargs):

            if len(args) > 0 or len(kwargs) > 0:
                # not running from Nema
                return func(*args, **kwargs)

            # now we need to pull data from Nema and upload the results back

            # check that all global IDs are valid
            for key, g_id in input_global_id_mapping.items():
                if g_id <= 0:
                    raise ValueError(
                        f"Global ID for input {key} is not set. Run `nema-python workflow create-data` to create the data."
                    )

            for key, g_id in output_global_id_mapping.items():
                if g_id <= 0:
                    raise ValueError(
                        f"Global ID for output {key} is not set. Run `nema-python workflow create-data` to create the data."
                    )

            # get the type of func
            annotations = func.__annotations__
            arg_name = list(annotations)[0]
            input_type = annotations[arg_name]
            converted_input = convert_app_input_to_dict(
                input_global_id_mapping, branch="main"
            )

            typed_argument = input_type(**converted_input)

            raw_output = call_function(func, converted_input)

            return InternalWorkflowOutput(
                input_data=typed_argument,
                output_data=raw_output,
                input_global_id_mapping=input_global_id_mapping,
                output_global_id_mapping=output_global_id_mapping,
            )

        return wrapper

    # # close all the data properties in the collection
    # data_collection.close()

    return decorator


def run_workflow(wf: Workflow, python_file: str):

    # to make sure that local imports work, we need to add the directory the code is in to the sys path
    add_code_directory_to_sys_path(python_file)

    # read the python file
    with open(python_file, "r") as f:
        code_to_execute = f.read()

    # execute the application code
    user_module = ModuleType("user_module")

    # load code into module
    exec(code_to_execute, user_module.__dict__)

    # execute code
    output: InternalWorkflowOutput = user_module.run()

    # put output back into the right format
    formatted_output = extract_output_dict_from_function_output(
        user_module.run, output.output_data
    )
    converted_nema_data = convert_app_output_to_nema_data(
        formatted_output, output.output_global_id_mapping
    )

    # sync output to API
    used_data = []
    for key_used, value_used in output.input_global_id_mapping.items():
        used_data.append(
            {
                "artifact": value_used,
                "id_in_function": key_used,
            }
        )

    wf.process_local_update(
        updated_data=converted_nema_data,
        used_data=used_data,
    )
