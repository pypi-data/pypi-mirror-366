from lynceus.core.exchange.lynceus_exchange import LynceusExchange
from lynceus.core.lynceus import LynceusSession
from lynceus.core.lynceus_client import LynceusClientClass
from .devops_analyzer import DevOpsAnalyzer
from .editor.devops_analyzer_editor import DevOpsAnalyzerEditor
from .editor.github_devops_analyzer_editor import GithubDevOpsAnalyzerEditor
from .editor.gitlab_devops_analyzer_editor import GitlabDevOpsAnalyzerEditor
from .github_devops_analyzer import GithubDevOpsAnalyzer
from .gitlab_devops_analyzer import GitlabDevOpsAnalyzer
from ..core.config import (
    CONFIG_AUTHENTICATION_KEY,
    CONFIG_PROJECT_CRED_SECRET,
    CONFIG_PROJECT_CRED_SECRET_GITHUB_DEFAULT,
    CONFIG_PROJECT_CRED_SECRET_GITLAB_DEFAULT,
    CONFIG_PROJECT_KEY,
    CONFIG_PROJECT_URI,
)
from ..core.config.lynceus_config import LynceusConfig


class DevOpsFactory(LynceusClientClass):
    """
    Factory class for creating DevOps analyzer instances.

    This factory provides a unified interface for creating different types of DevOps analyzers
    (GitLab, GitHub) with both read-only and editor capabilities. It automatically detects
    the platform type based on the URI and instantiates the appropriate analyzer class.

    Attributes:
        DEVOPS_CLASS_MAP: Mapping of (platform, editor_mode) tuples to analyzer classes
    """

    # N.B.: use declaration to avoid lower performance with dynamic class loading.
    DEVOPS_CLASS_MAP: dict[tuple[str, bool], type[DevOpsAnalyzer]] = {
        ("gitlab", False): GitlabDevOpsAnalyzer,
        ("gitlab", True): GitlabDevOpsAnalyzerEditor,
        ("github", False): GithubDevOpsAnalyzer,
        ("github", True): GithubDevOpsAnalyzerEditor,
    }

    def __init__(
            self, lynceus_session: LynceusSession, lynceus_exchange: LynceusExchange | None
    ):
        """
        Initialize the DevOps factory.

        Parameters
        ----------
        lynceus_session : LynceusSession
            The Lynceus session instance
        lynceus_exchange : LynceusExchange or None
            Exchange instance for data communication (optional)
        """
        super().__init__(lynceus_session, "devops", lynceus_exchange)

    def _create_devops_analyzer_instance(
            self, *, host: str, editor_mode: bool, uri: str, token: str
    ) -> DevOpsAnalyzer | DevOpsAnalyzerEditor:
        """
        Create a specific DevOps analyzer instance based on platform and mode.

        Parameters
        ----------
        host : str
            Platform identifier ('gitlab' or 'github')
        editor_mode : bool
            Whether to create an editor-capable instance
        uri : str
            Platform URI
        token : str
            Authentication token

        Returns
        -------
        DevOpsAnalyzer
            Platform-specific analyzer instance
        """
        self._logger.debug(
            f"Instantiating a {host.title()} implementation, according to uri '{uri}'."
        )
        return DevOpsFactory.DEVOPS_CLASS_MAP[(host, editor_mode)](
            self._lynceus_session, uri, token, self._lynceus_exchange
        )

    def _manage_new_devops_analyzer(self, *, editor_mode: bool, uri: str, token: str) -> DevOpsAnalyzer | DevOpsAnalyzerEditor:
        """
        Create a new DevOps analyzer by detecting the platform from URI.

        Parameters
        ----------
        editor_mode : bool
            Whether to create an editor-capable instance
        uri : str
            Platform URI (used to detect platform type)
        token : str
            Authentication token

        Returns
        -------
        DevOpsAnalyzer
            Appropriate analyzer instance for the detected platform

        Raises
        ------
        ValueError
            If the platform cannot be determined from the URI
        """
        if "gitlab" in uri:
            return self._create_devops_analyzer_instance(
                host="gitlab", editor_mode=editor_mode, uri=uri, token=token
            )
        if "github" in uri:
            return self._create_devops_analyzer_instance(
                host="github", editor_mode=editor_mode, uri=uri, token=token
            )
        raise ValueError(f"Host with uri '{uri}' is not supported by DevOps feature.")

    def new_devops_analyzer(self, uri: str, token: str) -> DevOpsAnalyzer:
        """
        Create a new read-only DevOps analyzer instance.

        Parameters
        ----------
        uri : str
            Platform URI
        token : str
            Authentication token

        Returns
        -------
        DevOpsAnalyzer
            Read-only analyzer instance
        """
        return self._manage_new_devops_analyzer(editor_mode=False, uri=uri, token=token)

    def new_devops_analyzer_editor(self, uri: str, token: str) -> DevOpsAnalyzerEditor:
        """
        Create a new editor-capable DevOps analyzer instance.

        Parameters
        ----------
        uri : str
            Platform URI
        token : str
            Authentication token

        Returns
        -------
        DevOpsAnalyzer
            Editor-capable analyzer instance
        """
        return self._manage_new_devops_analyzer(editor_mode=True, uri=uri, token=token)

    def get_access_token_simulating_anonymous_access(
            self, *, uri: str, lynceus_config: LynceusConfig
    ) -> str:
        """
        Get an access token for simulating anonymous access to a DevOps platform.

        This method retrieves a default credential secret from the configuration
        based on the platform type detected from the URI.

        Parameters
        ----------
        uri : str
            Platform URI (used to detect platform type)
        lynceus_config : LynceusConfig
            Configuration instance to read credentials from

        Returns
        -------
        str
            Access token for anonymous access simulation

        Raises
        ------
        ValueError
            If no appropriate credential secret is found in configuration
        """
        if "gitlab" in uri:
            default_credential_secret_key: str = (
                CONFIG_PROJECT_CRED_SECRET_GITLAB_DEFAULT
            )
        else:
            default_credential_secret_key: str = (
                CONFIG_PROJECT_CRED_SECRET_GITHUB_DEFAULT
            )

        default_credential_secret: str = lynceus_config.get_config(
            CONFIG_AUTHENTICATION_KEY, default_credential_secret_key, default=None
        )
        if default_credential_secret:
            self._logger.warning(
                f'No specific "{CONFIG_PROJECT_CRED_SECRET}" in your [{CONFIG_AUTHENTICATION_KEY}] configuration,'
                f' using the configured "{default_credential_secret_key}" one.'
            )
            lynceus_config[CONFIG_AUTHENTICATION_KEY][
                CONFIG_PROJECT_CRED_SECRET
            ] = default_credential_secret
            return default_credential_secret

        error_message: str = (
            f'Unable to find "{CONFIG_PROJECT_CRED_SECRET}" in your [{CONFIG_AUTHENTICATION_KEY}] configuration,'
        )
        error_message += f' and there is no "{default_credential_secret_key}" configured. Update your configuration and try again.'

        self._logger.warning(error_message)
        raise ValueError(error_message)

    def check_and_enhance_configuration_for_anonymous_access(
            self, lynceus_config: LynceusConfig, *, config_key: str = CONFIG_PROJECT_KEY
    ):
        """
        Check and enhance configuration for anonymous access support.

        This method ensures that the configuration has appropriate credential secrets
        for anonymous access. If not present, it attempts to use default credentials.

        Parameters
        ----------
        lynceus_config : LynceusConfig
            Configuration instance to check and modify
        config_key : str, optional
            Configuration key to check (defaults to project key)

        Raises
        ------
        ValueError
            If no appropriate credentials can be found or configured
        """
        uri: str = lynceus_config.get_config(config_key, CONFIG_PROJECT_URI)
        configured_credential_secret: str = lynceus_config.get_config(
            config_key, CONFIG_PROJECT_CRED_SECRET, default=None
        )
        if configured_credential_secret is None:
            lynceus_config[config_key][CONFIG_PROJECT_CRED_SECRET] = (
                self.get_access_token_simulating_anonymous_access(
                    uri=uri, lynceus_config=lynceus_config
                )
            )
