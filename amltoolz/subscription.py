import logging
import os
import subprocess
import sys

from azure.common.client_factory import get_client_from_cli_profile
from azure.common.credentials import get_cli_profile
from azure.mgmt.resource import SubscriptionClient
from knack.util import CLIError


_GREEN = "\033[0;32m"
_BOLD = "\033[;1m"


def _run_az_cli_login():
    process = subprocess.Popen(
        ["az", "login"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    for c in iter(lambda: process.stdout.read(1), b""):
        sys.stdout.write(_GREEN + _BOLD + c.decode(sys.stdout.encoding))


def list_subscriptions():
    logger = logging.getLogger(__name__)
    try:
        sub_client = get_client_from_cli_profile(SubscriptionClient)
    except CLIError:
        logger.info("Not logged in, running az login")
        _run_az_cli_login()
        sub_client = get_client_from_cli_profile(SubscriptionClient)

    return [["Subscription_name", "Subscription ID"]] + [
        [sub.display_name, sub.subscription_id]
        for sub in sub_client.subscriptions.list()
    ]


def select(sub_name_or_id):
    profile = get_cli_profile()
    profile.set_active_subscription(sub_name_or_id)


if __name__ == "__main__":
    logging.config.fileConfig(os.getenv("LOG_CONFIG", "logging.conf"))
    import fire

    fire.Fire({"list": list_subscriptions, "select": select})
