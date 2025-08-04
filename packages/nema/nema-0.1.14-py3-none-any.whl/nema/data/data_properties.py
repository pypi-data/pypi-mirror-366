from dataclasses import dataclass, field
import shutil
import tempfile
import os
import pint
from typing import Optional, List, IO

from nema.connectivity import CONNECTIVITY_CONFIG
from nema.utils.file_name import generate_random_file_name
from nema.utils.units import UNIT_REGISTRY, format_unit_str_for_backend


@dataclass
class DataProperties:

    @property
    def is_blob_data(self):
        return False

    @property
    def data_type(self):
        raise NotImplementedError("This method should be implemented by the subclass")

    def get_value(self):
        raise NotImplementedError("This method should be implemented by the subclass")

    def __nema_marshall__(self):
        raise NotImplementedError("This method should be implemented by the subclass")

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        raise NotImplementedError("This method should be implemented by the subclass")

    def close(self):
        pass

    def set_file_name(self, *args, **kwargs):
        raise NotImplementedError("This method should be implemented by the subclass")


@dataclass
class SingleValue(DataProperties):

    def __nema_marshall__(self):
        return {"value": self.value}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        return cls(value=data["value"])

    def get_value(self):
        return self.value


@dataclass
class BooleanValue(SingleValue):
    value: bool = False

    @property
    def data_type(self):
        return "BOOL"


@dataclass
class StringValue(SingleValue):
    value: str = ""

    @property
    def data_type(self):
        return "STRING"


@dataclass
class IntegerValue(SingleValue):
    value: int = 0

    @property
    def data_type(self):
        return "INT"


@dataclass
class FloatValue(SingleValue):
    value: float = 0.0

    @property
    def data_type(self):
        return "FLOAT"


@dataclass
class PercentageValue(FloatValue):

    @property
    def data_type(self):
        return "PERCENTAGE"


@dataclass
class CurrencyValue(FloatValue):
    currency_code: str = ""

    def __nema_marshall__(self):
        return {"value": self.value, "currency_code": self.currency_code}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        return cls(value=data["value"], currency_code=data["currency_code"])

    @property
    def data_type(self):
        return "CURRENCY"


@dataclass
class FloatValueWithArbitraryUnit(SingleValue):
    value: float = 0.0
    units: str = ""

    def __nema_marshall__(self):
        return {"value": self.value, "units": self.units}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        return cls(value=data["value"], unit=data["units"])


@dataclass
class IntValueWithArbitraryUnit(FloatValueWithArbitraryUnit):
    value: int = 0

    @property
    def data_type(self):
        return "INT_WITH_PHYSICAL_UNIT.V0"


@dataclass
class FloatValueWithPhysicalUnit(SingleValue):

    value: pint.Quantity = 0.0 * UNIT_REGISTRY("dimensionless")

    @property
    def data_type(self):
        return "FLOAT_WITH_PHYSICAL_UNIT.V0"

    def __nema_marshall__(self):
        unit_str = format_unit_str_for_backend(self.value.units)
        return {"value": self.value.magnitude, "units": unit_str}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        value = UNIT_REGISTRY.Quantity(data["value"], UNIT_REGISTRY(data["units"]))
        return cls(value=value)


@dataclass
class IntValueWithPhysicalUnit(FloatValueWithPhysicalUnit):

    @property
    def data_type(self):
        return "INT_WITH_PHYSICAL_UNIT.V0"


@dataclass
class BlobDataProperties(DataProperties):

    @property
    def is_blob_data(self):
        return True


@dataclass
class FileDataProperties(BlobDataProperties):
    _file_name: str = ""
    _display_file_name: str = ""
    _local_file_name: str = ""
    _input_folder: str = ""
    _temp_file_path: str = field(init=False, default=None)
    _file_reference: Optional[IO] = None
    extension: Optional[str] = None

    def __post_init__(self):
        suffix = f".{self.extension}" if self.extension else ""
        self._temp_file_path = tempfile.mkstemp(suffix=suffix)[1]

    def __nema_marshall__(self):
        return {}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        return cls(
            _file_name=data["file_name"],
            _display_file_name=data.get("display_file_name", ""),
        )

    def close(self):
        if self._temp_file_path is not None and os.path.exists(self._temp_file_path):
            os.remove(self._temp_file_path)

    def __del__(self):
        self.close()

    def get_file_name(self, *args, **kwargs):
        return self._local_file_name

    def set_file_name(self, file_name: str, *args, **kwargs):

        # extract file extension
        _, file_extension = os.path.splitext(file_name)

        self.close()  # remove path without file extension
        self._temp_file_path = tempfile.mkstemp(suffix=file_extension)[1]

        self._local_file_name = file_name

    @property
    def file_extension(self):
        if not self._temp_file_path:
            return ""

        extension = os.path.splitext(self._temp_file_path)[1]

        file_ext = extension[1:] if extension else ""
        self.extension = file_ext

        return file_ext

    def get_file_name_to_save(self, display_filename: Optional[str] = None):
        if display_filename:
            self._display_file_name = display_filename
            ## update extension if needed
            _, file_extension = os.path.splitext(display_filename)
            if file_extension:
                self.close()  # remove existing temp file
                self._temp_file_path = tempfile.mkstemp(suffix=file_extension)[1]

        return self._temp_file_path

    def get_file_name_to_read(self):
        return CONNECTIVITY_CONFIG.nema_data_folder + "/" + self._local_file_name

    def write_data_to_file_and_return_file_name(
        self, destination_folder: str, global_id: int
    ):

        # move to destination folder
        output_file_name = (
            self._display_file_name
            if self._display_file_name
            else generate_random_file_name(self.file_extension)
        )

        fldr = os.path.join(destination_folder, f"DATA-{global_id}")
        os.makedirs(fldr, exist_ok=True)
        destination_file_path = os.path.join(fldr, output_file_name)

        shutil.move(self._temp_file_path, destination_file_path)

        return output_file_name

    # This method is called when entering the 'with' block, and it accepts the mode
    def __enter__(self):
        # Dynamically set the mode (use 'r' by default if not provided)
        flpath = self.get_file_name_to_read()
        self._file_reference = open(flpath, self._file_reading_mode)
        return self._file_reference

    # This method is called when exiting the 'with' block
    def __exit__(self, exc_type, exc_value, traceback):
        if self._file_reference:
            self._file_reference.close()  # Ensure the file is closed properly

    # This will allow 'with open()' to pass the mode and other arguments
    def __call__(self, file_reading_mode: str):
        self._file_reading_mode = file_reading_mode
        return self

    @classmethod
    def from_existing_file(cls, file_name: str):
        extension = os.path.splitext(file_name)[1]
        extension = extension[1:] if extension else None
        new_instance = cls(extension=extension)
        shutil.copy(file_name, new_instance._temp_file_path)
        new_instance._local_file_name = file_name
        return new_instance

    def copy(self, destination_path: str):
        flpath = CONNECTIVITY_CONFIG.nema_data_folder + "/" + self._local_file_name
        shutil.copy(flpath, destination_path)


@dataclass
class ArbitraryFile(FileDataProperties):

    @property
    def data_type(self):
        return "ARBITRARY_FILE.V0"


@dataclass
class SingleFileInCollection:
    display_filename: str  # from the API
    local_filename: Optional[str] = None


@dataclass
class ArbitraryFileCollection(DataProperties):

    files: List[SingleFileInCollection] = field(default_factory=list)

    @property
    def data_type(self):
        return "ARBITRARY_FILE_COLLECTION.V0"

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        return cls(
            files=[
                SingleFileInCollection(display_filename=file["display_filename"])
                for file in data["files"]
            ]
        )

    def get_file_name(self, requested_filename: str):
        for file in self.files:
            if file.display_filename == requested_filename:
                return file.local_filename
        return None

    def set_file_name(self, local_filename: str, requested_filename: str):
        for file in self.files:
            if file.display_filename == requested_filename:
                file.local_filename = local_filename
                return
        raise ValueError(f"File with name {requested_filename} not found in collection")


@dataclass
class Dictionary(DataProperties):

    dictionary: dict = field(default_factory=dict)

    @property
    def data_type(self):
        return "DICTIONARY.V0"

    def get_value(self):
        return self.dictionary

    def __nema_marshall__(self):
        return {"dictionary": self.dictionary}

    @classmethod
    def __nema_unmarshall__(cls, data: dict):
        return cls(dictionary=data["dictionary"])

    def get_contents(self):
        return self.dictionary
