import time
from pathlib import Path

import gitlab

from lynceus.devops.editor.devops_analyzer_editor import DevOpsAnalyzerEditor
from lynceus.devops.gitlab_devops_analyzer import (
    GitlabDevOpsAnalyzer,
    gitlab_exception_handler,
)


class GitlabDevOpsAnalyzerEditor(GitlabDevOpsAnalyzer, DevOpsAnalyzerEditor):
    """
    GitLab-specific implementation of the DevOps analyzer with editor capabilities.

    This class extends GitlabDevOpsAnalyzer with write/edit operations specific to GitLab,
    including creating groups and users, managing memberships, and handling project
    import/export operations. It uses GitLab's REST API for all write operations.

    Inherits all read-only capabilities from GitlabDevOpsAnalyzer and adds:
    - Group creation and management
    - User creation and notification settings updates
    - Group membership management
    - Project import/export with status monitoring
    """

    # See: https://docs.gitlab.com/ce/api/project_import_export.html#export-status
    # See: https://docs.gitlab.com/ce/api/project_import_export.html#import-status

    # The following methods are performing write/delete operation on DevOps backend.
    @gitlab_exception_handler
    def _do_create_group(
        self,
        *,
        parent_group_full_path: str,
        new_group_name: str,
        new_group_relative_path: str,
        **kwargs,
    ):
        # Prepares the common parameters.
        group_create_params: dict[str, str] = {
            "name": new_group_name,
            "path": new_group_relative_path,
            **kwargs,
        }

        # Checks if the group must be created under an existing one.
        if parent_group_full_path:
            root_group = self._do_get_group(
                full_path=parent_group_full_path, exact_match=True
            )
            if not root_group:
                raise NameError(
                    f'Unable to find the parent group with name "{parent_group_full_path}".'
                )

            # Adds the parent parameter.
            group_create_params.update({"parent_id": root_group.id})

        # See: https://docs.gitlab.com/ee/api/groups.html#new-group
        # Requests group creation.
        return self._manager.groups.create(group_create_params)

    @gitlab_exception_handler
    def _do_create_user(self, *, name: str, username: str, email: str, **kwargs):
        # See: https://python-gitlab.readthedocs.io/en/stable/gl_objects/users.html
        return self._manager.users.create(
            {
                "name": name,
                "username": username,
                "email": email,
                "reset_password": True,
                **kwargs,
            }
        )

    @gitlab_exception_handler
    def _do_update_user_notification_settings(
        self, *, username: str, email: str, **kwargs
    ):
        # See: https://python-gitlab.readthedocs.io/en/stable/gl_objects/notifications.html

        # N.B.: in Gitlab, only the notification settings of the authenticated user can be updated.
        # so here, to update the settings of the specified user, we need to request a dedicated impersonation token.
        # See: https://python-gitlab.readthedocs.io/en/stable/gl_objects/users.html?highlight=impersonation#user-impersonation-tokens
        user = self._do_get_user(username=username, email=email)

        # Creates a new impersonation token.
        user_active_impersonation_tokens = user.impersonationtokens.list(state="active")
        self._logger.debug(
            f'Looking for existing "active" impersonation token for user "{self._extract_user_info(user)}": "{user_active_impersonation_tokens=}".'
        )
        impersonation_token = user.impersonationtokens.create(
            {"name": "notif_token", "scopes": ["api"]}
        )
        self._logger.debug(
            f'Successfully created new impersonation token for user "{self._extract_user_info(user)}": "{impersonation_token=}".'
        )

        # Creates a new dedicated Gitlab manager, to update the settings.
        user_gl = gitlab.Gitlab(self._uri, private_token=impersonation_token.token)
        user_notificationsettings = user_gl.notificationsettings.get()
        self._logger.debug(
            f'These are the current user notification settings: "{user_notificationsettings.attributes=}".'
        )

        # Updates notification settings.
        for setting, value in kwargs.items():
            self._logger.debug(
                f'Updating user notification settings "{setting}" to "{value}".'
            )
            setattr(user_notificationsettings, setting, value)
        user_notificationsettings.save()
        self._logger.debug(
            f'Successfully updated user notification settings to: "{user_notificationsettings.attributes=}".'
        )

        # Cleans the impersonation token.
        impersonation_token.delete()
        del user_gl

        # Returns the User which may hold some interesting information in some DevOps Backend implementation.
        return user

    @gitlab_exception_handler
    def _do_add_group_member(
        self, *, group_full_path: str, username: str, access, **kwargs
    ):
        group = self._do_get_group(full_path=group_full_path, exact_match=True)
        user = self._do_get_user(username=username)

        return group.members.create(
            {"user_id": user.id, "access_level": access, **kwargs}
        )

    def __wait_until_status_or_timeout(
        self,
        *,
        obj,
        refresh_func,
        attr_name: str,
        values: list[str],
        timeout_sec: int,
        step_sec: int = 2,
    ):
        """
        Wait for an object's attribute to reach one of the specified values or timeout.

        This is a utility method for polling GitLab operations that take time to complete,
        such as project imports and exports.

        Parameters
        ----------
        obj : object
            Object to monitor
        refresh_func : callable
            Function to call to refresh the object state
        attr_name : str
            Name of the attribute to monitor
        values : list[str]
            List of acceptable final values
        timeout_sec : int
            Maximum time to wait in seconds
        step_sec : int, optional
            Polling interval in seconds (default: 2)
        """
        self._logger.debug(
            f'Starting polling wait until maximum of {timeout_sec} seconds, for attributes "{attr_name=}" on "{obj=}" to reach one of the "{values=}" ...'
        )
        remaining_time: int = timeout_sec
        refresh_func(obj)
        while remaining_time > 0 and getattr(obj, attr_name) not in values:
            time.sleep(step_sec)
            remaining_time -= step_sec
            refresh_func(obj)

        self._logger.debug(
            f'Attribute "{attr_name=}" on "{obj=}" reached "{getattr(obj, attr_name)}", in "{timeout_sec - remaining_time}" seconds.'
        )

    @gitlab_exception_handler
    def _do_export_project(
        self,
        *,
        project_full_path: str,
        export_dst_full_path: Path,
        timeout_sec: int = 60,
        **kwargs,
    ):
        """
        Export a GitLab project to a file.

        Create an export request, wait for completion, and download the result.
        The export includes project data, issues, merge requests, and other metadata.

        Parameters
        ----------
        project_full_path : str
            Full path of the project to export
        export_dst_full_path : Path
            Destination path for the exported file
        timeout_sec : int, optional
            Maximum time to wait for export completion (default: 60 seconds)
        **kwargs
            Additional GitLab export parameters

        Raises
        ------
        ValueError
            If export fails or times out
        """
        # See: https://python-gitlab.readthedocs.io/en/stable/gl_objects/projects.html#import-export
        # See: https://docs.gitlab.com/ce/api/project_import_export.html

        # Safe-guard: prepares output structure.
        export_dst_full_path.parent.mkdir(parents=True, exist_ok=True)

        # Create the export.
        self._logger.info(
            f'Requesting export of project with full path "{project_full_path}" ...'
        )
        project = self._do_get_project(full_path=project_full_path)
        export = project.exports.create()

        # Waits till the export reaches a final status.
        self.__wait_until_status_or_timeout(
            obj=export,
            refresh_func=lambda instance: instance.refresh(),
            attr_name="export_status",
            values=[
                self.IMPORT_EXPORT_STATUS_SUCCESS,
                self.IMPORT_EXPORT_STATUS_FAILED,
            ],
            timeout_sec=timeout_sec,
        )

        # Checks status.
        if export.export_status != self.IMPORT_EXPORT_STATUS_SUCCESS:
            raise ValueError(
                f'Export of project with full path "{project_full_path}" did not reach'
                + f' "{self.IMPORT_EXPORT_STATUS_SUCCESS}" success status, in "{timeout_sec}" seconds'
                + f' but "{export.export_status}".'
            )

        # Saves the result.
        self._logger.debug(
            f'Export is now ready, saving it to "{export_dst_full_path}" ...'
        )
        with open(export_dst_full_path, "wb") as export_file:
            export.download(streamed=True, action=export_file.write)
        self._logger.info(
            f'Successfully exported project with full path "{project_full_path}" to "{export_dst_full_path}".'
        )

    @gitlab_exception_handler
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
        Import a project into GitLab from an exported file.

        Create an import request, wait for completion, and return the new project.
        The import file should be a GitLab project export archive.

        Parameters
        ----------
        parent_group_full_path : str
            Full path of the parent group for the new project
        new_project_name : str
            Display name for the new project
        new_project_path : str
            Path/identifier for the new project
        import_src_full_path : Path
            Path to the GitLab export file to import
        timeout_sec : int, optional
            Maximum time to wait for import completion (default: 60 seconds)
        **kwargs
            Additional GitLab import parameters

        Raises
        ------
        ValueError
            If the source file doesn't exist or import fails/times out
        """
        # See: https://python-gitlab.readthedocs.io/en/stable/gl_objects/projects.html#import-export
        # See: https://docs.gitlab.com/ce/api/project_import_export.html

        # Safe-guard: ensures import source file exists..
        if not import_src_full_path.exists():
            raise ValueError(
                f'Specified source file "{import_src_full_path}" does not exist. Aborting import.'
            )

        # Create the import.
        project_complete_path = (
            new_project_path
            if not parent_group_full_path
            else f"{parent_group_full_path}/{new_project_path}"
        )
        self._logger.info(
            f'Requesting import of project "{import_src_full_path}" to new project with full path "{project_complete_path}" ...'
        )

        with open(import_src_full_path, "rb") as file_source:
            output = self._manager.projects.import_project(
                file_source,
                namespace=parent_group_full_path,
                path=new_project_path,
                name=new_project_name,
                **kwargs,
            )
        new_project = self._manager.projects.get(output["id"])
        project_import = new_project.imports.get()

        # Waits till the import reaches a final status.
        self.__wait_until_status_or_timeout(
            obj=project_import,
            refresh_func=lambda instance: instance.refresh(),
            attr_name="import_status",
            values=[
                self.IMPORT_EXPORT_STATUS_SUCCESS,
                self.IMPORT_EXPORT_STATUS_FAILED,
            ],
            timeout_sec=timeout_sec,
        )

        # Checks status.
        if project_import.import_status != self.IMPORT_EXPORT_STATUS_SUCCESS:
            raise ValueError(
                f'Import of "{import_src_full_path}" to new project with full path "{new_project.path_with_namespace}" did not reach'
                + f' "{self.IMPORT_EXPORT_STATUS_SUCCESS}" success status, in "{timeout_sec}" seconds'
                + f' but "{project_import.import_status}".'
            )

        self._logger.info(
            f'Successfully imported "{import_src_full_path}" to new project with full path "{new_project.path_with_namespace}" ...'
        )
