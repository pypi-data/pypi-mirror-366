import re
from typing import Optional
from urllib.parse import urlparse

import requests
from packaging.version import InvalidVersion, Version
from rich import print

MAX_TIMEOUT = 10

"""
# TODO: Try to use semver library to compare versions
import semver


latest_version = response.json()["tag_name"]

if semver.compare(latest_version, VERSION) > 0:
    # update detected...
"""


def _get_latest_release_version(repo_url: str, is_gitlab: bool = False) -> str | None:
    """
    Retrieve the latest release version from the repository.

    Args:
        repo_url (str): The URL of the repository releases.
        is_gitlab (bool): Whether the repository is hosted on GitLab.

    Returns:
        str | None: The name of the latest release version if found, else None.
    """
    try:
        if is_gitlab:
            # Adjust the URL for GitLab's permalink for the latest release
            repo_url = repo_url.replace(
                "/releases/latest", "/releases/permalink/latest"
            )

        response: requests.Response = requests.get(repo_url, timeout=MAX_TIMEOUT)
        response.raise_for_status()

        tag_name = response.json().get("tag_name")
        name = response.json().get("name")
        # Check if the tag_name is a valid version
        if tag_name and re.match(r".*v?\d+\.\d+\.\d+", tag_name):
            return tag_name
        elif name and re.match(r".*v?\d+\.\d+\.\d+", name):
            return name
        return None
    except requests.exceptions.RequestException:
        return None


def _parse_version_tag(tag_name: str) -> Version:
    """
    Parse a version tag, stripping any leading non-numeric characters like 'v'.

    Args:
        tag_name (str): The name of the tag (e.g., 'v5.5.1').

    Returns:
        Version: Parsed Version object.
    """
    if not tag_name:
        return Version("0.0.0")
    # Remove any prefix like 'v' or 'release-'
    version_str = re.sub(r"^[^\d]*", "", tag_name)
    try:
        return Version(version_str)
    except InvalidVersion:
        return Version("0.0.0")


def _get_latest_tag(tags: list[dict[str, str]]) -> str:
    """
    Get the latest version tag from a list of tags.

    Args:
        tags (list[dict[str, str]]): List of tags retrieved from the repository.

    Returns:
        str: The name of the latest version tag.
    """
    # Parse all version tags and sort them
    parsed_tags = [(_parse_version_tag(tag["name"]), tag["name"]) for tag in tags]
    sorted_tags = sorted(parsed_tags, key=lambda x: x[0])

    # Return the name of the latest tag
    return sorted_tags[-1][1]  # The last tag in the sorted list is the latest


def _get_latest_tag_version(repo_url: str) -> str | None:
    """
    Retrieve the latest tag from the repository.

    Args:
        repo_url (str): The URL of the repository tags.

    Returns:
        str | None: The name of the latest tag if found, else None.
    """
    try:
        response: requests.Response = requests.get(repo_url, timeout=MAX_TIMEOUT)
        response.raise_for_status()
        tags = response.json()
        if tags:
            return _get_latest_tag(tags)
        return None
    except requests.exceptions.RequestException:
        return None


def _get_gitlab_project_id(api_url: str, gitlab_url: str) -> str | None:
    """
    Retrieve the GitLab project ID based on the given URL.

    Args:
        api_url (str): The base URL of the GitLab API.
        gitlab_url (str): The URL of the GitLab project.

    Returns:
        int | None: The project ID if found, else None.
    """
    gitlab_project_path: str = gitlab_url.split("https://gitlab.com/")[1].replace(
        "/", "%2F"
    )
    request_url: str = f"{api_url}/{gitlab_project_path}"
    try:
        response: requests.Response = requests.get(request_url, timeout=MAX_TIMEOUT)
        response.raise_for_status()
        return response.json().get("id")
    except requests.exceptions.RequestException:
        return None


def _is_newer_version(local_version: str, remote_version: str) -> bool:
    """
    Compare two versions to determine if the remote version is newer than the local version.

    Args:
        local_version (str): The current local version of the software.
        remote_version (str): The version retrieved from the remote repository.

    Returns:
        bool: True if the remote version is newer, False otherwise.
    """
    try:
        local_ver = Version(local_version)
        remote_ver = Version(remote_version)
        return remote_ver > local_ver
    except InvalidVersion as e:
        # The project version is not PEP 440 compliant
        # Compare the versions lexicographically
        return remote_version > local_version


def _get_api_base_and_project_id(git_url: str) -> tuple[str, str, bool]:
    """
    Extract the API base URL and project ID from the Git URL.

    Args:
        git_url (str): The URL of the Git repository.

    Returns:
        tuple[str, str, bool]: The API base URL, project ID, and whether the repository is GitLab.
    """
    api_base: str = ""
    project_id: str | None = ""
    is_gitlab = False

    host: str | None = urlparse(git_url).hostname
    match host:
        case "github.com":
            api_base = "https://api.github.com/repos"
            project_id = git_url.split("https://github.com/")[1]
        case "gitlab.com":
            is_gitlab = True
            api_base = "https://gitlab.com/api/v4/projects"
            project_id = _get_gitlab_project_id(api_base, git_url)
            if not project_id:
                print("[red]ERROR[/]: Could not retrieve the GitLab project ID.")
                return "", "", False
        case "gitee.com":
            api_base = "https://gitee.com/api/v5/repos"
            project_id = git_url.split("https://gitee.com/")[1]
        case "codeberg.org" | "gitea.com" | "gitea.angry.im" | "git.cryto.net":
            api_base = f"https://{host}/api/v1/repos"
            project_id = git_url.split(f"https://{host}/")[1]
        case _:
            print("[red]ERROR[/]: Unsupported platform.")
            return "", "", False

    return api_base, project_id, is_gitlab


def check_updates(git_url: str, current_version: str) -> None:
    """
    Check if there is a newer version of the script available in the Git repository.

    Supported platforms:
    - GitHub
    - GitLab
    - Codeberg
    - Gitea
    - Gitea Angry
    - Git Cryto
    - Gitee

    Args:
        git_url (str): The URL of the Git repository.
        current_version (str): The current version of the script.
    """
    # Remove trailing slashes and '.git' from the URL
    git_url = git_url.rstrip("/").removesuffix(".git")
    api_base, project_id, is_gitlab = _get_api_base_and_project_id(git_url)
    if not project_id:
        return

    release_url: str = f"{api_base}/{project_id}/releases/latest"
    tag_url: str = f"{api_base}/{project_id}/tags"

    latest_version: Optional[str] = _get_latest_release_version(release_url, is_gitlab)
    if latest_version is None:  # Try to get the latest tag if no release found
        latest_version = _get_latest_tag_version(tag_url)

    if latest_version and _is_newer_version(current_version, latest_version):
        print(
            "\n[yellow]Newer version of the script available: "
            f"{latest_version}.\nPlease consider updating your version.[/]"
        )
    elif latest_version is None:
        print("[red]ERROR[/]: Could not check for updates. No releases or tags found.")
