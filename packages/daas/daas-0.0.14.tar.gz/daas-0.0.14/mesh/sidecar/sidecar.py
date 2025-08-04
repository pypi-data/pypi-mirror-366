#
# Copyright (c) 2000, 2099, trustbe and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import os
import platform
import subprocess
import tempfile
from abc import ABC, abstractmethod
from importlib import resources
from typing import Dict, Coroutine, IO

from mesh.macro import spi, mpi, ServiceLoader
from mesh.mpc import Mesh
from mesh.psi import Network
from mesh.tool import Tool


@spi(name="mesh")
class Sidecar(ABC):

    @abstractmethod
    @mpi("${mesh.name}.sidecar.allocate")
    async def allocate(self, inst_id: str) -> Dict[str, str]:
        """
        :param inst_id:
        :return:
        """
        pass

    @abstractmethod
    @mpi("${mesh.name}.sidecar.finalize")
    async def finalize(self, inst_id: str):
        """
        :param inst_id:
        :return:
        """
        pass


class Selector:

    def __init__(self, inst_id: str):
        self.inst_id = inst_id
        self.addrs: Dict[str, str] = {}

    async def __aenter__(self) -> Dict[str, str]:
        self.addrs = await Mesh.context_safe(self.invoke(self.sidecar().allocate(self.inst_id)))
        return self.addrs

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await Mesh.context_safe(self.invoke(self.sidecar().finalize(self.inst_id)))

    @staticmethod
    async def invoke(routine: Coroutine) -> Coroutine:
        network = ServiceLoader.load(Network).get_default()
        await network.environ()
        Mesh.context().set_attribute(Mesh.REMOTE_NAME, "sidecar")
        Mesh.context().set_attribute(Mesh.REMOTE, os.environ.get("MESH_SIDECAR_ADDRESS", "127.0.0.1:7204"))
        return await routine

    @mpi
    def sidecar(self) -> Sidecar:
        pass


class SidecarDaemon:

    def __init__(self):
        uname = platform.system().lower()
        suffix = "" if uname != "windows" else ".exe"
        name = f"sidecar-{uname}-amd64{suffix}"
        body = resources.read_binary(__package__, name)
        fd, executable = tempfile.mkstemp(name)
        os.close(fd)
        os.chmod(executable, os.stat(executable).st_mode | 0o755)
        with open(file=executable, mode='wb+') as f:
            f.write(body)
            self.executable = executable
            self.running = False

    def open(self, inst_id: str, stdout: IO = None, mode: int = 0) -> Selector:
        if not self.running and 0 == mode:
            try:
                subprocess.Popen(self.executable, stdout=stdout, stderr=stdout, start_new_session=True, env={
                    "MESH_NAME": "sidecar",
                    "MESH_ADDRESS": Tool.get_mesh_address().string(),
                    "MESH_RUNTIME": f"{Tool.get_mesh_runtime().hostname}:7204"})
                self.running = True
            except subprocess.CalledProcessError as e:
                raise e

        return Selector(inst_id)


sidecar = SidecarDaemon()


def open_sidecar(inst_id: str, stdout: IO = None, mode: int = 0) -> Selector:
    return sidecar.open(inst_id, stdout, mode)
