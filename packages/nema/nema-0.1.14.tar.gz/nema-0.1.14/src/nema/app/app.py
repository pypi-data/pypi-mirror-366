from dataclasses import dataclass
from typing import Optional
import json
from typing import List

from nema.connectivity import ConnectivityManager

from .utils import extract_input_and_output_from_python_contents, AppIO


@dataclass
class App:
    global_id: int
    name: str = ""
    description: str = ""
    output_folder: Optional[str] = None
    code: Optional[str] = None
    app_io: Optional[AppIO] = None

    def download_code(self, branch: str) -> str:
        conn = ConnectivityManager()

        return conn.retrieve_app_code(self.global_id, branch=branch)

    def extract_io_from_code(self) -> None:
        self.app_io = extract_input_and_output_from_python_contents(self.code)

    def to_raw_data(self) -> List[tuple]:

        data = [
            ("name", self.name),
            ("description", self.description),
            ("function_type", "NEMA.APP_EXTERNAL.V0"),
            ("function_properties", json.dumps({"external_function_type": "PYTHON"})),
        ]

        if self.code:

            self.extract_io_from_code()

            for in_arg in self.app_io.input_data:
                data.append(("input_data_arguments", json.dumps(in_arg.marshall())))

            for out_arg in self.app_io.output_data:
                data.append(("output_data_arguments", json.dumps(out_arg.marshall())))

        return data

    def create(self) -> int:
        conn = ConnectivityManager()

        raw_data = self.to_raw_data()

        global_id = conn.create_app(raw_data)
        return global_id

    def update(self) -> None:
        conn = ConnectivityManager()

        raw_data = self.to_raw_data()

        conn.update_app(raw_data, global_id=self.global_id)

    def get_all_workflows(self) -> List:
        conn = ConnectivityManager()

        return conn.get_workflows_for_app(self.global_id)
