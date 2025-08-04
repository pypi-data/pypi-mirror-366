#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import Any, List

from mesh.codec import Codec
from mesh.macro import ServiceLoader, Binding
from mesh.types import Topic, Principal, Body, Event


class Objects:

    @staticmethod
    def wrap(value: Any) -> Body:
        if value is None:
            return Body()
        cdc = ServiceLoader.load(Codec)
        body = Body()
        body.codec = cdc.default_name()
        body.schema = ""
        body.buffer = cdc.get_default().encode(value)
        return body

    @staticmethod
    async def new_instance(payload: Any, topic: Topic) -> "Event":
        """
        Create local event instance.
        :param payload:
        :param topic:
        :return:
        """
        from mesh.context import Mesh
        environ = await Mesh.environ()
        target = Principal()
        target.id = environ.mdc
        return await Objects.new_instance_with_target(payload, topic, target)

    @staticmethod
    async def new_instance_with_target(payload: Any, topic: Topic, target: Principal) -> "Event":
        """
        Create any node event instance.
        :param payload:
        :param topic:
        :param target:
        :return:
        """
        from mesh.context import Mesh
        environ = await Mesh.environ()
        source = Principal()
        source.id = environ.mdc
        return Objects.new_instance_with_target_source(payload, topic, target, source)

    @staticmethod
    def new_instance_with_target_source(payload: Any, topic: Topic, target: Principal, source: Principal) -> "Event":
        """
        Create an event with source node and target node.
        :param payload:
        :param topic:
        :param target:
        :param source:
        :return:
        """
        event = Event()
        event.version = "1.0.0"
        event.tid = ""
        event.sid = ""
        event.eid = ""
        event.mid = ""
        event.timestamp = ""
        event.source = source
        event.target = target
        event.binding = topic
        event.entity = Objects.wrap(payload)
        return event

    @staticmethod
    def matches(topic: Topic, bindings: List[Binding]) -> bool:
        if not bindings:
            return False
        for b in bindings:
            if b.topic == topic.topic and b.code == topic.code:
                return True
        return False
