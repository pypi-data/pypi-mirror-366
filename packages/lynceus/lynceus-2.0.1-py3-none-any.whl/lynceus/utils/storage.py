from logging import Logger
from pathlib import Path

from lynceus.core.config import (
    CONFIG_PROJECT_KEY,
    CONFIG_PROJECT_ROOT_PATH_HOLDER,
    CONFIG_STORAGE_LOCAL,
)
from lynceus.core.config.lynceus_config import LynceusConfig
from lynceus.core.exchange.lynceus_exchange import LynceusExchange
from lynceus.core.lynceus import LynceusSession
from lynceus.files.file_factory import LynceusFileFactory
from lynceus.files.lynceus_file import LynceusFile
from lynceus.files.storage import StorageMetadataBase
from lynceus.lynceus_exceptions import LynceusConfigError, LynceusFileError
from lynceus.utils import lookup_root_path


def create_storage_file_factory(
        *,
        name: str,
        lynceus_session: LynceusSession,
        lynceus_config: LynceusConfig,
        logger: Logger,
        log_prefix: str,
        remote_config_section: str | None,
        remote_mode_forced_by_cli: bool = True,
        source_path_format: str = "{target}",
        dest_path_format: str = "{dest_file_name}",
        lynceus_exchange: LynceusExchange | None = None,
        remote_dynamic_type_class_map: dict[str, type[StorageMetadataBase]] | None = None,
        dynamic_storage_mandatory_param_map: dict[str, bool] | None = None,
) -> LynceusFileFactory | None:
    """
    Create a storage file factory for managing file operations.

    Create and configure a LynceusFileFactory instance for handling file storage
    operations across different storage backends (local, remote, dynamic remote).
    Validate configuration and return None if the specified configuration section
    doesn't exist.

    Parameters
    ----------
    name : str
        Name identifier for the storage factory.
    lynceus_session : LynceusSession
        The Lynceus session instance.
    lynceus_config : LynceusConfig
        Configuration object containing storage settings.
    logger : Logger
        Logger instance for logging operations.
    log_prefix : str
        Prefix string for log messages.
    remote_config_section : str | None
        Configuration section name for remote storage.
    remote_mode_forced_by_cli : bool, optional
        Whether remote mode is forced by CLI. Defaults to True.
    source_path_format : str, optional
        Format string for source paths. Defaults to '{target}'.
    dest_path_format : str, optional
        Format string for destination paths. Defaults to '{dest_file_name}'.
    lynceus_exchange : LynceusExchange | None, optional
        Exchange instance for remote operations. Defaults to None.
    remote_dynamic_type_class_map : dict[str, type[StorageMetadataBase]] | None, optional
        Mapping of storage types to metadata classes for dynamic remote storage. Defaults to None.
    dynamic_storage_mandatory_param_map : dict[str, bool] | None, optional
        Mapping of parameter names to their mandatory status for dynamic storage. Defaults to None.

    Returns
    -------
    LynceusFileFactory | None
        A configured file factory instance, or None if
        the remote config section doesn't exist.

    Warns
    -----
    Logs a warning if the specified remote_config_section doesn't exist in the configuration.
    """
    # Safe-guard: ensure specified config_section exists in Lynceus configuration.
    if remote_config_section and not lynceus_config.has_section(remote_config_section):
        logger.warning(
            f'{log_prefix} unable to register storage "{name}", because configuration section "{remote_config_section}" does not exist. Fix your configuration.'
        )
        return None

    # Creates a new Lynceus file factory corresponding to needs.
    return LynceusFileFactory(
        name=name,
        lynceus_session=lynceus_session,
        lynceus_config=lynceus_config,
        remote_config_section=remote_config_section,
        remote_mode_forced_by_cli=remote_mode_forced_by_cli,
        source_path_format=source_path_format,
        dest_path_format=dest_path_format,
        lynceus_exchange=lynceus_exchange,
        remote_dynamic_type_class_map=remote_dynamic_type_class_map,
        dynamic_storage_mandatory_param_map=dynamic_storage_mandatory_param_map,
    )


def extract_dynamic_remote_storage_params(
        lynceus_config: LynceusConfig,
        *,
        dynamic_storage_mandatory_param_map: dict[str, bool] | None = None,
) -> dict[str, str | int]:
    """
    Extract and validate parameters for dynamic remote storage from configuration.

    Retrieve configuration parameters required for dynamic remote storage operations,
    validate mandatory parameters, and handle type conversion for numeric values.

    Parameters
    ----------
    lynceus_config : LynceusConfig
        Configuration object to extract parameters from.
    dynamic_storage_mandatory_param_map : dict[str, bool] | None, optional
        Mapping of parameter names to their mandatory status. If a parameter is
        marked as mandatory (True) and missing, raises an exception. Defaults to None.

    Returns
    -------
    dict[str, str | int]
        Dictionary of extracted parameters with string or integer values.

    Raises
    ------
    LynceusConfigError
        If the project configuration section is missing or if a
        mandatory parameter is not found in the configuration.

    Notes
    -----
    Automatically converts numeric string values to integers for compatibility
    with different input sources (config files vs API/CLI/Tests).
    """
    if not lynceus_config.has_section(CONFIG_PROJECT_KEY):
        raise LynceusConfigError(
            f"Unable to find [{CONFIG_PROJECT_KEY}] configuration section in specified configuration file."
        )

    # [Flexible] Saves all project configuration as potential dynamic remote storage params.
    dynamic_remote_storage_params = {
        param: value for param, value in lynceus_config[CONFIG_PROJECT_KEY].items()
        if isinstance(value, (str | int | float))}

    # [Strict] Ensures all mandatory dynamic remote storage params are defined.
    for param, is_mandatory in (dynamic_storage_mandatory_param_map or {}).items():
        value = lynceus_config.get_config(CONFIG_PROJECT_KEY, param, default=None)
        if value is None:
            if is_mandatory:
                raise LynceusConfigError(
                    f'Unable to find "{param}" option (mandatory for dynamic remote storage) inside'
                    + f" [{CONFIG_PROJECT_KEY}] configuration section in specified configuration file."
                )
            continue

        # Checks the type of value, can be either:
        #  - string if coming from a static configuration file
        #  - int if coming from API, CLI or Tests
        if isinstance(value, str):
            value = value if not value.isnumeric() else int(value)

        dynamic_remote_storage_params[param] = value

    return dynamic_remote_storage_params


def get_lynceus_file_from_metadata(
        *,
        file_metadata: str,
        lynceus_config: LynceusConfig,
        logger: Logger,
        log_prefix: str,
        storage_file_factory_map: dict[str, LynceusFileFactory],
        locally_retrieved_repository_root_path: Path | None,
        must_exist: bool,
        overriden_root_path_if_local: Path = None,
        dynamic_storage_mandatory_param_map: dict[str, bool] | None = None,
) -> LynceusFile:
    """
    Create a LynceusFile instance from file metadata string.

    Parse file metadata to extract storage name and file path, then create
    an appropriate LynceusFile instance using the corresponding storage factory.
    Handle different storage types including local, remote, and dynamic remote storage.

    Parameters
    ----------
    file_metadata : str
        Metadata string in format 'storage_name:file_path'.
    lynceus_config : LynceusConfig
        Configuration object for storage settings.
    logger : Logger
        Logger instance for logging operations.
    log_prefix : str
        Prefix string for log messages.
    storage_file_factory_map : dict[str, LynceusFileFactory]
        Mapping of storage names to their corresponding file factory instances.
    locally_retrieved_repository_root_path : Path | None
        Root path of locally retrieved repository, required for local file operations.
    must_exist : bool
        Whether the file must exist when creating the LynceusFile instance.
    overriden_root_path_if_local : Path, optional
        Override root path for local files. Defaults to None.
    dynamic_storage_mandatory_param_map : dict[str, bool] | None, optional
        Mapping of parameter names to mandatory status for dynamic storage. Defaults to None.

    Returns
    -------
    LynceusFile
        A configured LynceusFile instance ready for file operations.

    Raises
    ------
    LynceusConfigError
        If the specified storage is not configured in the factory map.
    LynceusFileError
        If there's an error preparing dynamic remote storage.
    ValueError
        If repository root path is required but not provided for local files.

    Notes
    -----
    For local files, automatically handles path resolution including special
    placeholders and relative path conversion to absolute paths.
    """
    # Extracts storage name and file path from metadata.
    storage_name, file_path = LynceusFile.extract_storage_and_path(file_metadata)
    dest_path_format: str | None = None
    override_dest_path_kwargs: dict[str, str] | None = None

    storage_file_factory: LynceusFileFactory = storage_file_factory_map.get(
        storage_name
    )
    if not storage_file_factory:
        raise LynceusConfigError(
            f'{log_prefix} file option ("{file_metadata}"), is hosted on remote storage "{storage_name}"'
            + ", which is not configured!"
            + f" Available/configured remote storages: {storage_file_factory_map}."
        )

    # Manages dynamic remote storage if needed.
    if storage_file_factory.is_dynamic_remote:
        # TODO: limitation is that ALL remote file coming from a dynamic remote, share the same parameters linked to the parent project.
        # Thus: atm it is NOT possible to have a reference file on a dynamic remote and the solution file on another dynamic remote, for the same project.
        try:
            dynamic_remote_storage_params: dict[str, str | int] = (
                extract_dynamic_remote_storage_params(
                    lynceus_config,
                    dynamic_storage_mandatory_param_map=dynamic_storage_mandatory_param_map,
                )
            )
            storage_file_factory.update_dynamic_storage_params(
                dynamic_remote_storage_params
            )

            # Checks if the path must be formatted.
            if "{" in file_path:
                dest_path_format = str(file_path)
                override_dest_path_kwargs = dynamic_remote_storage_params

        except LynceusConfigError as exc:
            # pylint: disable=raise-missing-from
            raise LynceusFileError(
                f'Unable to prepare system to use dynamic remote storage "{storage_name}"',
                exc,
            )

    # Manages Local file if needed:
    if storage_name == CONFIG_STORAGE_LOCAL:
        if overriden_root_path_if_local:
            file_path: str = str(
                lookup_root_path(
                    file_path,
                    remaining_iteration=4,
                    root_path=overriden_root_path_if_local,
                )
                / Path(file_path)
            )
        else:
            #  - adds special CONFIG_PROJECT_ROOT_PATH_HOLDER keyword at beginning if relative path
            if CONFIG_PROJECT_ROOT_PATH_HOLDER not in file_path and not file_path.startswith("/"):
                file_path: str = CONFIG_PROJECT_ROOT_PATH_HOLDER + file_path

        #  - replaces CONFIG_PROJECT_ROOT_PATH_HOLDER keyword by retrieved repository root path
        if CONFIG_PROJECT_ROOT_PATH_HOLDER in file_path:
            if not locally_retrieved_repository_root_path:
                raise ValueError(
                    "Repository should have been locally retrieved for this request."
                )

            root_dir: str = str(locally_retrieved_repository_root_path)
            file_path: str = file_path.replace(
                CONFIG_PROJECT_ROOT_PATH_HOLDER, root_dir + "/"
            )

    # Creates a LynceusFile instance.
    logger.debug(
        f"{log_prefix} creating LynceusFile ({file_path=}; {dest_path_format=}; {override_dest_path_kwargs=}) ..."
    )
    lynceus_file: LynceusFile = storage_file_factory.new_file(
        source_name=None,
        source_file_name=file_path,
        dest_path_format=dest_path_format,
        override_dest_path_kwargs=override_dest_path_kwargs,
        create_sub_directories=False,
        must_exist=must_exist,
    )

    return lynceus_file


def retrieve_remote_file_locally(
        *,
        lynceus_file: LynceusFile,
        logger: Logger,
        log_prefix: str,
        dest_dir_path: Path,
        extension_if_none: str | None = None,
) -> Path | None:
    """
    Download a remote file to local filesystem for processing.

    Downloads remote files to a local directory to enable operations that require
    local file access (e.g., scoring engines, third-party tools). If the file is
    already local, returns its existing path.

    Parameters
    ----------
    lynceus_file : LynceusFile
        The file object to download. If None, returns None.
    logger : Logger
        Logger instance for logging operations.
    log_prefix : str
        Prefix string for log messages.
    dest_dir_path : Path
        Local directory path where the file should be downloaded.
    extension_if_none : str | None, optional
        File extension to add if the file
        has no extension. Should include the dot (e.g., '.txt'). Defaults to None.

    Returns
    -------
    Path | None
        Path to the local file (existing or downloaded), or None if
        lynceus_file is None.

    Notes
    -----
    This method is particularly useful when:
    - Scoring engines cannot work with remote files
    - Third-party tool configuration files are stored remotely
    - Local file access is required for processing

    Examples
    --------
    >>> local_path = retrieve_remote_file_locally(
    ...     lynceus_file=remote_config_file,
    ...     logger=logger,
    ...     log_prefix='[Config]',
    ...     dest_dir_path=Path('/tmp/config'),
    ...     extension_if_none='.json'
    ... )
    """
    # This method is useful in several situations, for instance:
    #  - scoring engine is unable to work with remote file ... retrieve the remote file locally first
    #  - third-party tool configuration file can be overriden and put on remote storage, so we retrieve them locally first
    if lynceus_file is None:
        return None

    if lynceus_file.is_local():
        return lynceus_file.path

    local_file_name: str = lynceus_file.get_name()
    local_path: Path = dest_dir_path / Path(local_file_name)
    if not lynceus_file.get_extension() and extension_if_none:
        local_path = local_path.with_suffix(
            extension_if_none
            if extension_if_none.startswith(".")
            else f".{extension_if_none}"
        )

    lynceus_file.download_to(local_path)
    logger.debug(f"{log_prefix} saved {lynceus_file=} to {local_path=} to ease usage.")
    return local_path
