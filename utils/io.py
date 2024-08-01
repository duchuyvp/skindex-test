import yaml


def yaml_to_dict(file_path: str):
    """yaml_to_dict.

    Args:
        file_path (str): file_path
    """
    with open(file_path, "r", encoding="utf-8") as file:

        d = yaml.load(file, Loader=yaml.FullLoader)
        return d
