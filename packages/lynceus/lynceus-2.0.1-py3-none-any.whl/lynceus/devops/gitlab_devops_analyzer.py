from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import gitlab
from gitlab.const import AccessLevel

from lynceus.core.config import DATETIME_FORMAT_SHORT
from lynceus.core.exchange.lynceus_exchange import LynceusExchange
from lynceus.core.lynceus import LynceusSession
from lynceus.devops.devops_analyzer import DevOpsAnalyzer
from lynceus.utils import flatten, parse_string_to_datetime
from lynceus.utils.lynceus_dict import LynceusDict


def gitlab_exception_handler(func):
    """
    Decorator to handle GitLab-specific exceptions and convert them to standard exceptions.

    Parameters
    ----------
    func : callable
        Function to wrap with exception handling

    Returns
    -------
    callable
        Wrapped function that handles GitLab exceptions

    Raises
    ------
    PermissionError
        For 401/403 HTTP status codes
    NameError
        For 404 HTTP status codes
    """

    def func_wrapper(*args, **kwargs):
        """
        Internal wrapper function that handles GitLab API errors.

        Parameters
        ----------
        *args : tuple
            Positional arguments passed to the wrapped function
        **kwargs
            Keyword arguments passed to the wrapped function

        Returns
        -------
        object
            Result of the wrapped function call

        Raises
        ------
        PermissionError
            For 401/403 HTTP status codes
        NameError
            For 404 HTTP status codes
        """
        try:
            return func(*args, **kwargs)
        except gitlab.exceptions.GitlabError as error:
            # Intercepts permission error.
            if error.response_code in (401, 403):
                raise PermissionError(
                    "You don't have enough permission to perform this operation on Gitlab."
                ) from error
            if error.response_code == 404:
                raise NameError("Unable to find requested Object.") from error

            # Raises any other error.
            raise

    return func_wrapper


def get_list_from_paginated_and_count(
        plist_func: Callable, count: int | None = None, **kwargs
) -> list:
    """
    Helper function to get a list from GitLab paginated results with optional count limit.

    Parameters
    ----------
    plist_func : Callable
        Function that returns paginated results
    count : int, optional
        Maximum number of items to retrieve
    **kwargs
        Additional arguments to pass to plist_func

    Returns
    -------
    list
        List of items from the paginated result
    """
    if count is not None and count:
        kwargs = {"per_page": count, "page": 1} | kwargs
    else:
        kwargs = {"all": True} | kwargs

    return list(plist_func(**kwargs))


# See: https://python-gitlab.readthedocs.io/en/stable/api-usage.html
# See: https://docs.gitlab.com/ee/api/README.html
# See: https://docs.gitlab.com/ee/api/api_resources.html
class GitlabDevOpsAnalyzer(DevOpsAnalyzer):
    """
    GitLab-specific implementation of the DevOps analyzer.

    This class provides concrete implementations for all DevOps operations
    specific to GitLab, including authentication, user/group/project management,
    repository operations, and statistics gathering. It uses the python-gitlab
    library to interact with GitLab's REST API.

    Attributes:
        IMPORT_EXPORT_STATUS_SUCCESS: Status indicating successful import/export
        IMPORT_EXPORT_STATUS_FAILED: Status indicating failed import/export
        IMPORT_EXPORT_STATUS_NONE: Status indicating no import/export operation
    """

    # See: https://docs.gitlab.com/ce/api/project_import_export.html#export-status
    # See: https://docs.gitlab.com/ce/api/project_import_export.html#import-status
    IMPORT_EXPORT_STATUS_SUCCESS: str = "finished"
    IMPORT_EXPORT_STATUS_FAILED: str = "failed"
    IMPORT_EXPORT_STATUS_NONE: str = "none"

    def __init__(
            self,
            lynceus_session: LynceusSession,
            uri: str,
            token: str,
            lynceus_exchange: LynceusExchange,
    ):
        """
        Initialize the GitLab DevOps analyzer.

        Parameters
        ----------
        lynceus_session : LynceusSession
            The Lynceus session instance
        uri : str
            The GitLab instance URI
        token : str
            Personal access token for GitLab authentication
        lynceus_exchange : LynceusExchange
            Exchange instance for data communication
        """
        super().__init__(lynceus_session, uri, "gitlab", lynceus_exchange)
        self._manager = gitlab.Gitlab(uri, private_token=token)
        self.__current_token: dict | None = None

    # The following methods are only for uniformity and coherence.
    def _extract_user_info(self, user) -> LynceusDict:
        # Extracts information which are always available.
        user_info = {
            "id": user.id,
            "name": user.name,
            "login": user.username,
            "username": user.username,
        }

        # Extracts extra information if available.
        for extra_info_key, extra_info_attr in (
                ("e-mail", "public_email"),
                ("avatar_url", "avatar_url"),
                ("bio", "bio"),
        ):
            value = (
                user.attributes[extra_info_attr]
                if extra_info_attr in user.attributes
                else self.INFO_UNDEFINED
            )
            user_info.update({extra_info_key: value})

        return LynceusDict(user_info)

    def _extract_group_info(self, group) -> LynceusDict:
        return LynceusDict(
            {"id": group.id, "name": group.name, "path": group.full_path}
        )

    def _extract_project_info(self, project) -> LynceusDict:
        return LynceusDict(
            {
                "id": project.id,
                "name": project.name,
                "path": project.path_with_namespace,
                "web_url": project.web_url,
            }
        )

    def _extract_member_info(self, member) -> LynceusDict:
        member_info = {
            "id": member.id,
            "name": member.name,
            "login": member.username,
            "username": member.username,
            "state": member.state,
        }

        # Extracts extra information if available.
        for extra_info_key, extra_info_attr in ("parent_id", "group_id"), (
                "parent_id",
                "project_id",
        ):
            value = (
                member.attributes[extra_info_attr]
                if extra_info_attr in member.attributes
                else None
            )
            if value:
                member_info.update({extra_info_key: value})

        return LynceusDict(member_info)

    def _extract_issue_event_info(self, issue_event, **kwargs) -> LynceusDict:
        return LynceusDict(
            {
                "id": issue_event.id,
                "issue_id": issue_event.target_iid,
                "action": issue_event.action_name,
                "target_type": issue_event.target_type,
                "created_at": parse_string_to_datetime(
                    datetime_str=issue_event.created_at
                ),
                "author": issue_event.author["name"],
                "title": issue_event.target_title,
                "issue_web_url": kwargs["project_web_url"] + f"/-/issues/{issue_event.target_iid}",
                # N.B.: project information is unable, and must be added by caller via kwargs.
            }
            | kwargs
        )

    def _extract_commit_info(self, commit) -> LynceusDict:
        return LynceusDict(
            {
                "id": commit.id,
                "short_id": commit.short_id,
                "parent_ids": commit.parent_ids,
                "message": commit.message,
                "created_at": commit.created_at,
                "author_name": commit.author_name,
                "author_email": commit.author_email,
                "committer_name": commit.committer_name,
                "committer_email": commit.committer_email,
            }
        )

    def _extract_branch_info(self, branch) -> LynceusDict:
        return LynceusDict(
            {
                "name": branch.name,
                "merged": branch.merged,
                "commit_id": branch.commit["id"],
                "commit_short_id": branch.commit["short_id"],
                "created_at": parse_string_to_datetime(
                    datetime_str=branch.commit["created_at"]
                ),
                # Not available for other DevOps: 'project_id': branch.project_id,
            }
        )

    def _extract_tag_info(self, tag) -> LynceusDict:
        return LynceusDict(
            {
                "name": tag.name,
                "commit_id": tag.commit["id"],
                "commit_short_id": tag.commit["short_id"],
                "created_at": parse_string_to_datetime(
                    datetime_str=tag.commit["created_at"]
                ),
                # Not available for other DevOps: 'project_id': branch.project_id,
            }
        )

    # The following methods are only performing read access on DevOps backend.
    @gitlab_exception_handler
    def authenticate(self):
        """
        Authenticate with the GitLab instance using the configured credentials.

        Perform authentication with the GitLab API using the access token
        or other credentials provided during initialization.
        """
        self._manager.auth()

    @gitlab_exception_handler
    def _do_get_current_user(self):
        return self._manager.user

    @gitlab_exception_handler
    def _do_get_user_without_cache(
            self, *, username: str = None, email: str = None, **kwargs
    ):
        if "user_id" in kwargs:
            return self._manager.users.get(id=kwargs["user_id"])

        # Note: there is still no API route to search an user directly
        #  from username or email (but only from only known id)
        #  - https://python-gitlab.readthedocs.io/en/stable/gl_objects/users.html#users-examples
        #  - https://docs.gitlab.com/api/users/
        users = self._manager.users.list(
            iterator=True, username=username, email=email, **kwargs
        )
        try:
            user = next(users)
            self._logger.debug(
                f'Successfully lookup user with parameters: "{username=}"/"{email=}".'
            )
            return user
        except StopIteration:
            # pylint: disable=raise-missing-from
            raise NameError(
                f'User "{username=}"/"{email=}" has not been found with specified parameters ({kwargs if kwargs else "none"}).'
            )

    @gitlab_exception_handler
    def _do_get_groups(self, *, count: int | None = None, **kwargs):
        return get_list_from_paginated_and_count(
            self._manager.groups.list, count, **kwargs
        )

    @gitlab_exception_handler
    def _do_get_group_without_cache(self, *, full_path: str, **kwargs):
        groups = self._manager.groups.list(
            iterator=True, search=full_path, search_namespaces=True, **kwargs
        )
        if not groups:
            raise NameError(
                f'Group "{full_path}" has not been found with specified parameters ({kwargs if kwargs else "none"}).'
            )

        # Checks if match must be exact (which is now the case by default ... check if has been defined to False manually).
        if not bool(kwargs.get("exact_match", True)):
            if len(groups) > 1:
                self._logger.warning(
                    f'There are more than one group matching requested path "{full_path}"'
                    + f'(add "exact_match" parameter to ensure getting only one group): {groups} '
                )
            return next(groups)

        try:
            group = next(
                filter(
                    lambda grp: str.lower(grp.full_path) == str.lower(full_path), groups
                )
            )
            self._logger.debug(
                f'Successfully lookup group with full path "{full_path}".'
            )
            return group
        except StopIteration:
            # pylint: disable=raise-missing-from
            raise NameError(
                f'Group "{full_path}" has not been found with specified parameters ({kwargs if kwargs else "none"}).'
                + f" Maybe you are looking for one of the following paths: {[group.full_path for group in groups]}"
            )

    @gitlab_exception_handler
    def _do_get_projects(self, *, count: int | None = None, **kwargs):
        return get_list_from_paginated_and_count(
            self._manager.projects.list, count, **kwargs
        )

    @gitlab_exception_handler
    def _do_get_project_without_cache(self, *, full_path: str, **kwargs):
        try:
            project = self._manager.projects.get(
                full_path, search_namespaces=True, **kwargs
            )
            self._logger.debug(
                f'Successfully lookup project with full path "{full_path}".'
            )
            return project
        except gitlab.exceptions.GitlabError as error:
            if error.response_code != 404:
                # Lets the @gitlab_exception_handler manages the exception.
                raise

            # pylint: disable=raise-missing-from
            raise NameError(
                f'Project "{full_path}" has not been found with specified parameters ({kwargs if kwargs else "none"}).'
            )

    @gitlab_exception_handler
    def __get_current_token(self):
        """
        Get information about the current personal access token.

        Returns
        -------
        dict
            Token information including ID, name, scopes, and expiration
        """
        if not self.__current_token:
            # Sample: {'id': 60, 'name': 'Lynceus CI/CD', 'revoked': False, 'created_at': '2020-10-22T15:50:13.516Z',
            #           'scopes': ['api', 'admin_mode'], 'user_id': 5, 'last_used_at': '2023-04-12T09:22:19.495Z',
            #           'active': True, 'expires_at': None}
            self.__current_token = self._manager.personal_access_tokens.get("self")

        return self.__current_token

    @gitlab_exception_handler
    # pylint: disable=too-many-return-statements
    def check_permissions_on_project(
            self,
            *,
            full_path: str,
            get_metadata: bool,
            pull: bool,
            push: bool = False,
            maintain: bool = False,
            admin: bool = False,
            **kwargs,
    ):
        """
        Check user permissions on a specific GitLab project.

        Verify that the authenticated user has the requested permissions
        on the specified project by checking their access level and membership.

        Parameters
        ----------
        full_path : str
            Full path to the GitLab project (e.g., 'group/project')
        get_metadata : bool
            Whether metadata access is required
        pull : bool
            Whether pull/read access is required
        push : bool, optional
            Whether push/write access is required (default: False)
        maintain : bool, optional
            Whether maintainer access is required (default: False)
        admin : bool, optional
            Whether admin access is required (default: False)
        **kwargs
            Additional project lookup arguments

        Returns
        -------
        bool
            Permission check results with granted access levels

        Raises
        ------
        PermissionError
            If required permissions are not granted
        """
        try:
            # First of all, checks get_metadata permission which is required anyway.
            _ = self._do_get_project(full_path=full_path, **kwargs)

            # From here, we consider get_metadata permission is OK.

            # See: https://docs.gitlab.com/ee/user/permissions.html
            # See: https://gitlab.com/gitlab-org/gitlab/-/blob/e97357824bedf007e75f8782259fe07435b64fbb/lib/gitlab/access.rb#L12-18

            # Retrieves current use, and corresponding membership information if any, for specified project.
            current_user = self._do_get_current_user()
            members = self._do_get_project_members(full_path=full_path, recursive=True)

            member = next(filter(lambda grp: grp.id == current_user.id, members))
            access_level = member.access_level

            # According to my tests, required role (aka access_level):
            #  - at least REPORTER role to get access to repository metadata (name, tags, branches ...)
            #  - at least DEVELOPER role to be able to pull the repository (the read_repository scope is NOT enough here)
            #  - at least MAINTAINER role to get access to project statistics

            # Checks scopes of the token.
            token = self.__get_current_token()
            token_scopes = token.scopes
            api_scope = "api" in token_scopes
            admin_scope = "admin" in token_scopes
            read_repository_scope = "read_repository" in token_scopes
            write_repository_scope = "write_repository" in token_scopes

            if pull and (
                    (not api_scope and not read_repository_scope)
                    or access_level < AccessLevel.DEVELOPER
            ):
                return False

            if push and (
                    (not api_scope and not write_repository_scope)
                    or access_level < AccessLevel.DEVELOPER
            ):
                return False

            if maintain and (
                    (not api_scope and not write_repository_scope)
                    or access_level < AccessLevel.MAINTAINER
            ):
                return False

            if admin and (
                    (not api_scope and not admin_scope) or access_level < AccessLevel.OWNER
            ):
                return False

            # All permission checks OK.
            return True
        except NameError:
            # Returns True if there were NO permission at all to check ...
            return (
                    not get_metadata
                    and not pull
                    and not push
                    and not maintain
                    and not admin
            )
        except StopIteration:
            # Returns True if there were NO more permission to check ...
            return not pull and not push and not maintain and not admin

    @gitlab_exception_handler
    def _do_get_project_commits(
            self, *, full_path: str, git_ref_name: str, count: int | None = None, **kwargs
    ):
        project = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(
            project.commits.list, count, ref_name=git_ref_name, **kwargs
        )

    @gitlab_exception_handler
    def _do_get_project_branches(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        project = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(project.branches.list, count, **kwargs)

    @gitlab_exception_handler
    def _do_get_project_tags(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        project = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(project.tags.list, count, **kwargs)

    @gitlab_exception_handler
    def _do_get_project_members(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        project = self._do_get_project(full_path=full_path, **kwargs)

        if not bool(kwargs.get("recursive", False)):
            return get_list_from_paginated_and_count(
                project.members.list, count, **kwargs
            )

        return get_list_from_paginated_and_count(
            project.members_all.list, count, **kwargs
        )

    @gitlab_exception_handler
    def _do_get_group_members(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        group = self._do_get_group(full_path=full_path, **kwargs)

        if not bool(kwargs.get("recursive", False)):
            return get_list_from_paginated_and_count(
                group.members.list, count, **kwargs
            )

        return get_list_from_paginated_and_count(
            group.members_all.list, count, **kwargs
        )

    @gitlab_exception_handler
    def _do_get_project_issue_events(
            self,
            *,
            full_path: str,
            action: str | None = None,
            from_date: datetime | None = None,
            to_date: datetime | None = None,
            count: int | None = None,
            **kwargs,
    ):
        # See: https://python-gitlab.readthedocs.io/en/stable/api/gitlab.v4.html?highlight=events#gitlab.v4.objects.ProjectEventManager
        # Object listing filters
        #   action => https://docs.gitlab.com/ee/user/profile/index.html#user-contribution-events
        #   target_type => https://docs.gitlab.com/ee/api/events.html#target-types
        #   sort
        project = self._do_get_project(full_path=full_path, **kwargs)

        # Adds filters if needed.
        if action:
            kwargs["action"] = action

        #   before & after => https://docs.gitlab.com/ee/api/events.html#date-formatting
        if from_date:
            kwargs["after"] = from_date.strftime("%Y-%m-%d")

        if to_date:
            kwargs["before"] = to_date.strftime("%Y-%m-%d")

        return get_list_from_paginated_and_count(
            project.events.list, count, target_type="issue", **kwargs
        )

    @gitlab_exception_handler
    def _do_get_project_issues(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        project = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(project.issues.list, count, **kwargs)

    @gitlab_exception_handler
    def _do_get_project_merge_requests(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        project = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(
            project.mergerequests.list, count, **kwargs
        )

    @gitlab_exception_handler
    def _do_get_project_milestones(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        project = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(
            project.milestones.list, count, **kwargs
        )

    @gitlab_exception_handler
    def __get_recursive_groups(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Recursively get all subgroups for a given group.

        Parameters
        ----------
        full_path : str
            Full path of the parent group
        count : int, optional
            Maximum number of groups to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of all groups including the parent and all recursive subgroups
        """
        # TODO: find a way to implement count properly.
        group = self._do_get_group(full_path=full_path, **kwargs)
        subgroups = get_list_from_paginated_and_count(
            group.subgroups.list, count, **kwargs
        )
        if not subgroups:
            return [group]
        return flatten(
            self.__get_recursive_groups(full_path=subgroup.full_path, **kwargs)
            for subgroup in subgroups
        )

    @gitlab_exception_handler
    def _do_get_group_projects(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        group = self._do_get_group(full_path=full_path, **kwargs)

        # Checks if recursive is requested.
        if not bool(kwargs.get("recursive", False)):
            project_list = get_list_from_paginated_and_count(
                group.projects.list, count, **kwargs
            )
        else:
            # TODO: find a way to implement count
            all_groups = {group} | set(
                self.__get_recursive_groups(full_path=full_path, **kwargs)
            )
            project_list = flatten(
                group.projects.list(all=True) for group in all_groups
            )

        return list(
            map(
                lambda gp: self._do_get_project(full_path=gp.path_with_namespace),
                project_list,
            )
        )

    @gitlab_exception_handler
    def _do_get_group_milestones(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        group = self._do_get_group(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(group.milestones.list, count, **kwargs)

    @gitlab_exception_handler
    def get_user_stats_commit_activity(
            self,
            *,
            group_full_path: str = None,
            project_full_path: str = None,
            since: datetime = None,
            keep_empty_stats: bool = False,
            count: int | None = None,
    ):
        """
        Get commit activity statistics for the authenticated user in GitLab.

        Parameters
        ----------
        group_full_path : str, optional
            Group path to limit statistics to
        project_full_path : str, optional
            Project path to include in statistics
        since : datetime, optional
            Start date for statistics (defaults to 365 days ago)
        keep_empty_stats : bool, optional
            Whether to include days with zero commits (default: False)
        count : int, optional
            Maximum number of projects to analyze

        Returns
        -------
        dict
            Mapping of dates to commit counts
        """
        # TODO: find a way to implement count
        # See: https://docs.gitlab.com/ee/api/project_statistics.html#get-the-statistics-of-the-last-30-days

        # Defines projects on which to perform statistics.
        if group_full_path is None:
            projects = self._do_get_projects(count=count)
        else:
            projects = self._do_get_group_projects(
                full_path=group_full_path, count=count
            )
            if project_full_path is not None:
                projects.append(self._do_get_project(full_path=project_full_path))

        # Defines threshold date.
        contributions_since: datetime = (
            since if since else datetime.now(tz=timezone.utc) - timedelta(days=365)
        )
        stats_user_commit_activity: dict[date, int] = defaultdict(int)
        for _project in projects:
            for commit_activity in _project.additionalstatistics.get().fetches["days"]:
                day_date = parse_string_to_datetime(
                    datetime_str=commit_activity["date"],
                    datetime_format=DATETIME_FORMAT_SHORT,
                )

                # Ignores oldest statistics.
                if day_date < contributions_since:
                    continue

                # Ignores 0 stats but if wanted.
                if not keep_empty_stats and not commit_activity["count"]:
                    continue

                stats_user_commit_activity[day_date.date()] += commit_activity["count"]

        return stats_user_commit_activity

    @gitlab_exception_handler
    # pylint: disable=unused-argument
    def get_user_contributions(
            self,
            *,
            since: datetime = None,
            keep_empty_stats: bool = False,
            count: int | None = None,
    ):
        """
        Get user contribution statistics (not implemented for GitLab).

        This method is not implemented for GitLab as the equivalent functionality
        is not readily available through the GitLab API.

        Parameters
        ----------
        since : datetime, optional
            Start date for contributions (unused)
        keep_empty_stats : bool, optional
            Whether to include empty statistics (unused) (default: False)
        count : int, optional
            Maximum number of projects to analyze (unused)

        Returns
        -------
        dict
            Empty dictionary
        """
        self._logger.warning(
            "get_user_contributions is not implemented yet for GitLab DevOps Analyzer"
        )
        return {}

    @gitlab_exception_handler
    def get_user_stats_code_frequency(self, *, count: int | None = None):
        """
        Get code frequency statistics (not implemented for GitLab).

        This method is not implemented for GitLab as the equivalent functionality
        is not readily available through the GitLab API.

        Parameters
        ----------
        count : int, optional
            Maximum number of projects to analyze (unused)

        Returns
        -------
        dict
            Empty dictionary
        """
        self._logger.warning(
            "get_user_stats_commit_activity is not implemented yet for GitLab DevOps Analyzer"
        )
        return {}

    @gitlab_exception_handler
    def _do_download_repository(
            self,
            *,
            project_full_path: str,
            dest_path: Path,
            reference: str = None,
            chunk_size: int = 1024,
            **kwargs,
    ):
        # See: https://docs.gitlab.com/ee/api/repositories.html#get-file-archive
        # See: https://github.com/python-gitlab/python-gitlab/blob/main/gitlab/v4/objects.py#L4465
        project = self._do_get_project(full_path=project_full_path, **kwargs)
        with open(dest_path, "wb") as dest_file:
            project.repository_archive(
                sha=reference,
                streamed=True,
                action=dest_file.write,
                chunk_size=chunk_size,
                **kwargs,
            )
