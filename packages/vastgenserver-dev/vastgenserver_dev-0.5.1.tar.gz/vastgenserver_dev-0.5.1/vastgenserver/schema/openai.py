#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from pydantic import BaseModel, Field
from typing import List, Union, Any


class ExampleReq(BaseModel):
    text: str = Field(..., description="text of the example request")


class ExampleRes(BaseModel):
    text: str = Field(..., description="text of the example response")


class ExampleStreamReq(BaseModel):
    count: int = Field(
        ..., description="number of times to loop in the example stream request"
    )


class ExampleParamsReq(BaseModel):
    text: str = Field(..., description="text of the example params request")


class ExampleParamsRes(BaseModel):
    text: str = Field(..., description="text of the example params response")


class EmbeddingReq(BaseModel):
    model: str = Field(..., description="model name for the embedding request")
    input: Union[str, List[str]] = Field(
        ..., description="text of the embedding request"
    )


class RerankerReq(BaseModel):
    model: str = Field(..., description="model name for the reranker request")
    query: str = Field(..., description="query of the reranker request")
    documents: List[str] = Field(..., description="documents of the reranker request")


class EmbeddingData(BaseModel):
    embedding: List[float]


class EmbeddingRes(BaseModel):
    data: List[EmbeddingData]
    model: str


class RerankerData(BaseModel):
    index: int = Field(..., description="index of the reranker response")
    score: float = Field(..., description="score of the reranker response")


class RerankerRes(BaseModel):
    results: List[RerankerData] = Field(
        ..., description="scores of the reranker response"
    )
