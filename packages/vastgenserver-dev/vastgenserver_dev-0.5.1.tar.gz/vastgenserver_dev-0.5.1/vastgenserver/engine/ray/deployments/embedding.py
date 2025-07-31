#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from vastgenserver.schema.openai import EmbeddingReq, EmbeddingRes, EmbeddingData
from ray import serve

import numpy as np
from typing import List, Union

from transformers import AutoTokenizer
from tqdm.autonotebook import trange

from vastgenserver.engine.ray.common.embeddingx import EmbeddingX
from vastgenserver.engine.ray.register import register


@register
class Embedding:
    def __init__(
        self,
        model_path: str = "",
        torch_model_or_tokenizer: str = "",
        device_id: int = 0,
        batch_size: int = 1,
        max_seqlen: int = 8192,
    ):
        self.device_id = device_id
        self.input_id = 0
        self.embeddingx = EmbeddingX(
            model_prefix_path=model_path,
            device_id=device_id,
            batch_size=batch_size,
        )

        self.torch_model_or_tokenizer = torch_model_or_tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.torch_model_or_tokenizer, trust_remote_code=True
        )

        self.max_seqlen = max_seqlen
        self.batch_size = batch_size

    def infer_batch(self, sentences: Union[str, List[str]]):
        if isinstance(sentences, str):
            sentences = [sentences]

        disable = False
        if len(sentences) < 3:
            disable = True

        outputs = []
        for start_index in trange(
            0, len(sentences), self.batch_size, desc="Batches", disable=disable
        ):
            sentences_batch = sentences[start_index : start_index + self.batch_size]
            features = self.tokenizer(
                sentences_batch,
                padding="max_length",
                truncation=True,
                max_length=self.max_seqlen,
                return_tensors="np",
            )

            features["token_type_ids"] = np.zeros(
                features["input_ids"].shape, dtype=np.int32
            )
            # default order array
            vsx_inputs = [
                features["input_ids"],
                features["attention_mask"],
                features["token_type_ids"],
                features["attention_mask"],
                features["attention_mask"],
                features["attention_mask"],
            ]

            # split to batches
            vsx_inputs = np.concatenate(vsx_inputs, axis=0)
            vsx_inputs = np.split(vsx_inputs, vsx_inputs.shape[0], axis=0)

            out = self.embeddingx.infer_batch(vsx_inputs)
            out = out[:, 0]
            for o in out.tolist():
                outputs.append(EmbeddingData(embedding=o))
        return outputs

    async def __call__(self, req: EmbeddingReq) -> EmbeddingRes:
        data = self.infer_batch(req.input)
        return EmbeddingRes(data=data, model=req.model)
