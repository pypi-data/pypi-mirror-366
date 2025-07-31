import typing as t
from dataclasses import fields, is_dataclass


def from_dict[T](cls: type[T], value: dict[str, t.Any]) -> T:
    # 1. Check if the provided class is a dataclass
    if not is_dataclass(cls.__class__):
        msg = f"The provided class {cls.__name__} is not a dataclass type."
        raise ValueError(msg)

    # 2. Convert list type in dictionary to tuple type
    # 3. Recursively convert dict to dataclass
    init_dict: dict[str, t.Any] = {}
    dfields_type = {f.name: f.type for f in fields(cls)}
    dfields_init = {f.name: f.init for f in fields(cls)}

    for k, v in value.items():
        if k in dfields_type:
            # no initialize parameter
            if not dfields_init[k]:
                continue
            # initialize parameter
            if isinstance(v, dict):
                inner_cls = dfields_type[k]
                if isinstance(inner_cls, type):
                    init_dict[k] = from_dict(inner_cls, v)
            elif isinstance(v, list):
                init_dict[k] = tuple(v)
            else:
                init_dict[k] = v

    return cls(**init_dict)
