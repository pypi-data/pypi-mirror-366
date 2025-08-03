# configration

A module to validate and load config files.

## Installation

```bash
pip install psiconfig
```

## How to use

*psiconfig* supports *json* and *toml* configurations. (To use *json* replace *TomlConfig* with *JsonConfig* in the following code.)

### Set up a module to handle configuration

1. Create a config module in your project:

```python

"""Config for <project>."""
from psiconfig import TomlConfig
CONFIG_PATH = <path to config file>  # NB need not exist


DEFAULT_CONFIG = {
    # a dictionary of default items that will be used if no config file is found
}


def get_config() -> TomlConfig:
    return TomlConfig(path=CONFIG_PATH, defaults=DEFAULT_CONFIG)


def save_config(config: TomlConfig) -> TomlConfig | None:
    result = config.save()
    if result != config.STATUS_OK:
        return None
    config = TomlConfig(CONFIG_PATH)
    return config


config = get_config()
```

### Accessing config in a module

If you want to access *config* in a module, then, if you want the config version at start up:

```python
from config import config
```

or, if you want the latest saved version of *config*:

```python
from config import get_config
...
    self.config = get_config()
```

### Config properties and methods

*config.config*: a dict of items in the configuration

*get_config(path)*: returns the config object

*save_config(config)*: saves the config items

### Updating config items

```python
config.config[<item key>] = <item value>
```
