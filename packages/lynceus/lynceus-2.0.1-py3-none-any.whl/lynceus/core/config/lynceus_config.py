import configparser
import json
from collections.abc import (Iterable,
                             MutableMapping)
from configparser import ConfigParser
from copy import deepcopy
from json import (JSONDecodeError,
                  JSONEncoder)
from logging import Logger
from pathlib import Path
from typing import Any, Callable

from lynceus.core.config import CONFIG_JSON_DUMP_KEY_END_KEYWORD
from lynceus.lynceus_exceptions import LynceusConfigError
from lynceus.utils import lookup_root_path


# pylint: disable=too-many-public-methods
class LynceusConfig(MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys.

       IMPORTANT: when a key does not exist, it is automatically created to ease definition like ['X']['Y']['Z'] = 'XXX'
       BUT: it means the 'in' operator should NOT be used, because it will always return True, because the checked key will be created if not existing,
        for such situation, you should use the lynceus.core.config.lynceus_config.LynceusConfig.has_section() method.
       """

    UNDEFINED_VALUE: str = '$*_UNDEFINED_*$'

    def __init__(self, *args, **kwargs):
        """
        Initialize a new LynceusConfig instance.

        Parameters
        ----------
        *args
            Positional arguments to initialize the config dictionary.
        **kwargs
            Keyword arguments to initialize the config dictionary.
        """
        self.__store = {}
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        """
        Get an item from the config, automatically creating sub-dictionaries if needed.

        Parameters
        ----------
        key
            The key to retrieve.

        Returns
        -------
        dict
            The value associated with the key.
        """
        # Creates automatically sub dictionary if needed.
        if LynceusConfig._keytransform(key) not in self.__store:
            self.__store[LynceusConfig._keytransform(key)] = {}

        return self.__store[LynceusConfig._keytransform(key)]

    def __setitem__(self, key, value):
        """
        Set an item in the config.

        Parameters
        ----------
        key
            The key to set.
        value
            The value to associate with the key.
        """
        self.__store[LynceusConfig._keytransform(key)] = LynceusConfig._valuetransform(value)

    def __delitem__(self, key):
        """
        Delete an item from the config.

        Parameters
        ----------
        key
            The key to delete.
        """
        del self.__store[LynceusConfig._keytransform(key)]

    def __iter__(self):
        """
        Iterate over the config keys.

        Returns
        -------
        iterator
            Iterator over the config keys.
        """
        return iter(self.__store)

    def __len__(self):
        """
        Get the number of items in the config.

        Returns
        -------
        int
            Number of items in the config.
        """
        return len(self.__store)

    @staticmethod
    def _keytransform(key):
        """
        Transform a key before using it in the store.

        Parameters
        ----------
        key
            The key to transform.

        Returns
        -------
        str
            The transformed key.
        """
        return key

    @staticmethod
    def _valuetransform(value):
        """
        Transform a value before storing it.

        Parameters
        ----------
        value
            The value to transform.

        Returns
        -------
        Any
            The transformed value.
        """
        if isinstance(value, LynceusConfig):
            # pylint: disable=protected-access
            return value.__store

        return value

    def copy(self):
        """
        Create a deep copy of this LynceusConfig instance.

        Returns
        -------
        LynceusConfig
            A new LynceusConfig instance with copied data.
        """
        lynceus_config_copy: LynceusConfig = LynceusConfig()
        # pylint: disable=protected-access,unused-private-member
        lynceus_config_copy.__store = deepcopy(self.__store)
        return lynceus_config_copy

    def as_dict(self):
        """
        Convert this LynceusConfig to a standard dictionary.

        Returns
        -------
        dict
            A deep copy of the internal store as a dictionary.
        """
        return deepcopy(self.__store)

    @staticmethod
    def dump_config_parser(config_parser: ConfigParser) -> str:
        """
        Convert a ConfigParser to a string representation.

        Parameters
        ----------
        config_parser : ConfigParser
            The ConfigParser instance to dump.

        Returns
        -------
        str
            String representation of the configuration.
        """
        result: str = ''
        for config_section in config_parser.sections():
            result += f'[{config_section}]\n'
            for key, value in config_parser.items(config_section):
                result += f'\t{key}={value}\n'
        return result

    def get_config(self, section: str, key: str, *, default: str | int | float | object | list | Path = UNDEFINED_VALUE) -> str | int | float | object | list | Path:
        """
        Get a configuration value from the specified section and key.

        Parameters
        ----------
        section : str
            The configuration section.
        key : str
            The configuration key.
        default : str or int or float or object or list, optional
            Default value to return if the config doesn't exist.

        Returns
        -------
        str or int or float or object or list or Path
            The configuration value or default.

        Raises
        ------
        LynceusConfigError
            If the config doesn't exist and no default is provided.
        """
        try:
            return self[section][key]
        except KeyError as error:
            # Safe-guard: raise an error if configuration not found and no default specified.
            if default == self.UNDEFINED_VALUE:
                raise LynceusConfigError(f'Configuration [\'{section}\'][\'{key}\'] does not exist in your configuration.') from error
            return default

    def unset_config(self, section: str, key: str) -> str | int | float | object | list | Path | None:
        """
        Unset configuration value from the specified section and key.

        Parameters
        ----------
        section : str
            The configuration section.
        key : str
            The configuration key.

        Returns
        -------
        str or int or float or object or list or Path or None
            The removed configuration value or None if it did not exist.

        Note:
            No exception will be raised if the config doesn't exist.
        """
        if not self.has_section(section):
            return None
        return self.__store[section].pop(key, None)

    def check_config_exists(self, section: str, key: str, *, transform_func=None) -> bool:
        """
        Check if a configuration option exists and optionally transform its value.

        This method verifies the existence of a configuration key under the specified
        section and can apply an optional transformation function to the value if found.
        The transformation is applied in-place, modifying the stored configuration value.

        Args:
            section: Configuration section name to check
            key: Configuration key to verify within the section
            transform_func: Optional function to transform the value if it exists.
                          Can be used for type casting or any value processing.
                          Caller must handle any exceptions during transformation.

        Returns:
            bool: True if the configuration option exists, False otherwise

        Note:
            If transform_func is provided and the configuration exists, the transformed
            value replaces the original value in the configuration store.
        """
        value = self.get_config(section, key, default=None)
        if value is None:
            return False

        # Checks if there is a trasnformation to apply.
        if transform_func:
            # Transforms (and registers) the value for further usage.
            self[section][key] = transform_func(value)

        # Returns the config option exists.
        return True

    @staticmethod
    def to_bool(value: str | None) -> bool | None:
        """
        Convert a string value to boolean.

        Parameters
        ----------
        value : str or None
            The value to convert.

        Returns
        -------
        bool or None
            True for '1', 'True', or True; False otherwise; None for None input.
        """
        if value is None:
            return None
        return value in ['1', 'True', True]

    def is_bool_config_enabled(self, section: str, key: str, *, default: bool = False) -> bool:
        """
        Check if a boolean configuration option is enabled.

        Parameters
        ----------
        section : str
            The configuration section.
        key : str
            The configuration key.
        default : bool, optional
            Default value if the config doesn't exist.

        Returns
        -------
        bool
            True if the configuration is enabled, False otherwise.
        """
        return LynceusConfig.to_bool(self.get_config(section=section, key=key, default=default))

    def get_config_as_dict(self, section: str, key: str):
        """
        Get a configuration value as a dictionary.

        Parameters
        ----------
        section : str
            The configuration section.
        key : str
            The configuration key.

        Returns
        -------
        dict
            The configuration value as a dictionary.
        """
        return self.get_config(section=section, key=key)

    def has_section(self, section: str) -> bool:
        """
        Check if a configuration section exists.

        Parameters
        ----------
        section : str
            The section name to check.

        Returns
        -------
        bool
            True if the section exists, False otherwise.
        """
        # Important: we must check the specified section on a list of keys, and not on the result of keys(), otherwise the automatic
        #  key addition will be performed in __getitem__() method, and this method will always return True.
        return section in list(self.keys())

    @staticmethod
    def __cleanse_value(value: str) -> str:
        """
        Remove quotes from string values.

        Parameters
        ----------
        value : str
            The value to cleanse.

        Returns
        -------
        str
            The cleansed value with quotes removed.
        """
        return value if not isinstance(value, str) else str(value).strip("'").strip('"')

    @staticmethod
    def transform_value_inner_keys(value, key_transform_func):
        """
        Recursively transform keys of a mapping using the provided key_transform_func.

        Parameters
        ----------
        value
            The value to transform.
        key_transform_func
            Function to transform keys.

        Returns
        -------
        dict or Any
            The value with transformed keys.
        """
        if not isinstance(value, (dict, MutableMapping)) or key_transform_func is None:
            return value

        return {key_transform_func(k): LynceusConfig.transform_value_inner_keys(v, key_transform_func) for k, v in value.items()}

    @staticmethod
    def merge_iterables(dest, src):
        """
        Helper function to merge iterable values.

        Parameters
        ----------
        dest
            Destination iterable to merge into.
        src
            Source iterable to merge from.

        Raises
        ------
        NotImplementedError
            If merging is not implemented for the destination type.
        """
        if isinstance(dest, list):
            dest.extend(src)
        elif isinstance(dest, set):
            dest.update(src)
        else:
            raise NotImplementedError(f'Merging not implemented for type {type(dest)}.')

    @staticmethod
    # pylint: disable=too-many-branches
    def recursive_merge(dict1: dict | MutableMapping,
                        dict2: dict | MutableMapping,
                        *,
                        override_section: bool = False,
                        override_value: bool = False,
                        key_transform_func: Callable[[str], str] | None = None):
        """
        Recursively merge configuration data from source into destination dictionary.

        This method performs a deep merge of two dictionaries, preserving existing values
        when possible and handling nested structures intelligently. It supports key
        transformation and configurable override behavior for sections and values.

        Args:
            dict1: Destination dictionary to merge data into (modified in-place)
            dict2: Source dictionary containing data to merge from
            override_section: If True, replaces existing sections completely.
                            If False, merges section contents recursively (default)
            override_value: If True, replaces existing non-mapping values.
                          If False, raises ValueError on conflicts (default)
            key_transform_func: Optional function to transform keys during merge.
                              Applied to both keys and nested dictionary keys

        Raises:
            ValueError: When value conflicts occur and override_value is False
            NotImplementedError: For unsupported iterable merge operations

        Note:
            - Automatically handles iterable values (lists, sets) by extending/updating
            - Creates new keys that don't exist in destination
            - Applies key transformation recursively to nested structures
            - Special handling for LynceusConfig objects to avoid auto-creation
        """
        for key, value in dict2.items():
            # Transform the key if a transformation function is provided.
            transformed_key = key_transform_func(key) if key_transform_func else key
            transformed_value = LynceusConfig.transform_value_inner_keys(value, key_transform_func) if key_transform_func else value

            # Checks if the corresponding key already exists in destination dict.
            # Important: do NOT use the in operator if first argument is a LynceusConfig, to avoid automatic creation of section here.
            if (isinstance(dict1, LynceusConfig) and not dict1.has_section(transformed_key)) or transformed_key not in dict1:
                dict1[transformed_key] = transformed_value
                continue

            # Handles iterable values that are not mappings.
            if isinstance(dict1[transformed_key], Iterable) and not isinstance(dict1[transformed_key], (dict, MutableMapping, str)):
                # Checks if "new" value is iterable
                if isinstance(transformed_value, Iterable) and not isinstance(transformed_value, str):
                    LynceusConfig.merge_iterables(dict1[transformed_key], transformed_value)
                    continue

            # Handles non-mapping values.
            if not isinstance(dict1[transformed_key], (dict, MutableMapping)):
                if override_value or dict1[transformed_key] == transformed_value:
                    dict1[transformed_key] = transformed_value
                    continue
                raise ValueError(f'Conflict at key "{transformed_key}": cannot merge non-mapping values'
                                 f' ({override_value=}; types {type(dict1[transformed_key])} vs {type(transformed_value)}).')

            # Handles mapping values.
            if isinstance(transformed_value, (dict, MutableMapping)):
                if override_section:
                    dict1[transformed_key] = transformed_value
                else:
                    LynceusConfig.recursive_merge(dict1[transformed_key],
                                                  transformed_value,
                                                  override_section=override_section,
                                                  override_value=override_value,
                                                  key_transform_func=key_transform_func)
            else:
                raise ValueError(f'Conflict at key "{transformed_key}": source value is not a mapping'
                                 f' ({override_value=}; types {type(dict1[transformed_key])} vs {type(transformed_value)}).')

    def merge(self, config_map: dict[str, Any] | MutableMapping, *,
              set_only_as_default_if_not_exist: bool = False, override_section: bool = False, override_value: bool = False, key_transform_func=None):
        """
        Merge a configuration dictionary into this LynceusConfig instance.

        This method provides flexible merging strategies for configuration data,
        supporting both additive merging and default-only merging modes. It automatically
        processes JSON dump parameters and handles complex nested structures.

        Args:
            config_map: Configuration dictionary or mapping to merge into this instance
            set_only_as_default_if_not_exist: If True, only sets values for keys that
                                            don't already exist (preserves existing values).
                                            If False, performs full recursive merge (default)
            override_section: Whether to replace existing sections completely rather
                            than merging their contents (default: False)
            override_value: Whether to replace existing non-mapping values rather
                          than raising conflicts (default: False)
            key_transform_func: Optional function to transform keys during merge.
                              Useful for namespacing or prefixing configuration keys.
                              Cannot be used with set_only_as_default_if_not_exist=True

        Raises:
            NotImplementedError: If key_transform_func is used with set_only_as_default_if_not_exist=True

        Note:
            - Automatically processes JSON dump parameters using special key endings
            - In default mode, uses Python 3.9+ dictionary merge operator for efficiency
            - In recursive mode, preserves existing nested structures while adding new data
        """
        # Processes automatically specified config_map to manage optional json dump options.
        config_map = LynceusConfig.load_json_params_from_lynceus_config(config_map).as_dict()

        if set_only_as_default_if_not_exist:
            if key_transform_func:
                raise NotImplementedError('key_transform_func option can not be used with set_only_as_default_if_not_exist option while merging config map.')

            # Uses the Python 3.9 ability to update Dictionary (considering existing values as the
            #  precedence ones).
            # TODO: it may be needed to iterate on each (key, value) pairs and recursively execute the | operator on them if value is dict-like instance ...
            self.__store = config_map | self.__store
            return

        # In this version, we need to merge everything, keeping existing inner (key; value) pairs.
        LynceusConfig.recursive_merge(self, config_map, override_section=override_section, override_value=override_value, key_transform_func=key_transform_func)

    def merge_from_lynceus_config(self, lynceus_config, *, override_section: bool = False, override_value: bool = False):
        """
        Merge configuration from another LynceusConfig instance.

        Parameters
        ----------
        lynceus_config : LynceusConfig
            The LynceusConfig instance to merge from.
        override_section : bool, optional
            Whether to override existing sections.
        override_value : bool, optional
            Whether to override existing values.
        """
        # pylint: disable=protected-access
        self.merge(lynceus_config.__store, override_section=override_section, override_value=override_value)

    def merge_from_config_parser(self, config_parser: ConfigParser, *, override_section: bool = False, key_transform_func=None):
        """
        Merge configuration data from a ConfigParser instance.

        This method converts ConfigParser sections and key-value pairs into dictionary
        format and merges them into this LynceusConfig instance. It automatically cleanses
        string values by removing quotes and supports key transformation.

        Args:
            config_parser: ConfigParser instance containing configuration data to merge
            override_section: If True, replaces existing sections completely.
                            If False, merges section contents with existing data (default)
            key_transform_func: Optional function to transform keys during merge.
                              Useful for adding prefixes or namespacing configuration keys

        Note:
            - Automatically removes quotes from string values during conversion
            - All merged values override existing non-mapping values (override_value=True)
            - ConfigParser sections become top-level keys in the LynceusConfig
        """
        # Merges each config parser section, as a dictionary, in this instance of Lynceus config.
        config_parser_to_dict = {config_section: {key: self.__cleanse_value(value) for key, value in config_parser.items(config_section)}
                                 for config_section in config_parser.sections()}
        self.merge(config_parser_to_dict, override_section=override_section, override_value=True, key_transform_func=key_transform_func)

    def lookup_configuration_file_and_update_from_it(self, config_file_name: Path | str, *,
                                                     must_exist: bool = True,
                                                     root_path: Path = Path().resolve(),
                                                     logger: Logger | None = None,
                                                     remaining_iteration: int = 3,
                                                     child_depth: int = 3,
                                                     **kwargs):
        """
        Look up a configuration file and update this config from it.

        Parameters
        ----------
        config_file_name : Path or str
            Name of the configuration file to look up.
        must_exist : bool, optional
            Whether the file must exist.
        root_path : Path, optional
            Root path to start the lookup from.
        logger : Logger, optional
            Optional logger for logging messages.
        remaining_iteration : int, optional
            Maximum number of parent directories
            to check. Defaults to 3.
        child_depth : int, optional
            The depth of child directories to explore at each level of the search.
            This allows the function to search within subdirectories up to the specified depth.
            Defaults to 3.
        **kwargs
            Additional arguments to pass to update_from_configuration_file.

        Raises
        ------
        FileNotFoundError
            If the file doesn't exist and must_exist is True.
        """
        try:
            # Retrieves the complete path of the configuration file, if exists.
            config_file_path = lookup_root_path(
                config_file_name,
                root_path=root_path,
                remaining_iteration=remaining_iteration,
                child_depth=child_depth) / Path(config_file_name)
            if logger:
                logger.debug(f'Found requested "{config_file_name=}" as "{config_file_path=}".')

            # Merges it in this instance.
            self.update_from_configuration_file(config_file_path, **kwargs)

            if logger:
                logger.info(f'Successfully load and merge configuration options from file "{config_file_name}".')
        except FileNotFoundError:
            # Raises FileNotFoundError only if configuration file should exist.
            if must_exist:
                raise

            if logger:
                logger.info(f'Configuration file "{config_file_name}" does not exist, so it will not be loaded (nor an error because {must_exist=}).')

    def update_from_configuration_file(self, file_path: Path, *,
                                       override_section: bool = False, key_transform_func=None) -> configparser.ConfigParser:
        """
        Load and merge configuration from a file into this LynceusConfig instance.

        This method reads a configuration file using ConfigParser, merges its contents
        into this LynceusConfig instance, and returns the loaded ConfigParser for
        additional operations such as fine-tuned logger configuration.

        Args:
            file_path: Path to the configuration file to load and merge
            override_section: If True, replaces existing sections completely.
                            If False, merges section contents with existing data (default)
            key_transform_func: Optional function to transform keys during merge.
                              Useful for adding prefixes or namespacing configuration keys

        Returns:
            configparser.ConfigParser: The loaded ConfigParser instance for additional operations

        Raises:
            FileNotFoundError: If the specified configuration file does not exist

        Note:
            - Uses UTF-8 encoding for file reading
            - Automatically merges all sections from the file into this instance
            - The returned ConfigParser can be used for logger configuration setup
        """
        if not file_path.exists():
            raise FileNotFoundError(f'Specified "{file_path}" configuration file path does not exist.')

        # Reads configuration file.
        config_parser: configparser.ConfigParser = configparser.RawConfigParser()
        config_parser.read(str(file_path), encoding='utf8')

        # Merges it into this instance.
        self.merge_from_config_parser(config_parser, override_section=override_section, key_transform_func=key_transform_func)

        return config_parser

    @staticmethod
    def format_config(config: MutableMapping | dict, *,
                      obfuscation_value: str | None = None,
                      sensitive_keys: list[str] | None = None,
                      obfuscation_value_from_length: int | None = None
                      ) -> dict:
        """
        Format a configuration dictionary with sensitive value obfuscation.

        Recursively processes a configuration dictionary to obfuscate sensitive
        values based on key patterns and value length. Useful for logging and
        debugging without exposing secrets.

        Args:
            config: Configuration dictionary to format
            obfuscation_value: String to replace sensitive values (default: '<secret>')
            sensitive_keys: List of key patterns to treat as sensitive
            obfuscation_value_from_length: Minimum length for automatic obfuscation

        Returns:
            dict: Formatted configuration with obfuscated sensitive values
        """
        obfuscation_value = obfuscation_value or '<secret>'
        sensitive_keys = sensitive_keys or ['secret', 'password', 'pwd', 'token']

        def obfuscator(key, value):
            """
            Apply obfuscation logic to key-value pairs.

            Args:
                key: Configuration key to check for sensitivity
                value: Configuration value to potentially obfuscate

            Returns:
                The original value or obfuscation string based on sensitivity rules
            """
            # Safe-guard: ensures key is iterable.
            if not isinstance(value, Iterable):
                return value

            # Returns obfuscation_value if key is in any specified sensitive ones.
            if any(sensitive_key in key for sensitive_key in sensitive_keys):
                return obfuscation_value

            # Returns untouched value if no length limit has been specified.
            if obfuscation_value_from_length is None:
                return value

            # Returns obfuscation_value if value has specified length or greater.
            return obfuscation_value if len(str(value)) >= obfuscation_value_from_length else value

        def process_value(key, value):
            """
            Recursively process configuration values for obfuscation.

            Args:
                key: Configuration key being processed
                value: Configuration value to process (dict, list, or scalar)

            Returns:
                Processed value with appropriate obfuscation applied
            """
            if isinstance(value, dict):
                return LynceusConfig.format_config(value,
                                                   obfuscation_value=obfuscation_value,
                                                   sensitive_keys=sensitive_keys,
                                                   obfuscation_value_from_length=obfuscation_value_from_length)

            if isinstance(value, list):
                return [process_value(key, item) for item in value]

            return obfuscator(key, value)

        return {key: process_value(key, value) for key, value in dict(config).items()}

    @staticmethod
    def format_dict_to_string(dict_to_convert: MutableMapping, indentation_level: int = 0) -> str:
        """
        Convert a dictionary to a formatted, indented string representation.

        Recursively formats nested dictionaries and LynceusConfig objects into
        a hierarchical string with proper indentation. Useful for configuration
        display and logging.

        Args:
            dict_to_convert: Dictionary to convert to string
            indentation_level: Current indentation level for nested formatting

        Returns:
            str: Formatted string representation with proper indentation
        """
        return '\n'.join('\t' * indentation_level + f'{key}={str(value)}'
                         if not isinstance(value, dict) and not isinstance(value, LynceusConfig)
                         else '\t' * indentation_level + f'[{key}]\n' + LynceusConfig.format_dict_to_string(value, indentation_level + 1)
                         for key, value in dict_to_convert.items())

    def dump_for_config_file(self) -> str:
        """
        Dump this config to a string suitable for saving to a configuration file.

        Returns
        -------
        str
            String representation of the configuration.
        """
        return LynceusConfig.dump_to_config_str(self.__store)

    @staticmethod
    def dump_to_config_str(value) -> str:
        """
        Dump a value to a JSON configuration string.

        Parameters
        ----------
        value
            The value to dump.

        Returns
        -------
        str
            JSON string representation of the value.
        """
        return json.dumps(value, cls=LynceusConfigJSONEncoder)

    @staticmethod
    def load_from_config_str(lynceus_config_dump: str | dict[str, Any]):
        """
        Load a LynceusConfig from a JSON configuration string.

        Parameters
        ----------
        lynceus_config_dump : str or dict
            JSON string or dict to load from.

        Returns
        -------
        LynceusConfig or dict
            Loaded configuration data.

        Raises
        ------
        LynceusConfigError
            If the JSON cannot be loaded.
        """
        # TODO: may be better to instantiate an empty LynceusConfig, and use merge method here too.
        try:
            loaded_collection = json.loads(lynceus_config_dump)
        except JSONDecodeError as exc:
            # pylint: disable=raise-missing-from
            raise LynceusConfigError(f'Unable to JSON load config from specified string: "{lynceus_config_dump}".', from_exception=exc)

        if isinstance(loaded_collection, dict):
            return LynceusConfig(loaded_collection)

        return loaded_collection

    @staticmethod
    def load_json_params_from_lynceus_config(config_map: dict[str, Any] | MutableMapping):
        """
        Load JSON parameters from a configuration map.

        Parameters
        ----------
        config_map : dict or MutableMapping
            Configuration map to load from.

        Returns
        -------
        LynceusConfig
            Loaded LynceusConfig instance.

        Raises
        ------
        LynceusConfigError
            If the config_map is not a dict or MutableMapping.
        """
        # Safe-guard: ensures specified parameter is a dict.
        if not isinstance(config_map, (dict, MutableMapping)):
            raise LynceusConfigError(f'Specified parameter {config_map=} should be a dict ({type(config_map)} actually.')

        # Loads the specified config (e.g. custom user Project Profile metadata, jobs overriding/configuration options):
        #  - if key ends with the special json keyword, loads it
        #  - otherwise keep the key, value metadata pair unchanged
        loaded_lynceus_config: LynceusConfig = LynceusConfig()
        for config_param_with_json_key in list(config_map):
            # Checks if it is a json dump metadata.
            config_param_with_json_key_name: str = str(config_param_with_json_key)
            if not config_param_with_json_key_name.endswith(CONFIG_JSON_DUMP_KEY_END_KEYWORD):
                # It is NOT a json dump.

                # Checks if the value is a complex one.
                if isinstance(config_map[config_param_with_json_key_name], (dict, MutableMapping)):
                    # Calls recursively this method on the complex value.
                    loaded_lynceus_config[config_param_with_json_key_name].update(LynceusConfig.load_json_params_from_lynceus_config(config_map[config_param_with_json_key_name]).as_dict())
                else:
                    # Registers this single value.
                    LynceusConfig.recursive_merge(loaded_lynceus_config, {config_param_with_json_key_name: config_map[config_param_with_json_key_name]})

                continue

            # Loads the json value, and merges it recursively.
            loaded_metadata_key = config_param_with_json_key_name.removesuffix(CONFIG_JSON_DUMP_KEY_END_KEYWORD)
            value_dump = config_map[config_param_with_json_key]
            LynceusConfig.recursive_merge(loaded_lynceus_config, {loaded_metadata_key: LynceusConfig.load_from_config_str(value_dump)})

        return loaded_lynceus_config

    def save_partial_to_config_file(self, *, section_key_map: list[tuple], file_path: Path,
                                    key_transform_func=None,
                                    logger: Logger | None = None, log_prefix: str | None = ''):
        """
        Save specific configuration options to a configuration file.

        This method extracts specified configuration options from this LynceusConfig
        instance and saves them to a configuration file in standard INI format.
        It handles different value types appropriately, using JSON serialization
        for complex types and string representation for simple types.

        Args:
            section_key_map: List of (section, key) tuples specifying which configuration
                           options to save. Non-existing options are silently skipped
            file_path: Path where the configuration file should be saved
            key_transform_func: Optional function to transform keys before saving.
                              Useful for adding prefixes or namespacing
            logger: Optional logger for recording save operations and debugging
            log_prefix: Optional prefix string for log messages

        Note:
            - Path objects are saved as strings, not JSON
            - Non-string complex types are saved as JSON with special key suffix
            - String values are saved directly without modification
            - Creates ConfigParser sections automatically as needed
            - Uses UTF-8 encoding for file writing
        """
        config_parser: ConfigParser = ConfigParser()
        not_existing_value: str = 'no/th/ing'

        # Defines the metadata lynceus file, from complete configuration file, if defined.
        for metadata_option in section_key_map:
            section: str = metadata_option[0]
            key: str = metadata_option[1]

            # Attempts to retrieve the value.
            value = self.get_config(section, key, default=not_existing_value)
            if value == not_existing_value:
                continue

            # Ensures section exists.
            if not config_parser.has_section(section):
                config_parser.add_section(section)

            # Transforms key if func is specified (useful to save project template config options, while processing the project to score).
            if key_transform_func:
                key = key_transform_func(key)

            # Registers it.
            if isinstance(value, Path):
                # - Path are saved as a string (not as a json dump, which is not loadable).
                value = str(value)
            elif not isinstance(value, str):
                # - all other type, but string, are saved as Json dump.
                key += CONFIG_JSON_DUMP_KEY_END_KEYWORD
                value = self.dump_to_config_str(value)
            #     - registers it inside config_parser.
            config_parser.set(section, key, value)

        if not config_parser.sections():
            logger.info(f'{log_prefix} no configuration option found to create Lynceus metadata file content among "{section_key_map}"')
            return

        if logger:
            logger.debug(f'{log_prefix} created Lynceus metadata file content:\n{LynceusConfig.dump_config_parser(config_parser)}')

        with open(file_path, 'w', encoding='utf8') as file:
            config_parser.write(file)

        if logger:
            logger.debug(f'{log_prefix} successfully written Lynceus metadata to file "{file_path}".')

    def is_empty(self):
        """
        Check if the configuration is empty.

        Returns
        -------
        bool
            True if the configuration has no items, False otherwise.
        """
        return len(self.__store) == 0

    def __repr__(self):
        """
        Return the string representation of this LynceusConfig.

        Returns
        -------
        str
            Formatted string representation of the configuration.
        """
        return str(LynceusConfig.format_config(self))

    def __str__(self):
        """
        Return the string representation of this LynceusConfig.

        Returns
        -------
        str
            Formatted string representation of the configuration.
        """
        return LynceusConfig.format_dict_to_string(LynceusConfig.format_config(self))

    def __or__(self, other):
        """
        Implement the | operator for merging configurations.

        Parameters
        ----------
        other : LynceusConfig or dict
            Another LynceusConfig or dict to merge with.

        Returns
        -------
        LynceusConfig
            New LynceusConfig instance with merged data.

        Raises
        ------
        ValueError
            If other is not a LynceusConfig or dict.
        """
        if isinstance(other, LynceusConfig):
            # pylint: disable=protected-access
            return LynceusConfig(self.__store | other.__store)

        # Implements Python 3.9+ dict | operator allowing mixing between LynceusConfig and dict.
        if isinstance(other, dict):
            return LynceusConfig(self.__store | other)

        raise ValueError(f'| operator can not be used on "{type(self)}" with'
                         f' an instance of type {type(other)}.')


class LynceusConfigJSONEncoder(JSONEncoder):
    """
    Custom JSON encoder for LynceusConfig objects.
    """

    def default(self, o):
        """
        Convert objects to JSON-serializable format.

        Parameters
        ----------
        o
            Object to encode.

        Returns
        -------
        Any
            JSON-serializable representation of the object.
        """
        if isinstance(o, LynceusConfig):
            return dict(o)

        if isinstance(o, set):
            return list(o)

        if isinstance(o, Path):
            return str(o)

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)
