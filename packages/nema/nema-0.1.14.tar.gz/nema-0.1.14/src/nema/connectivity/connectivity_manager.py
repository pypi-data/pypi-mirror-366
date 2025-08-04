from dataclasses import dataclass
import os
import json
import requests
import mimetypes
from typing import List, Optional

from nema.utils.global_config import GLOBAL_CONFIG


def get_mime_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"


NEMA_CONFIG_FOLDER = os.environ.get("NEMA_CONFIG_FOLDER", "~/.nema")
NEMA_PATH = os.path.expanduser(NEMA_CONFIG_FOLDER)
AUTH_PATH = os.path.join(NEMA_PATH, "auth")


@dataclass
class ConnectivityConfig:
    nema_data_folder: str


INPUT_NEMA_DATA_FOLDER = os.environ.get("NEMA_DATA_FOLDER", ".nema")
CONNECTIVITY_CONFIG = ConnectivityConfig(INPUT_NEMA_DATA_FOLDER)


def save_auth_data(refresh_token: str, access_token: str):
    os.makedirs(os.path.dirname(AUTH_PATH), exist_ok=True)

    with open(AUTH_PATH, "w") as f:
        f.write(
            json.dumps({"refresh_token": refresh_token, "access_token": access_token})
        )


@dataclass
class ConnectivityManager:
    _auth_token: str = ""
    _refresh_token: str = ""

    def __post_init__(self):

        if os.path.exists(AUTH_PATH):
            with open(AUTH_PATH, "r") as f:
                data = json.load(f)
                self._auth_token = data.get("access_token", "")
                self._refresh_token = data.get("refresh_token", "")

            return

        # otherwise, we need to set the auth token
        self._auth_token = os.environ.get("NEMA_AUTH_TOKEN", "")

    @property
    def auth_token(self):
        return self._auth_token

    def get_latest_commit(self) -> str:

        data_api_url = (
            f"{GLOBAL_CONFIG.project_api_url}/artifacts/overview/commit-history"
        )

        response = requests.get(
            data_api_url,
            headers=self.get_headers(),
            params={"count": 1},
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.get_latest_commit()
            else:
                raise ConnectionError(
                    f"Connection error calling {data_api_url}: {response.status_code} -- {response.text}"
                )

        data = response.json()

        return data["history"][0]["commit_hash"]

    def pull_blob_data(
        self,
        global_id: int,
        folder: str,
        commit_id: str,
        branch: str = "",
        requested_filename: Optional[str] = None,
    ):
        data_api_url = (
            f"{GLOBAL_CONFIG.project_api_url}/artifacts/data/{global_id}/download"
        ) + (f"/{requested_filename}" if requested_filename else "")

        response = requests.get(
            data_api_url,
            headers=self.get_headers(),
            stream=True,
            params={"commit_id": commit_id, "branch": branch},
        )

        if response.status_code == 413:
            # file is too large so we need to use a presigned link
            presigned_api_url = (
                f"{GLOBAL_CONFIG.project_api_url}/artifacts/data/{global_id}/download-link"
            ) + (f"/{requested_filename}" if requested_filename else "")

            response_presigned_api_url = requests.get(
                presigned_api_url,
                headers=self.get_headers(),
                stream=True,
                params={"commit_id": commit_id},
            )
            response_presigned_api_url.raise_for_status()
            data_response_presigned_api_url = response_presigned_api_url.json()
            link = data_response_presigned_api_url["link"]

            # Actually download the file
            response = requests.get(link, stream=True)

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.pull_blob_data(global_id, folder, commit_id, branch)
            else:
                raise ConnectionError(
                    f"Connection error calling {data_api_url}: {response.status_code} -- {response.text}"
                )

        # Raise an error if the request fails
        response.raise_for_status()

        # Try to get the filename from the 'Content-Disposition' header
        filename = None

        if "Content-Disposition" in response.headers:
            content_disposition = response.headers.get(
                "Content-Disposition", response.headers.get("content-disposition")
            )
            if "filename=" in content_disposition:
                filepath = content_disposition.split("filename=")[-1].strip('"')
                filename = os.path.basename(filepath).split("/")[-1]

        # If no filename in headers, infer from the URL
        if filename is None:
            filename = f"DATA_{global_id}"

        # Full path for saving the file
        fldr_path = os.path.join(folder, f"{global_id}")
        os.makedirs(fldr_path, exist_ok=True)
        filepath = os.path.join(fldr_path, filename)

        # Write the file in chunks to avoid memory overload
        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return f"{global_id}/{filename}"

    def get_headers(self):
        return {"Authorization": f"Bearer {self.auth_token}"}

    def refresh_auth_token(self):
        """Refresh the authentication token"""

        tenant_url = GLOBAL_CONFIG.tenant_api_url
        login_url = f"{tenant_url}/authentication/refresh-token"

        response = requests.post(login_url, json={"token": self._refresh_token})

        if not response.ok:
            if response.status_code == 401:
                raise ConnectionError("Token refresh failed, please login again.")
            else:
                raise ConnectionError(
                    f"Connection error calling {login_url}: {response.status_code} -- {response.text}"
                )

        response_data = response.json()
        self._refresh_token = response_data["refresh_token"]
        self._auth_token = response_data["access_token"]

        save_auth_data(self._refresh_token, self._auth_token)

    def pull_in_memory_data(
        self, global_id: int, commit_id: str = "", branch: str = ""
    ):

        data_api_url = f"{GLOBAL_CONFIG.project_api_url}/artifacts/data/{global_id}"

        response = requests.get(
            data_api_url,
            headers=self.get_headers(),
            params={"commit_id": commit_id, "branch": branch},
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.pull_in_memory_data(global_id, commit_id, branch)
            else:
                raise ConnectionError(
                    f"Connection error calling {data_api_url}: {response.status_code} -- {response.text}"
                )

        return response.json()

    def push_data_update(
        self,
        global_id: int,
        form_data: dict,
        files: Optional[list] = None,
        branch: Optional[str] = None,
    ):

        url = f"{GLOBAL_CONFIG.project_api_url}/artifacts/data/{global_id}"

        if files is None:
            # add a dummy file to force multipart
            files_to_send = [("dummy_file", ("dummy", b"", "application/octet-stream"))]

        else:
            files_to_send = [
                ("file", (fp.split("/")[-1], open(fp, "rb"), get_mime_type(fp)))
                for fp in files
            ]

        response = requests.put(
            url,
            headers={**self.get_headers()},
            data=form_data,
            files=files_to_send,
            params={"branch": branch},
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.push_data_update(global_id, form_data, files, branch)
            else:
                raise ConnectionError(
                    f"Connection error calling {url}: {response.status_code} -- {response.text}"
                )

        response.raise_for_status()

        return response

    def push_local_workflow_update(
        self, global_id: int, workflow_raw_data: dict, files: List[str] = []
    ):

        url = f"{GLOBAL_CONFIG.project_api_url}/artifacts/workflows/{global_id}/upload-external-results"

        files = [
            ("file", (fp.split("/")[-1], open(fp, "rb"), get_mime_type(fp)))
            for fp in files
        ]

        if (
            len(files) == 0
        ):  # until the API can support non-multipart, we need to do this, really dumb..
            files.append(("file", ("dummy", b"dummy", "application/octet-stream")))

        response = requests.post(
            url,
            headers={**self.get_headers()},
            data=workflow_raw_data,
            files=files,
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.push_workflow_update(global_id, workflow_raw_data)
            else:
                raise ConnectionError(
                    f"Connection error calling {url}: {response.status_code} -- {response.text}"
                )

        return response.json()

    def push_workflow_outputs(
        self,
        global_id: int,
        workflow_raw_data: dict,
        branch: Optional[str] = None,
        files: List[str] = [],
        local: bool = False,
    ):

        if local:
            url = f"{GLOBAL_CONFIG.project_api_url}/artifacts/workflows/{global_id}/upload-workflow-outputs"
        else:
            url = f"{GLOBAL_CONFIG.project_api_url}/artifacts/workflows/{global_id}/upload-internal-only-workflow-outputs"

        files = [
            ("file", (fp.split("/")[-1], open(fp, "rb"), get_mime_type(fp)))
            for fp in files
        ]

        if (
            len(files) == 0
        ):  # until the API can support non-multipart, we need to do this, really dumb..
            files.append(("file", ("dummy", b"dummy", "application/octet-stream")))

        response = requests.post(
            url,
            headers={**self.get_headers()},
            data=workflow_raw_data,
            files=files,
            params={"branch": branch},
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.push_workflow_update(global_id, workflow_raw_data)
            else:
                raise ConnectionError(
                    f"Connection error calling {url}: {response.status_code} -- {response.text}"
                )

        return response.json()

    def create_workflow(self, workflow_data: dict):
        """Create a new workflow in the nema platform"""

        url = f"{GLOBAL_CONFIG.project_api_url}/artifacts/workflows"

        # this is needed to force multipart
        files = [("dummy_file", ("dummy", b"dummy", "application/octet-stream"))]

        response = requests.post(
            url,
            headers=self.get_headers(),
            data=workflow_data,
            files=files,
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.create_app(app_data)
            else:
                raise ConnectionError(
                    f"Connection error calling {url}: {response.status_code} -- {response.text}"
                )

        return_data = response.json()
        return return_data["created_global_id"]

    def retrieve_app_code(
        self,
        global_id: int,
        commit_id: Optional[str] = None,
        branch: Optional[str] = None,
    ):
        data_api_url = (
            f"{GLOBAL_CONFIG.project_api_url}/artifacts/functions/{global_id}/download"
        )

        response = requests.get(
            data_api_url,
            headers=self.get_headers(),
            stream=True,
            params={"commit_id": commit_id, "branch": branch},
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.retrieve_app_code(global_id, commit_id, branch)
            else:
                raise ConnectionError(
                    f"Connection error calling {data_api_url}: {response.status_code} -- {response.text}"
                )

        # Raise an error if the request fails
        response.raise_for_status()

        return response.text

    def push_batch_data(
        self,
        raw_data: List[tuple],
    ) -> List[int]:

        url = f"{GLOBAL_CONFIG.project_api_url}/artifacts/data-batch"

        # this is needed to force multipart
        files = [("file", ("dummy", b"dummy", "application/octet-stream"))]

        response = requests.post(
            url,
            headers=self.get_headers(),
            data=raw_data,
            files=files,
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.push_batch_data(raw_data)
            else:
                raise ConnectionError(
                    f"Connection error calling {url}: {response.status_code} -- {response.text}"
                )

        return_data = response.json()
        return return_data["created_global_ids"]

    def create_app(self, app_data: List[tuple]):

        url = f"{GLOBAL_CONFIG.project_api_url}/artifacts/functions"

        # this is needed to force multipart
        files = [("dummy_file", ("dummy", b"dummy", "application/octet-stream"))]

        response = requests.post(
            url,
            headers=self.get_headers(),
            data=app_data,
            files=files,
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.create_app(app_data)
            else:
                raise ConnectionError(
                    f"Connection error calling {url}: {response.status_code} -- {response.text}"
                )

        return_data = response.json()
        return return_data["created_global_id"]

    def update_app(self, app_data: List[tuple], global_id: int) -> None:

        url = f"{GLOBAL_CONFIG.project_api_url}/artifacts/functions/{global_id}"

        # this is needed to force multipart
        files = [("dummy_file", ("dummy", b"dummy", "application/octet-stream"))]

        response = requests.put(
            url,
            headers=self.get_headers(),
            data=app_data,
            files=files,
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.create_app(app_data)
            else:
                raise ConnectionError(
                    f"Connection error calling {url}: {response.status_code} -- {response.text}"
                )

    def get_workflows_for_app(self, global_id: int) -> List:

        url = (
            f"{GLOBAL_CONFIG.project_api_url}/artifacts/functions/{global_id}/workflows"
        )

        response = requests.get(
            url,
            headers=self.get_headers(),
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.get_workflows_for_app(global_id)
            else:
                raise ConnectionError(
                    f"Connection error calling {url}: {response.status_code} -- {response.text}"
                )

        data = response.json()

        return data["workflows"]

    def get_workflow_io(self, global_id: int) -> dict:

        url = f"{GLOBAL_CONFIG.project_api_url}/artifacts/workflows/{global_id}"

        response = requests.get(
            url,
            headers=self.get_headers(),
        )

        if not response.ok:
            if response.status_code == 401:
                self.refresh_auth_token()
                return self.get_workflow_io()
            else:
                raise ConnectionError(
                    f"Connection error calling {url}: {response.status_code} -- {response.text}"
                )

        data = response.json()

        return data
