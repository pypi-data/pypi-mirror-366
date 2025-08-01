import configparser
import logging.config
import logging.handlers
from logging import Logger
from pathlib import Path

from lynceus.core.config import CONFIG_GENERAL_KEY
from lynceus.core.config.lynceus_config import LynceusConfig
from lynceus.lynceus_exceptions import LynceusConfigError
from lynceus.utils import format_exception_human_readable, lookup_root_path


class LynceusSession:
    """
    Central session management class for the Lynceus framework.

    This class manages configuration loading, logging setup, and session lifecycle
    for Lynceus applications. It implements a singleton-like pattern using registration
    keys to ensure proper session management and prevent memory leaks.

    The class handles:
    - Configuration file loading (default and user-specific)
    - Logger initialization and management
    - Session registration and retrieval
    - Fine-tuned logging configuration

    Attributes:
        TRACE (int): Additional log level more verbose than DEBUG
    """
    DEFAULT_SALT: str = 'lynceus'

    # Additional even more verbose than DEBUG log level.
    TRACE = 5

    __internal_key_preventing_external_usage_of_init = object()

    __REGISTERED_SESSIONS: dict = {}

    def __init__(self, *,
                 salt: str = DEFAULT_SALT,
                 root_logger_name: str = 'Lynceus',
                 load_core_default_config: bool = True,
                 overridden_root_logger_level: int | str | None = None,
                 _creation_key=None):
        """
        Initialize a new Lynceus session with configuration and logging setup.

        **WARNING**: This constructor should NEVER be called directly by clients.
        Always use :py:meth:`~lynceus.core.lynceus.LynceusSession.get_session`
        to obtain session instances.

        This method sets up the complete session infrastructure including:
        - Configuration file loading (default and user-specific)
        - Logger initialization with custom TRACE level
        - Root logger configuration with specified level

        Parameters
        ----------
        salt : str, optional
            Unique identifier for this session, used for configuration file lookup
        root_logger_name : str, optional
            Name prefix for all loggers created by this session.
            Used as namespace for :py:meth:`~lynceus.core.lynceus.LynceusSession.get_logger`
        load_core_default_config : bool, optional
            Whether to load Lynceus framework default configuration.
            Strongly recommended for proper framework operation
        overridden_root_logger_level : int, str, or None, optional
            Override for root logger level from configuration.
            Useful for CLI tools with --quiet, --debug options
        _creation_key : optional
            Internal safeguard key to prevent direct constructor usage.
            Should NEVER be specified by external callers

        Raises
        ------
        RuntimeError
            If called directly without proper internal creation key

        Notes
        -----
        - Automatically registers custom TRACE logging level (more verbose than DEBUG)
        - Loads configuration files in order: default → salt-specific (default and user) → salt-flavor-specific (according to merged configuration) → user files
        - Sets up root logger with level from config or override parameter
        """
        # Safe-guard: prevents direct call to this method.
        if _creation_key != LynceusSession.__internal_key_preventing_external_usage_of_init:
            raise RuntimeError(f'You should always use LynceusSession.get_session() method when requesting a LynceusSession ({salt=}).')

        # Initializes internal Lynceus config.
        self.__config = LynceusConfig()
        self.__root_logger_name = root_logger_name

        # Loads configuration file(s):
        #  - first the default config according to load_core_default_config toggle
        #  - then the default and user config corresponding to specify salt, if not the default one
        loaded_config_files = self.__load_configuration(salt, load_core_default_config=load_core_default_config)

        # Additional even more verbose than DEBUG log level.
        logging.TRACE = LynceusSession.TRACE
        logging.addLevelName(LynceusSession.TRACE, 'TRACE')

        # Setups default/root Lynceus logger.
        self.__logger = self.get_logger()
        root_level: int | str = logging.getLevelName(overridden_root_logger_level or self.get_config(CONFIG_GENERAL_KEY, 'logger.root.level', default='INFO'))
        self.__logger.setLevel(root_level)

        # Informs now that Logger is initialized.
        self.__logger.info(f'[{salt=}]This is the loading information of looked up configuration files (Format=<Path: isLoaded?>) "{loaded_config_files}".')

    @staticmethod
    # pylint: disable=protected-access
    def get_session(*,
                    salt: str = DEFAULT_SALT,
                    registration_key: dict[str, str] | None = None,
                    root_logger_name: str = 'Lynceus',
                    load_core_default_config: bool = True,
                    overridden_root_logger_level: str | None = None) -> 'LynceusSession':
        """
        Get or create a Lynceus session with specified configuration.

        This is the main entry point for obtaining a LynceusSession instance.
        It implements session caching based on registration keys to prevent
        duplicate sessions and memory leaks.

        Parameters
        ----------
        salt : str, optional
            Unique identifier for the session (default: 'lynceus')
        registration_key : dict or None, optional
            Dictionary used to identify and cache sessions.
            Required for non-default salt values to prevent memory leaks.
        root_logger_name : str, optional
            Name prefix for all loggers created by this session
        load_core_default_config : bool, optional
            Whether to load Lynceus default configuration
        overridden_root_logger_level : str or None, optional
            Override the root logger level from config

        Returns
        -------
        LynceusSession
            A configured Lynceus session instance

        Raises
        ------
        LynceusConfigError
            If registration_key is missing for non-default salt
        """
        # Safe-guard: a registration key is highly recommended if not an internal session (which would be the case with salt == DEFAULT_SALT).
        # Important: sometimes caller uses an optional **kwargs which then leads to empty dict (which is not None), and thus must be taken care too.
        if not registration_key:
            if salt != LynceusSession.DEFAULT_SALT:
                raise LynceusConfigError('It is mandatory to provide your own registration_key when getting a session.' +
                                         f' System will automatically consider it as {registration_key}, but you may not be able to retrieve your session.' +
                                         ' And it may lead to memory leak.')
            registration_key = {'default': salt}

        # Turns the registration_key to an hashable version.
        if registration_key is not None:
            registration_key = frozenset(registration_key.items())

        # Creates and registers the session if needed.
        if registration_key in LynceusSession.__REGISTERED_SESSIONS:
            session: LynceusSession = LynceusSession.__REGISTERED_SESSIONS[registration_key]
            session.__logger.debug(f'Successfully retrieved cached Session for registration key "{registration_key}": {session}.')
        else:
            session: LynceusSession = LynceusSession(salt=salt, root_logger_name=root_logger_name,
                                                     load_core_default_config=load_core_default_config,
                                                     overridden_root_logger_level=overridden_root_logger_level,
                                                     _creation_key=LynceusSession.__internal_key_preventing_external_usage_of_init)

            LynceusSession.__REGISTERED_SESSIONS[registration_key] = session
            session.__logger.debug(f'Successfully registered new Session (new total count={len(LynceusSession.__REGISTERED_SESSIONS)})'
                                   f' for registration key "{registration_key}": {session}.'
                                   f' This is its loaded configuration (salt={salt}):\n' +
                                   f'{LynceusConfig.format_dict_to_string(LynceusConfig.format_config(session.__config), indentation_level=1)}')

        # TODO: implement another method allowing to free a specific registered session
        # TODO: turn LynceusSession as a Context, allowing usage with the 'with' keyword to automatic free the session once used

        # Returns the Lynceus session.
        return session

    def __do_load_configuration_files(self, config_file_meta_list) -> dict[Path, bool]:
        """
        Load configuration files from a list of metadata specifications.

        This method processes a list of configuration file metadata and attempts
        to load each file into the internal configuration. It handles missing files
        gracefully and sets up fine-tuned logging configurations when present.

        Parameters
        ----------
        config_file_meta_list : list
            List of dictionaries containing configuration file metadata with keys:
            - 'config_path': Path to the configuration file
            - 'root_path': Optional root path for file lookup

        Returns
        -------
        dict[Path, bool]
            Mapping of configuration file paths to loading status

        Notes
        -----
        Missing configuration files are handled gracefully and logged as debug messages.
        Files with logger sections trigger fine-tuned logging configuration.
        """
        loaded_config_files: dict[Path, bool] = {}
        for config_file_meta in config_file_meta_list:
            conf_file_name = config_file_meta['config_path']
            conf_file_root_path = config_file_meta.get('root_path', Path().resolve())

            loaded: bool = False
            relative_file: Path = Path(conf_file_name)
            try:
                full_path: Path = lookup_root_path(relative_file, root_path=conf_file_root_path) / relative_file

                # Merges it in internal Lynceus config.
                additional_config: configparser.ConfigParser = self.__config.update_from_configuration_file(full_path)

                # Updates/Configures fine-tuned logger, if any in this (first or) additional configuration file.
                # N.B.: in ideal world, could be interesting to extract logger config from all configuration file(s) merged, and
                #  create a fake fileConfig in memory, to logging.config.fileConfig once for all, after all loading.
                # Without that, handlers and formatters must be redefined each time, in each configuration file definined fine-tuned logger configuration.
                if 'loggers' in additional_config.sections():
                    self.get_logger('internal').debug(f'Requesting fine-tuned logger configuration with configuration coming from {conf_file_name}.')
                    # Cf. https://docs.python.org/3.10/library/logging.config.html#logging.config.fileConfig
                    logging.config.fileConfig(full_path, disable_existing_loggers=False, encoding='utf-8')

                loaded = True
            except FileNotFoundError as exc:
                # Since recent version, there is no more mandatory configuration file to have, and several files can be loaded.
                # N.B.: it is valid, there is no logger yet here, so using print ...
                self.get_logger('internal').debug(f'WARNING: Unable to load "{conf_file_name}" configuration file,'
                                                  f' from "{conf_file_root_path}"'
                                                  f' (it is OK, because this configuration file is NOT mandatory) =>'
                                                  f' {format_exception_human_readable(exc, quote_message=True)}')

            # Registers configuration file loading information.
            loaded_config_files[relative_file] = loaded
        return loaded_config_files

    def __load_configuration(self, salt: str, load_core_default_config: bool) -> dict[Path, bool]:
        """
        Load all relevant configuration files for the session.

        This method orchestrates the loading of multiple configuration files
        in a specific order:
        1. Lynceus default configuration (if requested)
        2. Salt-specific default configuration
        3. Salt-specific configuration file
        4. Additional Salt-specific and flavor-specific configuration files

        Parameters
        ----------
        salt : str
            Session identifier used to determine configuration file names
        load_core_default_config : bool
            Whether to load the Lynceus default config

        Returns
        -------
        dict[Path, bool]
            Mapping of all configuration file paths to their loading status

        Notes
        -----
        Configuration files are loaded in order of precedence, with later files
        potentially overriding settings from earlier ones.
        """
        # Defines the potential configuration file to load.
        config_file_meta_list = []
        if load_core_default_config:
            # Adds the Lynceus default configuration file as requested.
            config_file_meta_list.append({'config_path': f'misc/{self.DEFAULT_SALT}.default.conf', 'root_path': Path(__file__).parent})

        # Adds default configuration file corresponding to specified salt, if not the default one.
        if salt != self.DEFAULT_SALT:
            config_file_meta_list.append({'config_path': f'misc/{salt}.default.conf'})

        # Adds user configuration file corresponding to specified salt.
        config_file_meta_list.append({'config_path': f'{salt}.conf'})

        # Looks up for configuration file(s), starting with a "default" one, and then optional user one.
        loaded_config_files: dict[Path, bool] = self.__do_load_configuration_files(config_file_meta_list)

        # Loads additional configuration files based on the optional conf_flavor_list setting, which can be specified in any of the configuration files that have just been loaded.
        conf_flavor_list: list[str] = self.get_config(CONFIG_GENERAL_KEY, 'conf_flavor_list', default=[])
        if conf_flavor_list:
            extra_config_file_meta_list = [{'config_path': f'{salt}_{flavor}.conf'} for flavor in conf_flavor_list]
            loaded_config_files |= self.__do_load_configuration_files(extra_config_file_meta_list)

        # Returns configuration file loading mapping, for information.
        return loaded_config_files

    def has_config_section(self, section: str) -> bool:
        """
        Check if a configuration section exists.

        Parameters
        ----------
        section : str
            Name of the configuration section to check

        Returns
        -------
        bool
            True if the section exists, False otherwise
        """
        return self.__config.has_section(section)

    def get_config(self, section: str, key: str, *, default: str | int | float | object | list | Path = LynceusConfig.UNDEFINED_VALUE) -> str | int | float | object | list | Path:
        """
        Retrieve a configuration value from the specified section and key.

        Parameters
        ----------
        section : str
            Configuration section name
        key : str
            Configuration key within the section
        default : str or int or float or object or list, optional
            Default value to return if the config doesn't exist.

        Returns
        -------
        str or int or float or object or list or Path
            The configuration value or default.

        Raises
        ------
        LynceusConfigError
            If the key is not found and no default is provided
        """
        return self.__config.get_config(section, key, default=default)

    def is_bool_config_enabled(self, section: str, key: str) -> bool:
        """
        Check if a boolean configuration option is enabled.

        Parameters
        ----------
        section : str
            Configuration section name
        key : str
            Configuration key within the section

        Returns
        -------
        bool
            True if the configuration value evaluates to True, False otherwise
        """
        return self.__config.is_bool_config_enabled(section=section, key=key)

    def get_config_section(self, section: str):
        """
        Retrieve an entire configuration section.

        Parameters
        ----------
        section : str
            Name of the configuration section to retrieve

        Returns
        -------
        dict
            Configuration section object containing all key-value pairs

        Raises
        ------
        KeyError
            If the section does not exist
        """
        return self.__config[section]

    def get_lynceus_config_copy(self) -> LynceusConfig:
        """
        Create a deep copy of the session's internal configuration.

        This method returns a complete copy of the current configuration state,
        including all loaded configuration files and merged settings. The copy
        is independent of the original and can be safely modified without
        affecting the session's configuration.

        Returns
        -------
        LynceusConfig
            Deep copy of the internal configuration with all
            loaded settings from default, user, and flavor-specific
            configuration files

        Notes
        -----
        - Useful for creating configuration templates or snapshots
        - The returned copy includes all merged configuration from multiple sources
        - Changes to the returned copy do not affect the session's configuration
        - Can be used to extract default configuration values for documentation
        """
        return self.__config.copy()

    def get_logger(self, name: str = None, *, parent_propagate: bool = True) -> Logger:
        """
        Get a logger instance with the session's root logger as prefix.

        Create or retrieve a logger with the full name constructed from
        the session's root logger name and the provided name.

        Parameters
        ----------
        name : str, optional
            Specific logger name (optional). If None, returns the root logger
        parent_propagate : bool, optional
            Whether the logger should propagate to its parent logger

        Returns
        -------
        Logger
            Configured logger instance
        """
        complete_name: str = f'{self.__root_logger_name}.{name}' if name else self.__root_logger_name
        logger: Logger = logging.getLogger(complete_name)
        if logger.parent:
            logger.parent.propagate = parent_propagate

        return logger
