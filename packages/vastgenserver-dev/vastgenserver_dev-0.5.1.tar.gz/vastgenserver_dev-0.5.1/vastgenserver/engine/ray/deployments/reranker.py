#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from vastgenserver.schema.openai import RerankerReq, RerankerRes, RerankerData
from ray import serve

import numpy as np
from typing import List, Union

from transformers import AutoTokenizer
from tqdm.autonotebook import trange

from vastgenserver.engine.ray.common.embeddingx import EmbeddingX
from vastgenserver.engine.ray.register import register
from vastgenserver.engine.ray.utils import logger


@register
class Reranker:
    def __init__(
        self,
        model_path: str = "",
        torch_model_or_tokenizer: str = "",
        device_id: int = 0,
        batch_size: int = 1,
        max_seqlen: int = 8192,
        do_sigmod: bool = True,
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
        self.do_sigmod = do_sigmod

    def post_precess(self, outputs: np.ndarray):
        def sigmoid(x):
            return 1 / (1 + np.exp(-x))

        embeddings = outputs[:, 0]

        if self.do_sigmod:
            score = sigmoid(embeddings)
        else:
            score = embeddings

        if score.shape == (1, 1):
            score = np.squeeze(score, axis=0)
        else:
            score = np.squeeze(score)

        return score

    def infer_batch(self, sentences: List[List[str]]):
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

            token_embeddings = self.post_precess(out)
            outputs.extend(token_embeddings.tolist())

        logger.info(f"Reranker outputs: {outputs}")
        indexed_data = list(enumerate(outputs))
        sorted_data = sorted(indexed_data, key=lambda x: x[1], reverse=True)
        res = []
        for idx, score in sorted_data:
            ins = RerankerData(index=idx, score=float(score))
            res.append(ins)
        return res

    async def __call__(self, req: RerankerReq) -> RerankerRes:
        pairs = [[req.query, text] for text in req.documents]
        results = self.infer_batch(pairs)
        return RerankerRes(results=results)
