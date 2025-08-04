from nema.data.data_type import DataType
from nema.data.data_properties import (
    StringValue,
    IntegerValue,
    FloatValue,
    CurrencyValue,
    FloatValueWithArbitraryUnit,
    IntValueWithArbitraryUnit,
    FloatValueWithPhysicalUnit,
    IntValueWithPhysicalUnit,
    Dictionary,
    ArbitraryFile,
)
from nema.data.tabular import CSVData
from nema.data.plots.figure_data_properties import Image
from nema.data.linear_algebra.vector import (
    FloatVector,
    FloatMatrix,
    FloatVectorWithPhysicalUnits,
)


def map_type_to_data_properties(data_type: DataType):
    if data_type == DataType.STRING:
        return StringValue
    elif data_type == DataType.INT:
        return IntegerValue
    elif data_type == DataType.FLOAT:
        return FloatValue
    elif data_type == DataType.CURRENCY:
        return CurrencyValue
    elif data_type == DataType.FLOAT_WITH_ARBITRARY_UNIT_V0:
        return FloatValueWithArbitraryUnit
    elif data_type == DataType.INT_WITH_ARBITRARY_UNIT_V0:
        return IntValueWithArbitraryUnit
    elif data_type == DataType.FLOAT_WITH_PHYSICAL_UNIT_V0:
        return FloatValueWithPhysicalUnit
    elif data_type == DataType.INT_WITH_PHYSICAL_UNIT_V0:
        return IntValueWithPhysicalUnit
    elif data_type == DataType.CSV_V0:
        return CSVData
    elif data_type == DataType.IMAGE_V0:
        return Image
    elif data_type == DataType.FLOAT_VECTOR_V0:
        return FloatVector
    elif data_type == DataType.FLOAT_VECTOR_WITH_PHYSICAL_UNITS_V0:
        return FloatVectorWithPhysicalUnits
    elif data_type == DataType.FLOAT_MATRIX_V0:
        return FloatMatrix
    elif data_type == DataType.DICTIONARY_V0:
        return Dictionary
    elif data_type == DataType.ARBITRARY_FILE_V0:
        return ArbitraryFile

    else:
        raise ValueError(f"Data type {data_type} not supported.")
