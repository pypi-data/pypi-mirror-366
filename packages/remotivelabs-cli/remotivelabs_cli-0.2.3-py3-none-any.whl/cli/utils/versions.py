from __future__ import annotations

import datetime
import json
import os
import platform
import urllib.request
from datetime import timedelta
from importlib import metadata as importlib_metadata
from importlib.metadata import version as python_project_version

from packaging.version import InvalidVersion, Version

from cli.errors import ErrorPrinter
from cli.settings import Settings


def cli_version() -> str:
    return python_project_version("remotivelabs-cli")


def python_version() -> str:
    return platform.python_version()


def host_os() -> str:
    return platform.system().lower()  # 'linux', 'darwin', 'windows'


def host_env() -> str:
    return "docker" if os.environ.get("RUNS_IN_DOCKER") else "native"


def platform_info() -> str:
    return f"python {python_version()}; {host_os()}; {host_env()}"


def _pypi_latest(
    project: str, *, include_prereleases: bool, timeout: float = 2.5, user_agent: str | None = None
) -> tuple[str | None, str | None]:
    """Return (latest_version, project_url) from PyPI, skipping yanked files."""
    url = f"https://pypi.org/pypi/{project}/json"
    headers = {"Accept": "application/json"}
    if user_agent:
        headers["User-Agent"] = user_agent
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
    except Exception:
        return None, None  # network/404/etc.

    releases = data.get("releases") or {}
    candidates: list[Version] = []
    for s, files in releases.items():
        try:
            v = Version(s)
        except InvalidVersion:
            continue
        the_files = files or []
        if any(f.get("yanked", False) for f in the_files):
            continue
        if (v.is_prerelease or v.is_devrelease) and not include_prereleases:
            continue
        candidates.append(v)

    if not candidates:
        return None, None

    latest = str(max(candidates))
    info = data.get("info") or {}
    proj_url = info.get("project_url") or info.get("package_url") or f"https://pypi.org/project/{project}/"
    return latest, proj_url


def _installed_version(distribution_name: str, fallback: str | None = None) -> str | None:
    try:
        return importlib_metadata.version(distribution_name)
    except importlib_metadata.PackageNotFoundError:
        return fallback


def check_for_update(settings: Settings) -> None:
    # Make it possible to disable update check, i.e in CI
    if os.environ.get("PYTHON_DISABLE_UPDATE_CHECK"):
        return
    project = "remotivelabs-cli"

    # Determine current version
    cur = cli_version() or _installed_version(project)
    if not cur:
        return  # unknown version → skip silently

    state = settings.get_state_file()
    if not state.last_update_check_time:
        if os.environ.get("RUNS_IN_DOCKER"):
            # To prevent that we always check update in docker due to ephemeral disks we write an "old" check if the state
            # is missing. If no disk is mounted we will never get the update check but if its mounted properly we will get
            # it on the second attempt. This is good enough
            last_update_check_time = (datetime.datetime.now() - timedelta(hours=10)).isoformat()
            settings.set_last_update_check_time(last_update_check_time)
            return

    elif not state.should_perform_update_check():
        return

    # We end up here if last_update_check_time is None or should_perform_update_check is true
    include_prereleases = Version(cur).is_prerelease or Version(cur).is_devrelease

    latest, proj_url = _pypi_latest(
        project, include_prereleases=include_prereleases, user_agent=f"{project}/{cur} (+https://pypi.org/project/{project}/)"
    )
    if latest:
        if Version(latest) > Version(cur):
            _print_update_info(
                cur,
                latest,
            )
    settings.set_last_update_check_time(datetime.datetime.now().isoformat())


def _print_update_info(cur: str, latest: str) -> None:
    instructions = (
        "upgrade with: docker pull remotivelabs/remotivelabs-cli"
        if os.environ.get("RUNS_IN_DOCKER")
        else "upgrade with: pipx install -U remotivelabs-cli"
    )

    ErrorPrinter.print_hint(
        f"Update available: remotivelabs-cli {cur} → {latest} , ({instructions}) we always recommend to use latest version"
    )
