import tarfile
from datetime import datetime
from pathlib import Path

from lynceus.core.exchange.lynceus_exchange import LynceusExchange
from lynceus.core.lynceus import LynceusSession
from lynceus.core.lynceus_client import LynceusClientClass
from lynceus.lynceus_exceptions import LynceusError
from lynceus.utils.lynceus_dict import LynceusDict


# TODO: add accessrequests/permissions listing feature


# pylint: disable=too-many-public-methods
class DevOpsAnalyzer(LynceusClientClass):
    """
    Abstract base class for DevOps platform analyzers (GitLab, GitHub).

    This class provides a unified interface for interacting with different DevOps platforms,
    enabling read-only operations such as retrieving users, projects, groups, commits, and
    various statistics. It includes caching mechanisms for improved performance and defines
    abstract methods that must be implemented by platform-specific subclasses.

    The class supports:
    - User, group, and project management
    - Repository operations (branches, tags, commits)
    - Issue and merge request tracking
    - Statistics and analytics
    - Repository downloads
    - Permission checks

    Attributes:
        STATUS_ACTIVE: Constant representing active status
        INFO_UNDEFINED: Constant representing undefined information
        CACHE_USER_TYPE: Cache type identifier for users
        CACHE_GROUP_TYPE: Cache type identifier for groups
        CACHE_PROJECT_TYPE: Cache type identifier for projects
    """

    STATUS_ACTIVE: str = "active"
    INFO_UNDEFINED: str = "undefined"

    CACHE_USER_TYPE: str = "user"
    CACHE_GROUP_TYPE: str = "group"
    CACHE_PROJECT_TYPE: str = "project"

    def __init__(
            self,
            lynceus_session: LynceusSession,
            uri: str,
            logger_name: str,
            lynceus_exchange: LynceusExchange | None,
    ):
        """
        Initialize the DevOps analyzer.

        Parameters
        ----------
        lynceus_session : LynceusSession
            The Lynceus session instance
        uri : str
            The URI of the DevOps platform
        logger_name : str
            Name for the logger instance
        lynceus_exchange : LynceusExchange
            Exchange instance for data communication
        """
        super().__init__(lynceus_session, logger_name, lynceus_exchange)
        self._uri: str = uri

        # Initializes cache system.
        self.__cache: dict[str, dict[tuple, object]] = {
            self.CACHE_USER_TYPE: {},
            self.CACHE_GROUP_TYPE: {},
            self.CACHE_PROJECT_TYPE: {},
        }

    # The following methods are only for uniformity and coherence.
    def _extract_user_info(self, user) -> LynceusDict:
        """
        Extract standardized user information from platform-specific user object.

        Parameters
        ----------
        user : object
            Platform-specific user object

        Returns
        -------
        LynceusDict
            Standardized user information dictionary

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _extract_group_info(self, group) -> LynceusDict:
        """
        Extract standardized group information from platform-specific group object.

        Parameters
        ----------
        group : object
            Platform-specific group object

        Returns
        -------
        LynceusDict
            Standardized group information dictionary

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _extract_project_info(self, project) -> LynceusDict:
        """
        Extract standardized project information from platform-specific project object.

        Parameters
        ----------
        project : object
            Platform-specific project object

        Returns
        -------
        LynceusDict
            Standardized project information dictionary

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _extract_member_info(self, member) -> LynceusDict:
        """
        Extract standardized member information from platform-specific member object.

        Parameters
        ----------
        member : object
            Platform-specific member object

        Returns
        -------
        LynceusDict
            Standardized member information dictionary

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _extract_issue_event_info(self, issue_event, **kwargs) -> LynceusDict:
        """
        Extract standardized issue event information from platform-specific issue event object.

        Parameters
        ----------
        issue_event : object
            Platform-specific issue event object
        **kwargs
            Additional context information (e.g., project metadata)

        Returns
        -------
        LynceusDict
            Standardized issue event information dictionary

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _extract_commit_info(self, commit) -> LynceusDict:
        """
        Extract standardized commit information from platform-specific commit object.

        Parameters
        ----------
        commit : object
            Platform-specific commit object

        Returns
        -------
        LynceusDict
            Standardized commit information dictionary

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _extract_branch_info(self, branch) -> str:
        """
        Extract standardized branch information from platform-specific branch object.

        Parameters
        ----------
        branch : object
            Platform-specific branch object

        Returns
        -------
        str
            Standardized branch information

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _extract_tag_info(self, tag) -> str:
        """
        Extract standardized tag information from platform-specific tag object.

        Parameters
        ----------
        tag : object
            Platform-specific tag object

        Returns
        -------
        str
            Standardized tag information

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def __get_from_cache(self, *, cache_type: str, cache_key: tuple, log_access: bool = True) -> object | None:
        """
        Retrieve an object from the internal cache.

        Parameters
        ----------
        cache_type : str
            Type of cache (user, group, or project)
        cache_key : tuple
            Key to look up in the cache
        log_access : bool, optional
            Whether to log the cache access (default: True)

        Returns
        -------
        object or None
            The cached object if found, None otherwise
        """
        if log_access:
            self._logger.debug(
                f'Checking if an instance is registered in cache, for type "{cache_type}" and key "{cache_key}".'
            )
        return self.__cache[cache_type].get(cache_key)

    def __register_in_cache(self, *, cache_type: str, cache_key: tuple, obj: object, obj_short: LynceusDict):
        """
        Register an object in the internal cache.

        Parameters
        ----------
        cache_type : str
            Type of cache (user, group, or project)
        cache_key : tuple
            Key to store the object under
        obj : object
            The complete object to cache
        obj_short : object
            Short representation of the object for logging
        """
        # Safe-guard: checks if it has already been registered in cache.
        from_cache = self.__get_from_cache(
            cache_type=cache_type, cache_key=cache_key, log_access=False
        )
        if from_cache:
            self._logger.warning(
                f'An instance of type "{cache_type}" has already been registered in cache, for key "{cache_key}". It will be overridden.'
            )

        self._logger.debug(
            f'Registering a complete/long instance of type "{cache_type}" in cache, for key "{cache_key}", whose short version is: "{obj_short}".'
        )
        self.__cache[cache_type][cache_key] = obj

    # The following methods are only performing read access on DevOps backend.
    def authenticate(self):
        """
        Authenticate with the DevOps platform.

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _do_get_current_user(self):
        """
        Get the current authenticated user from the platform.

        Returns
        -------
        object
            Platform-specific user object

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_current_user(self):
        """
        Get standardized information about the current authenticated user.

        Returns
        -------
        LynceusDict
            Standardized current user information
        """
        self._logger.debug("Retrieving current user information.")
        user = self._do_get_current_user()

        return self._extract_user_info(user)

    def _do_get_user_without_cache(
            self, *, username: str = None, email: str = None, **kwargs
    ):
        """
        Get a user from the platform without using cache.

        Parameters
        ----------
        username : str, optional
            Username to search for
        email : str, optional
            Email to search for
        **kwargs
            Additional search parameters

        Returns
        -------
        object
            Platform-specific user object

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _do_get_user(self, *, username: str = None, email: str = None, **kwargs):
        """
        Get a user from the platform with caching support.

        Parameters
        ----------
        username : str, optional
            Username to search for
        email : str, optional
            Email to search for
        **kwargs
            Additional search parameters

        Returns
        -------
        object
            Platform-specific user object (from cache or fresh)
        """
        # Checks if available in cache.
        cache_key: tuple = (username, email)
        user = self.__get_from_cache(
            cache_type=self.CACHE_USER_TYPE, cache_key=cache_key
        )

        # Retrieves it if not available in cache.
        if not user:
            user = self._do_get_user_without_cache(
                username=username, email=email, **kwargs
            )

            # Registers in cache.
            self.__register_in_cache(
                cache_type=self.CACHE_USER_TYPE,
                cache_key=cache_key,
                obj=user,
                obj_short=self._extract_user_info(user),
            )

        return user

    def get_user(self, *, username: str = None, email: str = None, **kwargs):
        """
        Get standardized information about a specific user.

        Parameters
        ----------
        username : str, optional
            Username to search for
        email : str, optional
            Email to search for
        **kwargs
            Additional search parameters

        Returns
        -------
        LynceusDict
            Standardized user information
        """
        self._logger.debug(f'Retrieving user "{username=}" with "{email}" ({kwargs=}).')
        user = self._do_get_user(username=username, email=email, **kwargs)
        return self._extract_user_info(user)

    def _do_get_groups(self, *, count: int | None = None, **kwargs):
        """
        Get groups from the platform.

        Parameters
        ----------
        count : int, optional
            Maximum number of groups to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific group objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_groups(self, *, count: int | None = None, **kwargs):
        """
        Get standardized information about groups.

        Parameters
        ----------
        count : int, optional
            Maximum number of groups to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        List[LynceusDict]
            List of standardized group information
        """
        self._logger.debug(f"Retrieving groups ({count=}; {kwargs=}).")
        groups = self._do_get_groups(count=count, **kwargs)
        return [self._extract_group_info(group) for group in groups]

    def _do_get_group_without_cache(self, *, full_path: str, **kwargs):
        """
        Get a group from the platform without using cache.

        Parameters
        ----------
        full_path : str
            Full path of the group
        **kwargs
            Additional search parameters

        Returns
        -------
        object
            Platform-specific group object

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _do_get_group(self, *, full_path: str, **kwargs):
        """
        Get a group from the platform with caching support.

        Parameters
        ----------
        full_path : str
            Full path of the group
        **kwargs
            Additional search parameters

        Returns
        -------
        object
            Platform-specific group object (from cache or fresh)
        """
        # Checks if available in cache.
        cache_key: tuple = (full_path,)
        group = self.__get_from_cache(
            cache_type=self.CACHE_GROUP_TYPE, cache_key=cache_key
        )

        # Retrieves it if not available in cache.
        if not group:
            group = self._do_get_group_without_cache(full_path=full_path, **kwargs)

            # Registers in cache.
            self.__register_in_cache(
                cache_type=self.CACHE_GROUP_TYPE,
                cache_key=cache_key,
                obj=group,
                obj_short=self._extract_group_info(group),
            )

        return group

    def get_group(self, *, full_path: str, **kwargs):
        """
        Get standardized information about a specific group.

        Parameters
        ----------
        full_path : str
            Full path of the group
        **kwargs
            Additional search parameters

        Returns
        -------
        LynceusDict
            Standardized group information
        """
        self._logger.debug(f'Retrieving group "{full_path=}" ({kwargs=}).')
        group = self._do_get_group(full_path=full_path, **kwargs)
        return self._extract_group_info(group)

    def _do_get_projects(self, *, count: int | None = None, **kwargs):
        """
        Get projects from the platform.

        Parameters
        ----------
        count : int, optional
            Maximum number of projects to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific project objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_projects(self, *, count: int | None = None, **kwargs):
        """
        Get standardized information about projects.

        Parameters
        ----------
        count : int, optional
            Maximum number of projects to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        List[LynceusDict]
            List of standardized project information
        """
        self._logger.debug(f"Retrieving projects ({count=}; {kwargs=}).")
        projects = self._do_get_projects(count=count, **kwargs)
        return [self._extract_project_info(project) for project in projects]

    def _do_get_project_without_cache(self, *, full_path: str, **kwargs):
        """
        Get a project from the platform without using cache.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        **kwargs
            Additional search parameters

        Returns
        -------
        object
            Platform-specific project object

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def _do_get_project(self, *, full_path: str, **kwargs):
        """
        Get a project from the platform with caching support.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        **kwargs
            Additional search parameters

        Returns
        -------
        object
            Platform-specific project object (from cache or fresh)
        """
        # Checks if available in cache.
        cache_key: tuple = (full_path,)
        project = self.__get_from_cache(
            cache_type=self.CACHE_PROJECT_TYPE, cache_key=cache_key
        )

        # Retrieves it if not available in cache.
        if not project:
            project = self._do_get_project_without_cache(full_path=full_path, **kwargs)

            # Registers in cache.
            self.__register_in_cache(
                cache_type=self.CACHE_PROJECT_TYPE,
                cache_key=cache_key,
                obj=project,
                obj_short=self._extract_project_info(project),
            )

        return project

    def get_project(self, *, full_path: str, **kwargs):
        """
        Get standardized information about a specific project.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        **kwargs
            Additional search parameters

        Returns
        -------
        LynceusDict
            Standardized project information
        """
        self._logger.debug(f'Retrieving project "{full_path=}" ({kwargs=}).')
        project = self._do_get_project(full_path=full_path, **kwargs)
        return self._extract_project_info(project)

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
        Check permissions of authenticated user on specific project.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        get_metadata : bool
            Check 'get project metadata' permission
        pull : bool
            Check 'pull' permission
        push : bool, optional
            Check 'push' permission (default: False)
        maintain : bool, optional
            Check 'maintain' permission (default: False)
        admin : bool, optional
            Check 'admin' permission (default: False)
        **kwargs
            Optional additional parameters

        Returns
        -------
        bool
            True if the authenticated user has requested permission, False otherwise
        """
        raise NotImplementedError()

    def _do_get_project_members(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get project members from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of members to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific member objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_project_commits(
            self, *, full_path: str, git_ref_name: str, count: int | None = None, **kwargs
    ):
        """
        Get standardized information about project commits.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        git_ref_name : str
            Git reference name (branch, tag, or commit)
        count : int, optional
            Maximum number of commits to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        List[LynceusDict]
            List of standardized commit information
        """
        self._logger.debug(
            f'Retrieving commits from git_reference "{git_ref_name}" of project "{full_path}" ({count=}; {kwargs=}).'
        )
        commits = self._do_get_project_commits(
            full_path=full_path, git_ref_name=git_ref_name, count=count, **kwargs
        )
        return [self._extract_commit_info(commit) for commit in commits]

    def _do_get_project_commits(
            self, *, full_path: str, git_ref_name: str, count: int | None = None, **kwargs
    ):
        """
        Get project commits from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        git_ref_name : str
            Git reference name (branch, tag, or commit)
        count : int, optional
            Maximum number of commits to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific commit objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_project_branches(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get standardized information about project branches.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of branches to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        List[LynceusDict]
            List of standardized branch information
        """
        self._logger.debug(
            f'Retrieving branches of project "{full_path=}" ({count=}; {kwargs=}).'
        )
        branches = self._do_get_project_branches(
            full_path=full_path, count=count, **kwargs
        )
        return [self._extract_branch_info(branch) for branch in branches]

    def _do_get_project_branches(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get project branches from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of branches to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific branch objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_project_tags(self, *, full_path: str, count: int | None = None, **kwargs):
        """
        Get standardized information about project tags.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of tags to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        List[LynceusDict]
            List of standardized tag information
        """
        self._logger.debug(
            f'Retrieving tags of project "{full_path=}" ({count=}; {kwargs=}).'
        )
        tags = self._do_get_project_tags(full_path=full_path, count=count, **kwargs)
        return [self._extract_tag_info(tag) for tag in tags]

    def _do_get_project_tags(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get project tags from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of tags to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific tag objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_project_members(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get standardized information about project members.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of members to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        List[LynceusDict]
            List of standardized member information
        """
        self._logger.debug(
            f'Retrieving members of project "{full_path=}" ({count=}; {kwargs=}).'
        )
        project_members = self._do_get_project_members(
            full_path=full_path, count=count, **kwargs
        )
        return [self._extract_member_info(member) for member in project_members]

    def _do_get_group_members(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get group members from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the group
        count : int, optional
            Maximum number of members to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific member objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_group_members(self, *, full_path: str, count: int | None = None, **kwargs):
        """
        Return all members of group (aka Organization).

        Parameters
        ----------
        full_path : str
            Full path of the group (including namespace)
        count : int, optional
            Maximum number of members to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        List[LynceusDict]
            List of standardized member information
        """
        self._logger.debug(
            f'Retrieving members of group "{full_path=}" ({count=}; {kwargs=}).'
        )
        members = self._do_get_group_members(full_path=full_path, count=count, **kwargs)
        return [self._extract_member_info(member) for member in members]

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
        """
        Get project issue events from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        action : str, optional
            Issue event action to filter on
        from_date : datetime, optional
            Datetime from which to consider issue events
        to_date : datetime, optional
            Datetime until which to consider issue events
        count : int, optional
            Maximum number of events to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific issue event objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_project_issue_events(
            self,
            *,
            full_path: str,
            action: str | None = None,
            from_date: datetime | None = None,
            to_date: datetime | None = None,
            count: int | None = None,
            **kwargs,
    ):
        """
        Return project issue events filtered according to specified parameters.

        Parameters
        ----------
        full_path : str
            Path of the project (including namespace)
        action : str, optional
            Issue event action to filter on, most of them are common to DevOps.
            See GitLab specs: https://docs.gitlab.com/ee/user/profile/index.html#user-contribution-events
            See GitHub specs: https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types#event-payload-object-6
        from_date : datetime, optional
            Datetime from which to consider issue events
        to_date : datetime, optional
            Datetime until which to consider issue events
        count : int, optional
            Maximum number of events to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        List[LynceusDict]
            Filtered issue events of the project
        """
        self._logger.debug(
            f'Retrieving issue events of project "{full_path=}" ({action=}; {from_date=}; {to_date=}; {count=}; {kwargs=}).'
        )
        project_events = self._do_get_project_issue_events(
            full_path=full_path,
            action=action,
            from_date=from_date,
            to_date=to_date,
            count=count,
            **kwargs,
        )

        # Important: in Github there is no project (either id or name) information attached to event, and on Gitlab there is only the id.
        # To return consistent result, we add both here.
        project = self.get_project(full_path=full_path)
        project_metadata = {
            "project_id": project.id,
            "project_name": project.name,
            "project_web_url": project.web_url,
        }

        return [
            self._extract_issue_event_info(event, **project_metadata)
            for event in project_events
        ]

    def _do_get_project_issues(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get project issues from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of issues to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific issue objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_project_issues(self, *, full_path: str, count: int | None = None, **kwargs):
        """
        Get all issues of a project.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of issues to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific issue objects
        """
        self._logger.debug(
            f'Retrieving issues of project "{full_path=}" ({count=}; {kwargs=}).'
        )
        return self._do_get_project_issues(full_path=full_path, count=count, **kwargs)

    def get_project_pull_requests(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get all pull requests of a project (alias for merge requests).

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of pull requests to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific pull/merge request objects
        """
        return self.get_project_merge_requests(
            full_path=full_path, count=count, **kwargs
        )

    def _do_get_project_merge_requests(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get project merge requests from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of merge requests to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific merge request objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_project_merge_requests(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get all merge requests of a project.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of merge requests to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific merge request objects
        """
        self._logger.debug(
            f'Retrieving merge/pull requests of project "{full_path=}" ({count=}; {kwargs=}).'
        )
        return self._do_get_project_merge_requests(
            full_path=full_path, count=count, **kwargs
        )

    def _do_get_project_milestones(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get project milestones from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of milestones to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific milestone objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_project_milestones(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get all milestones (sprints) of a project.

        Parameters
        ----------
        full_path : str
            Full path of the project (including namespace)
        count : int, optional
            Maximum number of milestones to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific milestone objects
        """
        self._logger.debug(
            f'Retrieving milestones of project "{full_path=}" ({count=}; {kwargs=}).'
        )
        return self._do_get_project_milestones(
            full_path=full_path, count=count, **kwargs
        )

    def _do_get_group_projects(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get all projects of a group from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the group
        count : int, optional
            Maximum number of projects to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific project objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_group_projects(self, *, full_path: str, count: int | None = None, **kwargs):
        """
        Get standardized information about all projects in a group.

        Parameters
        ----------
        full_path : str
            Full path of the group
        count : int, optional
            Maximum number of projects to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        List[LynceusDict]
            List of standardized project information
        """
        self._logger.debug(
            f'Retrieving projects of group "{full_path=}" ({count=}; {kwargs=}).'
        )
        projects = self._do_get_group_projects(
            full_path=full_path, count=count, **kwargs
        )
        return [self._extract_project_info(project) for project in projects]

    def _do_get_group_milestones(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get group milestones from the platform.

        Parameters
        ----------
        full_path : str
            Full path of the group
        count : int, optional
            Maximum number of milestones to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific milestone objects

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_group_milestones(
            self, *, full_path: str, count: int | None = None, **kwargs
    ):
        """
        Get all milestones (sprints) of a group.

        Parameters
        ----------
        full_path : str
            Full path of the group
        count : int, optional
            Maximum number of milestones to retrieve
        **kwargs
            Additional filtering parameters

        Returns
        -------
        list
            List of platform-specific milestone objects
        """
        self._logger.debug(
            f'Retrieving milestones of group "{full_path=}" ({count=}; {kwargs=}).'
        )
        return self._do_get_group_milestones(full_path=full_path, count=count, **kwargs)

    def get_user_stats_commit_activity(
            self,
            *,
            group_full_path: str = None,
            project_full_path: str = None,
            since: datetime | None = None,
            keep_empty_stats: bool = False,
            count: int | None = None,
    ):
        """
        Compute commit activity statistics for the authenticated user.

        Compute total statistics of all accessible projects of authenticated user,
        or all projects of specified group and/or of specified project.

        Parameters
        ----------
        group_full_path : str, optional
            Group path - statistics will be computed on all projects of this group
        project_full_path : str, optional
            Project path - statistics will be computed on this project
        since : datetime, optional
            Start date from which statistics must be computed
        keep_empty_stats : bool, optional
            Whether to include days with zero commits in results (default: False)
        count : int, optional
            Maximum number of projects to analyze

        Returns
        -------
        dict
            Dictionary mapping dates to commit counts

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_user_contributions(
            self,
            *,
            since: datetime = None,
            keep_empty_stats: bool = False,
            count: int | None = None,
    ):
        """
        Get user contribution statistics including additions, deletions, and commits.

        Parameters
        ----------
        since : datetime, optional
            Start date from which contributions must be computed
        keep_empty_stats : bool, optional
            Whether to include periods with zero contributions (default: False)
        count : int, optional
            Maximum number of projects to analyze

        Returns
        -------
        dict
            Dictionary mapping dates to contribution statistics

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def get_user_stats_code_frequency(self, *, count: int | None = None):
        """
        Get code frequency statistics showing additions and deletions over time.

        Parameters
        ----------
        count : int, optional
            Maximum number of projects to analyze

        Returns
        -------
        dict
            Dictionary mapping time periods to code frequency data

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def download_repository(
            self,
            *,
            project_full_path: str,
            dest_path: Path,
            reference: str = None,
            chunk_size: int = 1024,
            **kwargs,
    ):
        """
        Download a repository as an archive file.

        Parameters
        ----------
        project_full_path : str
            Full path of the project to download
        dest_path : Path
            Destination path for the downloaded archive
        reference : str, optional
            Git reference to download (branch, tag, commit). Uses default if None
        chunk_size : int, optional
            Size of chunks for streaming download (default: 1024 bytes)
        **kwargs
            Additional parameters for the download

        Raises
        ------
        ValueError
            If the git reference cannot be accessed or downloaded
        NameError
            If the project or reference is not found
        """
        self._logger.debug(
            f'Starting repository download of project "{project_full_path}" with git reference "{reference}", to destination file "{dest_path}" ...'
        )
        try:
            self._do_download_repository(
                project_full_path=project_full_path,
                dest_path=dest_path,
                reference=reference,
                chunk_size=chunk_size,
                **kwargs,
            )
            self._logger.info(
                f'Successfully downloaded repository of project "{project_full_path}" with git reference "{reference}", to destination file "{dest_path}".'
            )
        except NameError as exc:
            git_reference_str: str = (
                f'git reference "{reference}"'
                if reference is not None
                else "default git reference"
            )
            error_message: str = (
                f'Unable to download/access {git_reference_str} of project "{project_full_path}" (ensure your Token has permissions enough).'
            )
            self._logger.warning(error_message)
            raise ValueError(error_message) from exc

    def _do_download_repository(
            self,
            *,
            project_full_path: str,
            dest_path: Path,
            reference: str = None,
            chunk_size: int = 1024,
            **kwargs,
    ):
        """
        Platform-specific implementation for downloading a repository.

        Parameters
        ----------
        project_full_path : str
            Full path of the project to download
        dest_path : Path
            Destination path for the downloaded archive
        reference : str, optional
            Git reference to download (branch, tag, commit)
        chunk_size : int, optional
            Size of chunks for streaming download (default: 1024)
        **kwargs
            Additional platform-specific parameters

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError()

    def uncompress_tarball(
            self,
            *,
            tmp_dir: Path,
            tarball_path: Path,
            devops_project_downloaded: bool = True,
    ) -> Path:
        """
        Uncompress a tarball archive to a temporary directory.

        Parameters
        ----------
        tmp_dir : Path
            Temporary directory to extract the tarball into
        tarball_path : Path
            Path to the tarball file to extract
        devops_project_downloaded : bool, optional
            Whether this is a DevOps project download
            (affects validation of extracted structure) (default: True)

        Returns
        -------
        Path
            Path to the root directory of the extracted content

        Raises
        ------
        ValueError
            If the tarball structure is unexpected for a DevOps project
        """
        tarball_uncompress_path: Path = tmp_dir / Path("uncompress")
        self._logger.debug(
            f'Uncompressing the "{tarball_path}" tarball under "{tarball_uncompress_path}" ...'
        )
        try:
            with tarfile.open(tarball_path) as tarball:
                tarball.extractall(tarball_uncompress_path, filter='data')
            self._logger.info(f'Successfully uncompressed the "{tarball_path}" tarball ...')
        except Exception as exc:
            raise LynceusError(f'An error occured while uncompressing "{tarball_path}"') from exc

        # Retrieves the root directory of the project.
        files_in_root_uncompress_dir = list(tarball_uncompress_path.iterdir())
        if devops_project_downloaded:
            if len(files_in_root_uncompress_dir) > 1:
                raise ValueError(
                    f"Only one root directory is expected in downloaded repository tarball ({len(files_in_root_uncompress_dir)} found)."
                )

        return files_in_root_uncompress_dir[0]
