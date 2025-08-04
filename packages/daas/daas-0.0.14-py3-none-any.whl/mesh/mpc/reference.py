#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

import inspect
from asyncio import CancelledError
from typing import Any, Type, Dict, List

import mesh.log as log
from mesh.cause import MeshException, NotFoundException, CompatibleException, MeshCode
from mesh.codec import Codec
from mesh.context import Mesh, MeshKey, URN
from mesh.macro import mpi, InvocationHandler, T, ServiceLoader, Parameters, Inspector
from mesh.mpc.consumer import Consumer
from mesh.mpc.eden import Eden
from mesh.mpc.filter import Filter, CONSUMER
from mesh.mpc.inspector import MethodInspector
from mesh.mpc.invoker import Invoker, Invocation, ServiceInvocation, Execution
from mesh.psi import Key
from mesh.tool import Tool
from mesh.types import Reference

# Mesh invocation attributes.
INVOCATION: Key[Invocation] = MeshKey("mesh.invocation", str)


class ReferenceInvokeHandler(Invoker, InvocationHandler):
    """
    ReferenceInvokeHandler is mesh remote call.
    """

    def __init__(self, macro: mpi, kinds: List[Type[T]]):
        inspectors: Dict[Any, Inspector] = {}
        for kind in kinds:
            for interface in kind.__mro__:
                if not inspect.isabstract(interface):
                    continue
                for _, methods in Tool.get_declared_methods(interface).items():
                    for method in methods:
                        inspectors[method] = MethodInspector(macro, interface, method)
        self.macro = macro
        self.kinds = kinds
        self.invoker = Filter.composite(self, CONSUMER)
        self.inspectors = inspectors

    async def invoke(self, proxy: Any, method: Any, *args, **kwargs):
        return await Mesh.context_safe(self._invoke(proxy, method, *args, **kwargs))

    async def _invoke(self, proxy: Any, method: Any, *args, **kwargs):
        inspector = self.inspectors.get(method)
        execution: Execution[Reference] = self.refer_execution(inspector)
        urn = self.rewrite_urn(execution)
        Mesh.context().rewrite_urn(urn)
        Mesh.context().set_attribute(Mesh.REMOTE, self.rewrite_address(urn))

        parameters: Parameters = execution.inflect()
        parameters.set_arguments(*args)
        parameters.set_attachments({})

        invocation = ServiceInvocation(self, inspector, parameters, execution, URN.parse(urn))

        Mesh.context().set_attribute(INVOCATION, invocation)
        try:
            return await self.invoker.run(invocation)
        except CancelledError as e:
            log.error(f'{Mesh.context().get_trace_id()}, {e}')
            raise e
        except BaseException as e:
            log.error(f'{Mesh.context().get_trace_id()}, {e}')
            raise e

    async def run(self, invocation: Invocation) -> Any:
        execution = self.refer_execution(invocation.get_inspector())
        consumer = ServiceLoader.load(Consumer).get_default()
        address = Tool.anyone(Mesh.context().get_attribute(Mesh.REMOTE), Tool.get_mesh_address().any())
        name = execution.schema().codec
        codec = ServiceLoader.load(Codec).get(name)
        buff = codec.encode(invocation.get_parameters())
        ret = await consumer.consume(address, invocation.get_urn(), execution, buff)
        return self.deserialize(execution, codec, ret)

    @staticmethod
    def deserialize(execution: Execution[Reference], codec: Codec, ret: bytes) -> Any:
        returns = codec.decode(ret, execution.retype())
        if returns.get_cause():
            log.error(returns.get_cause().text())
            raise MeshException(returns.get_code(), returns.get_message())
        if MeshCode.NOT_FOUND.matches(returns.get_code()):
            raise NotFoundException(returns.get_message())
        if not MeshCode.SUCCESS.matches(returns.get_code()):
            raise MeshException(returns.get_code(), returns.get_message())
        if not execution.inspect().get_return_type():
            return None
        return returns.get_content()

    def refer_execution(self, inspector: Inspector) -> Execution[Reference]:
        eden = ServiceLoader.load(Eden).get_default()
        execution = eden.refer(self.macro, inspector.get_type(), inspector)
        if execution:
            return execution
        raise CompatibleException(f"Method {inspector.get_name()} cant be compatible")

    @staticmethod
    def rewrite_urn(execution: Execution[Reference]) -> str:
        urn = execution.schema().urn
        principal = Mesh.context().get_principals().peek()
        mdc = '' if not principal else principal.id
        remote_name = Mesh.context().get_attribute(Mesh.REMOTE_NAME)
        uname = Mesh.context().get_attribute(Mesh.UNAME)
        if Tool.optional(mdc) and Tool.optional(remote_name) and Tool.optional(uname):
            return urn
        urn = URN.parse(urn)
        if Tool.required(mdc):
            urn.node_id = mdc
        if Tool.required(uname):
            urn.name = uname
        if Tool.required(remote_name):
            urn.name = urn.name.replace("${mesh.name}", remote_name)
        return str(urn)

    def rewrite_address(self, uns: str):
        caddr = Mesh.context().get_attribute(Mesh.REMOTE)
        if Tool.required(caddr):
            return caddr
        urn = URN.parse(uns)
        if urn.name and urn.name.startswith(".mesh"):
            return Tool.get_mesh_address().any()
        if Tool.get_mesh_direct():
            names = Tool.get_mesh_direct().split(",")
            for name in names:
                pair = name.split("=")
                if self.is_direct(urn, pair):
                    return pair[1]
        address = urn.flag.address.replace(".", "")
        if address.isnumeric() and int(address) > 0:
            return f'{urn.flag.address}:{urn.flag.port}'
        return Tool.get_mesh_address().any()

    @staticmethod
    def is_direct(urn: URN, pair: list[str]) -> bool:
        if pair.__len__() < 2 or Tool.optional(pair[1]):
            return False
        if not pair[0].__contains__("@"):
            return urn.name.startswith(pair[0])
        nn = pair[0].split("@")
        if nn.__len__() < 2 or Tool.optional(nn[1]):
            return False
        return urn.node_id.lower() == nn[1].lower() and urn.name == nn[0]
