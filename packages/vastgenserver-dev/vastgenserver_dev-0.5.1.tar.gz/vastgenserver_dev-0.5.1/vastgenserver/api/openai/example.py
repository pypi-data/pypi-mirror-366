#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from fastapi import APIRouter
from vastgenserver.schema.openai import (
    ExampleReq,
    ExampleRes,
    ExampleStreamReq,
    ExampleParamsReq,
    ExampleParamsRes,
)
from vastgenserver.api.utils import get_handle_by_name

from fastapi.responses import StreamingResponse

example_router = APIRouter()


@example_router.post(
    "/example",
    tags=["Example"],
    response_model=ExampleRes,
)
async def run_example(
    request: ExampleReq,
) -> ExampleRes:
    handler = get_handle_by_name("Example")

    return await handler.remote(request)


@example_router.post(
    "/example_stream",
    tags=["Example"],
)
async def run_example_stream(
    request: ExampleStreamReq,
) -> StreamingResponse:
    handler = get_handle_by_name("ExampleStream", stream=True)

    response = handler.remote(request)
    return StreamingResponse(response, media_type="text/event-stream")


@example_router.post(
    "/example_params",
    tags=["Example"],
    response_model=ExampleParamsRes,
)
async def run_example_params(
    request: ExampleParamsReq,
) -> ExampleParamsRes:
    handler = get_handle_by_name("ExampleWithParams")

    return await handler.remote(request)
