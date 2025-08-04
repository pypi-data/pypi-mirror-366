#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from typing import Any, Dict

import mesh.log as log
from mesh.cause import MeshCode, Codeable, MeshException
from mesh.codec import Codec, Json
from mesh.context import Mesh
from mesh.macro import spi, ServiceLoader
from mesh.mpc.digest import Digest
from mesh.mpc.filter import Filter, Invoker, Invocation, PROVIDER
from mesh.psi import Header
from mesh.types import Location


@spi(name="provider", pattern=PROVIDER, priority=(1 << 32) - 1)
class ProviderFilter(Filter):

    async def invoke(self, invoker: Invoker, invocation: Invocation) -> Any:
        codec = ServiceLoader.load(Codec).get(Json)

        attachments: Dict[str, str] = invocation.get_parameters().get_attachments()
        if not attachments:
            attachments = {}
        attachments[Header.MESH_CONSUMER.key()] = attachments[Header.MESH_PROVIDER.key()]
        attachments[Header.MESH_PROVIDER.key()] = codec.encode_string(Mesh.localize(Location()))

        Mesh.context().decode(attachments)

        digest = Digest()
        try:
            ret = await invoker.run(invocation)
            digest.write("P", MeshCode.SUCCESS.get_code())
            return ret
        except BaseException as e:
            if isinstance(e, Codeable):
                digest.write("P", e.get_code())
            else:
                digest.write("P", MeshCode.SYSTEM_ERROR.get_code())
            if isinstance(e, MeshException):
                log.error(f"{digest.trace_id},{Mesh.context().get_urn()},{e.get_message}")
            raise e
