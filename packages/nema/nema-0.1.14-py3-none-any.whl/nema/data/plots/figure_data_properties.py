from dataclasses import dataclass

from nema.data.data_properties import DataProperties, FileDataProperties


@dataclass
class FigureDataProperties(DataProperties):
    pass


@dataclass
class Image(FigureDataProperties, FileDataProperties):

    def __post_init__(self):
        self.extension = self.extension or "png"
        return super().__post_init__()

    @property
    def data_type(self):
        return "IMAGE.V0"
