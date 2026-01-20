from __future__ import annotations

from .downloader import DownloaderModule
from .mod_manager import ModManagerModule


def load_modules() -> list[object]:
    return [DownloaderModule(), ModManagerModule()]
