import toml
import os
from dataclasses import dataclass, field
from typing import Dict, List

from .url import get_ids_from_app_url

CONFIG_FILE_PATH = "nema.toml"

# and remove the trailing slash
API_URL_RAW = os.environ.get("NEMA_API_URL", "https://api.nemasystems.io")
API_URL = API_URL_RAW.rstrip("/")


@dataclass
class GlobalConfigWorkflow:
    global_id: int = 0
    key: str = ""
    name: str = ""
    description: str = ""
    script: str = ""

    def _marshall(self):
        return {
            "global_id": self.global_id,
            "name": self.name,
            "description": self.description,
            "script": self.script,
        }


@dataclass
class GlobalConfigFunction(GlobalConfigWorkflow):
    pass


@dataclass
class GlobalConfig:

    _is_set: bool = False

    project_url: str = ""

    _project_id: str = ""
    _workspace_id: str = ""
    _tenant_id: str = ""

    workflows: Dict[str, GlobalConfigWorkflow] = field(default_factory=dict)
    functions: Dict[str, GlobalConfigFunction] = field(default_factory=dict)

    def __post_init__(self):

        if os.path.exists(CONFIG_FILE_PATH):
            config = toml.load(CONFIG_FILE_PATH)

            self.project_url = config.get("project_url")
            self._is_set = True

            ids = get_ids_from_app_url(self.project_url)
            self._tenant_id = ids.tenant_id
            self._workspace_id = ids.workspace_id
            self._project_id = ids.project_id

            # record workflows
            workflows_config = config.get("workflows", {})
            new_workflows = {}
            for key, workflow_config in workflows_config.items():
                new_workflow = GlobalConfigWorkflow(key=key, **workflow_config)
                new_workflows[key] = new_workflow
            self.workflows = new_workflows

            # record functions
            functions_config = config.get("functions", {})
            new_functions = {}
            for key, function_config in functions_config.items():
                new_function = GlobalConfigFunction(key=key, **function_config)
                new_functions[key] = new_function
            self.functions = new_functions

        else:
            self._is_set = False

    @property
    def is_set(self) -> bool:
        return self._is_set

    @property
    def tenant_id(self) -> bool:
        return self._tenant_id

    @property
    def workspace_id(self) -> bool:
        return self._workspace_id

    @property
    def project_id(self) -> bool:
        return self._project_id

    @property
    def tenant_api_url(self) -> str:
        return f"{API_URL}/app/{self.tenant_id}"

    @property
    def project_api_url(self) -> str:
        return f"{self.tenant_api_url}/{self.workspace_id}/{self.project_id}"

    def _marshall(self):
        return {
            "project_url": self.project_url,
            "type": "EXTERNAL",
            "workflows": {
                key: workflow._marshall() for key, workflow in self.workflows.items()
            },
            "functions": {
                key: function._marshall() for key, function in self.functions.items()
            },
        }

    def save(self):
        d = self._marshall()
        with open(CONFIG_FILE_PATH, "w") as f:
            f.write(toml.dumps(d))

    def update_configs(self, project_id: str, workspace_id: str, tenant_id: str):
        self._project_id = project_id
        self._workspace_id = workspace_id
        self._tenant_id = tenant_id
        self._is_set = True


GLOBAL_CONFIG = GlobalConfig()
