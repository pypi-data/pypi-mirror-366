#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import List, Dict, Any

from mesh.cause import ValidationException
from mesh.context import Mesh
from mesh.macro import T, spi, Proxy, InvocationHandler
from mesh.psi import Routable
from mesh.tool import Tool
from mesh.types import Principal


class MeshRouter(InvocationHandler):

    def __init__(self, reference: Any, principal: Principal, attachments: Dict[str, str], address: str):
        self.reference = reference
        self.principal = principal
        self.attachments = attachments
        self.address = address

    async def invoke(self, proxy: Any, method: Any, *args, **kwargs):
        return await Mesh.context_safe(self.safe_invoke(proxy, method, *args, **kwargs))

    async def safe_invoke(self, proxy: Any, method: Any, *args, **kwargs):
        overrides = self.get_override_attachments()
        try:
            Mesh.context().get_principals().append(self.principal)
            if Tool.required(self.address):
                Mesh.context().set_attribute(Mesh.REMOTE, self.address)
            if Tool.required(self.attachments):
                for (k, v) in self.attachments.items():
                    Mesh.context().get_attachments().__setitem__(k, v)

            executor = getattr(self.reference, method.__name__, method)
            if executor == method:
                return await executor(self.reference, *args, **kwargs)
            return await executor(*args, **kwargs)
        finally:
            Mesh.context().get_principals().pop()
            for (k, v) in overrides.items():
                Mesh.context().get_attachments().__setitem__(k, v)

    def get_override_attachments(self):
        if Tool.optional(self.attachments):
            return {}

        overrides = {}
        for (k, v) in self.attachments.items():
            overrides[k] = Mesh.context().get_attachments().get(k, '')

        return overrides


@spi("mesh")
class MeshRoutable(Routable):

    def __init__(self, reference: T = None, attachments: Dict[str, str] = None, address: str = ""):
        self.ref = reference
        self.attachments = attachments if attachments is not None else {}
        self.address = address

    def within(self, key: str, value: str) -> Routable[T]:
        return self.with_map({key: value})

    def with_map(self, attachments: Dict[str, str]) -> Routable[T]:
        if not attachments or attachments.__len__() < 1:
            return self
        kvs = {}
        if self.attachments.__len__() > 0:
            for (k, v) in self.attachments.items():
                kvs[k] = v
        for (k, v) in attachments.items():
            kvs[k] = v

        return MeshRoutable(self.ref, kvs)

    def with_address(self, address: str) -> Routable[T]:
        return MeshRoutable(self.ref, self.attachments, address)

    def local(self) -> T:
        interfaces = Proxy.get_interfaces(self.ref.__class__)
        return Proxy(interfaces, MeshRouter(self.ref, Principal(), self.attachments, self.address))

    def any(self, principal: Principal) -> T:
        if Tool.optional(principal.id()):
            raise ValidationException("Route key both cant be empty.")
        interfaces = Proxy.get_interfaces(self.ref.__class__)
        return Proxy(interfaces, MeshRouter(self.ref, principal, self.attachments, self.address))

    def any_inst(self, inst_id: str) -> T:
        principal = Principal()
        principal.inst_id = inst_id
        return self.any(principal)

    def many(self, principals: List[Principal]) -> List[T]:
        if Tool.optional(principals):
            return []
        references = []
        for principal in principals:
            references.append(self.any(principal))
        return references

    def many_inst(self, inst_ids: List[str]) -> List[T]:
        if Tool.optional(inst_ids):
            return []
        principals = []
        for inst_id in inst_ids:
            principal = Principal()
            principal.inst_id = inst_id
            principals.append(principal)
        return self.many(principals)
