#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from typing import Optional, List, Union, Dict, Any
from ray import serve
from dataclasses import dataclass, is_dataclass, fields, field
import yaml
import pathlib
from enum import Enum


@dataclass
class DeploymentConfig:
    deployment_name: str
    num_replicas: Optional[int] = 1
    enable: Optional[bool] = True
    num_cpus: Optional[float] = 0.0
    num_gpus: Optional[float] = 0.0
    params: Dict[Any, Any] = field(default_factory=dict)


@dataclass
class DeploymentMetadata:
    required: List[str] = field(default_factory=list)
    optional: Dict[str, Any] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    docstring: str = ""
    name: str = ""
    app_name: str = ""
    deployment: Optional[serve.Deployment] = None


@dataclass
class AppConfig:
    host: str = "localhost"
    port: int = 8001
    log_level: str = "info"
    allow_cors: bool = False
    version: str = "0.1.1"
    ray_config: List[DeploymentConfig] = field(default_factory=list)

    @classmethod
    def _from_dict(cls, data: dict):
        if "ray_config" in data:
            data["ray_config"] = [DeploymentConfig(**con) for con in data["ray_config"]]
        return cls(**data)

    @classmethod
    def from_yaml(cls, file_path: str | pathlib.Path):
        file_path = pathlib.Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        with file_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls._from_dict(data)

    def _to_dict(self) -> dict:
        def serialize(obj):
            if isinstance(obj, list):
                return [serialize(item) for item in obj]
            elif is_dataclass(obj):
                result = {}
                for f in fields(obj):
                    value = getattr(obj, f.name)
                    result[f.name] = serialize(value)
                return result
            elif isinstance(obj, Enum):
                return obj.value
            else:
                return obj

        return serialize(self)

    def to_yaml(self, file_path: Union[str, pathlib.Path]):
        data = self._to_dict()

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f, sort_keys=False, allow_unicode=True, default_flow_style=False
            )

    def get_registry(self, services: Optional[List[str]] = None):
        from vastgenserver.engine.ray.register import registry
        from vastgenserver.engine.ray.importer import DynamicImporter

        DynamicImporter.get_all_classes(services)

        keys = registry.keys()
        for key in keys:
            deployment_config = DeploymentConfig(key)
            app = registry.get(key)
            for required_params in app.required:
                if required_params not in deployment_config.params:
                    deployment_config.params[required_params] = None
            for optional_params in app.optional:
                if optional_params not in deployment_config.params:
                    deployment_config.params[optional_params] = app.optional[
                        optional_params
                    ]
            self.ray_config.append(deployment_config)
        return self
