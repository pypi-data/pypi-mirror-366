#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import json
import os
import platform
from typing import List, Dict

from mesh.macro import spi, mps, ServiceLoader
from mesh.psi import Builtin, Hodor
from mesh.tool import Tool
from mesh.types import Versions


@mps
@spi("mesh")
class MeshBuiltin(Builtin):

    async def doc(self, name: str, formatter: str) -> str:
        return ""

    async def version(self) -> Versions:
        def prop() -> Dict[str, str]:
            try:
                with open(os.path.join(Tool.pwd(), f"{Tool.get_mesh_name()}.version")) as vfd:
                    vps = json.load(vfd)
                    return vps if vps else {}
            except FileNotFoundError:
                return {}

        properties = prop()
        name = f"{Tool.get_mesh_name()}_version".upper()
        mv = Tool.get_property("", [name])
        version = Tool.anyone(mv, properties.get("version", "1.0.0"))
        versions = Versions()
        versions.version = version
        versions.infos = {
            f"{Tool.get_mesh_name()}.commit_id": properties.get("commit_id", "3dd81bc"),
            f"{Tool.get_mesh_name()}.os": platform.system(),
            f"{Tool.get_mesh_name()}.arch": platform.architecture()[0],
            f"{Tool.get_mesh_name()}.version": version,
        }
        return versions

    async def debug(self, features: Dict[str, str]):
        doors = ServiceLoader.load(Hodor).list('')
        if not doors:
            return
        for hodor in doors:
            await hodor.debug(features)

    async def stats(self, features: List[str]) -> Dict[str, str]:
        indies = {}
        doors = ServiceLoader.load(Hodor).list('')
        if not doors:
            return indies
        for hodor in doors:
            stats = await hodor.stats(features)
            if not stats:
                continue
            for key, value in stats.items():
                indies[key] = value
        return indies

    async def fallback(self):
        return "fallback"

    async def dump(self, names: List[str]) -> Dict[str, str]:
        return {}
