#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from mesh.macro import mps
from mesh.psi import Endpoint, EndpointSticker


@mps
class MeshEndpoint(Endpoint, EndpointSticker[bytes, bytes]):

    async def fuzzy(self, buff: bytes) -> bytes:
        pass

    async def stick(self, varg: bytes) -> bytes:
        pass
