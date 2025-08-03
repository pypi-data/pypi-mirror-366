from abc import ABC, abstractmethod


class ObjectAsKeyValuePersistenceMixin(ABC):
    """Adds KV persistence support."""
    @property
    @abstractmethod
    def kv_key(self) -> str:
        """The key to use when persisting object"""
        ...

    @property
    @abstractmethod
    def kv_value_as_dict(self) -> dict:
        """Returns value that will be persisted as a dictionary."""
        ...

    @abstractmethod
    def setup_by_dict(self, setup: dict):
        """Does de necessary setup of object given its persisted values"""
        ...
