#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import List

from mesh.context import MeshKey
from mesh.macro import spi, Mode
from mesh.mpc import ServiceProxy, Mesh
from mesh.psi import Network
from mesh.types import Route, Environ, Versions, Paging, Page


@spi("mesh")
class MeshNetwork(Network):

    def __init__(self):
        self.proxy = ServiceProxy.default_proxy(Network)
        self.environ_key = MeshKey("mesh-environ", Environ)
        self.environ: Environ = Mesh.dft_environ() if Mode.Isolate.on() else None

    async def environ(self) -> Environ:
        if self.environ:
            return self.environ
        if Mesh.context().get_attribute(self.environ_key):
            return Mesh.context().get_attribute(self.environ_key)
        environ = Mesh.dft_environ()
        Mesh.context().set_attribute(self.environ_key, environ)

        self.environ = await Mesh.context_safe(self.get_environ_safe())
        return self.environ

    async def get_environ_safe(self) -> Environ:
        Mesh.context().get_principals().clear()
        return await self.proxy.environ()

    async def accessible(self, route: Route) -> bool:
        return await self.proxy.accessible(route)

    async def refresh(self, routes: List[Route]) -> None:
        return await self.proxy.refresh(routes)

    async def route(self, mdc: str) -> Route:
        return await self.proxy.route(mdc)

    async def routes(self) -> List[Route]:
        return await self.proxy.routes()

    async def disable(self, mdc: str) -> None:
        return await self.proxy.disable(mdc)

    async def enable(self, mdc: str) -> None:
        return await self.proxy.enable(mdc)

    async def index(self, index: Paging) -> Page[Route]:
        return await self.proxy.index(index)

    async def version(self, mdc: str) -> Versions:
        return await self.proxy.version(mdc)

    async def exports(self, mdc: str) -> str:
        return await self.proxy.exports(mdc)

    async def imports(self, crt: str) -> None:
        return await self.proxy.imports(crt)
