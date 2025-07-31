#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from fastapi import APIRouter
from vastgenserver.schema.openai import RerankerReq, RerankerRes
from vastgenserver.api.utils import get_handle_by_name

reranker_router = APIRouter()


@reranker_router.post(
    "/rerank",
    tags=["Reranker"],
    response_model=RerankerRes,
)
async def run_example(
    request: RerankerReq,
) -> RerankerRes:
    handler = get_handle_by_name("Reranker")

    return await handler.remote(request)
