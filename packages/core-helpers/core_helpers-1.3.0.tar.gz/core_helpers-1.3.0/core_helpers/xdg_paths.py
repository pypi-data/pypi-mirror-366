"""XDG Base Directory Specification paths."""

from enum import Enum
from pathlib import Path
from typing import Callable

from platformdirs import (site_cache_path, site_config_path, site_data_path,
                          site_runtime_path, user_cache_path, user_config_path,
                          user_data_path, user_desktop_path,
                          user_documents_path, user_downloads_path,
                          user_log_path, user_music_path, user_pictures_path,
                          user_runtime_path, user_state_path, user_videos_path)


# Enum for path types
class PathType(Enum):
    CACHE = "cache"
    CONFIG = "config"
    DATA = "data"
    LOG = "log"
    RUNTIME = "runtime"
    STATE = "state"
    SITE_CACHE = "site_cache"
    SITE_CONFIG = "site_config"
    SITE_DATA = "site_data"
    SITE_RUNTIME = "site_runtime"
    DESKTOP = "desktop"
    DOCUMENTS = "documents"
    DOWNLOADS = "downloads"
    MUSIC = "music"
    PICTURES = "pictures"
    VIDEOS = "videos"


# Mapping app directories
APP_DIRS: dict[PathType, Callable] = {
    PathType.CACHE: user_cache_path,
    PathType.CONFIG: user_config_path,
    PathType.DATA: user_data_path,
    PathType.LOG: user_log_path,
    PathType.RUNTIME: user_runtime_path,
    PathType.STATE: user_state_path,
    PathType.SITE_CACHE: site_cache_path,
    PathType.SITE_CONFIG: site_config_path,
    PathType.SITE_DATA: site_data_path,
    PathType.SITE_RUNTIME: site_runtime_path,
}
# Mapping home directories
HOME_DIRS: dict[PathType, Callable] = {
    PathType.DESKTOP: user_desktop_path,
    PathType.DOCUMENTS: user_documents_path,
    PathType.DOWNLOADS: user_downloads_path,
    PathType.MUSIC: user_music_path,
    PathType.PICTURES: user_pictures_path,
    PathType.VIDEOS: user_videos_path,
}


def get_user_path(package: str, path_type: PathType) -> Path:
    """
    Return the requested path for the specified path type (e.g., 'cache', 'config', 'data', 'log').

    Args:
        package (str): The name of the package or project.
        path_type (PathType): The type of path requested.

    Returns:
        Path: The path to the requested directory.
    """
    path_func = APP_DIRS.get(path_type)
    if path_func:
        return path_func(appname=package, ensure_exists=True).resolve()
    path_func = HOME_DIRS.get(path_type)
    if path_func:
        return path_func().resolve()
    raise ValueError(f"Unsupported path type: {path_type}")
