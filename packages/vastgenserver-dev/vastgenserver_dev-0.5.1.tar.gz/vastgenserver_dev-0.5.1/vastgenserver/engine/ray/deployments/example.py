#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from ray import serve
from vastgenserver.schema.openai import (
    ExampleReq,
    ExampleRes,
    ExampleStreamReq,
    ExampleParamsReq,
    ExampleParamsRes,
)
from typing import Generator
from vastgenserver.engine.ray.utils import logger

from vastgenserver.engine.ray.register import register


@register
class Example:
    def __init__(self):
        logger.info("Init Example...")

    def run_example(self, input: str) -> str:
        return f"Hello {input}!"

    async def __call__(self, req: ExampleReq) -> ExampleRes:
        text = self.run_example(req.text)
        return ExampleRes(text=text)


@register
class ExampleStream:
    def __init__(self):
        logger.info("Init ExampleStream...")

    async def __call__(self, req: ExampleStreamReq) -> Generator[str, None, None]:
        loop_count = req.count if req.count else 5
        for i in range(loop_count):
            yield f"Streamed message {i + 1} of {loop_count}"
        yield "Stream ended."


@register
class ExampleWithParams:
    def __init__(
        self,
        int_param: int = 10,
        str_param: str = "default",
        float_param: float = 1.0,
        bool_param: bool = True,
        list_param: list = None,
    ):
        logger.info("Init ExampleWithParams...")
        logger.info(
            f"Params: int_param={int_param}, str_param={str_param}, "
            f"float_param={float_param}, bool_param={bool_param}, "
            f"list_param={list_param}"
        )

    async def __call__(self, req: ExampleParamsReq) -> ExampleParamsRes:
        return ExampleParamsRes(text="Received params: " + req.text)
