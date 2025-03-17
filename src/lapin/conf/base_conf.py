# base.py
from abc import ABC, abstractmethod


CONFIG_REGISTRY = {}

def register_config(cls):
    alias = cls.alias()
    CONFIG_REGISTRY[alias] = cls
    return cls



class BaseModelConfig(ABC):
    """
    Abstract base class for all model configurations.
    Each subclass must define:
      1) alias() -> str
      2) get_params() -> dict
      3) caller_class() -> reference to the appropriate caller
    """

    @classmethod
    @abstractmethod
    def alias(cls) -> str:
        pass

    @abstractmethod
    def get_params(self) -> dict:
        """
        Return a dictionary of parameters needed by the low-level caller.
        """
        pass

    @abstractmethod
    def caller_class(self):
        """
        Return the reference to the appropriate caller from llm_calls.py
        """
        pass
