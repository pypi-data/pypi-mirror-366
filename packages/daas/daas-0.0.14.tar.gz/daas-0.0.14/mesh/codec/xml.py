#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import Type

from mesh.codec import Codec
from mesh.macro import T, spi

Xml = "xml"


@spi(Xml)
class XmlCodec(Codec):

    def encode(self, value: T) -> bytes:
        pass

    def decode(self, value: bytes, kind: Type[T]) -> T:
        pass
