#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

import unittest

import mesh.asm as asm
import mesh.log as log
from mesh.macro import mpi
from mesh.psi import Network


class TestGrpc(unittest.IsolatedAsyncioTestCase):

    @mpi
    def network(self) -> Network:
        """"""
        pass

    async def test_get_environ(self):
        asm.init()
        environ = await self.network().environ()
        assert environ
        log.info(environ.mdc)


if __name__ == '__main__':
    unittest.main()
