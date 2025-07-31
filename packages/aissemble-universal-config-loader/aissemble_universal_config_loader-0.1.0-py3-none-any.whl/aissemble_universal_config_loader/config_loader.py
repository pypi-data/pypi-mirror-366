###
# #%L
# aiSSEMBLE::Universal Config::Loader
# %%
# Copyright (C) 2024 Booz Allen Hamilton Inc.
# %%
# This software package is licensed under the Booz Allen Public License. All Rights Reserved.
# #L%
###
from krausening.properties import PropertyManager
import os
import inspect


class ConfigLoader:
    """
    A aiSSEMBLE-universal-config config loader class acts as thin wrapper around Krausening PropertyManager class to provide functions to read properties. Also, provide the
     functions to load the properties into environment variables or global variables.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
        self._property_manager = PropertyManager.get_instance()

    def get_property(self, file: str, property_key: str) -> str:
        """
        get the given property key value from the given
        :param file: property file
        :param property_key: property key
        :return: value
        """
        return self._property_manager.get_properties(file).getProperty(property_key)

    def load(self, file: str = "configuration.properties"):
        """
        Load the .properties file from configurations/base directory
        :param file: (Optional) If not set, the default property file name, configuration.properties, is used
        :return properties
        """
        os.environ["KRAUSENING_BASE"] = os.environ.get("KRAUSENING_BASE", "")
        properties = self._property_manager.get_properties(file)

        return properties

    def load_as_env(self, file: str = "configuration.properties"):
        """
        Load the .properties file from configurations/base directory as environment variables
        :param file: (Optional) If not set, the default property file name, configuration.properties, is used
        :return properties
        """

        os.environ["KRAUSENING_BASE"] = os.environ.get("KRAUSENING_BASE", "")
        properties = self._property_manager.get_properties(file)

        for property_key, property_value in properties.items():
            os.environ[property_key] = property_value

        return properties

    def load_as_global(self, file: str = "configuration.properties"):
        """
        Load the .properties file from configurations/base directory as global variables.
        When read in variables, to be python compatible, the dash("-") in the variable name will be replaced with underscore ("_").
        :param file: (Optional) If not set, the default property file name, configuration.properties, is used
        :return properties
        """

        os.environ["KRAUSENING_BASE"] = os.environ.get("KRAUSENING_BASE", "")
        properties = self._property_manager.get_properties(file)
        # get caller frame
        frame = inspect.currentframe().f_back
        # retrieve caller's global namespaces from caller frame
        globals = frame.f_globals
        for property_key, property_value in properties.items():
            # replace dash (-) with underscore (_)
            property_key = property_key.replace("-", "_")
            globals[property_key] = property_value

        return properties

    def is_loaded(self, file: str):
        """
        Check if the given property file is a loaded
        :param file: property file
        :return: True/False value
        """
        return self._property_manager.is_loaded(file)
