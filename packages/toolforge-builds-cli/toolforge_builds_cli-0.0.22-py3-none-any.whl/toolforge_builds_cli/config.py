from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from toolforge_weld.config import Config, Section, load_config


@dataclass
class BuildConfig(Section):
    _NAME_: str = field(default="builds", init=False)
    dest_repository: str = "tools-harbor.wmcloud.org"
    builder_image: str = "tools-harbor.wmcloud.org/toolforge/heroku-builder-classic:22"
    build_service_namespace: str = "image-build"
    admin_group_names: list[str] = field(default_factory=lambda: ["admins", "system:masters"])
    builds_endpoint: str = "/builds/v1"

    @classmethod
    def from_dict(cls, my_dict: dict[str, Any]):
        params = {}
        if "dest_repository" in my_dict:
            params["dest_repository"] = my_dict["dest_repository"]
        if "builder_image" in my_dict:
            params["builder_image"] = my_dict["builder_image"]
        if "build_service_namespace" in my_dict:
            params["build_service_namespace"] = my_dict["build_service_namespace"]
        if "admin_group_names" in my_dict:
            params["admin_group_names"] = my_dict["admin_group_names"]
        if "builds_endpoint" in my_dict:
            params["builds_endpoint"] = my_dict["builds_endpoint"]
        return cls(**params)


@lru_cache(maxsize=None)
def get_loaded_config() -> Config:
    return load_config(client_name="builds", extra_sections=[BuildConfig])
