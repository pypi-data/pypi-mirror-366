#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from abc import abstractmethod
from typing import Any, Type

from mesh.cause import MeshException
from mesh.macro import spi, T


@spi("json")
class Codec:

    @abstractmethod
    def encode(self, value: T) -> bytes:
        pass

    @abstractmethod
    def decode(self, value: bytes, kind: Type[T]) -> T:
        pass

    def encode_string(self, value: Any) -> str:
        return self.encode(value).decode('UTF-8')

    def decode_string(self, value: str, kind: Type[T]) -> T:
        return self.decode(value.encode('UTF-8'), kind)


class CodecError(MeshException):
    def __init__(self, message: str):
        super().__init__("E000001", message)


