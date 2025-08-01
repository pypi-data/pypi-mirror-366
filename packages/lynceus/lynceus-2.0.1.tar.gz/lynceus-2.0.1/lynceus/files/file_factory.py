import inspect
from pathlib import Path

from lynceus.core.config import (
    CONFIG_GENERAL_KEY,
    CONFIG_STORAGE_DYNAMIC_TYPE,
    CONFIG_STORAGE_IS_DYNAMIC,
    CONFIG_STORAGE_REMOTE_TYPE,
)
from lynceus.core.config.lynceus_config import LynceusConfig
from lynceus.core.exchange.lynceus_exchange import LynceusExchange
from lynceus.core.lynceus import LynceusSession
from lynceus.core.lynceus_client import LynceusClientClass
from lynceus.files.lynceus_file import (
    LynceusFile,
    _LocalLynceusFile,
    _RemoteS3LynceusFile,
)
from lynceus.files.remote.s3 import S3Utils
from lynceus.files.storage import StorageMetadataBase
from lynceus.lynceus_exceptions import LynceusConfigError, LynceusFileError
from lynceus.utils import lookup_root_path


# pylint: disable=too-many-instance-attributes
class LynceusFileFactory(LynceusClientClass):
    """
    LynceusFileFactory is useful to create instance of Local or Remote according to various configuration provided once
    for all in Factory constructor.

    By default, it is configured to read and write parquet files, but it can be configured to manage any kind of file.
    """

    REMOTE_STORAGE_TYPE_S3: str = "s3"
    REMOTE_STORAGE_TYPE_SUPPORTED_LIST: set[str] = {REMOTE_STORAGE_TYPE_S3}

    # pylint: disable=too-many-branches,too-many-statements
    def __init__(
            self,
            *,
            lynceus_session: LynceusSession,
            lynceus_exchange: LynceusExchange | None,
            lynceus_config: LynceusConfig = None,
            name: str | None = None,
            env: str | None = None,
            env_suffix: str | None = None,
            remote_config_section: str | None = None,
            remote_config_key: str | None = None,
            remote_mode_forced_by_cli: bool = True,
            remote_mode_automatic_activation: bool = False,
            source_path_format: str = "{target}/{env}/parquet",
            source_mode: bool = False,
            dest_path_format: str = "{dest_file_name}/{source_name}.parquet",
            dest_path_kwargs: dict[str, str] | None = None,
            remote_dynamic_type_class_map: dict[str, type[StorageMetadataBase]] | None = None,
            dynamic_storage_mandatory_param_map: dict[str, bool] | None = None,
    ):
        """
        Initialize Lynceus file Factory generating File allowing local or remote management.

        Factory is configured according to remote mode toggle (depending on specified argument
        and optional overriding configuration).

        Parameters
        ----------
        lynceus_session : LynceusSession
            Active Lynceus session
        lynceus_exchange : LynceusExchange, optional
            Exchange instance for communication
        lynceus_config : LynceusConfig, optional
            Configuration to use (if not specified, configuration of specified lynceus session is used)
        name : str, optional
            Name identifier for the factory
        env : str, optional
            Name of the environment which will be used as parent directory of parquet files (for write access)
        env_suffix : str, optional
            Suffix to append to environment name
        remote_config_section : str, optional
            Config section containing remote storage configuration
        remote_config_key : str, optional
            Config key, in General section, giving config section (needed only if remote_config_section is not defined)
        remote_mode_forced_by_cli : bool, default True
            (forced by CLI) True to read remotely, False to read locally
        remote_mode_automatic_activation : bool, default False
            Automatic activation requested
        source_path_format : str, default "{target}/{env}/parquet"
            The format used to generate source path
        source_mode : bool, default False
            Whether this factory is used in source mode
        dest_path_format : str, default "{dest_file_name}/{source_name}.parquet"
            The format used to generate destination path
        dest_path_kwargs : dict, optional
            The parameters used to generate destination path
        remote_dynamic_type_class_map : dict, optional
            Mapping of dynamic type names to StorageMetadataBase classes
        dynamic_storage_mandatory_param_map : dict, optional
            Mapping of parameter names to mandatory flags for dynamic storage

        Notes
        -----
        remote_mode explanation:
         - by default destination files are read and write locally,
         - if Host is our Data Factory,
            or if NB_USER environment variable is defined to jovyan, indicating system is launched with Docker image,
            remote_mode automatic activation is requested
         - but the **override_to_local_mode** configuration (in configuration file), allow ignoring automatic activation request
         - in any case, the remote_mode_forced_by_cli toggle (e.g. set by a --remote-mode CLI option) can be used to force remote mode
            (it will be False here, BUT 100% of request will use the override_remote_mode method parameter).
         => this system could be lightened, but it is risky to do that while keeping backward compatibility.
        """
        super().__init__(
            logger_name="file",
            lynceus_session=lynceus_session,
            lynceus_exchange=lynceus_exchange,
        )

        # Safe-guard:
        if not source_path_format:
            raise LynceusFileError("Source path format must be defined!")

        self.__env: str = env
        self.__name: str = name or remote_config_section
        self.__remote_mode: bool = remote_mode_forced_by_cli
        self.__remote_mode_automatic_activation: bool = remote_mode_automatic_activation
        self.__local_mode_forced_by_config: bool = False
        self.__source_path_format: str = source_path_format
        self.__source_mode = source_mode
        self.__dest_path_format: str = dest_path_format
        self.__dest_path_kwargs: dict[str, str] = dest_path_kwargs or {}
        self.__previous_dest_path_kwargs = {}
        self.__remote_dynamic_type_class_map = remote_dynamic_type_class_map or {}
        self.__dynamic_storage_mandatory_param_map = dynamic_storage_mandatory_param_map or {}

        if not lynceus_config:
            lynceus_config = self._lynceus_session.get_lynceus_config_copy()

        # Loads remote configuration, and define some variable accordingly.
        self.__dynamic_container_name_params: dict[str, str] = {}
        if not remote_config_section and not remote_config_key:
            self._logger.warning(
                "No remote configuration given at all, this file factory will only be able to create Local file."
            )
            self.__remote_config = None
            self.__with_dynamic_container_name: bool = False
        else:
            if not remote_config_section:
                remote_config_section = lynceus_config.get_config(CONFIG_GENERAL_KEY, remote_config_key)
            self.__remote_config = lynceus_config[remote_config_section]
            if not self.__remote_config:
                raise ValueError(
                    f'There is no "{remote_config_section}" configuration in configuration file (are you sure you load the storage definition file ?).'
                )

            self._logger.debug(
                f'According to "{remote_config_section}" configuration section, LynceusFileFactory will'
                + f' consider remote configuration named "{remote_config_section}": "{LynceusConfig.format_config(self.__remote_config)}".'
            )

            if self.__remote_config.get(CONFIG_STORAGE_REMOTE_TYPE) not in LynceusFileFactory.REMOTE_STORAGE_TYPE_SUPPORTED_LIST:
                raise NotImplementedError(
                    f'Configured "{CONFIG_STORAGE_REMOTE_TYPE}={self.__remote_config.get(CONFIG_STORAGE_REMOTE_TYPE)}" is not supported.'
                    + f" Supported values: {LynceusFileFactory.REMOTE_STORAGE_TYPE_SUPPORTED_LIST}"
                )

            # Retrieves optional is_dynamic configuration option.
            self.__with_dynamic_container_name: bool = LynceusConfig.to_bool(self.__remote_config.get(CONFIG_STORAGE_IS_DYNAMIC))
            self.__with_dynamic_container_type: str = self.__remote_config.get(CONFIG_STORAGE_DYNAMIC_TYPE)

            remote_dynamic_type_supported_list: set[str] = set(self.__remote_dynamic_type_class_map.keys()) | {None}
            if self.__with_dynamic_container_type not in remote_dynamic_type_supported_list:
                raise NotImplementedError(
                    f'Configured "{CONFIG_STORAGE_DYNAMIC_TYPE}={self.__with_dynamic_container_type}" is not supported.'
                    + f" Supported values: {remote_dynamic_type_supported_list}"
                )

            # Initializes some utilities.
            self.__s3utils = S3Utils(
                lynceus_session=lynceus_session,
                lynceus_exchange=lynceus_exchange,
                lynceus_s3_config=self.__remote_config,
            )
            self.__s3utils.initialize()

            # Checks if local mode (against remote mode) is forced in configuration file.
            if "override_to_local_mode" in self.__remote_config:
                if LynceusConfig.to_bool(self.__remote_config["override_to_local_mode"]):
                    self.__local_mode_forced_by_config = True
                    # It is the case so defined the remote mode as False.
                    self.__remote_mode = False
                    # pylint: disable=logging-not-lazy
                    self._logger.info(
                        f'According to "override_to_local_mode" configuration in "{remote_config_section}"'
                        + ' remote mode is overridden to "local" (it can only be overridden by CLI option).'
                    )
            else:
                # In any case, set the remote mode as the value of CLI **or** auto activation.
                self.__remote_mode |= remote_mode_automatic_activation
                self._logger.info(
                    f'remote mode="{self.__remote_mode}" (forced by CLI option="{remote_mode_forced_by_cli}";'
                    + f' automatic activation according to environment="{self.__remote_mode_automatic_activation}").'
                )

            if "override_environment" in self.__remote_config:
                self.__env = self.__remote_config["override_environment"]
                self.__env = self.__define_complete_env(self.__env, env_suffix)
                self._logger.info(
                    f'According to "override_environment" configuration in "{remote_config_section}"'
                    + f' Environnment is overriden to "{self.__env}".'
                )

            # Defines remote root path, once for all.
            self.__remote_root_path: Path | None = None
            if not self.__with_dynamic_container_name:
                self.__remote_root_path = self.__define_remote_root_path(self.__env)

        # Defines default environment if needed.
        if self.__env is None:
            self.__env = self.__define_complete_env("dev", env_suffix)
            self._logger.info(
                f'No environment defined in CLI or configuration, defined it to "{self.__env}".'
            )

        # Defines local root path, once for all.
        self.__local_root_path: Path = self.__define_local_root_path(self.__env)

        # Defines string presentation of this LynceusFile Factory.
        self.__string_presentation = LynceusConfig.format_dict_to_string(
            LynceusConfig.format_config(
                self.get_context_info()
                | {
                    "env": self.__env,
                    "source_path_format": self.__source_path_format,
                    "source_mode": self.__source_mode,
                    "dest_path_format": self.__dest_path_format,
                    "storage": self.__remote_config or "Local only",
                    "dynamic": self.__dynamic_container_name_params,
                }
            ),
            indentation_level=2,
        )

    @property
    def name(self):
        """
        Get the name of this file factory.

        Returns
        -------
        str
            The factory name
        """
        return self.__name

    @property
    def is_dynamic_remote(self):
        """
        Check if this factory uses dynamic remote container naming.

        Returns
        -------
        bool
            True if using dynamic container names, False otherwise
        """
        return self.__with_dynamic_container_name

    def __define_complete_env(self, env: str, env_suffix: str):
        """
        Build the complete environment name including optional suffix.

        For source mode, suffix is ignored. For target mode, suffix is appended
        to create a hierarchical environment structure.

        Parameters
        ----------
        env : str
            Base environment name
        env_suffix : str
            Optional suffix to append (ignored in source mode)

        Returns
        -------
        str
            Complete environment name
        """
        # Checks if this factory is used as a source.
        if self.__source_mode:
            # It is the case, so suffix is NOT used here.
            return env

        # It is used as a target, so environment suffix must be taken care.
        return env if not env_suffix else f"{env}/{env_suffix}"

    def force_cache_refresh(self):
        """
        Force refresh of the remote storage cache.

        Invalidate any cached information about remote files to ensure
        fresh data is retrieved on next access.
        """
        if self.__remote_config:
            self.__s3utils.force_cache_refresh()

    def get_env(self) -> str:
        """
        Get the current environment name.

        Returns
        -------
        str
            The environment name used by this factory
        """
        return self.__env

    def __build_relative_path_dir(self, target: str, env: str | None):
        """
        Build relative directory path using the configured format.

        Use the source path format template with provided parameters
        to generate the relative directory structure.

        Parameters
        ----------
        target : str
            Target identifier for the path
        env : str, optional
            Environment name (can be None)

        Returns
        -------
        str
            Formatted relative directory path
        """
        return self.__source_path_format.format(
            **self.__dest_path_kwargs, target=target, env=env
        )

    def __define_local_root_path(self, env: str | None) -> Path:
        """
        Define the local root path for file operations.

        Construct the local filesystem root path based on the project
        structure and environment configuration.

        Parameters
        ----------
        env : str, optional
            Environment name for path building

        Returns
        -------
        Path
            Local root path for file operations
        """
        root_path: Path = lookup_root_path(
            "lynceus/misc", root_path=Path(__file__).parent
        )
        return root_path / Path(self.__build_relative_path_dir("target", env))

    def update_dynamic_storage_params(self, params: dict[str, str | int]):
        """
        Update parameters for dynamic storage container naming.

        Update the parameters used to generate dynamic container names
        and validate that all mandatory parameters are provided.

        Parameters
        ----------
        params : dict
            Dictionary of parameter names to values

        Raises
        ------
        LynceusFileError
            If mandatory parameters are missing
        """
        self.__dynamic_container_name_params |= params.copy()
        mandatory_params: set[str] = {
            param
            for param, is_mandatory in self.__dynamic_storage_mandatory_param_map.items()
            if is_mandatory
        }

        # Ensures there are all the mandatory params.
        if mandatory_params - set(self.__dynamic_container_name_params.keys()):
            raise LynceusFileError(
                f"Specified dynamic storage params ({set(self.__dynamic_container_name_params.keys())}),"
                + f" should contain at least all the awaited ones ({mandatory_params})."
            )

    def __define_remote_container_name(self) -> str:
        """
        Define the remote storage container name.

        For static storage, return the configured bucket name.
        For dynamic storage, instantiate the appropriate metadata class
        and generate a unique storage name.

        Returns
        -------
        str
            Container name for remote storage

        Raises
        ------
        LynceusConfigError
            If dynamic container type is not found
        LynceusFileError
            If unable to create the storage metadata instance
        """
        # Checks if it is a static or dynamic storage.
        if not self.__with_dynamic_container_name:
            return self.__remote_config["bucket_name"]

        # Safe-guard: Checks if it is a static or dynamic storage.
        if self.__with_dynamic_container_type not in self.__remote_dynamic_type_class_map:
            raise LynceusConfigError(
                f"Unable to find a dynamic container with type {self.__with_dynamic_container_type} in your configuration."
            )

        # Defines which StorageMetadata and params according to configuration.
        storage_metadata_class: type[StorageMetadataBase] = self.__remote_dynamic_type_class_map.get(self.__with_dynamic_container_type)
        awaited_params = set(inspect.getfullargspec(storage_metadata_class).args) - {"self"}

        # Creates the corresponding StorageMetadata, and requests the unique storage name building to be 100% sure
        #  it will be the exact same name used during creation, and during compute resources request.
        try:
            # Filters parameters to use to instantiate such StorageMetadata class.
            params = {
                key: value
                for key, value in self.__dynamic_container_name_params.items()
                if key in awaited_params
            }

            dynamic_storage: StorageMetadataBase = storage_metadata_class(**params)
            return dynamic_storage.build_unique_storage_name()
        except TypeError as exc:
            raise LynceusFileError(
                f'Unable to define the name of the dynamic remote container "{self}".',
                exc,
            ) from exc

    def __define_remote_root_path(self, env: str | None) -> Path:
        """
        Define the remote root path for file operations.

        Construct the S3 root path using the container name and environment.

        Parameters
        ----------
        env : str, optional
            Environment name for path building

        Returns
        -------
        Path
            Remote root path with S3 prefix
        """
        relative_path_dir: str = self.__build_relative_path_dir(
            self.__define_remote_container_name(), env
        )

        return Path(f"{LynceusFile.S3_PATH_BEGIN}{relative_path_dir}/")

    # pylint: disable=too-many-positional-arguments
    def new_file(
            self,
            source_name: str | None,
            source_file_name: Path | str,
            must_exist: bool = True,
            override_env: str = None,
            override_remote_mode: bool = None,
            create_sub_directories: bool = True,
            dest_path_format: str = None,
            override_dest_path_kwargs: dict = None,
            specific_dest_file_name: str = None,
    ) -> LynceusFile:
        """
        Create a new LynceusFile instance with the specified parameters.

        Build file paths using the configured format and create appropriate
        local or remote file instances based on the mode settings.

        Parameters
        ----------
        source_name : str, optional
            Name of the source (used in path formatting)
        source_file_name : str or Path
            Base filename or path
        must_exist : bool, default True
            Whether the file must exist (raises error if not)
        override_env : str, optional
            Environment override for this file
        override_remote_mode : bool, optional
            Override the default remote mode setting
        create_sub_directories : bool, default True
            Whether to create parent directories
        dest_path_format : str, optional
            Custom path format (overrides default)
        override_dest_path_kwargs : dict, optional
            Custom path formatting parameters
        specific_dest_file_name : str, optional
            Override the destination filename

        Returns
        -------
        LynceusFile
            Configured file instance (local or remote)

        Raises
        ------
        KeyError
            If path formatting fails due to missing parameters
        """
        # Safe-guard: ensures source_file_name is defined to minimum.
        source_file_name: str = str(source_file_name) or "/"

        # Defines destination file name, which is the same as the source file name by default.
        dest_file_name = (
            specific_dest_file_name if specific_dest_file_name else source_file_name
        )

        # Manages path kwargs overriding if needed.
        path_kwargs = (
            override_dest_path_kwargs
            if override_dest_path_kwargs
            else self.__dest_path_kwargs
        )

        # Special Hack (mainly needed for CustomerInfo auto merge system), using previous path kwargs if none is defined here.
        if not path_kwargs:
            path_kwargs = self.__previous_dest_path_kwargs
        else:
            # Registers path_kwargs for next potential iteration.
            self.__previous_dest_path_kwargs = path_kwargs

        # Formats the new file path.
        if not dest_path_format:
            dest_path_format = self.__dest_path_format

        try:
            new_file_path: str = dest_path_format.format(
                **path_kwargs, source_name=source_name, dest_file_name=dest_file_name
            )
        except KeyError:
            # Gives as much information as possible.
            self._logger.error(
                f'Unable to build the file path from format "{dest_path_format}" and arguments: "{source_name}", "{dest_file_name}", "{path_kwargs=}"'
            )
            # Stops on error anyway.
            raise

        return self._do_new_file(
            new_file_path,
            must_exist,
            override_env,
            override_remote_mode,
            create_sub_directories=create_sub_directories,
        )

    # pylint: disable=too-many-positional-arguments
    def new_env_directory(
            self,
            must_exist: bool = True,
            override_env: str = None,
            override_remote_mode: bool = None,
    ) -> LynceusFile:
        """
        Create a LynceusFile instance representing an environment directory.

        Create a file instance pointing to the environment root directory
        without creating subdirectories.

        Parameters
        ----------
        must_exist : bool, default True
            Whether the directory must exist
        override_env : str, optional
            Environment override
        override_remote_mode : bool, optional
            Override the default remote mode setting

        Returns
        -------
        LynceusFile
            File instance representing the environment directory
        """
        return self._do_new_file(
            "",
            must_exist,
            override_env,
            override_remote_mode,
            create_sub_directories=False,
        )

    def _do_new_file(
            self,
            path: str,
            must_exist: bool = True,
            override_env: str | None = None,
            override_remote_mode: bool = None,
            create_sub_directories: bool = True,
    ) -> LynceusFile:
        """
        Internal method to create a new file instance.

        Handle the core logic for creating local or remote file instances,
        including path resolution, globbing for remote files, and cache management.

        Parameters
        ----------
        path : str
            Relative path within the environment
        must_exist : bool, default True
            Whether the file must exist
        override_env : str, optional
            Environment override
        override_remote_mode : bool, optional
            Override the default remote mode setting
        create_sub_directories : bool, default True
            Whether to create parent directories

        Returns
        -------
        LynceusFile
            Configured file instance
        """
        if self.__remote_mode or override_remote_mode:
            root_path: Path = (
                self.__remote_root_path
                if override_env is None and not self.__with_dynamic_container_name
                else self.__define_remote_root_path(override_env)
            )

            complete_path: Path = root_path

            # Important: concatenates path only if it exists and not '/'.
            if path and path != "/":
                complete_path /= Path(path)

            # Manages optional globbing if needed.
            if "*" in path:
                matching_files = self.__s3utils.list_remote_files(
                    remote_root_path=_RemoteS3LynceusFile.get_raw_path_from_remote_path(root_path),
                    recursive=True,
                    pattern=path,
                    detail=True,
                )
                if not matching_files:
                    self._logger.warning(
                        f'Unable to find any remote files while globbing with "{complete_path}". It will certainly lead to not found file.'
                    )
                else:
                    # Sorts by last modification date.
                    sorted_matching_files = sorted(
                        matching_files.items(),
                        key=lambda kv: kv[1]["LastModified"],
                        reverse=True,
                    )
                    selected_file_path = sorted_matching_files[0][0]

                    complete_path = root_path / Path(selected_file_path)
        else:
            root_path: Path = (
                self.__local_root_path
                if override_env is None and not self.__with_dynamic_container_name
                else self.__define_local_root_path(override_env)
            )

            complete_path: Path = root_path / Path(path)
            # TODO: implement globbing on local path, something like root_path.glob(pattern)

        return self.create_from_full_path(
            complete_path,
            must_exist=must_exist,
            override_remote_mode=override_remote_mode,
            create_sub_directories=create_sub_directories,
        )

    def create_from_full_path(
            self,
            complete_path: Path,
            must_exist: bool = True,
            override_remote_mode: bool = None,
            create_sub_directories: bool = True,
    ) -> LynceusFile:
        """
        Create a LynceusFile instance from a complete file path.

        Create the appropriate local or remote file instance based on the path
        and factory configuration. Handle cache refresh for remote files.

        Parameters
        ----------
        complete_path : Path
            Complete file path (local or remote)
        must_exist : bool, default True
            Whether the file must exist (raises error if not)
        override_remote_mode : bool, optional
            Override the default remote mode setting
        create_sub_directories : bool, default True
            Whether to create parent directories for local files

        Returns
        -------
        LynceusFile
            File instance (local or remote)

        Raises
        ------
        LynceusFileError
            If file doesn't exist and must_exist is True
        """
        complete_path = Path(complete_path)
        if self.__remote_mode or override_remote_mode:
            new_lynceus_file: LynceusFile = _RemoteS3LynceusFile(
                complete_path,
                self._logger,
                self.__s3utils.get_s3filesystem(),
                self.__s3utils,
            )

            # Forces cache refresh if corresponding file existence if False atm.
            # it can happen if the file has been created (from elsewhere) after creation of this Factory.
            if must_exist and not new_lynceus_file.exists(reason="check if S3fs cache must be refreshed"):
                self.__s3utils.force_cache_refresh(path=_RemoteS3LynceusFile.get_raw_path_from_remote_path(complete_path.parent))
        else:
            # Creates subdirectories if needed.
            if create_sub_directories:
                complete_path.parent.mkdir(parents=True, exist_ok=True)

            new_lynceus_file: LynceusFile = _LocalLynceusFile(
                complete_path, self._logger
            )

        # Safe-guard: ensures corresponding file exists.
        if must_exist and not new_lynceus_file.exists():
            raise LynceusFileError(
                f'Requested file "{new_lynceus_file}" does not exist.'
            )

        return new_lynceus_file

    def get_parent_file(
            self,
            lynceus_file: LynceusFile,
            must_exist: bool = True,
            override_remote_mode: bool = None,
            create_sub_directories: bool = True,
    ) -> LynceusFile:
        """
        Get a LynceusFile instance for the parent directory of the given file.

        Create a file instance representing the parent directory using
        the same factory configuration.

        Parameters
        ----------
        lynceus_file : LynceusFile
            File whose parent directory is needed
        must_exist : bool, default True
            Whether the parent directory must exist
        override_remote_mode : bool, optional
            Override the default remote mode setting
        create_sub_directories : bool, default True
            Whether to create parent directories

        Returns
        -------
        LynceusFile
            File instance for the parent directory
        """
        return self.create_from_full_path(
            lynceus_file.get_parent_path(),
            must_exist=must_exist,
            override_remote_mode=override_remote_mode,
            create_sub_directories=create_sub_directories,
        )

    def get_context_info(self):
        """
        Get context information about the factory's mode settings.

        Return diagnostic information about how the factory was configured
        regarding local vs remote mode settings.

        Returns
        -------
        dict
            Context information with mode settings and their sources
        """
        return {
            "remote_mode (from CLI)": self.__remote_mode,
            "remote_mode (automatic)": self.__remote_mode_automatic_activation,
            "local_mode (from Config)": self.__local_mode_forced_by_config,
        }

    def __str__(self):
        """
        Get string representation of the file factory.

        Return formatted configuration information for debugging and logging.

        Returns
        -------
        str
            Detailed factory configuration information
        """
        return self.__string_presentation
