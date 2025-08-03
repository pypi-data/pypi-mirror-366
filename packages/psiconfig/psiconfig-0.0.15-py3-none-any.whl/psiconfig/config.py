"""Base class for config object for the application."""

from pathlib import Path

from .text import FIELD, NOT_IN_DICT


class Config():
    """
    The class takes a path to a config file and if valid returns a config dict.

    Attributes
    ----------

    path: str
        The path to the config file

    defaults: dict[str, object]
        The defaults are used if the path does not contain a valid config file.
    """

    STATUS_OK = 0
    STATUS_ERROR = 1
    STATUS_NOT_DEFINED = -1

    def __init__(
            self,
            path: str,
            defaults: dict[str, str] = {},
            restore_defaults: bool = False,
            ):
        self.path: str = path
        self.defaults: dict = defaults
        self.restore_defaults = restore_defaults
        self.status: int | str = self.STATUS_NOT_DEFINED
        self.error: str = ''
        self.config = self._get_config()
        for key, item in self.config.items():
            self.__dict__[key] = item

    def __repr__(self):
        output = ['Config:']
        for key, item in self.__dict__.items():
            output .append(f'{key}: {item}')
        return '\n'.join(output)

    def read(self) -> dict[str, object]:
        self._get_config()

    def _get_config(self) -> dict[str, object]:
        """Return config, if contents are valid."""
        config = {} if self.restore_defaults else self._read_config()
        for key, item in config.items():
            self.__dict__[key] = item

        if config:
            return config

        if self.defaults:
            return self.defaults
        return {}

    def update(self, field: str, value: object, force: bool = False) -> None:
        """Update the value of an attribute in config."""
        if not force and field not in self.__dict__['config']:
            self.status = self.STATUS_ERROR
            self.error = f'{FIELD} {field} {NOT_IN_DICT}'
            return

        self.__dict__[field] = value
        self.__dict__['config'][field] = value

    def create_directories(self) -> bool:
        """Create directories recursively."""
        create_parts = []
        create_path = Path(self.path).parent
        for part in create_path.parts:
            create_parts.append(part)
            new_path = Path(*create_parts)
            if not Path(new_path).is_dir():
                try:
                    Path(new_path).mkdir()
                except FileExistsError:
                    continue
                except PermissionError:
                    self.status = self.STATUS_ERROR
                    self.error = f'Invalid file path: {new_path}'
                    return False
        return True

    def check_defaults(self, config: dict) -> dict:
        """Make sure all default items in config."""
        for key, item in self.defaults.items():
            if key not in config:
                config[key] = item
        self.config = config
        return config

    @property
    def NOT_DEFINED(self):
        return self.STATUS_NOT_DEFINED

    @property
    def OK(self):
        return self.STATUS_OK

    @property
    def ERROR(self):
        return self.STATUS_ERROR
