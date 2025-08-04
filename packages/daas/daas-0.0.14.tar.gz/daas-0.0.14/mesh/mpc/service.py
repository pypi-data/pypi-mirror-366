#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import asyncio
import inspect
from typing import Any

import mesh.log as log
from mesh.context import Mesh
from mesh.macro import T, ServiceLoader
from mesh.mpc.eden import Eden
from mesh.mpc.filter import Filter, PROVIDER
from mesh.mpc.invoker import Invoker, Invocation


class ServiceInvoker(Invoker[T]):

    def __init__(self, service: Any):
        self.service = service

    async def run(self, invocation: Invocation) -> Any:
        r = await invocation.get_inspector().invoke(self.service, invocation.get_arguments())
        if not inspect.isawaitable(r):
            return r
        try:
            eden = ServiceLoader.load(Eden).get_default()
            execution = eden.infer(Mesh.context().get_urn())
            timeout = execution.schema().timeout
            return await asyncio.wait_for(r, timeout=max(timeout, 10000))
        except BaseException as e:
            log.error(f'Invoke {Mesh.context().get_urn()} fault because of {e}')
            raise e


class ServiceInvokeHandler(Invoker):
    """

    """

    def __init__(self, service: Any):
        self.invoker = Filter.composite(ServiceInvoker(service), PROVIDER)

    async def run(self, invocation: Invocation) -> Any:
        return await self.invoker.run(invocation)
