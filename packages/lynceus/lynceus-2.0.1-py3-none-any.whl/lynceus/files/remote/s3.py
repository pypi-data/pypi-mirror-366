from logging import Logger
from pathlib import Path

import s3fs

from lynceus.core.config import CONFIG_STORAGE_DYNAMIC_TYPE, CONFIG_STORAGE_IS_DYNAMIC, CONFIG_STORAGE_REMOTE_TYPE, LYNCEUS_S3_CONFIG_KEY
from lynceus.core.config.lynceus_config import LynceusConfig
from lynceus.core.exchange.lynceus_exchange import LynceusExchange
from lynceus.core.lynceus import LynceusSession
from lynceus.core.lynceus_client import LynceusClientClass
from lynceus.lynceus_exceptions import LynceusFileError


class S3Utils(LynceusClientClass):
    """
    Utility class for S3 filesystem operations and management.

    Provide S3-specific functionality including filesystem initialization,
    cache management, and file listing operations with glob support.
    """

    def __init__(self, *, lynceus_session: LynceusSession, lynceus_exchange: LynceusExchange | None, lynceus_s3_config: dict[str, str]):
        """
        Initialize S3 utilities with configuration.

        Parameters
        ----------
        lynceus_session : LynceusSession
            Active Lynceus session
        lynceus_exchange : LynceusExchange, optional
            Exchange instance for communication (optional)
        lynceus_s3_config : dict
            S3 configuration dictionary with connection details
        """
        super().__init__(lynceus_session=lynceus_session, logger_name='s3', lynceus_exchange=lynceus_exchange)
        self.__lynceus_s3_config = lynceus_s3_config
        self.__s3filesystem = None

    def initialize(self):
        """
        Initialize the S3 filesystem with the patched implementation.

        Replace the default s3fs.S3FileSystem with the Lynceus-patched version
        that includes additional configuration handling.
        """
        self._logger.info('Initializing s3fs according to configuration.')
        s3fs.S3FileSystem = S3FileSystemPatched

    def get_s3filesystem(self):
        """
        Get or create the S3 filesystem instance.

        Lazy initialization of the S3 filesystem with Lynceus configuration.
        The filesystem is cached for reuse across operations.

        Returns
        -------
        S3FileSystemPatched
            Configured S3 filesystem instance
        """
        if self.__s3filesystem is None:
            self.__s3filesystem = s3fs.S3FileSystem(**{LYNCEUS_S3_CONFIG_KEY: self.__lynceus_s3_config})

        return self.__s3filesystem

    def force_cache_refresh(self, path: Path | str | None = None):
        """
        Force refresh of the S3 filesystem cache.

        Invalidate cached file information to ensure fresh data is retrieved
        on subsequent operations. Can target a specific path or refresh all cache.

        Parameters
        ----------
        path : Path or str, optional
            Specific path to refresh (None for full cache refresh)
        """
        if self.__s3filesystem:
            self._logger.debug(f'Refreshing S3 fs cache ({path=}) ...')
            self.__s3filesystem.invalidate_cache(path=str(path) if path else None)

    def split_path(self, *, remote_file_path: str):
        """
        Split an S3 path into its components.

        Use the S3 filesystem's split_path method to decompose
        a full S3 path into bucket, key, and other components.

        Parameters
        ----------
        remote_file_path : str
            Full S3 path to split

        Returns
        -------
        tuple
            Path components (bucket, key, version)
        """
        return self.get_s3filesystem().split_path(remote_file_path)

    def list_remote_files(self, *,
                          remote_root_path: Path | str,
                          recursive: bool,
                          pattern: str | None = None,
                          maxdepth: int | None = None,
                          withdirs: bool | None = None,
                          detail: bool = False):
        """
        List files in a remote S3 directory with various filtering options.

        Provide flexible file listing with support for recursive traversal,
        pattern matching, depth control, and detailed metadata retrieval.

        Parameters
        ----------
        remote_root_path : Path or str
            Root path for the search
        recursive : bool
            Whether to search subdirectories recursively
        pattern : str, optional
            Optional glob pattern for file filtering
        maxdepth : int, optional
            Maximum directory depth for traversal
        withdirs : bool, optional
            Whether to include directories in results
        detail : bool, default False
            Whether to return detailed metadata or just paths

        Returns
        -------
        list or dict
            File paths (if detail=False) or detailed metadata (if detail=True)

        Raises
        ------
        LynceusFileError
            If an error occurs during file listing
        """

        def _retrieve_remote_files():
            """
            Internal function to retrieve remote files based on search criteria.

            Returns
            -------
            list or dict
                Raw file listing from S3 filesystem
            """
            if recursive:
                # s3fs Globing feature does not support path with the 's3:/' prefix ...
                return self.get_s3filesystem().glob(str(Path(remote_root_path) / Path(pattern or '**/*')),
                                                    maxdepth=maxdepth, detail=detail)

            # Uses the find method, because ls one is NOT implemented in s3fs.
            # Some options are used only if pattern is NOT defined.
            find_kwargs: dict[str, str | bool | int] = {
                'detail': detail
            }

            if pattern:
                find_kwargs.update({'prefix': pattern})
            else:
                find_kwargs.update(
                    {
                        'maxdepth': maxdepth or 1,
                        'withdirs': withdirs if withdirs is not None else True
                    }
                )

            # s3 find feature does not support path with the 's3:/' prefix ...
            return self.get_s3filesystem().find(path=remote_root_path, **find_kwargs)

        def _extract_path(remote_file_path):
            """
            Extract the path component from a full S3 file path.

            Parameters
            ----------
            remote_file_path : str
                Full S3 path

            Returns
            -------
            str
                Path component (key) from the S3 path
            """
            return self.split_path(remote_file_path=remote_file_path)[1]

        try:
            self._logger.debug(f'Looking/globbing for remote files ({remote_root_path=}; {pattern=}) ...')
            all_remote_file_metadata = _retrieve_remote_files()

            # Processed result according to requested detail
            #  - only path are returned as a list
            if not detail:
                return [_extract_path(remote_file_path) for remote_file_path in all_remote_file_metadata]

            #  - path, and lots of metadata are returned as a dict
            return {_extract_path(remote_file_key): remote_file_detailed_metadata
                    for remote_file_key, remote_file_detailed_metadata in all_remote_file_metadata.items()}
        except Exception as exc:  # pylint: disable=broad-except
            # pylint: disable=raise-missing-from
            raise LynceusFileError(f'An error occured while looking/globbing for remote files ({remote_root_path=}; {pattern=}) ...', from_exception=exc)


# Patch and initialize s3fs once for all.
# pylint: disable=useless-super-delegation,abstract-method
class S3FileSystemPatched(s3fs.S3FileSystem):
    """
    Patched version of s3fs.S3FileSystem with Lynceus-specific enhancements.

    Extend the base S3FileSystem to include:
    - Lynceus configuration integration
    - Enhanced OVH storage compatibility
    - Custom client configuration handling
    - Improved ls() method implementation
    """

    def __init__(self, *k, **kw):
        """
        Initialize the patched S3 filesystem with Lynceus configuration.

        Extract Lynceus-specific configuration and set up the S3 client
        with appropriate parameters for various S3-compatible storage providers.

        Parameters
        ----------
        *k : tuple
            Positional arguments passed to parent class
        **kw : dict
            Keyword arguments including LYNCEUS_S3_CONFIG_KEY

        Raises
        ------
        ValueError
            If LYNCEUS_S3_CONFIG_KEY is not provided
        """
        # Extracts s3 config key from parameters.
        self.lynceus_s3_config = kw.pop(LYNCEUS_S3_CONFIG_KEY, None)
        if not self.lynceus_s3_config:
            raise ValueError(f'{LYNCEUS_S3_CONFIG_KEY} is a mandatory parameter when initializing S3FileSystemPatched')

        lynceus: LynceusSession = LynceusSession.get_session(registration_key={'user': 's3filesystem'})
        logger: Logger = lynceus.get_logger('s3Init')
        logger.info(f'Using S3 config "{LynceusConfig.format_config(self.lynceus_s3_config)}".')

        # Builds config kwargs (with various element required by OVH storage, from botocore 1.36+.
        config_kwargs = {
            'request_checksum_calculation': 'when_required',
            'response_checksum_validation': 'when_required'
        }
        config_kwargs.update({key: value for key, value in self.lynceus_s3_config.items()
                              if key in ('signature_version',)})

        # Builds client kwargs.
        client_kwargs = {
            'endpoint_url': self.lynceus_s3_config['s3_endpoint'],
        }

        # Adds any additional/extra parameters to client kwargs.
        client_kwargs.update(
            {key: value for key, value in self.lynceus_s3_config.items()
             if key not in config_kwargs
             and key not in (CONFIG_STORAGE_REMOTE_TYPE, 'endpoint_url', 'bucket_name', 'username',
                             'access_key_id', 'secret_access_key', 's3_endpoint', 'addressing_style',
                             CONFIG_STORAGE_IS_DYNAMIC, CONFIG_STORAGE_DYNAMIC_TYPE)}
        )
        logger.info(f'System will use these S3 client kwargs: "{LynceusConfig.format_config(client_kwargs)}".')

        super().__init__(*k,
                         key=self.lynceus_s3_config.get('access_key_id'),
                         secret=self.lynceus_s3_config.get('secret_access_key'),
                         config_kwargs=config_kwargs,
                         client_kwargs=client_kwargs,
                         **kw)

    def ls(self, path, detail=True, **kwargs):
        """
        List files and directories at the specified S3 path.

        Improved implementation that uses the find method with appropriate
        parameters for directory listing.

        Parameters
        ----------
        path : str
            S3 path to list
        detail : bool, default True
            Whether to return detailed file information
        **kwargs
            Additional arguments passed to find method

        Returns
        -------
        list
            File and directory information
        """
        # See: s3fs.core.S3FileSystem._find
        return self.find(path, maxdepth=1, withdirs=True, detail=detail, **kwargs)
