#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import Dict, Iterator, Any, AsyncIterator

import grpc

from mesh.grpx.marshaller import GrpcMarshaller
from mesh.macro import ServiceLoader
from mesh.mpc import Transporter, PROVIDER, MeshContext
from mesh.psi import Context


class GrpcBindableService(grpc.GenericRpcHandler):

    def __init__(self):
        self.marshaller = GrpcMarshaller()
        self.handlers = grpc.method_handlers_generic_handler("mpc", self.grpc_handlers())

    def grpc_handlers(self) -> Dict[str, grpc.RpcMethodHandler]:
        return {
            "grpc": grpc.stream_stream_rpc_method_handler(
                self.stream_stream,
                request_deserializer=self.marshaller.deserialize,
                response_serializer=self.marshaller.serialize,
            ),
        }

    def service(self, handler_call_details):
        return self.handlers.service(handler_call_details)

    async def stream_stream(self, iterator: AsyncIterator[Any], ctx: grpc.aio.ServicerContext):
        ctx = self.context(ctx)
        transporter = ServiceLoader.load(Transporter).get(PROVIDER)
        async for buff in iterator:
            yield await transporter.transport(ctx, ctx.get_urn(), buff)

    @staticmethod
    def context(ctx: grpc.aio.ServicerContext) -> Context:
        metadata = ctx.invocation_metadata()
        return MeshContext.create_with_mapping(metadata)


class Transformer(Iterator[Any]):
    def __init__(self, iterator: Iterator[Any], ctx: Context):
        self.iterator = iterator
        self.transporter = ServiceLoader.load(Transporter).get(PROVIDER)
        self.ctx = ctx

    def __iter__(self):
        return self

    def __next__(self):
        buff = next(self.iterator)
        return self.transporter.transport(self.ctx, self.ctx.get_urn(), buff)
