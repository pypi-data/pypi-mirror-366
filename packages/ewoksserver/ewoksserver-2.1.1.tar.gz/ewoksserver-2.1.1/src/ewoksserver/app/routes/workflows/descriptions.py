from typing import Dict, Optional, Iterator

from ...backends import json_backend


_WORKFLOW_KEYWORDS = (
    "id",
    "label",
    "category",
    "keywords",
    "input_schema",
    "ui_schema",
)


def workflow_descriptions(
    root: json_backend.ResourceUrlType, keywords: Optional[Dict] = None
) -> Iterator[Dict]:
    for res in json_backend.resources(root):
        description = res["graph"]
        if not _include_resource(description.get("keywords", dict()), keywords):
            continue
        yield {
            key: value
            for key, value in description.items()
            if key in _WORKFLOW_KEYWORDS
        }


def _include_resource(res_keywords: dict, keywords: Optional[Dict] = None) -> bool:
    if keywords is None:
        return True
    return all(res_keywords.get(key) == value for key, value in keywords.items())
