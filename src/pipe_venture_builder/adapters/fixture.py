"""Sanitized fixture source that exercises the production adapter boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from pipe_venture_builder.inventory.safety import read_allowlisted_text

from .contracts import SourceContractFailure, SourcePayload, UnsafeSourcePayload
from .safety import payload_is_safe


class FixtureInventorySource:
    """Read bounded connector pages from a non-sensitive tracked fixture."""

    def __init__(
        self,
        path: str | Path,
        *,
        source_system: str,
        container_type: str,
    ) -> None:
        self._path = Path(path)
        self.source_system = source_system
        self.container_type = container_type

    def read(
        self,
        container_id: str,
        *,
        limit: int,
        max_pages: int,
    ) -> SourcePayload:
        result = read_allowlisted_text(self._path)
        if result.status == "blocked":
            raise UnsafeSourcePayload()
        if result.status != "safe" or result.text is None:
            raise SourceContractFailure()
        try:
            fixture = json.loads(result.text)
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise SourceContractFailure() from exc
        if not payload_is_safe(fixture):
            raise UnsafeSourcePayload()
        if not isinstance(fixture, dict):
            raise SourceContractFailure()
        if fixture.get("sourceSystem") != self.source_system:
            raise SourceContractFailure()
        container = fixture.get("container")
        pages = fixture.get("pages")
        if not isinstance(container, dict) or not isinstance(pages, list):
            raise SourceContractFailure()
        if str(container.get("requestedId")) != container_id:
            raise SourceContractFailure()

        items: list[Mapping[str, Any]] = []
        pages_read = 0
        truncated = False
        for page_index, page in enumerate(pages):
            if page_index >= max_pages:
                truncated = True
                break
            if not isinstance(page, dict) or not isinstance(page.get("items"), list):
                raise SourceContractFailure()
            pages_read += 1
            for item in page["items"]:
                if not isinstance(item, dict):
                    raise SourceContractFailure()
                if len(items) >= limit:
                    truncated = True
                    break
                items.append(item)
            if truncated:
                break
        if pages_read < len(pages):
            truncated = True
        return SourcePayload(
            container=container,
            items=tuple(items),
            pages_read=pages_read,
            truncated=truncated,
        )
