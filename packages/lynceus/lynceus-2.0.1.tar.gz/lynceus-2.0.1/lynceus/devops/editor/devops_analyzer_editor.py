from pathlib import Path

from lynceus.devops.devops_analyzer import DevOpsAnalyzer


# TODO: add members?


class DevOpsAnalyzerEditor(DevOpsAnalyzer):
    """
    Abstract base class extending DevOpsAnalyzer with write/edit operations.

    This class extends the read-only DevOpsAnalyzer with additional capabilities
    for creating, updating, and managing DevOps platform resources. It provides
    abstract methods for platform-specific write operations that must be implemented
    by concrete subclasses.

    Supported operations:
    - Creating groups/organizations and users
    - Managing group memberships
    - Updating user notification settings
    - Importing and exporting projects
    """

    # The following methods are performing write/delete operation on DevOps backend.
    def _do_create_group(
        self,
        *,
        parent_group_full_path: str,
        new_group_name: str,
        new_group_relative_path: str,
        **kwargs,
    ):
        """
        Platform-specific implementation for creating a new group.

        Parameters
        ----------
        parent_group_full_path : str or None
            Full path of the parent group, None for root group
        new_group_name : str
            Display name of the group to create
        new_group_relative_path : str
            Path of the group relative to its parent
        **kwargs
            Additional platform-specific parameters

        Returns
        -------
        object
            Platform-specific group object representing the created group

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def create_group(
        self,
        *,
        parent_group_full_path: str,
        new_group_name: str,
        new_group_relative_path: str,
        **kwargs,
    ):
        """
        Create a new group and return standardized information.

        Parameters
        ----------
        parent_group_full_path : str or None
            Full path of the parent group, None for root group
        new_group_name : str
            Display name of the group to create
        new_group_relative_path : str
            Path of the group relative to its parent
        **kwargs
            Additional platform-specific parameters

        Returns
        -------
        LynceusDict
            Standardized group information for the created group
        """
        self._logger.debug(
            f'Creating group "{new_group_name=}" ({parent_group_full_path=}; {new_group_relative_path=}; {kwargs=}).'
        )
        group = self._do_create_group(
            parent_group_full_path=parent_group_full_path,
            new_group_name=new_group_name,
            new_group_relative_path=new_group_relative_path,
            **kwargs,
        )
        return self._extract_group_info(group)

    def _do_create_user(self, *, name: str, username: str, email: str, **kwargs):
        """
        Platform-specific implementation for creating a new user.

        Parameters
        ----------
        name : str
            Display name of the user
        username : str
            Username/login for the user
        email : str
            Email address of the user
        **kwargs
            Additional platform-specific parameters

        Returns
        -------
        object
            Platform-specific user object representing the created user

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def create_user(self, *, name: str, username: str, email: str, **kwargs):
        """
        Create a new user and return standardized information.

        Parameters
        ----------
        name : str
            Display name of the user
        username : str
            Username/login for the user
        email : str
            Email address of the user
        **kwargs
            Additional platform-specific parameters

        Returns
        -------
        LynceusDict
            Standardized user information for the created user
        """
        self._logger.debug(
            f'Creating user "{name=}" ({username=}; {email=}; {kwargs=}).'
        )
        user = self._do_create_user(name=name, username=username, email=email, **kwargs)
        return self._extract_user_info(user)

    def _do_update_user_notification_settings(
        self, *, username: str, email: str, **kwargs
    ):
        """
        Platform-specific implementation for updating user notification settings.

        Parameters
        ----------
        username : str
            Username of the user to update
        email : str
            Email of the user to update
        **kwargs
            Notification settings to update

        Returns
        -------
        object
            Platform-specific user object with updated settings

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def update_user_notification_settings(self, *, username: str, email: str, **kwargs):
        """
        Update user notification settings and return standardized information.

        Parameters
        ----------
        username : str
            Username of the user to update
        email : str
            Email of the user to update
        **kwargs
            Notification settings to update

        Returns
        -------
        LynceusDict
            Standardized user information after settings update
        """
        self._logger.debug(
            f'Updating notification settings for "{username=}" ({email=}; {kwargs=}).'
        )
        user = self._do_update_user_notification_settings(
            username=username, email=email, **kwargs
        )
        return self._extract_user_info(user)

    def _do_add_group_member(
        self, *, group_full_path: str, username: str, access, **kwargs
    ):
        """
        Platform-specific implementation for adding a member to a group.

        Parameters
        ----------
        group_full_path : str
            Full path of the group
        username : str
            Username of the user to add
        access : object
            Access level/permissions for the member
        **kwargs
            Additional platform-specific parameters

        Returns
        -------
        object
            Platform-specific member object representing the added membership

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def add_group_member(
        self, *, group_full_path: str, username: str, access, **kwargs
    ):
        """
        Add a member to a group and return standardized information.

        Parameters
        ----------
        group_full_path : str
            Full path of the group
        username : str
            Username of the user to add
        access : object
            Access level/permissions for the member
        **kwargs
            Additional platform-specific parameters

        Returns
        -------
        LynceusDict
            Standardized member information for the added membership
        """
        self._logger.debug(
            f'Adding user "{username=}" as member of group "{group_full_path=} ({access=}; {kwargs=}).'
        )
        member = self._do_add_group_member(
            group_full_path=group_full_path, username=username, access=access, **kwargs
        )
        return self._extract_member_info(member)

    def _do_export_project(
        self,
        *,
        project_full_path: str,
        export_dst_full_path: Path,
        timeout_sec: int = 60,
        **kwargs,
    ):
        """
        Platform-specific implementation for exporting a project.

        Parameters
        ----------
        project_full_path : str
            Full path of the project to export
        export_dst_full_path : Path
            Destination path for the exported file
        timeout_sec : int, optional
            Maximum time to wait for export completion in seconds (default: 60)
        **kwargs
            Additional platform-specific parameters

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def export_project(
        self,
        *,
        project_full_path: str,
        export_dst_full_path: Path,
        timeout_sec: int = 60,
        **kwargs,
    ):
        """
        Export a project to a file.

        Parameters
        ----------
        project_full_path : str
            Full path of the project to export
        export_dst_full_path : Path
            Destination path for the exported file
        timeout_sec : int, optional
            Maximum time to wait for export completion in seconds (default: 60)
        **kwargs
            Additional platform-specific parameters

        Returns
        -------
        object
            Result of the export operation (platform-specific)
        """
        self._logger.debug(
            f'Exporting project "{project_full_path=}" ({export_dst_full_path=}; {timeout_sec=}; {kwargs=}).'
        )
        return self._do_export_project(
            project_full_path=project_full_path,
            export_dst_full_path=export_dst_full_path,
            timeout_sec=timeout_sec,
            **kwargs,
        )

    def _do_import_project(
        self,
        *,
        parent_group_full_path: str,
        new_project_name: str,
        new_project_path: str,
        import_src_full_path: Path,
        timeout_sec: int = 60,
        **kwargs,
    ):
        """
        Platform-specific implementation for importing a project.

        Parameters
        ----------
        parent_group_full_path : str
            Full path of the parent group for the new project
        new_project_name : str
            Display name for the new project
        new_project_path : str
            Path/identifier for the new project
        import_src_full_path : Path
            Path to the file to import from
        timeout_sec : int, optional
            Maximum time to wait for import completion in seconds (default: 60)
        **kwargs
            Additional platform-specific parameters

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def import_project(
        self,
        *,
        parent_group_full_path: str,
        new_project_name: str,
        new_project_path: str,
        import_src_full_path: Path,
        timeout_sec: int = 60,
        **kwargs,
    ):
        """
        Import a project from a file.

        Parameters
        ----------
        parent_group_full_path : str
            Full path of the parent group for the new project
        new_project_name : str
            Display name for the new project
        new_project_path : str
            Path/identifier for the new project
        import_src_full_path : Path
            Path to the file to import from
        timeout_sec : int, optional
            Maximum time to wait for import completion in seconds (default: 60)
        **kwargs
            Additional platform-specific parameters

        Returns
        -------
        object
            Result of the import operation (platform-specific)
        """
        self._logger.debug(
            f'Importing project "{new_project_path=}" ({parent_group_full_path=}; {new_project_name=}; {import_src_full_path=}; {timeout_sec=}; {kwargs=}).'
        )
        return self._do_import_project(
            parent_group_full_path=parent_group_full_path,
            new_project_name=new_project_name,
            new_project_path=new_project_path,
            import_src_full_path=import_src_full_path,
            timeout_sec=timeout_sec,
            **kwargs,
        )
