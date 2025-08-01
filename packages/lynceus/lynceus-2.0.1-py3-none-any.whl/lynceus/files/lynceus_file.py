import shutil
from abc import ABCMeta
from logging import Logger
from pathlib import Path
from typing import (Generic,
                    TypeVar)

import pandas as pd
from fsspec.asyn import AsyncFileSystem
from pandas import DataFrame

from lynceus.core.config import (CONFIG_STORAGE_LOCAL,
                                 LYNCEUS_S3_CONFIG_KEY)
from lynceus.core.config.lynceus_config import LynceusConfig
from lynceus.files.remote.s3 import (S3FileSystemPatched,
                                     S3Utils)
from lynceus.lynceus_exceptions import LynceusFileError

# pylint: disable=invalid-name
FileSystemType = TypeVar("FileSystemType", bound=AsyncFileSystem)


class LynceusFile(Generic[FileSystemType], metaclass=ABCMeta):
    """
    Abstract base class for file operations in the Lynceus system.

    Provides a unified interface for handling both local and remote files,
    supporting operations like reading, writing, copying, and listing files.
    Implements the filesystem abstraction pattern for different storage backends.

    Parameters
    ----------
    FileSystemType : type
        Generic type parameter for the underlying filesystem implementation
    """
    S3_PATH_BEGIN = 's3://'

    FILE_STORAGE_PATH_SEPARATOR: str = '|'

    def __init__(self,
                 path: Path,
                 logger: Logger,
                 filesystem: FileSystemType = None):
        """
        Initialize a LynceusFile instance.

        Parameters
        ----------
        path : Path
            The file path
        logger : Logger
            Logger instance for operations
        filesystem : FileSystemType, optional
            Optional filesystem implementation for operations
        """
        self._path: Path = path
        self._logger: Logger = logger
        self._filesystem: FileSystemType = filesystem

    @staticmethod
    def extract_storage_and_path(file_metadata: str):
        """
        Extract storage type and path from file metadata string.

        Parses file metadata to separate storage identifier from the actual path.
        If no storage separator is found, assumes local storage.

        Parameters
        ----------
        file_metadata : str
            String containing storage info and path separated by FILE_STORAGE_PATH_SEPARATOR

        Returns
        -------
        tuple
            (storage_name, file_path) where storage_name is the storage identifier
            and file_path is the actual path to the file
        """
        # Checks if there is storage information in the metadata.
        if LynceusFile.FILE_STORAGE_PATH_SEPARATOR in file_metadata:
            file_metadata_parts = file_metadata.split(LynceusFile.FILE_STORAGE_PATH_SEPARATOR)
            return file_metadata_parts[0], file_metadata_parts[1]

        # There is none, so consider it as a file hosted on Local storage.
        return CONFIG_STORAGE_LOCAL, file_metadata

    @staticmethod
    def build_file_metadata(storage_name: str, file_path: Path | str):
        """
        Build file metadata string from storage name and file path.

        Creates a standardized metadata string by combining storage identifier
        and file path with the appropriate separator.

        Parameters
        ----------
        storage_name : str
            Name of the storage system
        file_path : Path or str
            Path to the file (can be Path object or string)

        Returns
        -------
        str
            Formatted metadata string in format 'storage_name|file_path'
        """
        return f'{storage_name}{LynceusFile.FILE_STORAGE_PATH_SEPARATOR}{str(file_path)}'

    def read_parquet(self, **params) -> DataFrame:
        """
        Read corresponding (local or remote) file, considering it as a parquet file, with optional parameters.

        Parameters
        ----------
        **params : dict
            Optional parameters (usually, it can be columns, to specify which columns
            to read from parquet file).

        Returns
        -------
        DataFrame
            Corresponding DataFrame.
        """
        # Cf. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_parquet.html
        # Cf. http://arrow.apache.org/docs/python/generated/pyarrow.parquet.read_table.html

        self._logger.debug(f'Reading file {self} ...')
        return pd.read_parquet(self.get_path(), storage_options=self.get_storage_options(), **params)

    def write_to_parquet(self, dataframe: DataFrame, **kwargs):
        """
        Write a DataFrame to parquet format at the file location.

        Write the provided DataFrame as a parquet file with standardized settings
        for timestamp handling and storage options. Invalidate filesystem cache
        after writing to ensure consistency.

        Parameters
        ----------
        dataframe : DataFrame
            Pandas DataFrame to write
        **kwargs
            Additional parameters passed to pandas.DataFrame.to_parquet()
            (e.g., compression, index settings)
        """
        # N.B.: **kwargs is the opportunity to provide parameters for internal implementation (e.g. PyArrow),
        #  for instances, pyarrow filters param, to better control what is load in memory.
        #
        # Cf. https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_parquet.html
        # Cf. https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-parquet
        # Cf. https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html

        self._logger.debug(f'Writing specified DataFrame to file {self} ...')
        dataframe.to_parquet(self.get_path(),
                             coerce_timestamps='ms', allow_truncated_timestamps=True,
                             storage_options=self.get_storage_options(),
                             **kwargs)
        # Important: ensures cache is updated straight away after this operation.
        if self._filesystem:
            self._filesystem.invalidate_cache(str(self.get_parent_path()))

    def get_storage_options(self):
        """
        Get storage-specific options for file operations.

        Return configuration options specific to the storage backend.
        Default implementation returns None, subclasses should override
        to provide appropriate options for their storage type.

        Returns
        -------
        dict or None
            Storage options for the specific filesystem implementation
        """
        # pylint: disable=no-self-use
        return None

    def is_local(self):
        """
        Check if this file is stored locally.

        Abstract method that must be implemented by subclasses to determine
        whether the file is stored on the local filesystem.

        Returns
        -------
        bool
            True if file is stored locally, False otherwise

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def is_remote(self):
        """
        Check if this file is stored remotely.

        Convenience method that returns the inverse of is_local().

        Returns
        -------
        bool
            True if file is stored remotely, False if local
        """
        return not self.is_local()

    def delete(self):
        """
        Delete the file from its storage location.

        Remove the file from the filesystem. Log the operation before
        delegating to the implementation-specific delete method.

        Returns
        -------
        object
            Result of the delete operation (implementation-dependent)
        """
        self._logger.debug(f'Deleting file {self} ...')
        return self._do_delete()

    def _do_delete(self):
        """
        Implementation-specific delete operation.

        Abstract method that subclasses must implement to handle
        the actual file deletion for their storage type.

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def download_to(self, destination: Path, *, create_sub_directories: bool = True):
        """
        Download/copy the file to a local destination.

        Retrieve the file content and save it to the specified local path.
        Optionally create parent directories if they don't exist.

        Parameters
        ----------
        destination : Path
            Local path where the file should be saved
        create_sub_directories : bool, default True
            Whether to create parent directories if they don't exist

        Returns
        -------
        object
            Result of the download operation (implementation-dependent)
        """
        self._logger.debug(f'Retrieving/downloading file to "{destination}" from {self} ...')
        return self._do_download_to(destination=destination, create_sub_directories=create_sub_directories)

    def _do_download_to(self, *, destination: Path, create_sub_directories: bool):
        """
        Implementation-specific download operation.

        Abstract method that subclasses must implement to handle
        the actual file download for their storage type.

        Parameters
        ----------
        destination : Path
            Local path where the file should be saved
        create_sub_directories : bool
            Whether to create parent directories

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def exists(self, *, reason: str = None):
        """
        Check if the file exists in its storage location.

        Verify file existence and optionally log the reason for the check.

        Parameters
        ----------
        reason : str, optional
            Optional explanation for why existence is being checked

        Returns
        -------
        bool
            True if file exists, False otherwise
        """
        check_msg: str = f'Checking existence of file {self}'
        if reason:
            check_msg += f' (reason: {reason})'
        self._logger.debug(f'{check_msg} ...')
        return self._do_exists()

    def _do_exists(self):
        """
        Implementation-specific existence check.

        Abstract method that subclasses must implement to check
        file existence for their storage type.

        Returns
        -------
        bool
            True if file exists, False otherwise

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def list_files(self, *, recursive: bool = False, pattern: str | None = None, **kwargs):
        """
        List files in the directory represented by this file path.

        Return a list of files in the directory, with options for recursive
        traversal and pattern matching.

        Parameters
        ----------
        recursive : bool, default False
            Whether to search subdirectories recursively
        pattern : str, optional
            Optional glob pattern to filter files
        **kwargs
            Additional arguments for the listing operation

        Returns
        -------
        Iterable
            Collection of file paths or file objects
        """
        self._logger.debug(f'Listing files from {self}, {pattern=} ...')
        return self._do_list_files(recursive=recursive, pattern=pattern, **kwargs)

    def _do_list_files(self, *, recursive: bool, pattern: str | None = None, **kwargs):
        """
        Implementation-specific file listing operation.

        Abstract method that subclasses must implement to list
        files for their storage type.

        Parameters
        ----------
        recursive : bool
            Whether to search subdirectories recursively
        pattern : str, optional
            Optional glob pattern to filter files
        **kwargs
            Additional arguments for the listing operation

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def copy_to(self, destination: Path, *, create_sub_directories: bool = True) -> 'LynceusFile':
        """
        Copy this file to a new destination.

        Create a copy of the file at the specified destination path.
        Invalidate filesystem cache after the operation for consistency.

        Parameters
        ----------
        destination : Path
            Path where the file should be copied
        create_sub_directories : bool, default True
            Whether to create parent directories if they don't exist

        Returns
        -------
        LynceusFile
            New LynceusFile instance representing the copied file
        """
        self._logger.debug(f"Copying '{self}' to '{destination}' ...")
        copied_lynceus_file: LynceusFile = self._do_copy_to(destination=destination, create_sub_directories=create_sub_directories)
        # Important: ensures cache is updated straight away after this operation.
        if self._filesystem:
            self._filesystem.invalidate_cache(str(destination.parent))
        return copied_lynceus_file

    def _do_copy_to(self, *, destination: Path, create_sub_directories: bool) -> 'LynceusFile':
        """
        Implementation-specific copy operation.

        Abstract method that subclasses must implement to handle
        file copying for their storage type.

        Parameters
        ----------
        destination : Path
            Path where the file should be copied
        create_sub_directories : bool
            Whether to create parent directories

        Returns
        -------
        LynceusFile
            New LynceusFile instance for the copied file

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def get_name(self) -> str:
        """
        Get the filename (without directory path).

        Returns
        -------
        str
            The name portion of the file path
        """
        return self._path.name

    @property
    def path(self) -> Path:
        """
        Get the file path as a Path object.

        Returns
        -------
        Path
            The file path
        """
        return self._path

    def get_path(self) -> str:
        """
        Get the file path as a string.

        Returns
        -------
        str
            String representation of the file path
        """
        return str(self._path)

    def get_raw_path(self) -> str:
        """
        Get the raw path without any protocol prefixes.

        Abstract method that returns the underlying path without
        storage-specific prefixes (e.g., without 's3://' for S3 files).

        Returns
        -------
        str
            Raw path string

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def get_relative_path(self) -> str:
        """
        Get the relative path from remote storage container.

        Returns
        -------
        str
            For remote file: the relative path from remote storage container,
            for local file: same than raw_path.
        """
        raise NotImplementedError()

    def get_parent_path(self) -> Path:
        """
        Get the parent directory path.

        Returns
        -------
        Path
            Path object representing the parent directory
        """
        return self._path.parent

    def parent_exists(self):
        """
        Check if the parent directory exists.

        Verify that the parent directory of this file exists in the storage system.

        Returns
        -------
        bool
            True if parent directory exists, False otherwise
        """
        self._logger.debug(f'Checking existence of parent folder of file {self} ...')
        return self._do_parent_exists()

    def _do_parent_exists(self):
        """
        Implementation-specific parent directory existence check.

        Abstract method that subclasses must implement to check
        parent directory existence for their storage type.

        Returns
        -------
        bool
            True if parent directory exists, False otherwise

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def get_extension(self) -> str:
        """
        Get the file extension including the dot.

        Returns
        -------
        str
            File extension (e.g., '.txt', '.parquet') or empty string if no extension
        """
        return self._path.suffix

    def __str__(self):
        """
        Get string representation of the file.

        Returns
        -------
        str
            Human-readable string describing the file
        """
        return f'"{self.__class__.__name__}" with path "{self._path}"'

    def __repr__(self):
        """
        Get detailed string representation for debugging.

        Returns
        -------
        str
            String representation suitable for debugging
        """
        return str(self)


class _LocalLynceusFile(LynceusFile[AsyncFileSystem]):
    """
    Implementation of LynceusFile for local filesystem operations.

    Handle file operations on the local filesystem using standard
    Python pathlib and shutil operations.
    """

    def is_local(self):
        """
        Check if this file is stored locally.

        Returns
        -------
        bool
            Always True for local files
        """
        return True

    def _do_delete(self):
        """
        Delete the local file.

        Use pathlib's unlink() method to remove the file from
        the local filesystem.
        """
        self._path.unlink()

    def _do_download_to(self, *, destination: Path, create_sub_directories: bool):
        """
        Download/copy local file to destination.

        For local files, this is equivalent to copying the file.

        Parameters
        ----------
        destination : Path
            Target path for the copy
        create_sub_directories : bool
            Whether to create parent directories

        Returns
        -------
        object
            Result of the copy operation
        """
        return self._do_copy_to(destination=destination, create_sub_directories=create_sub_directories)

    def _do_exists(self):
        """
        Check if the local file exists.

        Returns
        -------
        bool
            True if file exists on local filesystem, False otherwise
        """
        return self._path.exists()

    def _do_parent_exists(self):
        """
        Check if the parent directory exists locally.

        Returns
        -------
        bool
            True if parent directory exists, False otherwise
        """
        return self.get_parent_path().exists()

    def _do_list_files(self, *, recursive: bool, pattern: str | None = None, **kwargs):
        """
        List files in the local directory.

        Parameters
        ----------
        recursive : bool
            If True, use glob for recursive search; if False, use iterdir
        pattern : str, optional
            Glob pattern for file matching (defaults to '**/*' for recursive)
        **kwargs
            Additional arguments (ignored for local implementation)

        Returns
        -------
        Iterator
            File paths matching the criteria
        """
        if not recursive:
            return self._path.iterdir()
        return self._path.glob(pattern or '**/*')

    def _do_copy_to(self, *, destination: Path, create_sub_directories: bool) -> LynceusFile:
        """
        Copy local file to destination.

        Create parent directories if needed and copy the file using shutil.copyfile.

        Parameters
        ----------
        destination : Path
            Target path for the copy
        create_sub_directories : bool
            Whether to create parent directories if they don't exist

        Returns
        -------
        _LocalLynceusFile
            New instance representing the copied file

        Raises
        ------
        LynceusFileError
            If parent directory doesn't exist and create_sub_directories is False
        """
        if not destination.parent.exists():
            if create_sub_directories:
                destination.parent.mkdir(parents=True, exist_ok=True)
            else:
                raise LynceusFileError(f'Parent directory of specified destination "{destination}" does not exist;' +
                                       ' you should either create it yourself, or use the corresponding option.')

        # Requests the copy.
        shutil.copyfile(self.get_path(), destination)
        return _LocalLynceusFile(path=destination, logger=self._logger)

    def get_raw_path(self) -> str:
        """
        Get the raw local file path.

        For local files, this is the same as the string representation of the path.

        Returns
        -------
        str
            Local file path as string
        """
        return str(self._path)

    def get_relative_path(self) -> str:
        """
        Get the relative path for local files.

        For local files, this returns the same as the raw path.

        Returns
        -------
        str
            Local file path as string
        """
        return self.get_raw_path()


class _RemoteS3LynceusFile(LynceusFile[S3FileSystemPatched]):
    """
    Implementation of LynceusFile for S3-compatible remote storage.

    Handle file operations on S3-compatible storage systems using
    the S3FileSystemPatched filesystem and S3Utils for operations.
    """

    # In addition there is a self.S3_PATH_BEGIN usage in Factory which should be adapted (in case it is NOT S3 !).
    def __init__(self, path: Path, logger: Logger, s3filesystem: S3FileSystemPatched, s3_utils: S3Utils):
        """
        Initialize remote S3 file instance.

        Parameters
        ----------
        path : Path
            S3 file path
        logger : Logger
            Logger instance
        s3filesystem : S3FileSystemPatched
            S3 filesystem implementation
        s3_utils : S3Utils
            S3 utilities for operations
        """
        super().__init__(path, logger, filesystem=s3filesystem)
        self.__s3_utils = s3_utils

    def get_storage_options(self):
        """
        Get S3-specific storage options for file operations.

        Build storage options including authentication and S3 configuration.
        Include special handling for OVH storage providers.

        Returns
        -------
        dict
            Storage options for S3 operations including authentication and ACL settings
        """
        # N.B.: in our Patched remote fs System, we added the needed lynceus_s3_config.
        storage_options = {
            'anon': False,
            LYNCEUS_S3_CONFIG_KEY: self._filesystem.lynceus_s3_config
        }

        # Checks if it is an OVH remote storage.
        if '.ovh.' in self._filesystem.lynceus_s3_config['s3_endpoint']:
            # Hacks ACL information to workaround OVH Bug, with default ACL specified by s3fs/botocore.
            # Leading to an useless "OSError: [Errno 22] Invalid Argument." ...
            storage_options.update(
                {
                    's3_additional_kwargs': {'ACL': 'private'}
                }
            )

        return storage_options

    def is_local(self):
        """
        Check if this file is stored locally.

        Returns
        -------
        bool
            Always False for remote S3 files
        """
        return False

    def _do_delete(self):
        """
        Delete the remote S3 file.

        Use the S3 filesystem's rm_file method to remove the file
        from remote storage.
        """
        self._filesystem.rm_file(self.get_raw_path())

    # pylint: disable=unused-argument
    def _do_download_to(self, *, destination: Path, create_sub_directories: bool):
        """
        Download remote S3 file to local destination.

        Use the S3 filesystem's get method to download the file.

        Parameters
        ----------
        destination : Path
            Local path where file should be downloaded
        create_sub_directories : bool
            Whether to create parent directories (ignored in this implementation)

        Returns
        -------
        object
            Result of the S3 filesystem get operation
        """
        return self._filesystem.get(self.get_path(), str(destination))

    def _do_exists(self):
        """
        Check if the remote S3 file exists.

        Returns
        -------
        bool
            True if file exists in S3 storage, False otherwise
        """
        return self._filesystem.exists(self.get_raw_path())

    def _do_parent_exists(self):
        """
        Check if the parent directory exists in S3.

        Returns
        -------
        bool
            True if parent directory exists in S3, False otherwise
        """
        return self._filesystem.exists(self.get_raw_path_from_remote_path(self.get_parent_path()))

    # pylint: disable=arguments-differ
    def _do_list_files(self, *,
                       recursive: bool,
                       pattern: str | None = None,
                       maxdepth: int | None = None,
                       withdirs: bool | None = None,
                       detail: bool = False):
        """
        List files in the remote S3 directory.

        Use S3Utils to list remote files with various filtering options.

        Parameters
        ----------
        recursive : bool
            Whether to search subdirectories recursively
        pattern : str, optional
            Optional glob pattern to filter files
        maxdepth : int, optional
            Maximum depth for directory traversal
        withdirs : bool, optional
            Whether to include directories in results
        detail : bool, default False
            Whether to return detailed metadata

        Returns
        -------
        list or dict
            File paths or detailed file information
        """
        return self.__s3_utils.list_remote_files(remote_root_path=Path(self.get_raw_path()),
                                                 recursive=recursive,
                                                 pattern=pattern,
                                                 maxdepth=maxdepth,
                                                 withdirs=withdirs,
                                                 detail=detail)

    # pylint: disable=unused-argument
    def _do_copy_to(self, *, destination: Path, create_sub_directories: bool) -> LynceusFile:
        """
        Copy remote S3 file to another S3 location.

        Copy the file within S3 storage using the filesystem's copy method.

        Parameters
        ----------
        destination : Path
            S3 destination path (must be relative for remote files)
        create_sub_directories : bool
            Whether to create parent directories (ignored)

        Returns
        -------
        _RemoteS3LynceusFile
            New instance representing the copied file

        Raises
        ------
        LynceusFileError
            If destination is absolute path for remote files
        """
        if self.is_remote() and destination.is_absolute():
            raise LynceusFileError(f'You should use only relative Path with remote file ("{self}"), which is not the case of destination "{destination}"')

        bucket_name, _, _ = self.__s3_utils.split_path(remote_file_path=self.get_path())
        complete_destination_path = Path(bucket_name) / destination
        self._filesystem.copy(self.get_path(), str(complete_destination_path))
        return _RemoteS3LynceusFile(path=Path(LynceusFile.S3_PATH_BEGIN) / complete_destination_path,
                                    logger=self._logger,
                                    s3filesystem=self._filesystem,
                                    s3_utils=self.__s3_utils)

    def get_path(self) -> str:
        """
        Get the full S3 path including the s3:// prefix.

        Returns
        -------
        str
            Complete S3 path with protocol prefix
        """
        # Important: to work, we must ensure the S3 PATH Begin is unaltered here (the double slash is mandatory ...).
        return LynceusFile.S3_PATH_BEGIN + self.get_raw_path()

    @staticmethod
    def get_raw_path_from_remote_path(path: Path | str):
        """
        Convert remote path to raw path without S3 prefix.

        Remove the 's3:/' prefix and ensure proper path formatting
        for S3 operations. Add trailing slash for root paths to avoid
        S3 traversal issues.

        Parameters
        ----------
        path : Path or str
            Remote path with S3 prefix

        Returns
        -------
        str
            Raw path suitable for S3 operations
        """
        # Removes the 's3:/' prefix to get a raw path.
        raw_path_from_remote_path = str(path)[len(LynceusFile.S3_PATH_BEGIN) - 1:]

        # Safe-guard: ensures there is at least one '/' in the final raw path (which is NOT the case for remote 'root path',
        #  to avoid issue with s3fs path splitting feature, and avoid 'Could not traverse all s3' issue).
        if '/' not in raw_path_from_remote_path:
            raw_path_from_remote_path += '/'

        return raw_path_from_remote_path

    def get_raw_path(self) -> str:
        """
        Get the raw S3 path without protocol prefix.

        Returns
        -------
        str
            S3 path without the s3:// prefix
        """
        return self.get_raw_path_from_remote_path(self._path)

    def get_relative_path(self) -> str:
        """
        Get the relative path within the S3 bucket.

        Extract the relative path portion from the full S3 path,
        excluding the bucket name.

        Returns
        -------
        str
            Relative path within the bucket
        """
        _, rpath, _ = self.__s3_utils.split_path(remote_file_path=self.get_path())
        return rpath

    def __str__(self):
        """
        Get string representation of the remote S3 file.

        Include the file path and remote storage configuration for debugging.

        Returns
        -------
        str
            Detailed string representation including remote config
        """
        return f'"{self.__class__.__name__}" with path "{self._path}" on remote "{LynceusConfig.format_config(self._filesystem.lynceus_s3_config)}"'
