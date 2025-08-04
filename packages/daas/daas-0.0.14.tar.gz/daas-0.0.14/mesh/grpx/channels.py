#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

import random
from typing import Any, List, Dict, Callable, Optional

import grpc
from grpc import Compression
from grpc.aio import Channel, insecure_channel, StreamStreamMultiCallable, StreamUnaryMultiCallable, \
    UnaryStreamMultiCallable, UnaryUnaryMultiCallable, StreamStreamCall

from mesh.grpx.interceptor import AsyncGrpcInterceptor
from mesh.grpx.marshaller import GrpcMarshaller
from mesh.tool import Tool


class GrpcChannels:

    def __init__(self):
        self.channels: Dict[str, GrpcMultiplexChannel] = {}
        self.marshaller = GrpcMarshaller()
        self.serializer = self.marshaller.serialize
        self.deserializer = self.marshaller.deserialize
        self.interceptor = AsyncGrpcInterceptor()
        self.path = "/mpc/grpc"
        self.streams: Dict[str, GrpcMultiplexStream] = dict()

    def __exit__(self, exc_type, exc_val, exc_tb):
        for _, channel in self.channels.items():
            channel.close()

    def create_if_absent(self, address: str) -> "GrpcMultiplexChannel":
        channel = self.channels.get(address, None)
        if not channel:
            self.channels[address] = channel = GrpcMultiplexChannel(address, self.interceptor)
        return channel

    def create_stream(self, address: str) -> grpc.StreamStreamMultiCallable:
        channel = self.create_if_absent(address)
        return channel.stream_stream(self.path, self.serializer, self.deserializer)

    async def unary(self, address: str, inbound: bytes, timeout: Any, metadata: Any) -> bytes:
        channel = self.create_if_absent(address)
        c = channel.unary_unary(self.path, self.serializer, self.deserializer)
        return await c(inbound, timeout=timeout, metadata=metadata, wait_for_ready=True, compression=Compression.Gzip)

    async def stream(self, address: str, inbound: bytes, timeout: Any, metadata: Any) -> bytes:
        stream = self.streams.get(address, None)
        if stream is None:
            stream = self.streams[address] = GrpcMultiplexStream(address, lambda addr: self.create_stream(addr))
        return await anext(aiter(stream.next(inbound, timeout, metadata)))


class GrpcMultiplexStream:

    def __init__(self, address: str, streamer: Callable[[str], StreamStreamMultiCallable]):
        self.address = address
        self.stream = streamer(address)
        self.streamer = streamer

    def next(self, inbound: bytes, timeout: Any, metadata: Any) -> StreamStreamCall:
        return self.stream(inbound, timeout, metadata, None, True, Compression.Gzip)


class GrpcMultiplexChannel(Channel):
    """
    https://github.com/grpc/grpc/blob/598e171746576c5398388a4c170ddf3c8d72b80a/include/grpc/impl/codegen/grpc_types.h#L170
    """

    def __init__(self, address: str, *interceptors):
        self.address = address
        self.interceptors = interceptors
        self.channels: List[Channel] = []
        self.compression_options = {
            "none": grpc.Compression.NoCompression,
            "gzip": grpc.Compression.Gzip,
        }

    async def __aenter__(self):
        for channel in self.channels:
            await channel.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for channel in self.channels:
            await channel.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self, grace: Optional[float] = None):
        for channel in self.channels:
            await channel.close()

    def get_state(self, try_to_connect: bool = False) -> grpc.ChannelConnectivity:
        return self.select().get_state(try_to_connect)

    async def wait_for_state_change(self, last_observed_state: grpc.ChannelConnectivity) -> None:
        await self.select().wait_for_state_change(last_observed_state)

    async def channel_ready(self) -> None:
        await self.select().channel_ready()

    def unary_unary(self, method: str, request_serializer: Optional[Any] = None,
                    response_deserializer: Optional[Any] = None) -> UnaryUnaryMultiCallable:
        return self.select().unary_unary(method, request_serializer, response_deserializer)

    def unary_stream(self, method: str, request_serializer: Optional[Any] = None,
                     response_deserializer: Optional[Any] = None) -> UnaryStreamMultiCallable:
        return self.select().unary_stream(method, request_serializer, response_deserializer)

    def stream_unary(self, method: str, request_serializer: Optional[Any] = None,
                     response_deserializer: Optional[Any] = None) -> StreamUnaryMultiCallable:
        return self.select().stream_unary(method, request_serializer, response_deserializer)

    def stream_stream(self, method: str, request_serializer: Optional[Any] = None,
                      response_deserializer: Optional[Any] = None) -> StreamStreamMultiCallable:
        return self.select().stream_stream(method, request_serializer, response_deserializer)

    def default_compression(self) -> Any:
        return self.compression_options["gzip"]

    def reset(self, channel: grpc.Channel):
        self.channels.append(channel)

    def select(self) -> Channel:
        """
        grpc.ssl_target_name_override
        grpc.default_authority
        https://github.com/grpc/grpc/blob/master/include/grpc/impl/codegen/compression_types.h
        https://github.com/grpc/grpc/blob/master/include/grpc/impl/codegen/grpc_types.h
        """
        if self.channels.__len__() > 0:
            return self.channels[random.randint(0, self.channels.__len__() - 1)]

        for _ in range(Tool.get_max_channels()):
            options = self.default_options()
            channel = insecure_channel(self.address, options, self.default_compression(), self.interceptors)
            self.channels.append(channel)

        return self.channels[random.randint(0, self.channels.__len__() - 1)]

    def default_options(self):
        return [
            ("grpc.enable_retries", True),
            ("grpc.default_compression_algorithm", self.default_compression()),
            ("grpc.client_idle_timeout_ms", 1000 * 32),
            ("grpc.max_send_message_length", 1 << 30),
            ("grpc.max_receive_message_length", 1 << 30),
            ("grpc.max_connection_age_ms", 1000 * 60),
            ("grpc.max_connection_age_grace_ms", 1000 * 12),
            ("grpc.per_message_compression", True),
            ("grpc.per_message_decompression", True),
            ("grpc.enable_deadline_checking", True),
            ("grpc.keepalive_time_ms", 1000 * 12),
            ("grpc.keepalive_timeout_ms", 1000 * 12),
        ]
