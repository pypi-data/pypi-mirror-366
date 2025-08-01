"""
Storage metadata classes allowing to easily configure various user, group and topic storages (default, and extra ones).

Inside Lynceus since version 0.7.0 (instead of LynceusCLI) to share unique key creation algorithm across all projects.

"""

from abc import ABC
from dataclasses import dataclass

from lynceus.utils import cleansed_str_value


@dataclass
class StorageMetadataBase(ABC):
    """
    Abstract base class for storage metadata configurations.

    Provide the foundation for different types of storage metadata including
    user storages, group storages, and other specialized storage configurations.
    This class defines the common interface and basic functionality needed
    to create and manage various storage containers with unique naming,
    access permissions, and caching behaviors.

    Attributes
    ----------
    instance_id : str
        Unique identifier allowing environment discrimination
    """

    # The Instance ID (allowing to have an environment discrimination)
    instance_id: str

    def cleansed_instance_id(self) -> str:
        """
        Get a cleansed version of the instance ID.

        Apply string cleansing operations to ensure the instance ID
        is safe for use in storage names and paths.

        Returns
        -------
        str
            Cleansed instance ID string
        """
        return cleansed_str_value(self.instance_id)

    def build_unique_storage_name(self) -> str:
        """
        Build a unique storage name for this metadata instance.

        Abstract method that subclasses must implement to generate
        a unique identifier for storage containers or buckets.

        Returns
        -------
        str
            Unique storage name

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def get_cache_toggle(self) -> bool:
        """
        Get the cache toggle setting for this storage.

        Abstract method that subclasses must implement to specify
        whether caching should be enabled for this storage type.

        Returns
        -------
        bool
            True if caching should be enabled, False otherwise

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def get_access_permission(self) -> str:
        """
        Get the access permission level for this storage.

        Abstract method that subclasses must implement to specify
        the access permissions required for this storage type.

        Returns
        -------
        str
            Access permission level identifier

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def build_storage_prefix(self) -> str:
        """
        Build a storage prefix for organizing files within the storage.

        Abstract method that subclasses must implement to generate
        a prefix used for organizing files within the storage container.

        Returns
        -------
        str
            Storage prefix path

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()

    def build_mount_path_relative_to_home_dir(self) -> str:
        """
        Build a mount path relative to the user's home directory.

        Abstract method that subclasses must implement to generate
        a local mount path for accessing the storage relative to the home directory.

        Returns
        -------
        str
            Mount path relative to home directory

        Raises
        ------
        NotImplementedError
            If not implemented by subclass
        """
        raise NotImplementedError()
