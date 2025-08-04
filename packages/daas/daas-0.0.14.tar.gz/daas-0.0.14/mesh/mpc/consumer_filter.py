#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from typing import Any, Dict

from mesh.cause import MeshCode, Codeable
from mesh.codec import Codec
from mesh.codec import Json
from mesh.context import Mesh
from mesh.macro import spi, ServiceLoader
from mesh.mpc.digest import Digest
from mesh.mpc.filter import Filter, Invoker, Invocation, CONSUMER
from mesh.psi import Header


@spi(name="consumer", pattern=CONSUMER, priority=1 - (1 << 32))
class ConsumerFilter(Filter):

    async def invoke(self, invoker: Invoker, invocation: Invocation) -> Any:
        codec = ServiceLoader.load(Codec).get(Json)
        consumer = Mesh.context().get_consumer()
        provider = Mesh.context().get_provider()

        attachments: Dict[str, str] = invocation.get_parameters().get_attachments()
        for key, value in Mesh.context().get_attachments().items():
            attachments[key] = value
        attachments[Header.MESH_TRACE_ID.key()] = Mesh.context().get_trace_id()
        attachments[Header.MESH_SPAN_ID.key()] = Mesh.context().get_span_id()
        attachments[Header.MESH_TIMESTAMP.key()] = f"{Mesh.context().get_timestamp()}"
        attachments[Header.MESH_RUN_MODE.key()] = f"{Mesh.context().get_run_mode()}"
        attachments[Header.MESH_URN.key()] = Mesh.context().get_urn()
        attachments[Header.MESH_CONSUMER.key()] = codec.encode_string(consumer)
        attachments[Header.MESH_PROVIDER.key()] = codec.encode_string(provider)

        digest = Digest()
        try:
            ret = await invoker.run(invocation)
            digest.write("C", MeshCode.SUCCESS.get_code())
            return ret
        except BaseException as e:
            if isinstance(e, Codeable):
                digest.write("C", e.get_code())
            else:
                digest.write("C", MeshCode.SYSTEM_ERROR.get_code())
            raise e
