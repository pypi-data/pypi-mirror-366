from itertools import chain
from pathlib import Path

from cli.settings.core import TokenNotFoundError
from cli.settings.token_file import TokenFile


def list_token_files(config_dir: Path) -> list[TokenFile]:
    """
    List all token files in the config directory

    Note! Dont use settings, as that will couple settings to the old config and token formats we want to migrate away from.
    """
    token_files = []
    patterns = ["personal-token-*.json", "service-account-token-*.json"]
    files = list(chain.from_iterable(config_dir.glob(pattern) for pattern in patterns))
    for file in files:
        try:
            token_file = TokenFile.from_json_str(file.read_text())
            token_files.append(token_file)
        except Exception:
            print(f"warning: invalid token file {file}. Consider removing it.")
    return token_files


def get_token_file(cred_name: str, config_dir: Path) -> TokenFile:
    """
    Get the token file for a given credentials name.

    Note! Dont use settings, as that will couple settings to the old config and token formats we want to migrate away from.
    """
    token_files = list_token_files(config_dir)
    matches = [token_file for token_file in token_files if token_file.name == cred_name]
    if len(matches) != 1:
        raise TokenNotFoundError(f"Token file for {cred_name} not found")
    return matches[0]
