
# 
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
# 
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# 
from typing import Union, Dict
import vaststreamx as vsx
import numpy as np


class EmbeddingX:
    def __init__(
        self,
        model_prefix_path: Union[str, Dict[str, str]],
        device_id: int = 0,
        batch_size: int = 1,
    ):
        self.device_id = device_id
        self.input_id = 0

        self.attr = vsx.AttrKey
        self.device = vsx.set_device(self.device_id)
        self.model = vsx.Model(model_prefix_path, batch_size)
        self.embedding_op = vsx.Operator(vsx.OpType.BERT_EMBEDDING_OP)
        self.graph = vsx.Graph(do_copy=False)
        self.model_op = vsx.ModelOperator(self.model)
        self.graph.add_operators(self.embedding_op, self.model_op)

        self.stream = vsx.Stream(self.graph, vsx.StreamBalanceMode.ONCE)
        self.stream.register_operator_output(self.model_op)
        self.stream.build()

    def infer_batch(self, vsx_inputs):
        vsx_batches = []
        for i in range(len(vsx_inputs) // 6):
            vsx_batch = []
            for inp in vsx_inputs[i :: len(vsx_inputs) // 6]:
                vsx_batch.append(
                    vsx.from_numpy(
                        np.array(inp, dtype=np.int32),
                        self.device_id if hasattr(self, "device_id") else 0,
                    )
                )
            vsx_batches.append(vsx_batch)
        self.stream.run_async(vsx_batches)
        vsx_outputs = self.stream.get_operator_output(self.model_op)
        return np.array(
            [vsx.as_numpy(vsx_outputs[i][0]) for i in range(len(vsx_outputs))]
        )
