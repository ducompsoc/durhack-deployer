from copy import copy
from dataclasses import asdict as dataclass_instance_as_dict, is_dataclass
import inspect
import json
from typing import Any, Type

from data_types import GitHubEvent

serialize_dataclasses: list[Type] = [GitHubEvent]
serialize_type_name_to_dataclass_map = {dataclass.__name__: dataclass for dataclass in serialize_dataclasses}


class DurHackDeployerJsonEncoder(json.JSONEncoder):
    def supported_dataclass(self, obj: object) -> Any:
        for dataclass in serialize_dataclasses:
            if isinstance(obj, dataclass):
                break
        else:
            raise ValueError("obj is not an instance of a supported dataclass")

        serialized = dataclass_instance_as_dict(obj)
        serialized["__type__"] = dataclass.__name__
        return serialized

    def default(self, obj: object) -> Any:
        if inspect.isclass(obj):
            raise ValueError("Class types cannot be serialized. Did you mean to serialize an instance?")

        if is_dataclass(obj):
            try:
                return self.supported_dataclass(obj)
            except ValueError:
                pass

        return json.JSONEncoder.default(self, obj)


def durhack_deployer_decode_object_hook(obj: dict) -> Any:
    if '__type__' in obj:
        obj_type_name = obj["__type__"]
        if not obj_type_name in serialize_type_name_to_dataclass_map:
            raise ValueError(f"Cannot deserialize unknown dataclass: '{obj_type_name}'")
        dataclass = serialize_type_name_to_dataclass_map[obj_type_name]
        obj_copy = copy(obj)
        del obj_copy["__type__"]
        return dataclass(**obj_copy)

    return obj


def durhack_deployer_json_dumps(obj):
    return json.dumps(obj, cls=DurHackDeployerJsonEncoder)


def durhack_deployer_json_loads(obj):
    return json.loads(obj, object_hook=durhack_deployer_decode_object_hook)