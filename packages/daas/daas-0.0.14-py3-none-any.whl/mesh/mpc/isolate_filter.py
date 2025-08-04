#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from typing import Any

from mesh.macro import spi, Mode
from mesh.mpc.filter import Filter, Invoker, Invocation, CONSUMER


@spi(name="isolate", pattern=CONSUMER, priority=100 - (1 << 32))
class IsolateFilter(Filter):

    async def invoke(self, invoker: Invoker, invocation: Invocation) -> Any:
        if Mode.Isolate.on() and self.is_isolate(invocation):
            return None
        return await invoker.run(invocation)

    @staticmethod
    def is_isolate(invocation: Invocation) -> bool:
        return "mesh.net.environ,mesh.registry.put,mesh.registry.puts,mesh.registry.remove".__contains__(
            invocation.get_urn().name)
