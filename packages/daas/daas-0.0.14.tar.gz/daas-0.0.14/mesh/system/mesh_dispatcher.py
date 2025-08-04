#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import Any, Dict

from mesh.macro import spi
from mesh.psi import Dispatcher


@spi("mesh")
class MeshDispatcher(Dispatcher):

    async def invoke(self, urn: str, param: Dict[str, Any]) -> Any:
        pass

    async def invoke0(self, urn: str, param: Any) -> Any:
        pass
