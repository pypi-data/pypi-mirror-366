# Defines various constants.

# * Date/time format
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
DATETIME_FORMAT_SHORT = "%Y-%m-%d"

# * Internals constants (avoiding circular import).
LYNCEUS_S3_CONFIG_KEY: str = 'lynceus_s3_config'

# * Configuration instance
CONFIG_GENERAL_KEY: str = 'General'

# Constants definition for 'Processing' configuration level: where any process can store information // used by jobs to share info.
CONFIG_PROCESS_KEY: str = 'Processing'
CONFIG_RUN_EXECUTION_ID: str = 'execution_id'

CONFIG_PROJECT_REPO_ANALYSE_DIR: str = 'uncompress_repo_directory'

CONFIG_PROCESS_REPO_ALL_FILE: str = 'interesting_files_list'
CONFIG_PROCESS_REPO_FILE_COUNT: str = 'interesting_files_count'

CONFIG_PROCESS_REPO_LINES_COUNT: str = 'interesting_lines_count'

# Constants definition for 'Storage' configuration level: where user can configure some directory to work into (like temporary root directory).
CONFIG_STORAGE_KEY: str = 'StorageConfiguration'

CONFIG_STORAGE_REMOTE_TYPE: str = 'storage_type'
CONFIG_STORAGE_LOCAL: str = 'Local'
CONFIG_STORAGE_IS_REMOTE: str = 'is_remote'
CONFIG_STORAGE_IS_DYNAMIC: str = 'is_dynamic'
CONFIG_STORAGE_DYNAMIC_TYPE: str = 'dynamic_type'
CONFIG_STORAGE_REMOTE_AVAILABLE: str = 'available_remote_storages'

# Lynceus client (API, CLI ...) related config.
#  * configuration option
CONFIG_JSON_DUMP_KEY_END_KEYWORD: str = '_json_dump'
CONFIG_AUTHENTICATION_KEY: str = 'Authentication'

CONFIG_PARTICIPANT_EMAIL: str = 'participant_email'
CONFIG_SCORE_PARTICIPANT: str = 'score_participant'
CONFIG_DISCRIMINANT: str = 'discriminant'
CONFIG_PROGRAM_ID: str = 'program_id'

#   - other parameters related to logging
CONFIG_LOG_MESSAGE_STATUS_KEY: str = 'message_status'

#  * various constants


# Constants definition for 'Jobs' configuration level: configuration of jobs.
CONFIG_JOBS_KEY: str = 'Jobs'
CONFIG_JOBS_DISABLED_LIST: str = 'disabled_job_list'

# Constants definition for 'Project' configuration level: configuration of project to analyze.
CONFIG_PROJECT_KEY: str = 'Project'
CONFIG_PROJECT_URI: str = 'uri'
CONFIG_PROJECT_NAME: str = 'name'
CONFIG_PROJECT_PATH: str = 'project_path'

CONFIG_PROJECT_CRED_SECRET: str = 'credential_secret'
CONFIG_PROJECT_CRED_SECRET_GITLAB_DEFAULT: str = 'gitlab_default_credential_secret'
CONFIG_PROJECT_CRED_SECRET_GITHUB_DEFAULT: str = 'github_default_credential_secret'

CONFIG_PROJECT_ROOT_PATH_HOLDER: str = '<PROJECT_ROOT_PATH>'

# * Compute Resources related constants.
ACCESS_PERMISSION_RO: str = 'RO'
ACCESS_PERMISSION_RW: str = 'RW'
ACCESS_PERMISSION_RWD: str = 'RWD'
