from dataclasses import dataclass


@dataclass
class IDs:
    tenant_id: str
    workspace_id: str
    project_id: str


def get_ids_from_app_url(app_url: str) -> IDs:

    app_url_without_https = app_url.replace("https://", "").replace("http://", "")

    # check if the project is pooled
    if "https://app.nemasystems.io" in app_url or "http://localhost" in app_url:
        url_splits = app_url_without_https.split("/")
        tenant_id = url_splits[1]
        workspace_id = url_splits[2]
        project_id = url_splits[3]
    else:
        # tenant is siloed
        tenant_id = app_url_without_https.split(".")[0]
        url_splits = app_url_without_https.split("/")
        workspace_id = url_splits[1]
        project_id = url_splits[2]

    return IDs(
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        project_id=project_id,
    )
