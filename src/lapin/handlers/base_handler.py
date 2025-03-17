# model_handler.py
from typing import Dict, Any, List, Optional

from llm_libs.conf.base_conf import CONFIG_REGISTRY #relative import, this will work?

class ModelHandler:
    """
    Manages the orchestration between configuration classes and caller classes.
    """
    def __init__(self):
        # Optionally, you can store state here or load more context if needed
        pass

    def get_response(self, alias: str, prompt: str) -> str:
        """
        High-level method that:
          1) Looks up the config class by alias in CONFIG_REGISTRY.
          2) Instantiates the config object.
          3) Retrieves the caller class from config.caller_class().
          4) Builds the caller with config.get_params().
          5) Calls the LLM and returns the text.
        """
        config_cls = CONFIG_REGISTRY.get(alias)
        if not config_cls:
            raise ValueError(f"No configuration found for alias '{alias}'.")
        # print ("a")
        config_obj = config_cls()  # Instantiate the configuration
        # print ("b")

        caller_cls = config_obj.caller_class()
        # print ("c")

        params = config_obj.get_params()

        caller = caller_cls(params)
        return caller.call_llm(prompt)

    # Additional methods could be added here. For example:
    # - a method to list available aliases
    # - a method to refresh environment variables
    # - concurrency or request tracking
    def list_available_models(self) -> List[str]:
        """
        Return a list of all available model aliases.
        """
        return sorted(CONFIG_REGISTRY.keys())