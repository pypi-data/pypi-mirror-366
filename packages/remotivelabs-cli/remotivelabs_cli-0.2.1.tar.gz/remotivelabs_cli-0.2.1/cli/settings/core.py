from __future__ import annotations

import os
import stat
import sys
from json import JSONDecodeError
from pathlib import Path
from typing import Optional, Tuple

from rich.console import Console

from cli.errors import ErrorPrinter
from cli.settings import config_file, token_file
from cli.settings import token_file as tf
from cli.settings.config_file import ConfigFile
from cli.settings.token_file import TokenFile

err_console = Console(stderr=True)


CONFIG_DIR_PATH = Path.home() / ".config" / "remotive"
CLI_CONFIG_FILE_NAME = "config.json"


TokenFileMetadata = Tuple[TokenFile, Path]


class InvalidSettingsFilePathError(Exception):
    """Raised when trying to access an invalid settings file or file path"""


class TokenNotFoundError(Exception):
    """Raised when a token cannot be found in settings"""


class Settings:
    """
    Settings handles tokens and other config for the remotive CLI
    """

    config_dir: Path

    def __init__(self, config_dir: Path) -> None:
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file_path = self.config_dir / CLI_CONFIG_FILE_NAME
        if not self.config_file_path.exists():
            self._write_config_file(ConfigFile())

    def set_default_organisation(self, organisation: str) -> None:
        cli_config = self.get_cli_config()
        try:
            token = settings.get_active_token_file()
            cli_config.set_account_field(token.account.email, organisation)
            self._write_config_file(cli_config)
        except TokenNotFoundError:
            ErrorPrinter.print_hint("You must have an account activated in order to set default organization")
            sys.exit(1)

    def get_cli_config(self) -> ConfigFile:
        try:
            return self._read_config_file()
        except TokenNotFoundError:
            return ConfigFile()

    def get_active_token(self) -> str:
        """
        Get the current active token secret
        """
        token_file = self.get_active_token_file()
        return token_file.token

    def get_active_token_file(self) -> TokenFile:
        """
        Get the current active token file
        """
        active_account = self.get_cli_config().get_active()
        if active_account is not None:
            token_file_name = active_account.credentials_file
            return self._read_token_file(self.config_dir / token_file_name)

        raise TokenNotFoundError

    def activate_token(self, token_file: TokenFile) -> None:
        """
        Activate a token by name or path

        The token secret will be set as the current active secret.
        """
        cli_config = self.get_cli_config()
        cli_config.activate(token_file.account.email)
        self._write_config_file(cli_config)

    def clear_active_token(self) -> None:
        """
        Clear the current active token
        """
        config = self.get_cli_config()
        config.active = None
        self._write_config_file(config)

    def get_token_file_by_email(self, email: str) -> Optional[TokenFile]:
        """
        Get a token file by email.

        If multiple tokens are found, the first one is returned.
        """
        tokens = [t for t in self.list_personal_tokens() if t.account is not None and t.account.email == email]
        if len(tokens) > 0:
            return tokens[0]
        tokens = [t for t in self.list_service_account_tokens() if t.account is not None and t.account.email == email]
        if len(tokens) > 0:
            return tokens[0]
        return None

    def get_token_file(self, name: str) -> TokenFile:
        """
        Get a token file by name or path
        """
        # 1. Try relative path
        if (self.config_dir / name).exists():
            return self._read_token_file(self.config_dir / name)

        # 2. Try absolute path
        if Path(name).exists():
            return self._read_token_file(Path(name))

        # 3. Try name
        return self._get_token_by_name(name)[0]

    def remove_token_file(self, name: str) -> None:
        """
        Remove a token file by name or path

        TODO: what about manually downloaded tokens?
        """
        if Path(name).exists():
            if self.config_dir not in Path(name).parents:
                raise InvalidSettingsFilePathError(f"cannot remove a token file not located in settings dir {self.config_dir}")
            return Path(name).unlink()

        # TODO: what about the active token?
        path = self._get_token_by_name(name)[1]
        return path.unlink()

    def add_personal_token(self, token: str, activate: bool = False, overwrite_if_exists: bool = False) -> TokenFile:
        """
        Add a personal token
        """
        file = tf.loads(token)
        if file.type != "authorized_user":
            raise ValueError("Token type MUST be authorized_user")

        file_name = file.get_token_file_name()
        path = self.config_dir / file_name
        if path.exists() and not overwrite_if_exists:
            raise FileExistsError(f"Token file already exists: {path}")

        self._write_token_file(path, file)
        cli_config = self.get_cli_config()
        cli_config.init_account(email=file.account.email, token_file=file)
        self._write_config_file(cli_config)

        if activate:
            self.activate_token(file)

        return file

    def list_personal_tokens(self) -> list[TokenFile]:
        """
        List all personal tokens
        """
        return [f[0] for f in self._list_personal_tokens()]

    def list_personal_token_files(self) -> list[Path]:
        """
        List paths to all personal token files
        """
        return [f[1] for f in self._list_personal_tokens()]

    def add_service_account_token(self, token: str, overwrite_if_exists: bool = False) -> TokenFile:
        """
        Add a service account token
        """
        token_file = tf.loads(token)
        if token_file.type != "service_account":
            raise ValueError("Token type MUST be service_account")

        file = token_file.get_token_file_name()
        path = self.config_dir / file
        if path.exists() and not overwrite_if_exists:
            raise FileExistsError(f"Token file already exists: {path}")

        self._write_token_file(path, token_file)
        cli_config = self.get_cli_config()
        cli_config.init_account(email=token_file.account.email, token_file=token_file)
        self._write_config_file(cli_config)

        return token_file

    def list_service_account_tokens(self) -> list[TokenFile]:
        """
        List all service account tokens
        """
        return [f[0] for f in self._list_service_account_tokens()]

    def list_service_account_token_files(self) -> list[Path]:
        """
        List paths to all service account token files
        """
        return [f[1] for f in self._list_service_account_tokens()]

    def _list_personal_tokens(self) -> list[TokenFileMetadata]:
        return self._list_token_files(prefix=token_file.PERSONAL_TOKEN_FILE_PREFIX)

    def _list_service_account_tokens(self) -> list[TokenFileMetadata]:
        return self._list_token_files(prefix=token_file.SERVICE_ACCOUNT_TOKEN_FILE_PREFIX)

    def _get_token_by_name(self, name: str) -> TokenFileMetadata:
        token_files = self._list_token_files()
        matches = [token_file for token_file in token_files if token_file[0].name == name]
        if len(matches) != 1:
            raise TokenNotFoundError(f"Ambiguous token file name {name}, found {len(matches)} files")
        return matches[0]

    def _list_token_files(self, prefix: str = "") -> list[TokenFileMetadata]:
        """
        list all tokens with the correct prefix in the config dir, but omit files that are not token files

        TODO: improve is_valid_json and is_valid_token_file using token_file parsing instead
        """

        def is_valid_json(path: Path) -> bool:
            try:
                self._read_token_file(path)
                return True
            except JSONDecodeError:
                # TODO - this should be printed but printing it here causes it to be displayed to many times
                # err_console.print(f"File is not valid json, skipping. {path}")
                return False

        def is_valid_token_file(path: Path) -> bool:
            is_token_file = path.name.startswith(tf.SERVICE_ACCOUNT_TOKEN_FILE_PREFIX) or path.name.startswith(
                tf.PERSONAL_TOKEN_FILE_PREFIX
            )
            has_correct_prefix = path.is_file() and path.name.startswith(prefix)
            is_cli_config = path == self.config_file_path
            is_present_in_cli_config_accounts = any(
                path.name == account.credentials_file for account in self.get_cli_config().accounts.values()
            )
            return is_token_file and is_valid_json(path) and has_correct_prefix and not is_cli_config and is_present_in_cli_config_accounts

        paths = [path for path in self.config_dir.iterdir() if is_valid_token_file(path)]
        return [(self._read_token_file(token_file), token_file) for token_file in paths]

    def _read_token_file(self, path: Path) -> TokenFile:
        data = self._read_file(path)
        return tf.loads(data)

    def _read_config_file(self) -> ConfigFile:
        data = self._read_file(self.config_dir / CLI_CONFIG_FILE_NAME)
        return config_file.loads(data)

    def _read_file(self, path: Path) -> str:
        if not path.exists():
            raise TokenNotFoundError(f"File could not be found: {path}")
        return path.read_text(encoding="utf-8")

    def _write_token_file(self, path: Path, token: TokenFile) -> Path:
        data = tf.dumps(token)
        path = self._write_file(path, data)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        return path

    # Temporary function while considering how to solve this
    def write_config_file(self, config: ConfigFile) -> Path:
        return self._write_config_file(config)

    def _write_config_file(self, config: ConfigFile) -> Path:
        """
        TODO: add read cache to avoid parsing the config every time we read it
        """
        data = config_file.dumps(config)
        path = self._write_file(self.config_file_path, data)
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        return path

    def _write_file(self, path: Path, data: str) -> Path:
        if self.config_dir not in path.parents:
            raise InvalidSettingsFilePathError(f"file {path} not in settings dir {self.config_dir}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf8")
        return path


settings = Settings(CONFIG_DIR_PATH)
"""
Global/module-level settings instance. Module-level variables are only loaded once, at import time.

TODO: Migrate away from singleton instance
"""
