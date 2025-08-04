#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

import time
from typing import Dict, Any, Optional, Type

import mesh.log as log
from mesh.codec import Codec, Json
from mesh.context.urn import LOCAL_MDC
from mesh.macro import ServiceLoader
from mesh.macro import T
from mesh.psi import Key, RunMode, Context, Header
from mesh.psi.context import Queue
from mesh.tool import Tool
from mesh.types import Principal, Location, Environ


class MeshContext(Context):

    @staticmethod
    def create_with_mapping(metadata: tuple[str, str]) -> Context:
        if metadata is None:
            return MeshContext.create()
        mtx = MeshContext()
        for (name, value) in metadata:
            std_name = name.replace("_", "-").lower()
            if std_name == Header.MESH_URN.key() or std_name == 'authority':
                mtx.urn = value
                mtx.attachments[Header.MESH_URN.key()] = value
                continue
            if std_name == Header.MESH_TRACE_ID.key():
                mtx.trace_id = value
                mtx.attachments[Header.MESH_TRACE_ID.key()] = value
                continue
            if std_name == Header.MESH_SPAN_ID.key():
                mtx.span_id = value
                mtx.attachments[Header.MESH_SPAN_ID.key()] = value
                continue
            mtx.attachments[std_name] = value
        return mtx

    @staticmethod
    def create() -> "MeshContext":
        return MeshContext()

    @staticmethod
    def environ() -> Environ:
        env = Environ()
        env.mdc = LOCAL_MDC
        return env

    @staticmethod
    def localize(self: Location):
        env = MeshContext.environ()
        self.mdc = env.mdc
        self.ip = Tool.get_mesh_direct()
        self.host = Tool.get_hostname()
        self.port = f"{Tool.get_mesh_runtime().port}"
        self.name = Tool.get_mesh_name()
        return self

    def __init__(self):
        self.trace_id = Tool.new_trace_id()
        self.span_id = Tool.new_span_id("", 0)
        self.timestamp = int(time.time() * 1000)
        self.run_mode = RunMode.ROUTINE.value
        self.urn = ''
        self.calls = 0
        self.consumer = self.localize(Location())
        self.provider = self.localize(Location())
        self.attachments = dict()
        self.attributes = dict()
        self.principals = Queue()

    def get_trace_id(self) -> str:
        return self.trace_id

    def get_span_id(self) -> str:
        return self.span_id

    def get_timestamp(self) -> int:
        return self.timestamp

    def get_run_mode(self) -> int:
        return self.run_mode

    def get_urn(self) -> str:
        return self.urn

    def get_consumer(self) -> Location:
        return self.consumer

    def get_provider(self) -> Location:
        return self.provider

    def get_attachments(self) -> Dict[str, str]:
        return self.attachments

    def get_principals(self) -> Queue[Principal]:
        return self.principals

    def get_attributes(self) -> Dict[str, Any]:
        return self.attributes

    def get_attribute(self, key: Key[T]) -> T:
        return self.attributes.get(key.name, None)

    def set_attribute(self, key: Key[T], value: T) -> None:
        self.attributes[key.name] = value

    def rewrite_urn(self, urn: str) -> None:
        self.urn = urn

    def rewrite_context(self, another: Context) -> None:
        if Tool.required(another.get_trace_id()):
            self.trace_id = another.get_trace_id()
        if Tool.required(another.get_span_id()):
            self.span_id = another.get_span_id()
        if another.get_timestamp() > 0:
            self.timestamp = another.get_timestamp()
        if RunMode.ROUTINE.value != another.get_run_mode():
            self.run_mode = another.get_run_mode()
        if Tool.required(another.get_urn()):
            self.urn = another.get_urn()
        if Tool.required(another.get_consumer()):
            self.consumer = another.get_consumer()
        if Tool.required(another.get_provider()):
            self.provider = another.get_provider()
        if Tool.required(another.get_attachments()):
            for key, value in another.get_attachments().items():
                self.attachments[key] = value
        if Tool.required(another.get_attributes()):
            for key, value in another.get_attributes().items():
                self.attributes[key] = value
        if Tool.required(another.get_principals()):
            for value in another.get_principals():
                self.principals.append(value)

    def resume(self) -> Context:
        self.calls += 1
        context = MeshContext()
        context.rewrite_context(self)
        return context

    def encode(self) -> Dict[str, str]:
        return self.get_attachments()

    def decode(self, attachments: Dict[str, str]) -> None:
        if not attachments:
            attachments = {}
        codec = ServiceLoader.load(Codec).get(Json)
        trace_id = attachments.get(Header.MESH_TRACE_ID.key(), Tool.new_trace_id())
        span_id = attachments.get(Header.MESH_SPAN_ID.key(), Tool.new_span_id("", 0))
        timestamp = attachments.get(Header.MESH_TIMESTAMP.key(), '')
        run_mode = attachments.get(Header.MESH_RUN_MODE.key(), '')
        urn = attachments.get(Header.MESH_URN.key())
        cstr = attachments.get(Header.MESH_CONSUMER.key(), '{}')
        consumer: Location = codec.decode_string(cstr, Type[Location])
        pstr = attachments.get(Header.MESH_PROVIDER.key(), '{}')
        provider: Location = codec.decode_string(pstr, Type[Location])

        # Refresh context
        context = MeshContext()
        context.trace_id = trace_id
        context.span_id = span_id
        context.timestamp = self.resolve_timestamp(timestamp)
        context.run_mode = self.resolve_run_mode(run_mode)
        context.urn = urn
        context.consumer = consumer
        context.provider = provider
        for key, value in attachments.items():
            context.attachments[key] = value

        self.rewrite_context(context)

    @staticmethod
    def resolve_timestamp(v: str) -> int:
        if Tool.optional(v):
            return int(time.time() * 1000)
        try:
            return int(v)
        except Exception as e:
            log.error("Parse timestamp failed. ", e)
            return int(time.time() * 1000)

    @staticmethod
    def resolve_run_mode(v: str) -> int:
        if Tool.optional(v):
            return RunMode.ROUTINE.value
        try:
            return int(v)
        except Exception as e:
            log.error("Parse run mode failed.", e)
            return RunMode.ROUTINE.value


class MeshKey(Key):

    def __init__(self, name: str, kind: Type[T]):
        super().__init__(name)
        self.name = name
        self.kind = kind

    def get_if_absent(self) -> T:
        pass

    def map(self, fn) -> Optional[Any]:
        pass

    def if_present(self, fn):
        pass

    def or_else(self, v: T) -> T:
        pass

    def is_present(self) -> bool:
        pass
