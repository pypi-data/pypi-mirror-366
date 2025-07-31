#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from fastapi import APIRouter
from vastgenserver.schema.openai import EmbeddingReq, EmbeddingRes
from vastgenserver.api.utils import get_handle_by_name

embedding_router = APIRouter()


@embedding_router.post(
    "/embeddings",
    tags=["Embedding"],
    response_model=EmbeddingRes,
)
async def run_embeddings(
    request: EmbeddingReq,
) -> EmbeddingRes:
    handler = get_handle_by_name("Embedding")

    return await handler.remote(request)
