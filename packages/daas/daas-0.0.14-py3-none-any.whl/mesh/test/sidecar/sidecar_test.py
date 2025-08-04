#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import os
import socket
import unittest

from mesh.sidecar import open_sidecar


class TestSidecar(unittest.IsolatedAsyncioTestCase):

    async def test_tcp(self):
        os.environ.setdefault('MESH_ADDRESS', '10.99.167.33:8866')
        async with open_sidecar('LX0000010008760') as selector:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            vs = selector.get('libpsi').split(":")
            conn.connect((vs[0], int(vs[1])))
            for i in range(1000):
                conn.send(f"Hello {i}\n".encode())
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(data.decode())

            conn.close()


if __name__ == '__main__':
    unittest.main()
