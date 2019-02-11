import os

DEFAULT_AML_PATH = os.getenv("DEFAULT_AML_PATH", "aml_config/azml_config.json")
WORKSPACE = os.getenv("_WORKSPACE", "distributed_benchmark")
RESOURCE_GROUP = os.getenv("_RESOURCE_GROUP", "msdistbenchaml")
SUBSCRIPTION_ID = os.getenv("_SUBSCRIPTION_ID", "")
REGION = os.getenv("_REGION", "eastus")