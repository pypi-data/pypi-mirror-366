#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import collections
from typing import Callable, Union, Awaitable, List, Tuple

import grpc
from grpc.aio import UnaryUnaryCall, UnaryStreamCall, StreamUnaryCall, StreamStreamCall
from grpc.aio._typing import ResponseIterableType, RequestType, ResponseType, RequestIterableType

from mesh.mpc import Mesh
from mesh.psi import Header
from mesh.tool import Tool


class ClientCallDetails(
    collections.namedtuple('_ClientCallDetails',
                           ('method', 'timeout', 'metadata', 'credentials',
                            'wait_for_ready', 'compression')), grpc.ClientCallDetails):
    pass


class MeshInterceptor:
    Keys = [
        Header.MESH_INCOMING_PROXY,
        Header.MESH_OUTGOING_PROXY,
        Header.MESH_SUBSET,
        Header.MESH_VERSION,
        Header.MESH_TIMESTAMP,
        Header.MESH_RUN_MODE,
        # INC
        Header.MESH_TECH_PROVIDER_CODE,
        Header.MESH_TOKEN,
        Header.MESH_SRC_IDC,
        Header.MESH_DST_IDC,
        Header.MESH_SESSION_ID
    ]

    @staticmethod
    def context_metadata() -> List[Tuple[str, str]]:
        # python metadata must be lowercase
        attachments = Mesh.context().get_attachments()
        metadata = []
        Header.MESH_URN.append(metadata, Mesh.context().get_urn())
        Header.MESH_TRACE_ID.append(metadata, Mesh.context().get_trace_id())
        Header.MESH_SPAN_ID.append(metadata, Mesh.context().get_span_id())
        Header.MESH_SRC_IDC.append(metadata, Mesh.context().get_consumer().id)
        Header.MESH_INCOMING_HOST.append(metadata, f"{Tool.get_mesh_name()}@{str(Tool.get_mesh_runtime())}")
        Header.MESH_OUTGOING_HOST.append(metadata, attachments.get(Header.MESH_INCOMING_HOST.key(), ''))

        for mk in GrpcInterceptor.Keys:
            mk.append(metadata, attachments.get(mk.key(), ''))

        return metadata

    @staticmethod
    def client_context(ctx):
        wait_for_ready = ctx.wait_for_ready if hasattr(ctx, 'wait_for_ready') else None
        compression = ctx.compression if hasattr(ctx, 'compression') else None
        credentials = ctx.credentials if hasattr(ctx, 'credentials') else None
        return ClientCallDetails(ctx.method, ctx.timeout, ctx.metadata, credentials, wait_for_ready, compression)

    @staticmethod
    def server_context(handler_call_details):
        """

        :param handler_call_details:
        :return:
        """
        pass


class GrpcInterceptor(MeshInterceptor,
                      grpc.ServerInterceptor,
                      grpc.StreamStreamClientInterceptor,
                      grpc.StreamUnaryClientInterceptor,
                      grpc.UnaryStreamClientInterceptor,
                      grpc.UnaryUnaryClientInterceptor, ):

    def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        return continuation(self.client_context(client_call_details), request_iterator)

    def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        return continuation(self.client_context(client_call_details), request_iterator)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        return continuation(self.client_context(client_call_details), request)

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return continuation(self.client_context(client_call_details), request)

    def intercept_service(self, continuation, handler_call_details):
        self.server_context(handler_call_details)
        return continuation(handler_call_details)


class AsyncGrpcInterceptor(MeshInterceptor,
                           grpc.aio.ServerInterceptor,
                           grpc.aio.StreamStreamClientInterceptor,
                           grpc.aio.StreamUnaryClientInterceptor,
                           grpc.aio.UnaryStreamClientInterceptor,
                           grpc.aio.UnaryUnaryClientInterceptor, ):

    async def intercept_service(self,
                                continuation: Callable[[grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]],
                                caller: grpc.HandlerCallDetails) -> grpc.RpcMethodHandler:
        self.server_context(caller)
        return await continuation(caller)

    async def intercept_stream_stream(self, continuation: Callable[
        [ClientCallDetails, RequestType], StreamStreamCall
    ], client_call_details: ClientCallDetails, request_iterator: RequestIterableType) -> Union[
        ResponseIterableType, StreamStreamCall]:
        return continuation(self.client_context(client_call_details), request_iterator)

    async def intercept_stream_unary(self, continuation: Callable[
        [ClientCallDetails, RequestType], StreamUnaryCall
    ], client_call_details: ClientCallDetails, request_iterator: RequestIterableType) -> StreamUnaryCall:
        return await continuation(self.client_context(client_call_details), request_iterator)

    async def intercept_unary_stream(self, continuation: Callable[
        [ClientCallDetails, RequestType], UnaryStreamCall
    ], client_call_details: ClientCallDetails, request: RequestType) -> Union[ResponseIterableType, UnaryStreamCall]:
        return continuation(self.client_context(client_call_details), request)

    async def intercept_unary_unary(self, continuation: Callable[
        [ClientCallDetails, RequestType], UnaryUnaryCall
    ], client_call_details: ClientCallDetails, request: RequestType) -> Union[UnaryUnaryCall, ResponseType]:
        return await continuation(self.client_context(client_call_details), request)
