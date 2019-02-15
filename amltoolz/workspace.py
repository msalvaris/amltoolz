import logging
import os
from itertools import product, chain
from pathlib import Path

import azureml
from azureml.core.authentication import AuthenticationException
from azureml.core.authentication import (
    AzureCliAuthentication,
    InteractiveLoginAuthentication,
)
from azureml.core.authentication import ServicePrincipalAuthentication
from tabulate import tabulate
from toolz import pipe

from amltoolz import subscription
from amltoolz.collection import Collection
from amltoolz.compute_target import ComputeTarget
from amltoolz.defaults import (
    DEFAULT_AML_PATH,
    WORKSPACE,
    RESOURCE_GROUP,
    SUBSCRIPTION_ID,
    REGION,
)
from amltoolz.experiment import Experiment, runs_to_df
import pandas as pd


def _workspace_for(
    workspace_name,
    resource_group,
    subscription_id=None,
    workspace_region="eastus",
    auth=None,
):
    return azureml.core.Workspace.create(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        location=workspace_region,
        create_resource_group=True,
        exist_ok=True,
        auth=auth,
    )


def create_workspace(
    workspace_name,
    resource_group,
    subscription_id=None,
    workspace_region="eastus",
    filename="azml_config.json",
):
    logger = logging.getLogger(__name__)
    auth = _get_auth()
    ws = _workspace_for(
        workspace_name,
        resource_group,
        subscription_id=subscription_id,
        workspace_region=workspace_region,
        auth=auth,
    )

    logger.info(ws.get_details())
    ws.write_config(file_name=filename)
    return ws


def _get_auth():
    logger = logging.getLogger(__name__)
    if os.environ.get("AML_SP_PASSWORD", None) is not None:
        logger.debug("Trying to create Workspace with Service Principal")
        aml_sp_password = os.environ.get("AML_SP_PASSWORD")
        aml_sp_tennant_id = os.environ.get("AML_SP_TENNANT_ID")
        aml_sp_username = os.environ.get("AML_SP_USERNAME")
        auth = ServicePrincipalAuthentication(
            tenant_id=aml_sp_tennant_id,
            username=aml_sp_username,
            password=aml_sp_password,
        )
    else:
        logger.debug("Trying to create Workspace with CLI Authentication")
        try:
            auth = AzureCliAuthentication()
            auth.get_authentication_header()
        except AuthenticationException:
            logger.debug("Trying to create Workspace with Interactive login")
            auth = InteractiveLoginAuthentication()

    return auth


def load_workspace(path):
    auth = _get_auth()
    ws = azureml.core.Workspace.from_config(auth=auth, path=path)
    logger = logging.getLogger(__name__)
    logger.info(
        "\n".join(
            [
                "Workspace name: " + str(ws.name),
                "Azure region: " + str(ws.location),
                "Subscription id: " + str(ws.subscription_id),
                "Resource group: " + str(ws.resource_group),
            ]
        )
    )
    return ws


def _get_experiments(aml_workspace):
    # Need to create copy otherwise accessing the same key causes a reread from AML server
    experiments = aml_workspace.experiments
    return {
        exp_key: Experiment(exp_key, experiments[exp_key]) for exp_key in experiments
    }


def _get_compute_targets(aml_workspace):
    compute_targets = aml_workspace.compute_targets
    return {
        cmp_key: ComputeTarget(cmp_key, compute_targets[cmp_key])
        for cmp_key in compute_targets
    }


def _get_sub_id():
    pipe(
        subscription.list_subscriptions(),
        lambda x: tabulate(x, headers="firstrow"),
        print,
    )
    return input("Please choose a subscription id ")


def workspace_for_user(
    workspace_name=WORKSPACE,
    resource_group=RESOURCE_GROUP,
    subscription_id=SUBSCRIPTION_ID,
    workspace_region=REGION,
    path=DEFAULT_AML_PATH,
):
    if os.path.isfile(DEFAULT_AML_PATH):
        return load_workspace(DEFAULT_AML_PATH)
    else:
        if subscription_id is None:
            subscription_id = _get_sub_id()

        path_obj = Path(path)
        filename = path_obj.name
        return create_workspace(
            workspace_name,
            resource_group,
            subscription_id=subscription_id,
            workspace_region=workspace_region,
            filename=filename,
        )


_EXPERIMENT_COLUMNS = (
    "workspace",
    "experiment",
    "runId",
    "status",
    "startTimeUtc",
    "endTimeUtc",
)


def _experiment_df_from(experiment):
    return runs_to_df(experiment).assign(
        experiment=experiment.name, workspace=experiment.workspace.name
    )[list(_EXPERIMENT_COLUMNS)]


def _extract(ct_dict, nodes_iter):
    key = next(nodes_iter)
    value = ct_dict[key]
    if isinstance(value, dict):
        yield from _extract(value, nodes_iter)
    else:
        yield key, value
        yield from _extract(ct_dict, nodes_iter)


def _compute_target_df_from(compute_target):
    ct_dict = compute_target.serialize()

    # Traverses the nested structure extracting the leaves at a level before moving on to a branch.
    # The properties extracted are
    # name
    # location
    # properties                            computeType, provisioningState
    # properties properties                 vmSize, vmPriority
    # properties properties scaleSettings   minNodeCount, maxNodeCount, nodeIdleTimeBeforeScaleDown

    nodes_iter = (
        "name",
        "location",
        "properties",
        "computeType",
        "provisioningState",
        "properties",
        "vmSize",
        "vmPriority",
        "scaleSettings",
        "minNodeCount",
        "maxNodeCount",
        "nodeIdleTimeBeforeScaleDown",
    )

    return pipe(_extract(ct_dict, iter(nodes_iter)),
                dict,
                pd.DataFrame)


class Workspace(object):
    def __init__(
        self,
        workspace_name=WORKSPACE,
        resource_group=RESOURCE_GROUP,
        subscription_id=SUBSCRIPTION_ID,
        workspace_region=REGION,
        config_path=DEFAULT_AML_PATH,
    ):

        self.aml_workspace = workspace_for_user(
            workspace_name=workspace_name,
            resource_group=resource_group,
            subscription_id=subscription_id,
            workspace_region=workspace_region,
            path=config_path,
        )
        self.experiments = Collection(lambda: _get_experiments(self.aml_workspace))
        self.compute_targets = Collection(
            lambda: _get_compute_targets(self.aml_workspace)
        )

    def experiments_to_df(self):
        exp_iter = map(lambda x: getattr(x, "aml_experiment"), self.experiments)
        df_list = list(map(_experiment_df_from, exp_iter))
        return pd.concat(df_list)

    def compute_targets_to_df(self):
        ct_iter = map(lambda x: getattr(x, "aml_compute_target"), self.compute_targets)
        df_list = list(map(_compute_target_df_from, ct_iter))
        return pd.concat(df_list)


if __name__ == "__main__":
    logging.config.fileConfig(os.getenv("LOG_CONFIG", "logging.conf"))
    import fire

    fire.Fire({"create": create_workspace})
