'''
Module: src/instant_crud/core/strings.py
This module contains string constants used throughout the instant-crud library.
'''

from typing import Final


class Strings:
    """
    Class containing all string constants used in the instant-crud library.
    """
    CONFIG_SETTINGS_FILE_NOT_FOUND: Final[str] = "Config file {filename} not found, using defaults"
    CONFIG_SETTINGS_FILE_LOADED: Final[str] = "Configuration loaded from {filename}"
    CONFIG_SETTINGS_INVALID_JSON: Final[str] = "Invalid JSON in config file {filename}: {error}"
    CONFIG_SETTINGS_INVALID_JSON_NO_NAME: Final[str] = "Invalid JSON in config file: {error}"
    CONFIG_SETTINGS_ERROR_LOADING: Final[str] = "Error loading config file {filename}: {error}"
    CORE_FACTORY_CRUD_ROUTER_CREATED: Final[str] = "CRUDRouter created for model {model_name} with prefix {prefix}"
    CORE_FACTORY_SERVICE_CREATED: Final[str] = "Service created for model {model_name} with class {service_class}"
    CORE_FACTORY_ROUTER_CREATED: Final[str] = "Router created with prefix {prefix} and tags {tags}"
    CORE_FACTORY_MODEL_REGISTERED: Final[str] = "Model {model_name} registered for auto CRUD"
    CORE_FACTORY_ROUTERS_CREATED: Final[str] = "Created {count} routers for registered models"
    CORE_FACTORY_ROUTER_NOT_FOUND: Final[str] = "Router not found for prefix {prefix}"
    CORE_FACTORY_SERVICE_NOT_FOUND: Final[str] = "Service not found for model {model_name}"
    SERVICES_BASE_OPERATION: Final[str] = "Operation: {operation} {extra}"
