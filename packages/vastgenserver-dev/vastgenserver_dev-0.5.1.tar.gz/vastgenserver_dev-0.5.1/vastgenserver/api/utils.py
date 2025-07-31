#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from fastapi import HTTPException, status
from vastgenserver.engine.ray.register import registry


def get_handle_by_name(name: str, stream: bool = False):
    if not registry.exists(name):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Deployment '{name}' not registered.",
        )
    handler = registry.handle(name, stream)

    if handler is None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Deployment '{name}' not enable.",
        )
    return handler
