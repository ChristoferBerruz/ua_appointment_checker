from functools import wraps
from dataclasses import dataclass, field
from typing import Any, Dict, Callable
from collections import OrderedDict


@dataclass
class RegistryEntry:
    func: Callable
    description: str
    endpoint: str


@dataclass
class RegistryManager:
    registry: Dict[str, RegistryEntry] = field(default_factory=OrderedDict)

    def register(self, endpoint: str, description: str):
        def decorator(func: Callable) -> Callable:
            entry = RegistryEntry(
                func=func,
                description=description,
                endpoint=endpoint
            )
            self.registry[endpoint] = entry
            return func
        return decorator


manager = RegistryManager()
