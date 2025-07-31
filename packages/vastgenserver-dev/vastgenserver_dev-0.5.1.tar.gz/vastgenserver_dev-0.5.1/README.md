# VastGenServer


## Installation

1. download vastgenserver*.whl package from minio
2. pip install vastgenserver*.whl

## Usage

1. vastgenserver list
2. vastgenserver service --gen-config your_config.yaml --service-list embedding
3. modify your_config.yaml, such as: host, port, model_path, etc.
4. vastgenserver service --run-config your_config.yaml

> Note: different service depend on different python packages, please install them before running.
## Deploy

## Embedding or Reranker

If you want to deploy embedding or reranker service,you need to install the following requirements manually.

```txt
vaststreamx
transformers
numpy
```
