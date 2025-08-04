#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

import unittest

import mesh.log as log
from mesh.tool import Tool
from mesh.types import Service


class TestTools(unittest.TestCase):

    def test_abstract_class(self):
        service = Service()
        service.address = '1'
        log.info(service.address)

    def test_new_trace_id(self):
        log.info(Tool.new_trace_id())
        log.info(Tool.get_ip())

    def test_required(self):
        log.info(f"{Tool.required(True)}")
        log.info(f"{Tool.required(True, False)}")
        log.info(f"{Tool.required(0, 0)}")
        log.info(f"{Tool.required([])}")
        log.info(f"{Tool.required([], [])}")
        log.info("False begin")
        log.info(f"{Tool.required()}")
        log.info(f"{Tool.required(1, None)}")
        log.info(Tool.get_ip())
        log.info(Tool.get_ip())


if __name__ == '__main__':
    unittest.main()
