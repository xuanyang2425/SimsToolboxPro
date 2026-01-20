from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class DownloadMeta:
    url: str
    domain: str
    item_id: str | None


class DownloadMetaService:
    def parse(self, url: str) -> DownloadMeta:
        parsed = urlparse(url)
        domain = parsed.netloc
        item_id = parsed.path.strip("/").split("/")[-1] or None
        return DownloadMeta(url=url, domain=domain, item_id=item_id)
