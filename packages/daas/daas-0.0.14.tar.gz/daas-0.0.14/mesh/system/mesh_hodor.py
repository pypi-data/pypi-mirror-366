#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from typing import Dict, List

from mesh.macro import spi
from mesh.psi import Hodor


@spi("mesh")
class MeshHodor(Hodor):

    async def stats(self, features: List[str]) -> Dict[str, str]:
        return {"status": "true"}

    async def debug(self, features: Dict[str, str]):
        """ debug """
        pass

    async def dump(self) -> str:
        return ""
