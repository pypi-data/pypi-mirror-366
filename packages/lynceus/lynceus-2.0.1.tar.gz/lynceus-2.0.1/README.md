# Lynceus

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Latest Release](https://gitlab.com/bertrand-benoit/lynceus/-/badges/release.svg)](https://gitlab.com/bertrand-benoit/lynceus/-/releases)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/2de5ae3d923b4a7fb728448f0577e95f)](https://app.codacy.com/gl/bertrand-benoit/lynceus/dashboard?utm_source=gl&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Coverage Report](https://gitlab.com/bertrand-benoit/lynceus/badges/main/coverage.svg)](https://gitlab.com/bertrand-benoit/lynceus/-/commits/main)
[![Pipeline Status](https://gitlab.com/bertrand-benoit/lynceus/badges/main/pipeline.svg)](https://gitlab.com/bertrand-benoit/lynceus/-/commits/main)
[![PyPI version](https://badge.fury.io/py/lynceus.svg)](https://badge.fury.io/py/lynceus)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Lynceus is a sophisticated and resilient Python toolbox designed to serve as the foundational core layer of your Python applications. It offers powerful features for configuration management with inheritance, automatic logger configuration, efficient session management, and unified file handling for both local and remote storages.

## 📋 Table of Contents

- [✨ Key Features](#-key-features)
- [🚀 Installation](#-installation)
  - [As a Dependency (Recommended)](#as-a-dependency-recommended)
  - [For Contributing to Lynceus](#for-contributing-to-lynceus)
- [📖 Quick Start](#-quick-start)
- [⚙️ Configuration](#-configuration)
  - [Salt-Based Configuration with Inheritance](#salt-based-configuration-with-inheritance)
  - [Configuration Flavors](#configuration-flavors)
  - [Configuration File Structure](#configuration-file-structure)
  - [Basic Configuration](#basic-configuration)
  - [Logger Configuration](#logger-configuration)
  - [Credentials Flavor Configuration](#credentials-flavor-configuration)
  - [Storages Flavor Configuration](#storages-flavor-configuration)
  - [Extra Configuration](#extra-configuration)
- [📖 Advanced Usage Examples](#-advanced-usage-examples)
- [📚 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)
- [🔗 Links](#-links)

## ✨ Key Features

- **⚙️ Session Management** - Efficient session handling with salt-based configuration discovery
- **🔧 Advanced Configuration Management** - Hierarchical configuration with inheritance and JSON loading
- **📝 Smart Logger Configuration** - Automated logger setup with customizable handlers and formatters
- **🗂️ Unified File Handling** - Seamless local and remote storages management (S3, etc.)
- **🔗 DevOps Integration** - Versatile DevOpsAnalyzer abstract layer offering project analysis and statistics, featuring GitLab and GitHub implementations with the flexibility to extend to additional platforms
- **📊 Data Processing** - Built-in utilities for data analysis and processing
- **🔒 Secure Authentication** - Separate configuration files for sensitive credentials

## 🚀 Installation

Lynceus packages are available on [PyPI](https://pypi.org/project/lynceus/) and can be installed with any package manager of your choice.

### As a Dependency (Recommended)

Add Lynceus to your existing project as a dependency:

```bash
# Using Poetry
poetry add lynceus

# Using pip
pip install lynceus

# Using uv
uv add lynceus

# Using conda
conda install -c conda-forge lynceus

# Using pipenv
pipenv install lynceus
```

For detailed installation instructions with Poetry, please refer to the [Poetry documentation](https://python-poetry.org/docs/).

### For Contributing to Lynceus

If you want to contribute to Lynceus development:

```bash
# Fork/Clone the repository
git clone https://gitlab.com/bertrand-benoit/lynceus.git
cd lynceus

# Install development dependencies
poetry install

# Run tests
poetry run pytest
```

**⚠️ Important:** Only clone this repository if you intend to contribute to Lynceus itself. For using Lynceus in your projects, install it as a dependency instead.

## 📖 Quick Start

Let's refer to your envisioned project as **Argo** throughout this documentation; as Argo, the legendary vessel of epic adventures in Greek mythology, with Lynceus among its Argonauts.

Then start using Lynceus in your source code:

```python
from logging import Logger

from lynceus.core.lynceus import LynceusSession

# Initialize a session with your project's salt
session: LynceusSession = LynceusSession.get_session(
    salt="argo",
    registration_key={"environment": "production", "service": "api"}
)

# Get logger from session (default prefix is 'Lynceus')
logger: Logger = session.get_logger('task.processor')  # Creates 'Lynceus.task.processor' logger
logger.warning('⚠️ Prepare for departure as Argo vessel is about to set sail! 🚢💨')
```

## ⚙️ Configuration

Lynceus is highly configurable through configuration files. The system uses a **salt-based approach** to locate the appropriate configuration files for your project.

### Salt-Based Configuration with Inheritance

Lynceus supports multiple configuration files that are merged hierarchically.
When initializing Lynceus session, you provide a **salt** (project identifier) that determines which configuration files to load.

The system searches for configuration files, from their relative paths, using `lynceus.utils.lookup_root_path()`, which iteratively searches up to three directory levels by default.

**Configuration Loading Order:**

1. **`lynceus.default.conf`** - Core default configuration (embedded in lynceus/misc/ folder of Lynceus package)
2. **`{salt}_default.conf`** - Default configuration for your salt (optional)
3. **`{salt}.conf`** - Main project configuration (optional)
4. **`{salt}_{flavor}.conf`** - Flavor-specific configurations (optional, based on `conf_flavor_list_json_dump`)

Later configurations override earlier ones, allowing for flexible customization while maintaining sensible defaults.

### Configuration Flavors

Lynceus supports **"flavors"** - optional configuration categories that allow you to organize different types of configuration files in a structured way.

Default flavors are ["storages", "credentials"], and can be overriden in your configuration file.

**Flavors examples:**

- **`storages`** - Remote storage configurations (S3, etc.)
- **`credentials`** - Authentication tokens and secrets
- **`environments`** - Environment-specific settings
- **`integrations`** - Third-party service configurations

**Enabling Flavors:**

Add the following to your main configuration file to override default flavor list:

```ini
# {salt}.conf (e.g., argo.conf)
[General]
project_name = Argo Project

# Define the list of flavors to load - this will automatically load {salt}_{flavor}.conf files
conf_flavor_list_json_dump = ["storages", "credentials"]
```

This will automatically load:

- `argo_storages.conf` (if exists)
- `argo_credentials.conf` (if exists)

**Note:** If a flavor file doesn't exist, Lynceus will log a warning and continue loading other flavors. The system is designed to be fault-tolerant.

### Configuration File Structure

Create configuration files named with your project's salt, and place them in the root directory or a subdirectory of your project. Ensure the relative path of these files does not exceed three directory levels from any executed Python files.
**Note:** Typically, the **`{salt}_default.conf`** file is intended to be packaged with the source code, so it can be placed within a subdirectory of the main package.

All configuration files are **optional**, for example, here is a possible structure for a project with salt `argo`:

```
project_root/
├── argo.conf                  # (Optional) Main project configuration
├── argo_storages.conf         # (Optional) Storages flavor configuration
├── argo_credentials.conf      # (Optional) Credentials flavor configuration
├── argo_environments.conf     # (Optional) Environments flavor configuration
└── argo/                      # Main Python package
    └── misc/
        └── argo_default.conf  # (Optional) Default configuration for Argo project
```

**Flavor-Based Configuration Flow:**

```
lynceus.default.conf (core defaults)
        ↓ (merged with)
argo_default.conf (project defaults)
        ↓ (merged with)
argo.conf (main config + flavor list)
        ↓ (loads flavors from conf_flavor_list_json_dump)
argo_storages.conf + argo_credentials.conf + ...
        ↓ (final configuration)
Merged Configuration
```

#### Basic Configuration

For general configuration, you have the option to place it in either the **`{salt}.conf`** file or the **`{salt}_default.conf`** file.

**`{main_package}/misc/{salt}_default.conf`** (e.g., `argo/misc/argo_default.conf`):
```ini
[General]
# Project information
project_name=Argo Project

# Define the list of flavors to load - this will automatically load {salt}_{flavor}.conf files
conf_flavor_list_json_dump = ["storages", "credentials", "specific_flavor"]

[StorageConfiguration]
work_dir=/tmp/argo_workdir
```

#### Logger Configuration

Lynceus supports advanced logger configuration using Python's standard logging system.

**`{salt}.conf`** (e.g., `argo.conf`):
```ini
[loggers]
keys = root, argo

[handlers]
keys = file, console_out, console_err

[formatters]
keys = default

[logger_root]
level = DEBUG
handlers = file, console_out, console_err

[handler_file]
class=FileHandler
level=DEBUG
formatter=default
# N.B.: use 'w' to override file each time a process is running, use 'a' to append to potential existing file to avoid log lost.
args=('/tmp/argo.log', 'a')

[handler_console_out]
; N.B.: lynceus.core.logger_utils.FilteredStdoutLoggerHandler is a special class allowing to filter out messages from Warning.
; Thus, with combination of a dedicated 'console error handler' configuration, it allows to have:
;  - warning, error and critical messages log on stderr
;  - the others messages on stdout
class = lynceus.core.logger_utils.FilteredStdoutLoggerHandler
args = (sys.stdout,)
; Overrides console out level to DEBUG, allowing to see DEBUG messages of all logger having corresponding level (including those inherited from previously loaded configuration files).
level = DEBUG
formatter = default

[handler_console_err]
class = StreamHandler
args = (sys.stderr,)
level = WARNING
formatter = default

[formatter_default]
style={
format = {asctime:20} {name:16} {levelname:8} {message}
datefmt = %Y/%m/%d %H:%M:%S

[logger_argo]
; Defines to logs for this logger only from INFO.
level=INFO
handlers=
qualname=argo
```

#### Credentials Flavor Configuration

For sensitive credentials, create a **credentials flavor** configuration file. This file will be automatically loaded if "credentials" is included in merged `conf_flavor_list_json_dump`.

**`{salt}_credentials.conf`** (e.g., `argo_credentials.conf`):
```ini
[DevOps-GitLab]
credential_secret=glpat-xxxxxxxxxxxxxxxxxxxx

[DevOps-GitHub]
credential_secret=ghp-xxxxxxxxxxxxxxxxxxxx

[AWS-S3-Production]
access_key_id=AKIAIOSFODNN7EXAMPLE
secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[OVH-S3-Backup]
access_key_id=OVHEXAMPLEKEY
secret_access_key=OVHEXAMPLESECRET
```

#### Storages Flavor Configuration

For remote storage, create a **storages flavor** configuration file. This file will be automatically loaded if "storages" is included in merged `conf_flavor_list_json_dump`.

**`{salt}_storages.conf`** (e.g., `argo_storages.conf`):
```ini
[StorageConfiguration]
available_remote_storages=AWS-S3-Production,OVH-S3-Backup

[AWS-S3-Production]
storage_type=s3
bucket_name=my-production-bucket
username=my-user
s3_endpoint = https://s3-eu-west-1.amazonaws.com
signature_version = s3v4

[OVH-S3-Backup]
storage_type=s3
bucket_name=my-backup-bucket
username=backup-user
s3_endpoint = https://s3.gra.cloud.ovh.net
region_name = gra
signature_version = s3v4
addressing_style = virtual
```

#### Extra Configuration

For any other configuration, you can create any count of configuration files (and request manual loading), or put the configuration inside your **`{salt}.conf`** one.

For instance for DevOps integration, configure your project details inside a **`conf_dir/argo_custom.conf`**:

```ini
[Project]
name=Argo Analytics Project
uri=https://gitlab.com
credential_secret=<your-token>
username=Argo Bot
project_path=my-org/argo-analytics
project_profile=SOURCE_CODE_DATA_SCIENCE
```

For instance for Tests, configure your project details inside a **`conf_dir/tests/argo_tests.conf`**:

```ini
[Tests-DevOps-Gitlab]
name=Gitlab public project
uri=https://gitlab.com
credential_secret=<your-token>
project_path=fdroid/fdroidserver
git_reference=master
project_profile=SOURCE_CODE_DEFAULT
```

## 📖 Advanced Usage Examples

```python
from logging import Logger

from lynceus.core.config.lynceus_config import LynceusConfig
from lynceus.core.lynceus import LynceusSession

# Multiple sessions for different services
api_session: LynceusSession = LynceusSession.get_session(
    salt="argo",
    registration_key={"service": "api", "env": "production"},
    root_logger_name="ArgoAPI"
)

worker_session: LynceusSession = LynceusSession.get_session(
    salt="argo",
    registration_key={"service": "worker", "env": "production"},
    root_logger_name="ArgoWorker"
)

# Each session maintains its own logger hierarchy
api_logger: Logger = api_session.get_logger('request.handler')       # 'ArgoAPI.request.handler'
worker_logger: Logger = worker_session.get_logger('task.processor')  # 'ArgoWorker.task.processor'

# Configuration can be read from any session.
storage_work_dir: str = worker_session.get_config('StorageConfiguration', 'work_dir')
worker_logger.info(f'Will create internal files under {storage_work_dir=}')

# Load additional configuration from files
config: LynceusConfig = api_session.get_lynceus_config_copy()
config.lookup_configuration_file_and_update_from_it('conf_dir/argo_custom.conf')
config.lookup_configuration_file_and_update_from_it('conf_dir/tests/argo_tests.conf')

# Configuration can be read directly from any LynceusConfig instance.
devops_uri: str = config.get_config('Tests-DevOps-Gitlab', 'uri')
tests_logger: Logger = worker_session.get_logger('tests')  # 'ArgoWorker.tests'
tests_logger.info(f'Some Gitlab DevOps Tests will be performed on {devops_uri} project')
```

## 📚 Documentation

For comprehensive documentation, visit the **[Complete Technical Documentation](docs/)** directory.

## 🤝 Contributing

We welcome contributions! Please see [Contributing Guide](https://opensource.guide/how-to-contribute/) for details.

Don't hesitate to [contact me](mailto:contact@bertrand-benoit.net) if you need information about:

- Development environment setup
- Code standards and best practices
- Testing procedures
- Submission process

You can [report issues or request features](https://gitlab.com/bertrand-benoit/lynceus/issues) and propose [merge requests](https://gitlab.com/bertrand-benoit/lynceus/merge_requests).

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

### Key points about GPL-3.0

- **Free to use, modify, and distribute**
- **Source code must be made available** when distributing
- **Modifications must also be GPL-3.0 licensed**
- **No warranty provided**

For complete license terms, see the [LICENSE](LICENSE) file or visit [https://www.gnu.org/licenses/gpl-3.0](https://www.gnu.org/licenses/gpl-3.0).

## 🔗 Links

- **Repository**: [GitLab](https://gitlab.com/bertrand-benoit/lynceus)
- **Releases**: [GitLab Releases](https://gitlab.com/bertrand-benoit/lynceus/-/releases)
- **Package**: [PyPI](https://pypi.org/project/lynceus/)
- **Issues**: [GitLab Issues](https://gitlab.com/bertrand-benoit/lynceus/-/issues)

---

Built with ❤️ for the open source community
