import click
from types import ModuleType
from typing import List
import requests
from typing import Optional

from nema.utils.global_config import (
    GLOBAL_CONFIG,
    GlobalConfig,
    GlobalConfigWorkflow,
    GlobalConfigFunction,
)
from nema.app import App
from nema.workflow.workflow import Workflow
from nema.connectivity.connectivity_manager import save_auth_data
from nema.run.workflow import run_workflow
from nema.run.app import run_wf_from_app
from nema.run.utils import add_code_directory_to_sys_path
from nema.utils.create_data_for_workflow import (
    get_new_data_for_workflow,
    submit_new_data_to_nema,
    update_workflow_file_with_new_global_ids,
)


def authenticate_user(username, password):

    # Authenticate the user
    if GLOBAL_CONFIG.is_set:

        tenant_url = GLOBAL_CONFIG.tenant_api_url

        login_url = f"{tenant_url}/authentication/login"

    else:
        raise Exception(
            "There is no nema.toml file in this directory. Please run `nema init` to create one."
        )

    # Make a request to the login URL
    response = requests.post(
        login_url, json={"username": username, "password": password}
    )

    if not response.ok:
        if response.status_code == 401:
            print("Invalid credentials")
        else:
            print(response.status_code, response.text)
            print("Failed to login")
        return None

    # save the authentication and refresh token to the home directory
    response_data = response.json()
    tokens = response_data["tokens"]
    refresh_token = tokens["refresh_token"]
    access_token = tokens["access_token"]

    # create the directory if it does not exist
    save_auth_data(refresh_token=refresh_token, access_token=access_token)

    print("Login successful \U00002705")


@click.group()
def cli():
    pass


@cli.command()
def login():
    """Login to Nema."""
    username = click.prompt("Please enter your username or email address")
    password = click.prompt("Please enter your password", hide_input=True)
    authenticate_user(username, password)


@cli.command()
def init():
    "Initialize nema.toml file"
    print("Initializing nema.toml file")

    new_global_config = GlobalConfig()

    new_global_config.project_url = click.prompt(
        "Please enter the project URL", type=str
    )

    new_artifact_type = click.prompt(
        "Please enter whether you want to create a workflow or a function",
        type=click.Choice(["workflow", "function"]),
    )
    new_identifier = click.prompt(
        f"Please enter a {new_artifact_type} identifier (this is only used locally)",
        type=str,
        default=f"my-first-{new_artifact_type}",
    )
    new_name = click.prompt(
        f"Please enter a name for the {new_artifact_type}",
        type=str,
        default=new_identifier,
    )
    new_description = click.prompt(
        f"Please enter a {new_artifact_type} description",
        type=str,
        default=f"A Python {new_artifact_type}",
    )

    if new_artifact_type == "workflow":
        new_workflow = GlobalConfigWorkflow(
            key=new_identifier,
            name=new_name,
            description=new_description,
            script=f"nema_{new_artifact_type}.py",
        )

        new_global_config.workflows[new_identifier] = new_workflow
    else:
        new_function = GlobalConfigFunction(
            key=new_identifier,
            name=new_name,
            description=new_description,
            script=f"nema_{new_artifact_type}.py",
        )

        new_global_config.functions[new_identifier] = new_function

    new_global_config.save()


@cli.group()
def workflow():
    pass


@workflow.command()
@click.argument("identifier", required=False)
def init(identifier: Optional[str]):
    "Record the workflow in Nema"

    if identifier is None:
        print("No workflow specified -- initializing all workflows")
        all_identifiers = GLOBAL_CONFIG.workflows.keys()
    else:
        all_identifiers = [identifier]

    for this_identifier in all_identifiers:
        print(f"Initializing workflow with identifier '{this_identifier}'")
        existing_workflow = GLOBAL_CONFIG.workflows[this_identifier]

        if existing_workflow.global_id > 0:
            print("Workflow already exists. Skipping.")
            continue

        workflow = Workflow(
            global_id=0,
            name=existing_workflow.name,
            description=existing_workflow.description,
        )

        global_id = workflow.create()
        print(f"Workflow successfully created with global id {global_id}. \U00002705")

        existing_workflow.global_id = global_id

    # save the global ID to the config file
    GLOBAL_CONFIG.save()


@workflow.command()
@click.argument("identifier", required=False)
def run(identifier: Optional[str]):
    "Run the workflow"

    if identifier is None:
        print("No workflow specified -- running all workflows")
        all_identifiers = GLOBAL_CONFIG.workflows.keys()
    else:
        all_identifiers = [identifier]

    for this_identifier in all_identifiers:
        print(f"Running workflow with identifier '{this_identifier}'")

        existing_workflow = GLOBAL_CONFIG.workflows[this_identifier]

        python_file = existing_workflow.script

        this_wf = Workflow(
            global_id=existing_workflow.global_id,
            name=existing_workflow.name,
            description=existing_workflow.description,
            # output_folder=output_folder,
        )

        run_workflow(this_wf, python_file)

        print(
            f"Workflow '{this_identifier}' successfully run \U0001f680 and results uploaded to Nema. \U00002705"
        )


@workflow.command(name="create-data")
@click.argument("identifier", required=False)
def create_data(identifier: Optional[str]):
    "Create data for the workflow"

    if identifier is None:
        print("No workflow specified -- creating data for all workflows")
        all_identifiers = GLOBAL_CONFIG.workflows.keys()
    else:
        all_identifiers = [identifier]

    for this_identifier in all_identifiers:
        print(f"Creating data for workflow with identifier '{this_identifier}'")

        existing_workflow = GLOBAL_CONFIG.workflows[this_identifier]

        python_file = existing_workflow.script

        # read the python file
        with open(python_file, "r") as f:
            code_to_execute = f.read()

        # to make sure that local imports work, we need to add the directory the code is in to the sys path
        add_code_directory_to_sys_path(python_file)

        # execute the application code
        user_module = ModuleType("user_module")

        # load code into module
        exec(code_to_execute, user_module.__dict__)

        # execute code
        run_function = user_module.run

        annotations = run_function.__annotations__
        arg_name = list(annotations)[0]
        input_type = annotations[arg_name]
        output_type = annotations["return"]

        data_to_create_inputs = get_new_data_for_workflow(
            run_function.__workflow_attributes__["input_global_id_mapping"], input_type
        )
        data_to_create_outputs = get_new_data_for_workflow(
            run_function.__workflow_attributes__["output_global_id_mapping"],
            output_type,
        )

        data_to_create = data_to_create_inputs + data_to_create_outputs

        # create the data
        submit_new_data_to_nema(data_to_create)

        new_workflow_file = update_workflow_file_with_new_global_ids(
            code_to_execute, data_to_create_inputs, data_to_create_outputs
        )

        # save the new workflow file
        with open(python_file, "w") as f:
            f.write(new_workflow_file)


@cli.group()
def function():
    pass


@function.command()
@click.argument("identifier", required=False)
def init(identifier: Optional[str]):
    "Record the function in Nema"

    if identifier is None:
        print("No function specified -- initializing all functions")
        all_identifiers = GLOBAL_CONFIG.functions.keys()
    else:
        all_identifiers = [identifier]

    for this_identifier in all_identifiers:
        print(f"Initializing function with identifier '{this_identifier}'")
        existing_function = GLOBAL_CONFIG.functions[this_identifier]

        if existing_function.global_id > 0:
            print("Function already exists. Skipping.")
            continue

        python_file = existing_function.script

        # read the python file
        try:
            with open(python_file, "r") as f:
                code_to_execute = f.read()
        except FileNotFoundError:
            print(f"Python file {python_file} not found.")
            code_to_execute = None

        function = App(
            global_id=0,
            name=existing_function.name,
            description=existing_function.description,
            code=code_to_execute,
        )

        global_id = function.create()
        print(f"Function successfully created with global id {global_id}. \U00002705")

        existing_function.global_id = global_id

    # save the global ID to the config file
    GLOBAL_CONFIG.save()


@function.command()
@click.argument("identifier", required=False)
def update(identifier: Optional[str]):
    "Update the function name, description and arguments in Nema" ""

    if identifier is None:
        print("No function specified -- updating all functions")
        all_identifiers = GLOBAL_CONFIG.functions.keys()
    else:
        all_identifiers = [identifier]

    for this_identifier in all_identifiers:
        print(f"Updating function with identifier '{this_identifier}'")
        existing_function = GLOBAL_CONFIG.functions[this_identifier]

        if existing_function.global_id == 0:
            print("Function needs to be initialized with Nema first. Skipping.")
            continue

        python_file = existing_function.script

        # read the python file
        with open(python_file, "r") as f:
            code_to_execute = f.read()

        function = App(
            global_id=existing_function.global_id,
            name=existing_function.name,
            description=existing_function.description,
            code=code_to_execute,
        )

        function.update()
        print(
            f"Function '{this_identifier}' successfully updated \U0001f680. Note that the associated workflows are not yet run."
        )


@function.command()
@click.argument("identifier", required=False)
@click.option(
    "--only-outdated",
    is_flag=True,
    default=False,
    help="Only run the outdated workflows",
)
@click.option(
    "--workflow-id",
    type=int,
    required=False,
    help="The specific workflow ID to run",
)
def run(
    identifier: Optional[str], workflow_id: Optional[int], only_outdated: bool = False
):
    "Run the function"

    if identifier is None:
        print("No function specified -- running all workflows\n")
        all_identifiers = GLOBAL_CONFIG.functions.keys()
    else:
        all_identifiers = [identifier]

    for this_identifier in all_identifiers:
        print(f"Running function with identifier '{this_identifier}'")

        existing_function = GLOBAL_CONFIG.functions[this_identifier]

        python_file = existing_function.script

        # read the python file
        with open(python_file, "r") as f:
            code_to_execute = f.read()

        # to make sure that local imports work, we need to add the directory the code is in to the sys path
        add_code_directory_to_sys_path(python_file)

        function = App(
            global_id=existing_function.global_id,
            name=existing_function.name,
            description=existing_function.description,
            code=code_to_execute,
        )

        function.extract_io_from_code()

        all_workflows_that_use_this_app = function.get_all_workflows()

        if len(all_workflows_that_use_this_app) == 0:
            print("No workflows use this function. Skipping.")
            continue

        if workflow_id is None:
            all_workflows_to_run = all_workflows_that_use_this_app
        else:
            all_workflows_to_run = [
                wf
                for wf in all_workflows_that_use_this_app
                if wf["global_id"] == workflow_id
            ]
            if len(all_workflows_to_run) == 0:
                print(f"No workflows found with ID {workflow_id}. Skipping. \U0000274c")
                continue

        for this_workflow_details in all_workflows_to_run:

            wf_global_id = this_workflow_details["global_id"]
            wf_name = this_workflow_details["name"]

            print(f"Running workflow '{wf_name}' (#{wf_global_id})..")

            this_wf = Workflow(
                global_id=wf_global_id,
                name=this_workflow_details["name"],
                description=this_workflow_details["description"],
            )

            has_run = run_wf_from_app(
                this_wf, function, only_run_outdated=only_outdated
            )

            if has_run:
                print(
                    f"Workflow '{wf_name}' (#{wf_global_id}) successfully run \U0001f680 and results uploaded to Nema. \U00002705 \n"
                )


if __name__ == "__main__":
    cli()
