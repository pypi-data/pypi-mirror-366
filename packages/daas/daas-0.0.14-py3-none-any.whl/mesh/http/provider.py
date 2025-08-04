#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse

from aiohttp import web

import mesh.log as log
from mesh.cause import ValidationException
from mesh.codec import Codec, Json, Xml, Yaml, Protobuf
from mesh.macro import spi, ServiceLoader
from mesh.mpc import Provider, Mesh, Transporter, PROVIDER
from mesh.psi import Header
from mesh.tool import Tool


class HttpHandler(BaseHTTPRequestHandler):
    pass


@spi("http")
class HTTPProvider(Provider):

    def __init__(self):
        self.address = ""
        self.server = None
        self.runner = None
        self.site: web.TCPSite = None
        self.transporter = ServiceLoader.load(Transporter).get(PROVIDER)
        self.json = ServiceLoader.load(Codec).get(Json)
        self.xml = ServiceLoader.load(Codec).get(Xml)
        self.yml = ServiceLoader.load(Codec).get(Yaml)
        self.protobuf = ServiceLoader.load(Codec).get(Protobuf)

    async def start(self, address: str, tc: Any):
        self.address = address
        if Tool.optional(address):
            raise ValidationException("HTTP address cant be empty.")
        self.server = web.Server(self.forward)
        self.runner = web.ServerRunner(self.server)
        parsed = urlparse(f"https://{address}")
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, parsed.hostname, parsed.port)
        await self.site.start()
        log.info(f"Listening and serving HTTP 1.x on {address}")

    async def close(self):
        log.info(f"Graceful stop HTTP 1.x serving on {self.address}")
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        if self.server:
            await self.server.shutdown()

    async def wait(self):
        """"""
        pass

    async def forward(self, r: web.Request) -> web.StreamResponse:
        return await Mesh.context_safe(self.context_safe_forward(r))

    async def context_safe_forward(self, r: web.Request) -> web.StreamResponse:
        trace_id = r.headers.get(Header.MESH_TRACE_ID.key())
        span_id = r.headers.get(Header.MESH_SPAN_ID.key())
        timestamp = r.headers.get(Header.MESH_SPAN_ID.key())
        uname = r.headers.get(Header.MESH_URN.key())
        if trace_id:
            Mesh.context().trace_id = trace_id
        if span_id:
            Mesh.context().span_id = span_id
        if timestamp:
            Mesh.context().timestamp = timestamp

        for (k, v) in r.headers.items():
            Mesh.context().get_attachments[k] = v

        buf = await self.decode(r)
        ret = await self.transporter.transport(Mesh.context(), uname, buf)
        return web.Response(body=ret, content_type='application/json')

    async def decode(self, r: web.Request) -> bytes:
        if r.content_type == 'application/json':
            return await r.read()
        if r.content_type == 'application/xml' or r.content_type == 'text/xml':
            return await r.read()
        if r.content_type == 'application/x-yaml':
            return await r.read()
        if r.content_type == 'application/x-protobuf':
            return await r.read()
        parameters = {}
        for (k, v) in r.query.items():
            parameters[k] = v
        if r.content_type == 'application/x-www-form-urlencoded' or r.content_type == 'multipart/form-data':
            form = await r.post()
            for (k, v) in form.items():
                parameters[k] = v
            return await r.read()

        return self.json.encode(parameters)
