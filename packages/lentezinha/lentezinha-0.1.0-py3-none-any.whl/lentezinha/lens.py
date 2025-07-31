from typing import Any, Callable, Mapping
from functools import reduce
from pydantic import BaseModel


def read(data, path: str, separator: str = ".") -> Any:
    """Get a value from nested dict, list and Pydantic model

    >>> user = {"profile": {"age": 20}}
    >>> read(user, "profile.age")
    20
    """
    return Lens(path, separator).get(data)


def update(data: Any, path: str, value: Any, separator: str = ".") -> Any:
    """Set a value in a nested dict, list or Pydantic model

    >>> user = {"profile": {"age": 20}}
    >>> update(user, "profile.age", 21)
    >>> user
    {"profile": {"age": 21}}
    """
    return Lens(path, separator).set(data, value)


class Lens:
    def __init__(self, lens: str, separator: str = "."):
        if not self._is_valid(lens):
            raise ValueError(f"Invalid lens '{lens}'")
        self.keys = lens.split(separator)

    def get(self, data) -> Any:
        return get_deep(data, self.keys)

    def set(self, data, value: Any) -> None:
        if len(self.keys) == 1:
            last_but_one = data
        else:
            last_but_one = get_deep(data, self.keys[:-1])
        _agnostic_set(last_but_one, self.keys[-1], value)

        return get_deep(data, self.keys)

    def _is_valid(self, path: str) -> bool:  # TODO: implement
        return True


def _agnostic_set(container: dict | list | BaseModel, key: Any, value: Any) -> None:
    """Equivalent to container[key] = value or container.key = value"""
    if isinstance(container, dict):
        if isinstance(value, Callable):
            container[key] = value(container[key])
        else:
            container[key] = value

    elif isinstance(container, list):
        index: int = int(key)
        if isinstance(value, Callable):
            container[index] = value(container[index])
        else:
            container[index] = value

    elif isinstance(container, BaseModel):
        if isinstance(value, Callable):
            vars(container)[key] = value(vars(container)[key])
        else:
            vars(container)[key] = value


def _agnostic_get(container: Any, attribute: str) -> Any | None:
    """Equivalent to container.get(attribute) or container[attribute] or None"""
    if isinstance(container, dict):
        return container.get(attribute)
    elif isinstance(container, list):
        try:
            index: int = int(attribute)
            return container[index] if 0 <= index < len(container) else None
        except ValueError:
            return None
    elif isinstance(container, BaseModel):
        return vars(container)[attribute]
    return None


def get_deep(data: Mapping[str, Any], attributes: list[str]) -> Any:
    return reduce(_agnostic_get, attributes, data)
