from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import github
import requests
from github import Github, GithubObject, Permissions, UnknownObjectException

from lynceus.core.exchange.lynceus_exchange import LynceusExchange
from lynceus.core.lynceus import LynceusSession
from lynceus.devops.devops_analyzer import DevOpsAnalyzer
from lynceus.utils import filter_kwargs
from lynceus.utils.lynceus_dict import LynceusDict


def github_exception_handler(func):
    """
    Decorator to handle GitHub-specific exceptions and convert them to standard exceptions.

    Parameters
    ----------
    func : callable
        Function to wrap with exception handling

    Returns
    -------
    callable
        Wrapped function that handles GitHub exceptions

    Raises
    ------
    PermissionError
        For 401/403 HTTP status codes
    NameError
        For 404 HTTP status codes
    """

    def func_wrapper(*args, **kwargs):
        """
        Internal wrapper function that handles GitHub API errors.

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
        except github.GithubException as error:
            # Intercepts permission error.
            if error.status in (401, 403):
                raise PermissionError(
                    "You don't have enough permission to perform this operation on Github."
                ) from error
            if error.status == 404:
                raise NameError("Unable to find requested Object.") from error

            # Raises any other error.
            raise

    return func_wrapper


def get_list_from_paginated_and_count(
        plist_func: Callable, count: int | None = None, need_state: bool = False, **kwargs
) -> list:
    """
    Helper function to get a list from GitHub paginated results with optional count limit.

    Parameters
    ----------
    plist_func : Callable
        Function that returns paginated results
    count : int, optional
        Maximum number of items to retrieve
    need_state : bool, optional
        Whether state parameter is required (default: False)
    **kwargs
        Additional arguments to pass to plist_func

    Returns
    -------
    list
        List of items from the paginated result, limited by count if specified
    """

    if need_state and "state" not in kwargs:
        kwargs = {"state": "all"} | kwargs

    plist = plist_func(**kwargs)

    # Tries to return cut list according to specified count.
    try:
        if count is not None and count:
            return list(plist[:count])
    except IndexError:
        # Ignores IndexError, to returns the complete list, like if count was never specified.
        pass

    # Returns the complete list.
    return list(plist)


# Cf. https://pygithub.readthedocs.io/en/latest/introduction.html
# Cf. https://docs.github.com/en/rest
# Cf. https://pygithub.readthedocs.io/en/stable/changes.html#breaking-changes for 2.x version breaking changes (mainly on datetime which are no more naive).
# Important:
#  - the Gitlab group notion corresponds to Organization notion on Github
#  - the Team notion of Github is NOT managed
class GithubDevOpsAnalyzer(DevOpsAnalyzer):
    """
    GitHub-specific implementation of the DevOps analyzer.

    This class provides concrete implementations for all DevOps operations
    specific to GitHub, including authentication, user/organization/repository management,
    and statistics gathering. It uses the PyGithub library to interact with GitHub's REST API.

    Important notes:
    - GitLab "groups" correspond to GitHub "organizations"
    - GitHub "teams" are not currently managed by this implementation
    - Some features may have different capabilities compared to GitLab
    """

    def __init__(
            self,
            lynceus_session: LynceusSession,
            uri: str,
            token: str,
            lynceus_exchange: LynceusExchange,
    ):
        """
        Initialize the GitHub DevOps analyzer.

        Parameters
        ----------
        lynceus_session : LynceusSession
            The Lynceus session instance
        uri : str
            The GitHub instance URI (for GitHub Enterprise) or None for github.com
        token : str
            Personal access token for GitHub authentication
        lynceus_exchange : LynceusExchange
            Exchange instance for data communication
        """
        super().__init__(lynceus_session, uri, "github", lynceus_exchange)
        kwargs = {"auth": github.Auth.Token(token), "timeout": 60}
        if uri:
            kwargs["base_url"] = uri

        self.__manager = Github(**kwargs)

    # The following methods are only for uniformity and coherence.
    def _extract_user_info(self, user) -> LynceusDict:
        return LynceusDict(
            {
                "id": user.id,
                "name": user.name,
                "login": user.login,
                "username": user.login,
                "e-mail": user.email,
                "avatar_url": user.avatar_url,
                "bio": user.bio,
            }
        )

    def _extract_group_info(self, group) -> LynceusDict:
        return LynceusDict(
            {
                "id": group.id,
                "name": group.name,
                # N.B.: it does not seem to be any "path" for Github organization
                "path": group.login,
            }
        )

    def _extract_project_info(self, project) -> LynceusDict:
        return LynceusDict(
            {
                "id": project.id,
                "name": project.name,
                "path": project.full_name,
                "web_url": project.html_url,
            }
        )

    def _extract_member_info(self, member) -> LynceusDict:
        # In Github the corresponding notion is 'contributors', and there is no 'status' information.
        return LynceusDict(
            {
                "id": member.id,
                "name": member.name,
                "login": member.login,
                "username": member.login,
                "parent_id": self.INFO_UNDEFINED,
                "state": self.STATUS_ACTIVE,
            }
        )

    def _extract_issue_event_info(self, issue_event, **kwargs) -> LynceusDict:
        return LynceusDict(
            {
                "id": issue_event.id,
                "issue_id": issue_event.issue.number,
                "action": issue_event.event,
                "target_type": "issue",
                "created_at": issue_event.created_at,
                "author": (
                    self.INFO_UNDEFINED
                    if not issue_event.actor
                    else issue_event.actor.name
                ),
                "title": issue_event.issue.title,
                "issue_web_url": kwargs["project_web_url"] + f"/issues/{issue_event.issue.number}",
                # N.B.: project information is unable, and must be added by caller via kwargs.
            }
            | kwargs
        )

    def _extract_commit_info(self, commit) -> LynceusDict:
        return LynceusDict(
            {
                "id": commit.sha,
                "short_id": commit.sha[:8],
                "parent_ids": [parent_commit.sha for parent_commit in commit.parents],
                "message": commit.raw_data["commit"].get("message"),
                "created_at": commit.commit.author.date,
                "author_name": commit.author.name,
                "author_email": commit.raw_data["commit"]["author"]["email"],
                "committer_name": commit.committer.name,
                "committer_email": commit.raw_data["commit"]["committer"]["email"],
            }
        )

    def _extract_branch_info(self, branch) -> LynceusDict:
        return LynceusDict(
            {
                "name": branch.name,
                "merged": len(branch.commit.parents) > 1,
                "commit_id": branch.commit.sha,
                "commit_short_id": branch.commit.sha[:8],
                "created_at": branch.commit.commit.author.date,
            }
        )

    def _extract_tag_info(self, tag) -> LynceusDict:
        return LynceusDict(
            {
                "name": tag.name,
                "commit_id": tag.commit.sha,
                "commit_short_id": tag.commit.sha[:8],
                "created_at": tag.commit.commit.author.date,
            }
        )

    # The following methods are only performing read access on DevOps backend.
    @github_exception_handler
    def authenticate(self):
        """
        Authenticate with the GitHub instance using the configured credentials.

        GitHub doesn't have a direct authentication endpoint, so this method
        validates the credentials by attempting to retrieve the current user
        information. If successful, the credentials are valid.
        """
        # There is no direct authentication with Github,
        #  simply retrieves the current user to test it.
        self._do_get_current_user()

    @github_exception_handler
    def _do_get_current_user(self):
        return self.__manager.get_user()

    # pylint: disable=unused-argument
    @github_exception_handler
    def _do_get_user_without_cache(
            self, *, username: str = None, email: str = None, **kwargs
    ):
        kwargs_filtered = filter_kwargs(args_filter=["user_id"], **kwargs)
        if kwargs_filtered:
            return self.__manager.get_user_by_id(**kwargs_filtered)

        return self.__manager.get_user(login=username)

    @github_exception_handler
    def _do_get_groups(self, *, count: int | None = None, **kwargs):
        return get_list_from_paginated_and_count(
            self.__manager.get_organizations, count, **kwargs
        )

    @github_exception_handler
    def _do_get_group_without_cache(self, *, full_path: str, **kwargs):
        # https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html?highlight=organization#github.Repository.Repository.organization
        # https://pygithub.readthedocs.io/en/latest/github_objects/Team.html?highlight=organization#github.Team.Team.organization
        # https://pygithub.readthedocs.io/en/latest/examples/MainClass.html?highlight=organization#get-organization-by-name

        try:
            # There are no optional kwargs available in this implementation.
            return self.__manager.get_organization(full_path)
        except UnknownObjectException as exception:
            raise NameError(f'Group "{full_path}" has not been found.') from exception

    @github_exception_handler
    def _do_get_projects(self, *, count: int | None = None, **kwargs):
        return get_list_from_paginated_and_count(
            self._do_get_current_user().get_repos, count, **kwargs
        )

    @github_exception_handler
    def _do_get_project_without_cache(self, *, full_path: str, **kwargs):
        try:
            # There are no optional kwargs available in this implementation.
            return self.__manager.get_repo(full_path)
        except UnknownObjectException as exception:
            raise NameError(
                f'Project/repository "{full_path}" has not been found.'
            ) from exception

    @github_exception_handler
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
        Check user permissions on a specific GitHub repository.

        Verify that the authenticated user has the requested permissions
        on the specified repository by checking the repository permissions object.

        Parameters
        ----------
        full_path : str
            Full path to the GitHub repository (e.g., 'owner/repo')
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
            Additional repository lookup arguments

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
            # Retrieves repository metadata (can lead to NameError if authenticated user has not enough permissions).
            repository = self._do_get_project(full_path=full_path, **kwargs)

            # From here, we consider get_metadata permission is OK.

            # Checks others permissions.
            permissions: Permissions = repository.permissions
            if pull and not permissions.pull:
                return False

            if push and not permissions.push:
                return False

            if maintain and not permissions.maintain:
                return False

            if admin and not permissions.admin:
                return False

            # All permissions check are OK.
            return True
        except (PermissionError, NameError):
            # Returns True if there were NO permission at all to check ...
            return (
                    not get_metadata
                    and not pull
                    and not push
                    and not maintain
                    and not admin
            )

    @github_exception_handler
    def _do_get_project_commits(
            self, *, full_path: str, git_ref_name: str, count: int | None = None, **kwargs
    ):
        repository = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(
            repository.get_commits, count, sha=git_ref_name or GithubObject.NotSet
        )

    @github_exception_handler
    def _do_get_project_branches(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        repository = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(repository.get_branches, count)

    @github_exception_handler
    def _do_get_project_tags(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        repository = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(repository.get_tags, count)

    @github_exception_handler
    def _do_get_project_members(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        repository = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(
            repository.get_contributors, count, **filter_kwargs(args_filter=["anon"], **kwargs)
        )

    @github_exception_handler
    def _do_get_group_members(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        # https://pygithub.readthedocs.io/en/latest/github_objects/Organization.html?highlight=member#github.Organization.Organization.get_members
        organization = self._do_get_group(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(
            organization.get_members, count, **filter_kwargs(args_filter=["role", "filter_"], **kwargs)
        )

    @github_exception_handler
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
        # https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types
        # https://docs.github.com/en/rest/activity/events

        repository = self._do_get_project(full_path=full_path, **kwargs)
        # Important: unfortunately it is NOT possible to filter on server side ...
        issue_events = get_list_from_paginated_and_count(
            repository.get_issues_events, count
        )

        # Filters issue event according to specified parameter(s).
        for issue_event in issue_events:
            if action and issue_event.event != action:
                continue

            if from_date and issue_event.created_at < from_date:
                # Stops the iteration since this issue event is the first being too old.
                break

            if to_date and issue_event.created_at > to_date:
                # Ignores this issue event.
                continue

            yield issue_event

    @github_exception_handler
    def _do_get_project_issues(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        repository = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(
            repository.get_issues, count, need_state=True, **kwargs
        )

    @github_exception_handler
    def _do_get_project_merge_requests(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        repository = self._do_get_project(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(
            repository.get_pulls, count, need_state=True, **kwargs
        )

    @github_exception_handler
    def _do_get_project_milestones(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        repository = self._do_get_project(full_path=full_path, **kwargs)
        milestone_list = get_list_from_paginated_and_count(
            repository.get_milestones, count, **kwargs
        )
        return [milestone.title for milestone in milestone_list]

    @github_exception_handler
    def _do_get_group_milestones(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        self._logger.warning(
            "There is no milestone on Organization under Github (you need to check milestones directly from a project/repository)."
        )
        return []

    @github_exception_handler
    def _do_get_group_projects(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        organization = self._do_get_group(full_path=full_path, **kwargs)
        return get_list_from_paginated_and_count(
            organization.get_repos, count, **filter_kwargs(args_filter=["type", "sort", "direction"], **kwargs)
        )

    @github_exception_handler
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
        Get commit activity statistics for the authenticated user in GitHub.

        Parameters
        ----------
        group_full_path : str, optional
            Organization path to limit statistics to (unused)
        project_full_path : str, optional
            Repository path to include in statistics (unused)
        since : datetime, optional
            Start date for statistics (defaults to 365 days ago)
        keep_empty_stats : bool, optional
            Whether to include days with zero commits (default: False)
        count : int, optional
            Maximum number of repositories to analyze

        Returns
        -------
        dict
            Mapping of dates to commit counts
        """
        # Cf. https://developer.github.com/v3/repos/statistics/#get-the-last-year-of-commit-activity-data

        # Defines threshold date.
        contributions_since: datetime = (
            since if since else datetime.now(tz=timezone.utc) - timedelta(days=365)
        )
        stats_user_commit_activity: dict[date, int] = defaultdict(int)
        for repo in self._do_get_projects(count=count):
            for commit_activity in repo.get_stats_commit_activity() or []:
                # TODO: define how to ensure it is the good author ?
                # if not current_user.name == commit_activity.author:
                #     print('TODO: remove // AUTHOR is NOT the same: ', current_user.name, commit_activity.author)
                #     continue

                # Ignores oldest statistics.
                if commit_activity.week < contributions_since:
                    continue

                # Ignores 0 stats but if wanted.
                if not keep_empty_stats and not commit_activity.total:
                    continue

                # For each stats.
                for day, commit_count in enumerate(commit_activity.days):
                    # Ignores 0 stats but if wanted.
                    if not keep_empty_stats and not commit_count:
                        continue

                    day_date = commit_activity.week + timedelta(days=day)
                    stats_user_commit_activity[day_date.date()] += commit_count

        return stats_user_commit_activity

    @github_exception_handler
    def get_user_contributions(
            self,
            *,
            since: datetime = None,
            keep_empty_stats: bool = False,
            count: int | None = None,
    ):
        """
        Get detailed user contribution statistics including additions, deletions, and commits.

        Parameters
        ----------
        since : datetime, optional
            Start date for contributions (defaults to 365 days ago)
        keep_empty_stats : bool, optional
            Whether to include periods with zero contributions (default: False)
        count : int, optional
            Maximum number of repositories to analyze

        Returns
        -------
        dict
            Mapping of dates to contribution statistics (additions, deletions, commits)
        """
        # Cf. https://developer.github.com/v3/repos/statistics/

        # Defines threshold date.
        contributions_since: datetime = (
            since if since else datetime.now(tz=timezone.utc) - timedelta(days=365)
        )
        current_user = self._do_get_current_user()
        stats_user_contributions: dict[date, dict[str, int]] = {}
        for repo in self._do_get_projects(count=count):
            for contribution in repo.get_stats_contributors() or []:
                if not current_user.name == contribution.author:
                    continue

                # For each stats.
                for stats in contribution.weeks:
                    # Ignores oldest statistics.
                    if stats.w < contributions_since:
                        continue

                    # Ignores 0 stats but if wanted.
                    if (
                            not keep_empty_stats
                            and not stats.a
                            and not stats.d
                            and not stats.c
                    ):
                        continue

                    try:
                        stats_map = stats_user_contributions[stats.w.date()]
                    except KeyError:
                        stats_map = {"additions": 0, "deletions": 0, "commits": 0}
                        stats_user_contributions[stats.w.date()] = stats_map

                    stats_map["additions"] += stats.a
                    stats_map["deletions"] += stats.d
                    stats_map["commits"] += stats.c

        return stats_user_contributions

    @github_exception_handler
    def get_user_stats_code_frequency(self, *, count: int | None = None):
        """
        Get code frequency statistics showing additions and deletions over time.

        Parameters
        ----------
        count : int, optional
            Maximum number of repositories to analyze

        Returns
        -------
        dict
            Mapping of time periods to code frequency data (additions, deletions)
        """
        stats_code_frequency = {}
        for repo in self._do_get_projects(count=count):
            for stats in repo.get_stats_code_frequency() or []:
                try:
                    stats_map = stats_code_frequency[stats.week]
                except KeyError:
                    stats_map = {"additions": 0, "deletions": 0}
                    stats_code_frequency[stats.week] = stats_map

                stats_map["additions"] += stats.additions
                stats_map["deletions"] += stats.deletions
        return stats_code_frequency

    @github_exception_handler
    def _do_download_repository(
            self,
            *,
            project_full_path: str,
            dest_path: Path,
            reference: str = None,
            chunk_size: int = 1024,
            **kwargs,
    ):
        # Cf. https://developer.github.com/v3/repos/contents/#get-archive-link
        # Cf. https://github.com/PyGithub/PyGithub/blob/main/github/Repository.py#L1535
        repository = self._do_get_project(full_path=project_full_path, **kwargs)
        url: str = repository.get_archive_link(
            archive_format="tarball", ref=reference or GithubObject.NotSet
        )
        with requests.get(url, stream=True, timeout=60) as reader:
            # Ensures specified reference exists.
            if reader.status_code == 404:
                raise NameError(
                    f'Reference "{reference}" does not exists for project/repository "{project_full_path}".'
                )

            with open(dest_path, "wb") as dest_file:
                for chunk in reader.iter_content(chunk_size=chunk_size):
                    dest_file.write(chunk)
