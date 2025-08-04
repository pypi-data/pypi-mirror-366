from dataclasses import dataclass

from nema.data.data_properties import DataProperties


@dataclass
class NormalDistribution(DataProperties):
    mean: float
    std_dev: float

    @property
    def data_type(self):
        return "NORMAL_DISTRIBUTION.V0"


@dataclass
class UniformDistribution(DataProperties):
    lower_bound: float
    upper_bound: float

    @property
    def data_type(self):
        return "UNIFORM_DISTRIBUTION.V0"


@dataclass
class ExponentialDistribution(DataProperties):
    rate: float

    @property
    def data_type(self):
        return "EXPONENTIAL_DISTRIBUTION.V0"


@dataclass
class TriangularDistribution(DataProperties):
    lower_bound: float
    upper_bound: float
    mode: float

    @property
    def data_type(self):
        return "TRIANGULAR_DISTRIBUTION.V0"
