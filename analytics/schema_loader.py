import yaml


SCHEMA_PATH = "semantic_layer/schema.yaml"


def load_schema():
    """
    Load semantic schema configuration
    """

    with open(SCHEMA_PATH, "r") as f:
        schema = yaml.safe_load(f)

    return schema
