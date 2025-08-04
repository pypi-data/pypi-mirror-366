from dataclasses import dataclass, field
import numpy as np
import pint

from nema.data.data_properties import DataProperties
from nema.utils.units import UNIT_REGISTRY, format_unit_str_for_backend


@dataclass
class FloatVector(DataProperties):
    vector: np.ndarray

    def __post_init__(self):

        # convert to numpy array if needed
        if not isinstance(self.vector, np.ndarray):
            self.vector = np.array(self.vector)

        if len(self.vector.shape) > 1:
            raise ValueError("Vector must be 1D")

    @property
    def data_type(self):
        return "FLOAT_VECTOR.V0"

    def __nema_marshall__(self):
        return {"vector": self.vector.tolist()}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        return cls(vector=np.array(data["vector"]))


@dataclass
class FloatVectorWithPhysicalUnits(FloatVector):
    vector: np.ndarray = field(default_factory=list)

    def __post_init__(self):

        # convert to numpy array if needed
        if not isinstance(self.vector, pint.Quantity):
            self.vector = np.array([]) * pint.Unit("dimensionless")

        if len(self.vector.shape) > 1:
            raise ValueError("Vector must be 1D")

    @property
    def data_type(self):
        return "FLOAT_VECTOR_WITH_PHYSICAL_UNITS.V0"

    def __nema_marshall__(self):
        unit_str = format_unit_str_for_backend(self.vector.units)

        return {"vector": self.vector.magnitude.tolist(), "units": unit_str}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        vector_magnitude = np.array(data["vector"])
        vector = vector_magnitude * UNIT_REGISTRY(data["units"])
        return cls(vector=vector)


@dataclass
class FloatMatrix(DataProperties):
    matrix: np.ndarray

    def __post_init__(self):

        # convert to numpy array if needed
        if not isinstance(self.matrix, np.ndarray):
            self.matrix = np.array(self.matrix)

        if len(self.matrix.shape) != 2:
            raise ValueError("Matrix must be 2D")

    @property
    def data_type(self):
        return "FLOAT_MATRIX.V0"

    def __nema_marshall__(self):
        return {"matrix": self.matrix.tolist()}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        return cls(matrix=np.array(data["matrix"]))
