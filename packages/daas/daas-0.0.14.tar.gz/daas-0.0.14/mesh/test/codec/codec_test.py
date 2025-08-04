#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import unittest

import mesh.codec as codec
import mesh.codec.tools as tools
import mesh.log as log
from mesh.cause import MeshException
from mesh.types import Paging, Page
from mesh.macro import Returns, ServiceLoader, mpi, serializable, Cause
from mesh.mpc import Compiler


@serializable
class A:
    x: str


class TestCodec(unittest.TestCase):

    @staticmethod
    @mpi("xxx")
    def x() -> dict:
        pass

    def throw(self):
        raise MeshException("", "xxx")

    def test_json_codec(self):
        encoder = ServiceLoader.load(codec.Codec).get(codec.Json)

        try:
            self.throw()
        except BaseException as e:
            compiler = ServiceLoader.load(Compiler).get("mpyc")
            r: Returns = compiler.retype(self.x)()
            r.set_content(dict(x=1, y="2", z={"x": 1, "value": (1, 2)}, v=(1, 2)))
            r.set_code("1")
            r.set_cause(Cause.of(e))
            r.set_message("1")
            log.info(encoder.encode_string(r))

        cls = Page[bytes]
        log.info(tools.get_raw_type(cls))
        paging = Paging()
        paging.index = 1
        inbound = encoder.encode_string(paging)
        log.info(inbound)
        log.info(encoder.encode_string({'x': 'y'}))
        a = A()
        a.x = 'y'
        log.info(encoder.encode_string(a))

        encoder.decode_string('{}', Page[bytes])


if __name__ == '__main__':
    unittest.main()
