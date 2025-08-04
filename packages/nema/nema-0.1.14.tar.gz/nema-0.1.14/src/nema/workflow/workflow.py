from dataclasses import dataclass
from typing import Optional, List
import json
import os
import shutil

from nema.connectivity import ConnectivityManager, CONNECTIVITY_CONFIG
from nema.data import Data


def get_all_files_from_output_folder(output_folder: str):

    files = []
    for root, _, found_files in os.walk(output_folder):
        for file_name in found_files:
            file_path = os.path.join(root, file_name)
            files.append(file_path)

    return files


@dataclass
class Workflow:
    global_id: int
    name: str = ""
    description: str = ""
    output_folder: Optional[str] = None

    def marshall_create(self):
        return {
            "name": self.name,
            "description": self.description,
            "workflow_type": "NEMA.EXTERNAL.V0",
            "workflow_properties": {"external_workflow_type": "PYTHON"},
        }

    def create(self):
        conn = ConnectivityManager()
        global_id = conn.create_workflow(self.to_raw_data())
        return global_id

    def to_raw_data(self) -> List[tuple]:

        data = [
            ("name", self.name),
            ("description", self.description),
            (
                "workflow_type",
                "NEMA.EXTERNAL.V0",
            ),
            ("workflow_properties", json.dumps({"external_workflow_type": "PYTHON"})),
        ]

        return data

    def process_local_update(
        self,
        updated_data: List[Data],
        used_data: List[dict],
    ):
        conn = ConnectivityManager()

        output_folder = self.output_folder or CONNECTIVITY_CONFIG.nema_data_folder

        files_output_folder = os.path.join(output_folder, "data-output")
        shutil.rmtree(files_output_folder, ignore_errors=True)
        os.makedirs(files_output_folder, exist_ok=True)

        raw_data_output = [
            (
                "updated_data",
                json.dumps(
                    data.process_output_data(destination_folder=files_output_folder)
                ),
            )
            for data in updated_data
        ]

        raw_uses_data = [
            (
                "used_data",
                json.dumps(i_data),
            )
            for i_data in used_data
        ]

        raw_data = raw_data_output + raw_uses_data

        # read files from output folder
        files = get_all_files_from_output_folder(files_output_folder)

        conn.push_local_workflow_update(self.global_id, raw_data, files=files)

    def push_outputs_to_API(
        self,
        updated_data: List[Data],
        branch_name: Optional[str] = None,
        local: bool = False,
    ):
        conn = ConnectivityManager()

        output_folder = self.output_folder or CONNECTIVITY_CONFIG.nema_data_folder

        files_output_folder = os.path.join(output_folder, "data-output")
        shutil.rmtree(files_output_folder, ignore_errors=True)
        os.makedirs(files_output_folder, exist_ok=True)

        raw_data = [
            (
                "updated_data",
                json.dumps(
                    data.process_output_data(destination_folder=files_output_folder)
                ),
            )
            for data in updated_data
        ]

        # read files from output folder
        files = get_all_files_from_output_folder(files_output_folder)

        conn.push_workflow_outputs(
            self.global_id, raw_data, branch=branch_name, files=files, local=local
        )

    def get_workflow_details(self) -> dict:
        conn = ConnectivityManager()

        return conn.get_workflow_io(self.global_id)
