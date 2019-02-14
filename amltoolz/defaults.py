import os

DEFAULT_AML_PATH = os.getenv("DEFAULT_AML_PATH", "aml_config/azml_config.json")
WORKSPACE = os.getenv("WORKSPACE", "distributed_benchmark")
RESOURCE_GROUP = os.getenv("RESOURCE_GROUP", "msdistbenchaml")
SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID", "")
REGION = os.getenv("REGION", "eastus")