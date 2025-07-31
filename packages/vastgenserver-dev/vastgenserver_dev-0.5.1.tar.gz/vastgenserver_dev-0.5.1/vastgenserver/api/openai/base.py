#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from fastapi import APIRouter
from vastgenserver.api.openai.example import example_router
from vastgenserver.api.openai.embedding import embedding_router
from vastgenserver.api.openai.reranker import reranker_router

openai_router = APIRouter(prefix="/v1", tags=["OPENAI API"])
openai_router.include_router(example_router)
openai_router.include_router(embedding_router)
openai_router.include_router(reranker_router)
