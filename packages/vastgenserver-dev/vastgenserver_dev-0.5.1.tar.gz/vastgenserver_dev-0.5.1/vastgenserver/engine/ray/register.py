#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
import random
import string
from ray import serve
from ray.serve.exceptions import RayServeException
from typing import Callable, Optional
import inspect
from vastgenserver.schema.config import DeploymentMetadata


def get_random_string(length=5):
    return "".join(random.sample(string.ascii_letters + string.digits, length))


class Registry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Registry, cls).__new__(cls)
            cls._instance._data = {}
        return cls._instance

    def get(self, key: str):
        return self._data.get(key)

    def add(self, key: str, value: list):
        if key in self._data:
            return
        self._data[key] = value

    def remove(self, key: str):
        if key in self._data:
            del self._data[key]

    def clear(self):
        self._data.clear()

    def exists(self, key: str):
        return key in self._data

    def handle(self, key: str, stream: bool = False):
        if not self.exists(key):
            return None
        metadata = self._data[key]
        try:
            app_handle = serve.get_app_handle(metadata.app_name).options(stream=stream)
        except RayServeException:
            return None
        return app_handle

    def keys(self):
        return self._data.keys()


registry = Registry()


def register(
    _class: Optional[Callable] = None,
    name: Optional[str] = None,
):

    def decorator(cls):
        class_name = cls.__name__
        init_method = cls.__init__

        signature = inspect.signature(init_method)
        parameters = signature.parameters

        param_info = DeploymentMetadata(
            docstring=inspect.getdoc(init_method) or "",
            name=class_name,
            app_name=class_name.lower() + "_" + get_random_string(5),
        )

        for name, param in parameters.items():
            if name == "self":
                continue

            annotation = (
                param.annotation
                if param.annotation != inspect.Parameter.empty
                else None
            )
            param_info.annotations[name] = str(annotation) if annotation else "Any"

            if param.default == inspect.Parameter.empty:
                param_info.required.append(name)
            else:
                param_info.optional[name] = param.default

        deployment = serve.deployment(cls)
        param_info.deployment = deployment
        registry.add(class_name, param_info)
        return cls

    if _class is None:
        return decorator
    else:
        return decorator(_class)
