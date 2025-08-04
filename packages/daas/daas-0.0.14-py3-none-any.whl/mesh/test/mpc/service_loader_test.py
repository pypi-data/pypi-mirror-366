#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import unittest

from mesh.codec import Codec
from mesh.macro import ServiceLoader


class TestServiceLoad(unittest.TestCase):

    def test_load(self):
        codec = ServiceLoader.load(Codec).load()


if __name__ == '__main__':
    unittest.main()
