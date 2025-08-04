#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from asyncio import CancelledError
from typing import Any
from urllib.parse import urlparse

import grpc
from grpc.aio import Server

import mesh.log as log
from mesh.cause import ValidationException
from mesh.grpx import GrpcBindableService, AsyncGrpcInterceptor
from mesh.macro import spi
from mesh.mpc import Provider
from mesh.tool import Tool


@spi("grpc")
class GrpcProvider(Provider):
    """
    Grpc provider wrap the grpc protocol implementation.
    """

    def __init__(self):
        self.interceptor = AsyncGrpcInterceptor()
        self.service = GrpcBindableService()
        self.address = ""
        self.server: Server = None

    async def start(self, address: str, tc: Any):
        self.address = address
        if not self.server:
            self.server = grpc.aio.server(
                handlers=[self.service],
                interceptors=[self.interceptor],
                options=[('grpc.max_message_length', 1 << 30),
                         ('grpc.max_send_message_length', 1 << 30),
                         ('grpc.max_receive_message_length', 1 << 30)],
                compression=grpc.Compression.Gzip,
            )
        if Tool.optional(address):
            raise ValidationException("GRPC address cant be empty.")
        parsed = urlparse(f"https://{address}")
        self.server.add_insecure_port(f"{parsed.hostname}:{parsed.port}")
        self.server.add_generic_rpc_handlers([self.service])
        await self.server.start()
        log.info(f"Listening and serving HTTP 2.0 on {address}")

    async def close(self):
        if not self.server:
            return
        try:
            await self.server.stop(grace=12)
        except CancelledError as e:
            pass
        finally:
            log.info(f"Graceful stop HTTP 2.0 serving on {self.address}")

    async def wait(self):
        if not self.server:
            return
        try:
            await self.server.wait_for_termination()
        except CancelledError as e:
            pass
