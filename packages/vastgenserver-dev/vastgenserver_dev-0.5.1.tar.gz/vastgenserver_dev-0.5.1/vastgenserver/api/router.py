
# 
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
# 
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# 
from fastapi import FastAPI
from vastgenserver.api.openai.base import openai_router


def include_routers(app: FastAPI):
    app.include_router(openai_router)
