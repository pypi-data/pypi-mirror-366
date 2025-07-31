from typing import Dict


class ParameterDiff:
    def __init__(self, to_add: Dict[str, str], to_update: Dict[str, str], to_remove: Dict[str, str]) -> None:
        self.to_add = to_add
        self.to_update = to_update
        self.to_remove = to_remove


def diff_parameters(local_parameters: Dict[str, str], remote_parameters: Dict[str, str]) -> ParameterDiff:
    to_add = {}
    to_update = {}
    to_remove = {}

    for key, value in local_parameters.items():
        if key in remote_parameters.keys():
            if value != remote_parameters[key]:
                to_update[key] = value
        else:
            to_add[key] = value

    for key, value in remote_parameters.items():
        if key not in local_parameters:
            to_remove[key] = value

    return ParameterDiff(to_add=to_add, to_update=to_update, to_remove=to_remove)
