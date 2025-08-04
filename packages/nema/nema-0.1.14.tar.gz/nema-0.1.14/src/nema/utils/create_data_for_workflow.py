from typing import List, Type
import json
import re

from nema.data.data import Data
from nema.connectivity import ConnectivityManager


def get_new_data_for_workflow(
    global_id_mapping: dict, argument_type: Type
) -> List[Data]:

    data_to_create: List[Data] = []

    # do this for outputs to TODO
    for key, global_id in global_id_mapping.items():
        if global_id > 0:
            print(f"Data for key '{key}' already exists. Skipping.")
            continue

        # find class for properties
        data_properties_cls = argument_type.__annotations__[key]
        new_data_properties = data_properties_cls()

        data = Data.init_from_properties(
            global_id=0,
            data_properties=new_data_properties,
            id_in_function=key,
        )
        data_to_create.append(data)

    return data_to_create


def submit_new_data_to_nema(data: List[Data]):

    raw_data = []
    for idx, d in enumerate(data):

        raw_data += [
            (
                f"entries[{idx}].data_properties",
                json.dumps(d.data.__nema_marshall__()),
            ),
            (
                f"entries[{idx}].description",
                "<p></p>",
            ),
            (
                f"entries[{idx}].name",
                d.id_in_function,
            ),
            (
                f"entries[{idx}].data_type",
                d.data.data_type,
            ),
        ]

    connectivity_manager = ConnectivityManager()

    resulting_data_ids = connectivity_manager.push_batch_data(raw_data)

    for idx, data_id in enumerate(resulting_data_ids):
        data[idx].global_id = data_id


def update_workflow_file_with_new_global_ids(
    code_str: str, new_data_inputs: List[Data], new_data_outputs: List[Data]
):
    input_mapping_dict = {d.id_in_function: d.global_id for d in new_data_inputs}
    output_mapping_dict = {d.id_in_function: d.global_id for d in new_data_outputs}

    def update_mapping(mapping_block, mapping_dict):
        for key, new_id in mapping_dict.items():
            # Replace the number after "key":
            mapping_block = re.sub(
                rf'("{key}"\s*:\s*)\d+',  # Match the key and the number after ":"
                lambda match: f"{match.group(1)}{new_id}",  # Replace with the new number
                mapping_block,
            )
        return mapping_block

    # Replace input_global_id_mapping block
    input_match = re.search(r"input_global_id_mapping=\{(.*?)\}", code_str, re.DOTALL)
    if input_match:
        input_block = input_match.group(1)
        updated_input_block = update_mapping(input_block, input_mapping_dict)
        code_str = code_str.replace(input_block, updated_input_block)

    # Replace output_global_id_mapping block
    output_match = re.search(r"output_global_id_mapping=\{(.*?)\}", code_str, re.DOTALL)
    if output_match:
        output_block = output_match.group(1)
        updated_output_block = update_mapping(output_block, output_mapping_dict)
        code_str = code_str.replace(output_block, updated_output_block)

    return code_str
