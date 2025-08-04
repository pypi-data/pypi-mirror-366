#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from abc import ABC, abstractmethod

import mesh.log as log
from mesh.cause import MeshCode, Codeable
from mesh.codec import Codec
from mesh.context import Mesh, URN
from mesh.macro import spi, ServiceLoader, Cause
from mesh.mpc.eden import Eden
from mesh.mpc.invoker import ServiceInvocation, Execution
from mesh.mpc.meshflag import MeshFlag
from mesh.psi import Context
from mesh.types import Outbound, Service

PROVIDER = "provider"
CONSUMER = "consumer"


@spi(PROVIDER)
class Transporter(ABC):

    @abstractmethod
    async def transport(self, ctx: Context, urn: str, buff: bytes) -> bytes:
        """
        Transport the stream.
        :param ctx:
        :param urn:
        :param buff:
        :return:
        """
        pass

    @staticmethod
    def get_codec(flag: str) -> type[Codec]:
        codec = ServiceLoader.load(Codec).get(MeshFlag.of_code(flag).get_name())
        if codec:
            return codec
        return ServiceLoader.load(Codec).get_default()


@spi(PROVIDER)
class ProviderTransporter(Transporter):

    async def transport(self, ctx: Context, urn: str, buff: bytes) -> bytes:
        return await Mesh.context_safe(self.transport_safe(ctx, urn, buff))

    async def transport_safe(self, ctx: Context, uname: str, buff: bytes) -> bytes:
        try:
            Mesh.context().rewrite_context(ctx)
            Mesh.context().rewrite_urn(uname)
            urn = URN.parse(uname)
            eden = ServiceLoader.load(Eden).get_default()
            codec = self.get_codec(urn.flag.codec)
            execution = eden.infer(uname)
            if execution is None:
                outbound = Outbound()
                outbound.code = MeshCode.NO_SERVICE.code
                outbound.message = f"No mpi named {urn.name}."
                return codec.encode(outbound)
            return await self.service(urn, codec, execution, buff)
        except BaseException as e:
            trace_id = Mesh.context().get_trace_id()
            span_id = Mesh.context().get_span_id()
            log.error(f"{trace_id}#{span_id} Invoke service {uname} with error.", e)
            outbound = Outbound()
            outbound.code = MeshCode.SYSTEM_ERROR.code
            outbound.message = str(e)
            outbound.cause = Cause.of(e)
            return ServiceLoader.load(Codec).get_default().encode(outbound)

    @staticmethod
    async def service(urn: URN, codec: Codec, execution: Execution[Service], buff: bytes) -> bytes:
        returns = execution.reflect()
        try:
            parameters = codec.decode(buff, execution.intype())
            invocation = ServiceInvocation(execution, execution.inspect(), parameters, execution, urn)
            result = await execution.run(invocation)
            returns.set_code(MeshCode.SUCCESS.get_code())
            returns.set_message(MeshCode.SUCCESS.get_message())
            returns.set_content(result)
            return codec.encode(returns)
        except BaseException as e:
            log.error("{}#{} Invoke service {} with error.",
                      Mesh.context().get_trace_id(), Mesh.context().get_trace_id(), Mesh.context().get_urn(), e)
            if isinstance(e, Codeable):
                returns.set_code(e.get_code())
                returns.set_message(e.get_message())
            else:
                returns.set_code(MeshCode.SYSTEM_ERROR.code)
                returns.set_message(str(e))
            returns.set_cause(Cause.of(e))
            return codec.encode(returns)


@spi(CONSUMER)
class ConsumerTransporter(Transporter):

    async def transport(self, ctx: Context, urn: str, buff: bytes) -> bytes:
        Mesh.context().rewrite_context(ctx)
        return b'unknown'
