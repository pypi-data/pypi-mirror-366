#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from ray import serve
import logging

SERVE_LOGGER_NAME = "ray.serve"
logger = logging.getLogger(SERVE_LOGGER_NAME)
