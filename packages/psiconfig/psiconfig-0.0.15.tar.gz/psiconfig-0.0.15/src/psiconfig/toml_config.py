"""Return a config object from a toml file for the application."""
from psi_toml.parser import TomlParser, TOMLDecodeError

from .config import Config
import psiconfig.text as text

toml = TomlParser()


class TomlConfig(Config):
    """
        A class to handle config files in toml format
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _read_config(self) -> dict[str, object]:
        """Open the config file and return the contents as a dict."""
        self.status = self.OK
        try:
            with open(self.path, 'r', encoding='utf-8') as f_config:
                text = f_config.read()
            with open(self.path, 'r', encoding='utf-8') as f_config:
                try:
                    config = toml.load(f_config)
                    return self.check_defaults(config)
                except TOMLDecodeError as err:
                    if self.defaults:
                        msg = (f'*** WARNING. TOMLDecodeError '
                               f'{err.args[0]}. Defaults used ***')
                        print(msg)
                        return self.defaults
                    else:
                        self.error = f'{text.INVALID_TOML} {self.path}'
        except FileNotFoundError:
            if self.defaults:
                return self.defaults
            else:
                self.error = text.DEFAULTS_ERR
        except NotADirectoryError:
            if self.defaults:
                return self.defaults
            else:
                self.error = text.DEFAULTS_ERR
        self.status = self.STATUS_ERROR
        return {}

    def save(self):
        if not self.path.parent.is_dir():
            self.create_directories()
        try:
            with open(self.path, mode='w') as f_config:
                toml.dump(self.__dict__['config'], f_config)
            self._get_config()
            return self.STATUS_OK
        except Exception as err:
            self.status = self.STATUS_ERROR
            self.error = err
