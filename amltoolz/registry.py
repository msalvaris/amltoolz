import json

import requests
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.containerregistry import ContainerRegistryManagementClient
from azureml._model_management._constants import WORKSPACE_RP_API_VERSION
from azureml.core.runconfig import AzureContainerRegistry
from azureml.exceptions import WebserviceException

_KEYS_URL = (
    "https://management.azure.com/subscriptions/{}/resourceGroups/{}/providers/"
    "Microsoft.MachineLearningServices/workspaces/"
    "{}/listKeys"
)


def _registry_dict_for(
    subscription_id, resource_group, workspace_name, authentication_header
):
    keys_endpoint = _KEYS_URL.format(subscription_id, resource_group, workspace_name)
    # headers = self.workspace._auth.get_authentication_header()
    params = {"api-version": WORKSPACE_RP_API_VERSION}
    try:
        keys_resp = requests.post(
            keys_endpoint, headers=authentication_header, params=params
        )
        keys_resp.raise_for_status()
    except requests.exceptions.HTTPError:
        raise WebserviceException(
            "Unable to retrieve workspace keys to run image:\n"
            "Response Code: {}\n"
            "Headers: {}\n"
            "Content: {}".format(
                keys_resp.status_code, keys_resp.headers, keys_resp.content
            )
        )
    content = keys_resp.content
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    return json.loads(content)


def _extract_credentials(registry_dict):
    try:
        username = registry_dict["containerRegistryCredentials"]["username"]
        passwords = registry_dict["containerRegistryCredentials"]["passwords"]
        password = passwords[0]["value"]
    except KeyError:
        raise WebserviceException(
            "Unable to retrieve workspace keys to run image, response "
            "payload missing container registry credentials."
        )

    return username, password


def credentials_from(workspace):
    registry_dict = _registry_dict_for(
        workspace.subscription_id,
        workspace.resource_group,
        workspace.name,
        workspace._auth.get_authentication_header(),
    )
    return _extract_credentials(registry_dict)


def address_for(registry_client, resource_group, registry_name):
    mreg = registry_client.registries.get(resource_group, registry_name)
    return mreg.login_server


def username_password_for(
    registry_client, resource_group, registry_name, password_index=0
):
    creds = registry_client.registries.list_credentials(resource_group, registry_name)
    return creds.username, creds.passwords[password_index].value


def properties(resource_group, registry_name, subscription_id=None):
    if subscription_id is None:
        registry_client = get_client_from_cli_profile(ContainerRegistryManagementClient)
    else:
        registry_client = get_client_from_cli_profile(
            ContainerRegistryManagementClient, subscription_id=subscription_id
        )

    username, password = username_password_for(
        registry_client, resource_group, registry_name
    )

    properties_dict = {
        "address": address_for(registry_client, resource_group, registry_name),
        "username": username,
        "password": password,
    }
    return properties_dict


def _print_properties(resource_group, registry_name, subscription_id=None):
    print(properties(resource_group, registry_name, subscription_id=subscription_id))


def azure_container_registry_for(resource_group, registry_name, subscription_id=None):
    properties_dict = properties(
        resource_group, registry_name, subscription_id=subscription_id
    )
    azr = AzureContainerRegistry()
    azr.address = properties_dict["address"]
    azr.username = properties_dict["username"]
    azr.password = properties_dict["password"]
    return azr


def azure_container_registry_for_workspace(workspace):
    return azure_container_registry_for(
        workspace.resource_group,
        _extract_registry_name_from(workspace),
        subscription_id=workspace.subscription_id,
    )


def _extract_registry_name_from(workspace):
    return workspace.get_details()["containerRegistry"].split("/")[-1]


def properties_from(workspace):
    return properties(
        workspace.resource_group,
        _extract_registry_name_from(workspace),
        subscription_id=workspace.subscription_id,
    )
