#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import unittest

import mesh.codec as codec
import mesh.log as log
from mesh.macro import ServiceLoader
from mesh.mpc import GenericExecution, Consumer


class TestGrpc(unittest.TestCase):

    def test_invoke_grpc(self):
        encoder = ServiceLoader.load(codec.Codec).get('json')
        inbound = encoder.encode("")
        execution = GenericExecution()
        self.consumer = ServiceLoader.load(Consumer).get_default()
        outbound = self.consumer.consume('https://10.12.0.83:572', execution, inbound)
        log.info(f"{outbound}")


if __name__ == '__main__':
    unittest.main()
