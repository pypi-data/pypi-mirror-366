#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import threading
from collections import deque
from contextvars import ContextVar
from typing import Any, Deque, Type, Coroutine

from mesh.context import MeshContext, MeshKey
from mesh.context.urn import LOCAL_MDC
from mesh.macro import T, mpi, Mode
from mesh.psi import Context, Key, Network
from mesh.types import Environ, Lattice, Location

__context__: ContextVar[Deque[Context]] = ContextVar[Deque[Context]]('mesh_context', default=deque())


class Mesh:
    __env__ = None
    __env_key__: Key[Environ] = MeshKey("mesh.mpc.environ", Environ)
    # Mesh invoke timeout
    TIMEOUT: Key[int] = MeshKey("mesh.mpc.timeout", int)

    # Mesh invoke mpi name attributes.
    UNAME: Key[str] = MeshKey("mesh.mpc.uname", str)

    # Mesh mpc remote address.
    REMOTE: Key[str] = MeshKey("mesh.mpc.address", str)

    # Remote app name.
    REMOTE_NAME: Key[str] = MeshKey("mesh.mpc.remote.name", str)

    # Generic codec type
    GENERIC_CODEC_TYPE: Key[str] = MeshKey("mesh.codec.generic.type", Type[T])

    @staticmethod
    def context() -> Context:
        mtx: Deque[Context] = __context__.get()
        if mtx.__len__() < 1:
            return MeshContext.create()
        return mtx[-1]

    @staticmethod
    def release():
        if not Mesh.is_empty():
            __context__.set(deque())

    @staticmethod
    def reset(ctx: Context):
        mtx = deque()
        mtx.append(ctx)
        __context__.set(mtx)

    @staticmethod
    def is_empty() -> bool:
        return __context__.get().__len__() < 1

    @staticmethod
    def push(ctx: Context):
        __context__.get().append(ctx)

    @staticmethod
    def pop():
        mtx: Deque[Context] = __context__.get()
        if not Mesh.is_empty():
            mtx.pop()

    @staticmethod
    async def context_safe(routine: Coroutine) -> Any:
        """ Execute with context safety. """
        context_disable = Mesh.is_empty()
        try:
            if context_disable:
                Mesh.reset(MeshContext.create())
            else:
                Mesh.push(Mesh.context().resume())
            return await routine
        finally:
            if context_disable:
                Mesh.release()
            else:
                Mesh.pop()

    @staticmethod
    def context_id() -> str:
        return f"{threading.current_thread().ident}-{threading.current_thread().name}"

    @staticmethod
    async def environ() -> Environ:
        if Mode.Isolate.on() and not Mesh.__env__:
            env = Environ()
            env.mdc = LOCAL_MDC
            Mesh.__env__ = env
        if Mesh.__env__:
            return Mesh.__env__

        env = Mesh.context().get_attribute(Mesh.__env_key__)
        if env:
            return env

        return await Mesh.context_safe(Mesh.__environ())

    @staticmethod
    def dft_environ() -> Environ:
        env = Environ()
        env.mdc = LOCAL_MDC
        env.name = ''
        env.version = '1.0.0'
        env.crt = ''
        env.key = ''
        env.root_crt = ''
        env.lattice = Lattice()
        return env

    @staticmethod
    async def __environ() -> Environ:
        Mesh.context().set_attribute(Mesh.__env_key__, Mesh.dft_environ())
        return await Mesh.network().environ()

    @staticmethod
    @mpi
    def network() -> Network:
        """"""
        pass

    @staticmethod
    def localize(self: Location):
        return MeshContext.localize(self)
