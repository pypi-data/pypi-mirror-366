
# 
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
# 
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# 
import importlib
from typing import Type, Dict, List, Optional
from functools import lru_cache

# add your custom deployments here
CLASS_MAPPING = {
    "Example": "vastgenserver.engine.ray.deployments.example",
    "ExampleStream": "vastgenserver.engine.ray.deployments.example",
    "ExampleWithParams": "vastgenserver.engine.ray.deployments.example",
    "Embedding": "vastgenserver.engine.ray.deployments.embedding",
    "Reranker": "vastgenserver.engine.ray.deployments.reranker",
}


def get_all_services():
    return CLASS_MAPPING.keys()


class DynamicImporter:
    _cache: Dict[str, Type] = {}

    @classmethod
    @lru_cache(maxsize=32)
    def get_class(cls, class_name: str) -> Type:
        if class_name in cls._cache:
            return cls._cache[class_name]

        if class_name not in CLASS_MAPPING:
            raise ValueError(f"class {class_name} not exists in CLASS_MAPPING")

        module_path = CLASS_MAPPING[class_name]

        try:
            module = importlib.import_module(module_path)
            class_obj = getattr(module, class_name)
            cls._cache[class_name] = class_obj
            return class_obj
        except ImportError as e:
            raise ImportError(
                f"import {class_name} from {module_path} failed - {str(e)} - skipping"
            )
        except AttributeError:
            raise AttributeError(f"module {module_path} not found {class_name}")

    @classmethod
    def get_all_classes(cls, services: Optional[List[str]] = None) -> Dict[str, Type]:
        results = {}
        if services is None:
            services = get_all_services()
        for class_name in CLASS_MAPPING:
            if class_name not in services:
                continue
            try:
                results[class_name] = cls.get_class(class_name)
            except Exception as e:
                print(f"{str(e)}")
        return results
