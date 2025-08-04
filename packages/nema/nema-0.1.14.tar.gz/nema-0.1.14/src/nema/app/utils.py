from dataclasses import dataclass, field
import ast
from typing import List, Optional, Set, Any

from nema.data.data_type import DataType

### THIS IS PRETTY MUCH ALL COPIED FROM PROD CODE ###


@dataclass
class DataCoreSubTypeForFunctionArgument:
    type: Optional[DataType] = None
    union: Optional[Set[DataType]] = None
    any: Optional[List[Any]] = None

    def marshall(self):
        return {
            "type": self.type.value if self.type else None,
            "union": [t.value for t in self.union] if self.union else None,
            "any": self.any,
        }


@dataclass
class DataSubTypeForFunctionArgument(DataCoreSubTypeForFunctionArgument):
    list: Optional[DataCoreSubTypeForFunctionArgument] = None
    dictionary: Optional[DataCoreSubTypeForFunctionArgument] = None

    def marshall(self):
        core = super().marshall()
        return {
            **core,
            "list": self.list.marshall() if self.list else None,
            "dictionary": self.dictionary.marshall() if self.dictionary else None,
        }


@dataclass
class FunctionDataArgument:
    id_in_function: str
    description: str
    artifact_type: DataSubTypeForFunctionArgument

    def marshall(self):

        return {
            "id_in_function": self.id_in_function,
            "description": self.description,
            "artifact_type": self.artifact_type.marshall(),
        }


@dataclass
class AppIO:
    """
    Class used to keep the extracted input and output arguments from an app.
    """

    input_data: List[FunctionDataArgument] = field(default_factory=list)
    output_data: List[FunctionDataArgument] = field(default_factory=list)


NEMA_PY_TYPE_MAPPING = {
    "int": DataType.INT,
    "float": DataType.FLOAT,
    "str": DataType.STRING,
    "bool": DataType.BOOL,
    "pint.Quantity": DataType.FLOAT_WITH_PHYSICAL_UNIT_V0,
    "StringValue": DataType.STRING,
    "IntegerValue": DataType.INT,
    "FloatValue": DataType.FLOAT,
    "CurrencyValue": DataType.CURRENCY,
    "PercentageValue": DataType.PERCENTAGE,
    "FloatValueWithArbitraryUnit": DataType.FLOAT_WITH_ARBITRARY_UNIT_V0,
    "IntValueWithArbitraryUnit": DataType.INT_WITH_ARBITRARY_UNIT_V0,
    "FloatValueWithPhysicalUnit": DataType.FLOAT_WITH_PHYSICAL_UNIT_V0,
    "FloatVectorWithPhysicalUnits": DataType.FLOAT_VECTOR_WITH_PHYSICAL_UNITS_V0,
    "IntValueWithPhysicalUnit": DataType.INT_WITH_PHYSICAL_UNIT_V0,
    "ArbitraryFile": DataType.ARBITRARY_FILE_V0,
    "ArbitraryFileCollection": DataType.ARBITRARY_FILE_COLLECTION_V0,
    "Dictionary": DataType.DICTIONARY_V0,
    "CSVData": DataType.CSV_V0,
    "Image": DataType.IMAGE_V0,
    "FloatVector": DataType.FLOAT_VECTOR_V0,
    "FloatMatrix": DataType.FLOAT_MATRIX_V0,
    "NormalDistribution": DataType.NORMAL_DISTRIBUTION_V0,
    "UniformDistribution": DataType.UNIFORM_DISTRIBUTION_V0,
    "ExponentialDistribution": DataType.EXPONENTIAL_DISTRIBUTION_V0,
    "TriangularDistribution": DataType.TRIANGULAR_DISTRIBUTION_V0,
}


def extract_return_type(return_annotation: ast.expr, tree: ast.Module):
    """Extract the return type from the return annotation."""

    data_outputs: List[FunctionDataArgument] = []

    if isinstance(return_annotation, ast.Subscript):
        if isinstance(return_annotation.value, ast.Name):
            if return_annotation.value.id.lower() == "tuple":
                # Handle tuple return types
                for element in return_annotation.slice.elts:
                    output_type = extract_types(element, tree)
                    if output_type.get("fields"):
                        # Decode fields if it's a class
                        class_fields = extract_field_from_ast_tree(
                            tree, output_type["fields"]
                        )
                        data_outputs.extend(class_fields)
                    else:
                        data_outputs.append(
                            FunctionDataArgument(
                                id_in_function=f"output_{len(data_outputs) + 1}",
                                description="",
                                artifact_type=DataSubTypeForFunctionArgument(
                                    **output_type
                                ),
                            )
                        )
                return data_outputs

    output_type = extract_types(return_annotation, tree)
    if output_type.get("fields"):
        # Decode fields if it's a class
        class_fields = extract_field_from_ast_tree(tree, output_type["fields"])
        data_outputs.extend(class_fields)
    else:
        data_outputs.append(
            FunctionDataArgument(
                id_in_function="output",
                description="",
                artifact_type=DataSubTypeForFunctionArgument(**output_type),
            )
        )

    return data_outputs


def extract_input_and_output_from_python_contents(code: str) -> AppIO:
    tree = ast.parse(code)

    data_inputs = []

    # Walk through the AST to find the run function
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "run":
            # Extract the argument type annotations of the `run` function
            for arg in node.args.args:
                if arg.annotation:
                    input_type = extract_types(arg.annotation, tree)
                    if input_type.get("fields"):
                        # Decode fields if it's a class
                        class_fields = extract_field_from_ast_tree(
                            tree, input_type["fields"]
                        )
                        data_inputs.extend(class_fields)
                    else:
                        data_inputs.append(
                            FunctionDataArgument(
                                id_in_function=arg.arg,
                                description="",
                                artifact_type=DataSubTypeForFunctionArgument(
                                    **input_type
                                ),
                            )
                        )

            # Extract the return type annotation of the `run` function
            if node.returns:
                data_outputs = extract_return_type(node.returns, tree)

    return AppIO(
        input_data=data_inputs,
        output_data=data_outputs,
    )


def extract_types(annotation: ast.expr, tree):
    """Recursively extract types from annotations."""
    if isinstance(annotation, ast.Name):
        if annotation.id in NEMA_PY_TYPE_MAPPING:
            return {"type": NEMA_PY_TYPE_MAPPING[annotation.id]}
        return {"fields": annotation.id}  # to be decoded later

    if isinstance(annotation, ast.Attribute):
        this_id = annotation.value.id + "." + annotation.attr
        if this_id in NEMA_PY_TYPE_MAPPING:
            return {"type": NEMA_PY_TYPE_MAPPING[this_id]}
        return {"any": []}

    elif isinstance(annotation, ast.Subscript):
        # Handle subscripted types (e.g., List[int], Union[int, str])
        if isinstance(annotation.value, ast.Name):
            if annotation.value.id == "list":
                element_type = extract_types(annotation.slice, tree)
                return {"list": DataCoreSubTypeForFunctionArgument(**element_type)}

            elif annotation.value.id == "Union":
                if isinstance(annotation.slice, ast.Tuple):
                    union_types = [
                        NEMA_PY_TYPE_MAPPING.get(elt.id, None)
                        for elt in annotation.slice.elts
                        if isinstance(elt, ast.Name)
                    ]
                    return {"union": union_types}

    elif isinstance(annotation, ast.BinOp):
        # Handle Python 3.10+ union syntax (e.g., float|int)
        return {"union": extract_union_from_bin_op(annotation)}

    return {"any": []}


def extract_union_from_bin_op(bin_op):
    """Handle Python 3.10+ union syntax (e.g., float|int)."""
    types = []
    if isinstance(bin_op, ast.BinOp) and isinstance(bin_op.op, ast.BitOr):
        left = bin_op.left
        right = bin_op.right

        if isinstance(left, ast.Name):
            types.append(NEMA_PY_TYPE_MAPPING.get(left.id, None))
        if isinstance(right, ast.Name):
            types.append(NEMA_PY_TYPE_MAPPING.get(right.id, None))

    return types


def extract_field_from_ast_tree(
    tree: ast.Module, class_name: str
) -> List[FunctionDataArgument]:
    fields = []

    # Look for the class definition of the given class_name
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            # Extract fields from the dataclass
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign):
                    key = stmt.target.id

                    artifact_type = extract_types(stmt.annotation, tree)
                    fields.append(
                        FunctionDataArgument(
                            id_in_function=key,
                            description="",
                            artifact_type=DataSubTypeForFunctionArgument(
                                **artifact_type
                            ),
                        )
                    )

    return fields


######


def find_matches_in_workflow_arguments(
    arguments: List[dict],
    id_in_function: str,
):

    return [x for x in arguments if x["id_in_function"] == id_in_function]


def map_workflow_arguments_to_app_arguments(
    workflow_arguments: List[dict],
    app_arguments: List[FunctionDataArgument],
):

    app_inputs = {}
    for input_data_type in app_arguments:
        id_in_function = input_data_type.id_in_function

        argument_matches = find_matches_in_workflow_arguments(
            workflow_arguments, id_in_function
        )

        if (
            input_data_type.artifact_type.type is not None
            or input_data_type.artifact_type.any is not None
        ):
            assert len(argument_matches) == 1

            global_id_of_match = argument_matches[0]["artifact"]

            app_inputs[id_in_function] = global_id_of_match

        elif input_data_type.artifact_type.dictionary is not None:
            this_dict = {}
            for argument_match in argument_matches:
                global_id_of_match = argument_match["artifact"]
                this_dict[argument_match.member_type.key_in_dictionary] = (
                    global_id_of_match
                )
            app_inputs[id_in_function] = this_dict

        elif input_data_type.artifact_type.list is not None:
            this_list = [None for _ in argument_matches]
            for argument_match in argument_matches:
                global_id_of_match = argument_match["artifact"]
                idx = argument_match["member_type"]["index_in_list"]
                this_list[idx] = global_id_of_match
            app_inputs[id_in_function] = this_list

    return app_inputs
