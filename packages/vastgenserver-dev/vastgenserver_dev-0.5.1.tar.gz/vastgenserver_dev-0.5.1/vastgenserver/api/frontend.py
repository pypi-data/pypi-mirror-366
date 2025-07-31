#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from vastgenserver.api.router import include_routers
from vastgenserver.schema.config import AppConfig
from vastgenserver.engine.ray.manager import RayManager
from vastgenserver.engine.ray.utils import logger


class FastApiFrontend:
    def __init__(
        self,
        app_config: AppConfig,
    ):
        self.host = app_config.host
        self.port = app_config.port
        self.log_level = app_config.log_level
        self.allow_cors = app_config.allow_cors
        self.version = app_config.version

        self.use_ray = (
            app_config.ray_config is not None and len(app_config.ray_config) > 0
        )

        if self.use_ray:
            self.ray_manager = RayManager(app_config.ray_config)

        self.app = self._create_app()

    def __del__(self):
        self.stop()

    def start(self):
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level=self.log_level,
            timeout_keep_alive=5,
        )
        server = uvicorn.Server(config)
        server.run()

    def stop(self):
        # if self.use_ray:
        #     self.ray_manager.stop()
        pass

    def _create_app(self):
        app = FastAPI(
            title="OpenAI API",
            description="The OpenAI REST API.",
            version=self.version,
        )

        include_routers(app)

        if self.allow_cors:
            self._add_cors_middleware(app)

        return app

    def _add_cors_middleware(self, app: FastAPI):
        # Allow API calls through browser /docs route for debug purposes
        origins = [
            "http://0.0.0.0",
        ]

        logger.warning(f"Adding CORS for the following origins: {origins}")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
