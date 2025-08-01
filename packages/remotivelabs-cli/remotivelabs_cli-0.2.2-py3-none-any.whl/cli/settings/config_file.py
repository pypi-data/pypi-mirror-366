from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from typing import Any, Optional

from dacite import from_dict

from cli.settings.token_file import TokenFile


def loads(data: str) -> ConfigFile:
    d = json.loads(data)
    return from_dict(ConfigFile, d)


def dumps(config: ConfigFile) -> str:
    return json.dumps(dataclasses.asdict(config), default=str)


@dataclass
class Account:
    credentials_file: str
    default_organization: Optional[str] = None
    # Add project as well


@dataclass
class ConfigFile:
    version: str = "1.0"
    active: Optional[str] = None
    accounts: dict[str, Account] = dataclasses.field(default_factory=dict)

    def get_active_default_organisation(self) -> Optional[str]:
        active_account = self.get_active()
        return active_account.default_organization if active_account else None

    def get_active(self) -> Optional[Account]:
        if not self.active:
            return None
        account = self.get_account(self.active)
        if not account:
            raise KeyError(f"Activated account {self.active} is not a valid account")
        return account

    def activate(self, email: str) -> None:
        account = self.get_account(email)
        if not account:
            raise KeyError(f"Account {email} does not exists")
        self.active = email

    def get_account(self, email: str) -> Optional[Account]:
        if not self.accounts:
            return None
        return self.accounts.get(email, None)

    def remove_account(self, email: str) -> None:
        if self.accounts:
            self.accounts.pop(email, None)

    def init_account(self, email: str, token_file: TokenFile) -> None:
        if self.accounts is None:
            self.accounts = {}

        account = self.get_account(email)
        if not account:
            account = Account(credentials_file=token_file.get_token_file_name())
        else:
            account.credentials_file = token_file.get_token_file_name()
        self.accounts[email] = account

    def set_account_field(self, email: str, default_organization: Optional[str] = None) -> ConfigFile:
        if self.accounts is None:
            self.accounts = {}

        account = self.get_account(email)
        if not account:
            raise KeyError(f"Account with email {email} has not been initialized with token")

        # Update only fields explicitly passed
        if default_organization is not None:
            account.default_organization = default_organization

        return self

    @staticmethod
    def from_json_str(data: str) -> ConfigFile:
        return loads(data)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> ConfigFile:
        return from_dict(ConfigFile, data)
