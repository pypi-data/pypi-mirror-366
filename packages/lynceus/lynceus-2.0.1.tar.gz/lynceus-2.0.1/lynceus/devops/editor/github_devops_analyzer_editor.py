from pathlib import Path

from lynceus.devops.editor.devops_analyzer_editor import DevOpsAnalyzerEditor
from lynceus.devops.github_devops_analyzer import (
    GithubDevOpsAnalyzer,
    github_exception_handler,
)


class GithubDevOpsAnalyzerEditor(GithubDevOpsAnalyzer, DevOpsAnalyzerEditor):
    """
    GitHub-specific implementation of the DevOps analyzer with editor capabilities.

    This class extends GithubDevOpsAnalyzer with write/edit operations. However,
    most write operations are not available through GitHub's API or are restricted,
    so most methods raise NotImplementedError with appropriate explanations.

    GitHub API limitations:
    - Organization creation requires enterprise features
    - User creation is not available through API
    - Project import/export is not supported through standard API
    - Team membership management has limited API access

    This class serves as a placeholder to maintain API consistency while
    clearly indicating which operations are not supported on GitHub.
    """

    @github_exception_handler
    def _do_create_group(
        self,
        *,
        parent_group_full_path: str,
        new_group_name: str,
        new_group_relative_path: str,
        **kwargs
    ):
        """
        Create a new organization (not supported on GitHub via API).

        GitHub does not provide API endpoints for creating organizations.
        Organizations must be created through the web interface.

        Parameters
        ----------
        parent_group_full_path : str
            Parent organization path (unused)
        new_group_name : str
            Name of the organization (unused)
        new_group_relative_path : str
            Path of the organization (unused)
        **kwargs
            Additional parameters (unused)

        Raises
        ------
        NotImplementedError
            Always raised as this feature is not available
        """
        raise NotImplementedError(
            "This feature is not available with the implementation for Github."
        )

    @github_exception_handler
    def _do_create_user(self, *, name: str, username: str, email: str, **kwargs):
        """
        Create a new user (not supported on GitHub via API).

        GitHub does not provide API endpoints for creating user accounts.
        Users must register through the web interface.

        Parameters
        ----------
        name : str
            Display name of the user (unused)
        username : str
            Username for the user (unused)
        email : str
            Email address of the user (unused)
        **kwargs
            Additional parameters (unused)

        Raises
        ------
        NotImplementedError
            Always raised as this feature is not available
        """
        raise NotImplementedError(
            "This feature is not available with the implementation for Github."
        )

    @github_exception_handler
    def _do_update_user_notification_settings(
        self, *, username: str, email: str, **kwargs
    ):
        """
        Update user notification settings (not supported on GitHub via API).

        GitHub does not provide API endpoints for modifying user notification
        settings on behalf of other users.

        Parameters
        ----------
        username : str
            Username of the user (unused)
        email : str
            Email of the user (unused)
        **kwargs
            Notification settings (unused)

        Raises
        ------
        NotImplementedError
            Always raised as this feature is not available
        """
        raise NotImplementedError(
            "This feature is not available with the implementation for Github."
        )

    @github_exception_handler
    def _do_add_group_member(
        self, *, group_full_path: str, username: str, access, **kwargs
    ):
        """
        Add a member to an organization (not supported on GitHub via API).

        GitHub's API for organization membership management is limited and
        requires special permissions that are not typically available.

        Parameters
        ----------
        group_full_path : str
            Full path of the organization (unused)
        username : str
            Username of the user to add (unused)
        access : object
            Access level for the member (unused)
        **kwargs
            Additional parameters (unused)

        Raises
        ------
        NotImplementedError
            Always raised as this feature is not available
        """
        # https://pygithub.readthedocs.io/en/latest/github_objects/Team.html?highlight=member#github.Team.Team.add_to_members
        raise NotImplementedError(
            "This feature is not available with the implementation for Github."
        )

    @github_exception_handler
    def _do_export_project(
        self,
        *,
        project_full_path: str,
        export_dst_full_path: Path,
        timeout_sec: int = 60,
        **kwargs
    ):
        """
        Export a project (not supported on GitHub via API).

        GitHub does not provide API endpoints for exporting repositories
        in a format similar to GitLab's project export functionality.

        Parameters
        ----------
        project_full_path : str
            Full path of the project (unused)
        export_dst_full_path : Path
            Destination path (unused)
        timeout_sec : int, optional
            Timeout in seconds (unused) (default: 60)
        **kwargs
            Additional parameters (unused)

        Raises
        ------
        NotImplementedError
            Always raised as this feature is not available
        """
        raise NotImplementedError(
            "This feature is not available with the implementation for Github."
        )

    @github_exception_handler
    def _do_import_project(
        self,
        *,
        parent_group_full_path: str,
        new_project_name: str,
        new_project_path: str,
        import_src_full_path: Path,
        timeout_sec: int = 60,
        **kwargs
    ):
        """
        Import a project (not supported on GitHub via API).

        GitHub does not provide API endpoints for importing projects
        in a format similar to GitLab's project import functionality.

        Parameters
        ----------
        parent_group_full_path : str
            Parent organization path (unused)
        new_project_name : str
            Name for the new project (unused)
        new_project_path : str
            Path for the new project (unused)
        import_src_full_path : Path
            Source file path (unused)
        timeout_sec : int, optional
            Timeout in seconds (unused) (default: 60)
        **kwargs
            Additional parameters (unused)

        Raises
        ------
        NotImplementedError
            Always raised as this feature is not available
        """
        raise NotImplementedError(
            "This feature is not available with the implementation for Github."
        )
