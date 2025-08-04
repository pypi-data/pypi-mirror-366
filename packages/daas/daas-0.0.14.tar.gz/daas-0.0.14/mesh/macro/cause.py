#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#


import traceback

from mesh.cause import MeshException
from mesh.macro.codec import serializable
from mesh.macro.index import idx


@serializable
class Cause:

    @idx(0)
    def name(self) -> str:
        return ''

    @idx(5)
    def pos(self) -> str:
        return ''

    @idx(10)
    def text(self) -> str:
        return ''

    @idx(15)
    def buff(self) -> bytes:
        return b''

    @staticmethod
    def of(e: BaseException) -> "Cause":
        cause = Cause()
        cause.name = e.__class__.__name__ if e.__class__ else str(e)
        cause.pos = '0'
        cause.text = traceback.format_exc()
        return cause

    @staticmethod
    def of_cause(code: str, message: str, cause: "Cause") -> BaseException:
        raise MeshException(f"{code},{message},{cause.text}")
