from __future__ import annotations

import dataclasses
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Literal

DEFAULT_EMAIL = "unknown@remotivecloud.com"
PERSONAL_TOKEN_FILE_PREFIX = "personal-token-"
SERVICE_ACCOUNT_TOKEN_FILE_PREFIX = "service-account-token-"

TokenType = Literal["authorized_user", "service_account"]


def _parse_date(date_str: str) -> date:
    normalized = date_str.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).date()


def _parse_token_type(token: str) -> TokenType:
    if token.startswith("pa"):
        return "authorized_user"
    if token.startswith("sa"):
        return "service_account"
    raise ValueError(f"Unknown token type for token: {token}")


def _from_dict(d: dict[str, Any]) -> TokenFile:
    if "version" not in d:
        token_type = _parse_token_type(d["token"])
        return TokenFile(
            version="1.0",
            type=token_type,
            name=d["name"],
            token=d["token"],
            created=_parse_date(d["created"]),
            expires=_parse_date(d["expires"]),
            account=TokenFileAccount(email=DEFAULT_EMAIL),
        )

    account_email = d.get("account", {}).get("email", DEFAULT_EMAIL)
    return TokenFile(
        version=d["version"],
        type=d["type"],
        name=d["name"],
        token=d["token"],
        created=_parse_date(d["created"]),
        expires=_parse_date(d["expires"]),
        account=TokenFileAccount(email=account_email),
    )


def loads(data: str) -> TokenFile:
    return _from_dict(json.loads(data))


def dumps(token: TokenFile) -> str:
    return json.dumps(dataclasses.asdict(token), default=str)


@dataclass
class TokenFileAccount:
    email: str


@dataclass
class TokenFile:
    version: str
    type: TokenType
    name: str
    token: str
    created: date
    expires: date
    account: TokenFileAccount

    def get_token_file_name(self) -> str:
        def email_to_safe_filename(email: str) -> str:
            # Replace any invalid character with an underscore
            return re.sub(r'[<>:"/\\|?*]', "_", email)

        # From now, user will never be None when adding a token so in this case token_file.user is never None
        email = email_to_safe_filename(self.account.email) if self.account is not None else "unknown"
        if self.type == "authorized_user":
            return f"{PERSONAL_TOKEN_FILE_PREFIX}{self.name}-{email}.json"
        return f"{SERVICE_ACCOUNT_TOKEN_FILE_PREFIX}{self.name}-{email}.json"

    def is_expired(self) -> bool:
        return datetime.today().date() > self.expires

    def expires_in_days(self) -> int:
        return (self.expires - datetime.today().date()).days

    @staticmethod
    def from_json_str(data: str) -> TokenFile:
        return loads(data)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> TokenFile:
        return _from_dict(data)
