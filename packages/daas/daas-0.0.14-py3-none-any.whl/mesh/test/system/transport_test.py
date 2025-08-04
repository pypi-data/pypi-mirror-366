#
# Copyright (c) 2000, 2023, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import asyncio
import os
import unittest

import mesh.log as log
from mesh.context import Mesh
from mesh.macro import ServiceLoader
from mesh.psi import Transport, Routable, Header


class TestServiceLoad(unittest.TestCase):

    async def test_transport_split_async(self):
        os.environ.setdefault("mesh.address", "127.0.0.1:17304")

        transport = Routable.of(ServiceLoader.load(Transport).get("mesh"))

        session = await transport.with_address("127.0.0.1:8866").local().open('session_id_001', {
            Header.MESH_VERSION.key(): '',
            Header.MESH_TECH_PROVIDER_CODE.key(): 'LX',
            Header.MESH_TRACE_ID.key(): Mesh.context().get_trace_id(),
            Header.MESH_TOKEN.key(): 'x',
            Header.MESH_SESSION_ID.key(): 'session_id_001',
            Header.MESH_DST_IDC.key(): 'LX0000000000000',
        })
        session2 = await transport.with_address("127.0.0.1:8866").local().open('session_id_001', {
            Header.MESH_VERSION.key(): '',
            Header.MESH_TECH_PROVIDER_CODE.key(): 'LX',
            Header.MESH_TRACE_ID.key(): Mesh.context().get_trace_id(),
            Header.MESH_TOKEN.key(): 'x',
            Header.MESH_SESSION_ID.key(): 'session_id_001',
            Header.MESH_DST_IDC.key(): 'LX0000000000000',
        })
        for index in range(1):
            wb = b"ABC" * (1 << 26)
            await session.push(wb, {}, "1")
            rb = await session2.pop(1000 * 120, "1")
            if wb.decode('utf-8') != rb.decode('utf-8'):
                log.info("PUSH-POP读写不匹配")
            else:
                log.info("PUSH-POP读写匹配")

            await session.push(wb, {}, "1")
            rb = await session2.peek("1")
            if wb.decode('utf-8') != rb.decode('utf-8'):
                log.info("PUSH-PEEK读写不匹配")
            else:
                log.info("PUSH-PEEK读写匹配")

        await session.release(0)
        await session2.release(0)

    def test_transport_split(self):
        asyncio.run(self.test_transport_split_async())


if __name__ == '__main__':
    unittest.main()
