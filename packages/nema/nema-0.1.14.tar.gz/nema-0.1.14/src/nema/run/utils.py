from typing import List
import os
import sys
import inspect
from dataclasses import is_dataclass, fields
import pint
import typing

from nema.data.data_properties import (
    DataProperties,
    StringValue,
    FloatValue,
    FloatValueWithPhysicalUnit,
    IntegerValue,
    BooleanValue,
)
from nema.connectivity import CONNECTIVITY_CONFIG
from nema.data.data import Data, FileData


def get_data_properties_from_global_id(global_id: int, branch: str) -> DataProperties:
    data = Data.init_from_cloud_and_download(global_id, branch=branch)

    if data.data.is_blob_data:
        data = FileData(
            _global_id=global_id,
            _data=data.data,
            _input_folder=CONNECTIVITY_CONFIG.nema_data_folder,
            _branch=branch,
        )

        # TODO: this is super messy!
        if hasattr(data.data, "get_contents"):

            data.contents  # this downloads the file and extracts the contents

        elif hasattr(data.data, "get_file_name"):

            data.get_file_path()  # this downloads the file

    return data.data  # return the data properties


def convert_app_input_to_dict(inputs: dict, branch: str = "main") -> dict:
    """The input is a dictionary of global IDs. This function will convert the global IDs to the actual data properties"""
    converted_input = {}
    for key, value in inputs.items():
        if isinstance(value, list):
            converted_input[key] = [
                get_data_properties_from_global_id(v, branch) for v in value
            ]
        elif isinstance(value, dict):
            converted_input[key] = convert_app_input_to_dict(value, branch)
        else:
            converted_input[key] = get_data_properties_from_global_id(value, branch)

    return converted_input


def convert_app_output_to_nema_data(output, output_dict: dict) -> List[Data]:
    """The output is a dictionary of data properties. This function will convert the properties to Nema Data objects, which can be uploaded to Nema"""

    converted_output = []
    for key, value in output_dict.items():
        this_output = output.get(key)
        if isinstance(value, list):
            for idx, lv in enumerate(value):
                converted_output.append(
                    Data.init_from_properties(
                        global_id=lv, data_properties=this_output[idx]
                    )
                )
        elif isinstance(value, dict):
            for lk, lv in zip(value, getattr(output, key)):
                converted_output.append(
                    Data.init_from_properties(
                        global_id=lv, data_properties=this_output[lk]
                    )
                )
        else:
            converted_output.append(
                Data.init_from_properties(value, this_output, id_in_function=key)
            )

    return converted_output


def map_input_primitive_to_required_type(
    input_data_properties: DataProperties, input_type: type
):

    if (
        input_type == str
        or input_type == int
        or input_type == float
        or input_type == bool
        or input_type == pint.Quantity
    ):
        return input_data_properties.value

    return input_data_properties


def map_output_raw_to_data_properties(raw_output) -> DataProperties:

    if isinstance(raw_output, str):
        return StringValue(value=raw_output)

    if isinstance(raw_output, int):
        return IntegerValue(value=raw_output)

    if isinstance(raw_output, float):
        return FloatValue(value=raw_output)

    if isinstance(raw_output, bool):
        return BooleanValue(value=raw_output)

    if isinstance(raw_output, pint.Quantity):
        return FloatValueWithPhysicalUnit(value=raw_output)

    return raw_output


def call_function(func, inputs_dict):
    """
    Call `func` using values from `inputs_dict`.

    For each parameter of `func`:
      - If the parameter is annotated with a dataclass, instantiate that dataclass
        from the matching fields in `inputs_dict`.
      - Otherwise, use the matching key from `inputs_dict` directly.

    Example: If the function signature is:
        run(inputs: Inputs, c: bool) -> float
    and 'Inputs' has fields 'a', 'b',
    and inputs_dict = {"a": "add", "b": 5, "c": True},
    then:
      - 'inputs' parameter gets constructed by Inputs(a="add", b=5).
      - 'c' parameter is set to True.
    """
    sig = inspect.signature(func)
    bound_args = {}

    for param_name, param in sig.parameters.items():
        # The user must provide a type annotation, or we can't infer a dataclass
        param_type = param.annotation

        if param_type == inspect.Parameter.empty:
            # No type annotation => pass the dictionary value directly
            if param_name not in inputs_dict:
                raise ValueError(f"Missing value for parameter '{param_name}'.")
            bound_args[param_name] = map_input_primitive_to_required_type(
                inputs_dict[param_name], None
            )
            continue

        if is_dataclass(param_type) and not issubclass(param_type, DataProperties):
            # It's a dataclass. Collect the subfields from the dictionary.
            subfields = {(f.name, f.type) for f in fields(param_type)}
            subdict = {}
            for fname, ftype in subfields:
                if fname not in inputs_dict:
                    raise ValueError(
                        f"Missing value for field '{fname}' of dataclass '{param_type.__name__}'."
                    )
                subdict[fname] = map_input_primitive_to_required_type(
                    inputs_dict[fname], ftype
                )
            bound_args[param_name] = param_type(**subdict)
        else:
            # It's a normal (non-dataclass) parameter. Use the direct key from inputs_dict
            if param_name not in inputs_dict:
                raise ValueError(f"Missing value for parameter '{param_name}'.")
            bound_args[param_name] = map_input_primitive_to_required_type(
                inputs_dict[param_name], param_type
            )

    return func(**bound_args)


def extract_output_dict_from_function_output(func, output):

    sig = inspect.signature(func)

    # 2) Inspect the return annotation
    return_type = sig.return_annotation
    # If there's no type annotation, just return the raw result
    if return_type == inspect.Signature.empty:
        return {"output": map_output_raw_to_data_properties(output)}

    # 2a) If it's a dataclass, convert to a dictionary
    if is_dataclass(return_type) and isinstance(output, return_type):
        # convert to dict, but keep value dataclasses as dataclasses
        return {
            f.name: map_output_raw_to_data_properties(output.__dict__[f.name])
            for f in fields(return_type)
        }

    # 2b) If it's a typing.Tuple[...] or just `tuple` with type arguments
    #     We'll map each index to "output_1", "output_2", etc.
    #     (In Python 3.9+, we often see `tuple[int, float]` as `typing.Tuple[int, float]`.)
    #     We also ensure the return is actually a tuple.
    if _is_tuple_type(return_type) and isinstance(output, tuple):
        return _tuple_to_dict(output)

    # Fallback: if not a dataclass or a tuple, return the raw result
    return {"output": map_output_raw_to_data_properties(output)}


# Helper: detect if the annotation is a tuple type
def _is_tuple_type(t):
    """
    Check if `t` is a `Tuple[...]` (from typing) or `tuple[...]` in Python 3.9+.
    """
    if t == tuple:
        return True
    # For older Python versions with `typing.Tuple`
    if hasattr(typing, "Tuple") and getattr(t, "__origin__", None) is typing.Tuple:
        return True
    # For Python 3.9+ where `tuple[int, float]` has `__origin__ == tuple`
    if getattr(t, "__origin__", None) is tuple:
        return True
    return False


def _tuple_to_dict(tup):
    """
    Convert a tuple into a dictionary
    with keys: "output_1", "output_2", etc.
    """
    return {
        f"output_{i+1}": map_output_raw_to_data_properties(value)
        for i, value in enumerate(tup)
    }


def add_code_directory_to_sys_path(file_path):
    """Add the file's directory to sys.path."""
    code_dir = os.path.dirname(os.path.abspath(file_path))
    if code_dir not in sys.path:
        sys.path.insert(0, code_dir)
