#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import asyncio
import os
import unittest
from abc import ABC, abstractmethod
from typing import Coroutine

from mesh.types import Principal
from mesh.macro import mpi, mps, ServiceLoader, MethodProxy
from mesh.mpc import Mesh
from mesh.psi import Routable, Network


class Service(ABC):

    @abstractmethod
    @mpi(name='Service.foo')
    def foo(self, hi: str) -> str:
        pass


@mps
class Implement(Service):

    def foo(self, hi: str) -> str:
        return f'I am {str}'


class TestServiceInvoke(unittest.IsolatedAsyncioTestCase):

    @mpi
    @property
    def service(self) -> Service:
        return self.service

    async def test_foo(self):
        ret = self.service.foo("Terminator")
        self.assertEqual(ret, "I am Terminator")

    @staticmethod
    async def print():
        print(-1)

    async def test_context_safe(self):
        await Mesh.context_safe(
            TestServiceInvoke.phase(TestServiceInvoke.phase(TestServiceInvoke.phase(self.print()))))
        print(len(Mesh.context().get_principals()))

    @staticmethod
    async def phase(fn: Coroutine):
        Mesh.context().get_principals().append(Principal())
        await Mesh.context_safe(fn)
        print(len(Mesh.context().get_principals()))

    async def test_proxy(self):
        os.environ.setdefault('mesh.address', '10.99.27.33:8866')
        router = Routable.of(ServiceLoader.load(MethodProxy).get_default().proxy(Network))
        await asyncio.gather(router.any_inst('XX00000000000000').get_routes(),
                             router.any_inst('XX00000000000000').get_routes())


if __name__ == '__main__':
    unittest.main()
