#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
from ray import serve
from vastgenserver.schema.config import DeploymentConfig
from typing import List
from vastgenserver.engine.ray.importer import DynamicImporter
from vastgenserver.engine.ray.utils import logger
from vastgenserver.engine.ray.register import registry


class RayManager:
    def __init__(self, deployment_list: List[DeploymentConfig]):
        logger.info("Initializing Ray Serve...")
        serve.start(proxy_location="Disabled")
        self.deployment_list = deployment_list
        for config in deployment_list:
            deployment_name = config.deployment_name
            DynamicImporter.get_class(deployment_name)
            app = registry.get(deployment_name)
            if app is None:
                raise ValueError(f"Deployment {deployment_name} not found in registry.")
            if config.enable is False:
                logger.info(f"Deployment {deployment_name} is disabled, skipping...")
                continue

            logger.info(f"Deploying {deployment_name} with name {app.app_name}...")
            ray_actor_options = {}
            if config.num_cpus != 0.0:
                ray_actor_options["num_cpus"] = config.num_cpus
            if config.num_gpus != 0.0:
                ray_actor_options["num_gpus"] = config.num_gpus
            handle = app.deployment.options(
                num_replicas=config.num_replicas, ray_actor_options=ray_actor_options
            ).bind(**config.params)
            serve.run(
                handle, name=app.app_name, route_prefix=f"/{app.app_name.lower()}"
            )

    def stop(self):
        logger.info("Shutting down Ray Serve...")
        # TODO: how to graceful delete apps on ray cluster?
        # for config in self.deployment_list:
        #     deployment_name = config.deployment_name
        #     app = registry.get(deployment_name)
        #     if app is not None:
        #         serve.delete(app.name)
        #         logger.info(f"Removing deployment {deployment_name} with name {app.name}...")
        #     else:
        #         logger.info(f"Deployment {deployment_name} not found in registry.")
