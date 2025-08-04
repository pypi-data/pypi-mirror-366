#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import unittest

from mesh.metrics.collector import Collector


class TestCollector(unittest.TestCase):

    def test_collect(self):
        Collector().collect()


if __name__ == '__main__':
    unittest.main()
