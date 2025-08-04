from dataclasses import dataclass, field
from datetime import datetime
from typing import Type, Optional
from copy import deepcopy

from nema.connectivity import ConnectivityManager

from .data_properties import DataProperties
from .map_type_to_data_properties import map_type_to_data_properties
from .data_type import DataType


@dataclass
class CacheInfo:
    last_time_updated: datetime = datetime(1970, 1, 1)
    number_of_times_hit: int = 0
    in_sync_cloud: bool = False


@dataclass
class Data:
    _global_id: int
    _data: DataProperties
    _cache_info: CacheInfo = field(default_factory=CacheInfo)
    _userdefined_id: Optional[str] = None
    _commit_id: Optional[str] = None
    _branch: Optional[str] = None
    _id_in_app: Optional[str] = None

    @classmethod
    def init_from_cloud(
        cls,
        global_id: int,
        data_class: Type[DataProperties],
        userdefined_id: Optional[str] = None,
        commit_id: Optional[str] = None,
        id_in_function: Optional[str] = None,
        **kwargs,
    ):
        data = data_class(**kwargs)

        return cls(
            _global_id=global_id,
            _userdefined_id=userdefined_id,
            _data=data,
            _commit_id=commit_id,
            _id_in_app=id_in_function,
        )

    @classmethod
    def init_from_cloud_and_download(
        cls,
        global_id: int,
        commit_id: Optional[str] = None,
        branch: Optional[str] = None,
    ):
        connectivity_manager = ConnectivityManager()
        raw_data = connectivity_manager.pull_in_memory_data(
            global_id,
            commit_id=commit_id,
            branch=branch,
        )

        data_type = DataType(raw_data["data_type"])

        data_properties_class = map_type_to_data_properties(data_type)

        data = data_properties_class.__nema_unmarshall__(raw_data["data_properties"])

        return cls(
            _global_id=global_id,
            _data=data,
            _commit_id=commit_id,
            _branch=branch,
        )

    @classmethod
    def init_from_properties(
        cls,
        global_id: int,
        data_properties: DataProperties,
        userdefined_id: Optional[str] = None,
        commit_id: Optional[str] = None,
        id_in_function: Optional[str] = None,
    ):
        return cls(
            _global_id=global_id,
            _data=data_properties,
            _userdefined_id=userdefined_id,
            _commit_id=commit_id,
            _id_in_app=id_in_function,
        )

    @property
    def global_id(self):
        return self._global_id

    @global_id.setter
    def global_id(self, value: int):
        self._global_id = value

    @property
    def id_in_function(self):
        return self._id_in_app

    @property
    def data(self):
        # update cache info
        self._cache_info.number_of_times_hit += 1

        return self._data

    @property
    def value(self):
        return self.data.get_value()

    def update_data(self, new_data: DataProperties):
        if self._cache_info.number_of_times_hit > 0:
            raise ValueError("Data can only be updated if it has not been accessed")

        self._data = new_data
        self._cache_info.last_time_updated = datetime.now()
        self._cache_info.number_of_times_hit = 0
        self._cache_info.in_sync_cloud = False

    @property
    def userdefined_id(self):
        return self._userdefined_id

    @userdefined_id.setter
    def userdefined_id(self, value: str):
        self._userdefined_id = value

    @property
    def cache_info(self):
        return deepcopy(self._cache_info)

    def sync_from_API(
        self,
        connectivity_manager: ConnectivityManager,
        input_folder: str = "",
        commit_id: Optional[str] = None,
    ):
        # Sync data from the API

        raw_data = connectivity_manager.pull_in_memory_data(
            self.global_id, commit_id=commit_id
        )

        # we need to use _data here, otherwise we record a cache hit
        self._data = self._data.__nema_unmarshall__(raw_data["data_properties"])

    def marshall_data_properties(self):
        return self._data.__nema_marshall__()

    @property
    def is_updated(self):
        return (
            self._cache_info.in_sync_cloud == False
            and self._cache_info.last_time_updated.year > 1980
        )

    @property
    def data_type(self):
        return self._data.data_type

    def process_output_data(self, destination_folder: str):

        core_dict = {
            "global_id": self.global_id,
            "data_properties": self.marshall_data_properties(),
            "data_type": self.data_type,
            "id_in_function": self.id_in_function or "",
        }

        if self._data.is_blob_data:
            core_dict["file_name"] = self._data.write_data_to_file_and_return_file_name(
                destination_folder=destination_folder, global_id=self.global_id
            )

        return core_dict

    def close(self):
        return self._data.close()


@dataclass
class FileData(Data):

    _input_folder: Optional[str] = None

    def sync_from_API(self, *args, input_folder: str = "", **kwargs):
        super().sync_from_API(*args, input_folder=input_folder, **kwargs)
        self._input_folder = input_folder

    def get_file_path(self, requested_filename: Optional[str] = None):
        file_name = self.data.get_file_name(requested_filename)

        if file_name is None or file_name == "":
            local_file_name = self.download_blob_data(requested_filename)
            self._data.set_file_name(local_file_name, requested_filename)
            return f"{self._input_folder}/{local_file_name}"
        else:
            return f"{self._input_folder}/{file_name}"

    @property
    def contents(self):
        contents = (
            self.data.get_contents()
        )  # only use self.data once in this function to ensure cache hit is only recorded once

        if contents is None:
            # need to download the file
            filename = self.download_blob_data()
            return self._data.extract_contents(
                file_path=f"{self._input_folder}/{filename}"
            )
        else:
            return contents

    def download_blob_data(self, requested_filename: Optional[str] = None):
        connectivity_manager = ConnectivityManager()

        return connectivity_manager.pull_blob_data(
            self.global_id,
            folder=self._input_folder,
            commit_id=self._commit_id,
            requested_filename=requested_filename,
            branch=self._branch,
        )

    def get_file_name_to_save(self):
        self._cache_info.last_time_updated = datetime.now()
        self._cache_info.number_of_times_hit = 0
        self._cache_info.in_sync_cloud = False

        return self._data.get_file_name_to_save()
