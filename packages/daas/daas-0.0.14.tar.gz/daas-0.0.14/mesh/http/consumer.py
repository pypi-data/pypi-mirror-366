#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

import aiohttp

from mesh.context import URN
from mesh.macro import spi
from mesh.mpc import Consumer, Execution
from mesh.types import Reference


@spi("http")
class HTTPConsumer(Consumer):

    def __init__(self):
        self.session = aiohttp.ClientSession(base_url='/mpc/invoke')

    async def __aenter__(self):
        await self.start()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def start(self):
        pass

    async def consume(self, address: str, urn: URN, execution: Execution[Reference], inbound: bytes) -> bytes:
        request = self.session.post(
            url=f"http://{address}/mpc/invoke",
            data=inbound,
            headers={
                'Content-Type': 'application/json',
                'mesh-urn': urn.string(),
            })
        async with request as response:
            return await response.read()
