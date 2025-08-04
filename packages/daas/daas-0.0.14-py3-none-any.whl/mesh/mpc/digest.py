#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import time

import mesh.log as log
from mesh.context import Mesh
from mesh.tool import Tool


class Digest:

    def __init__(self):
        self.trace_id = Mesh.context().get_trace_id()
        self.span_id = Mesh.context().get_span_id()
        self.mode = Mesh.context().get_run_mode()
        self.cdc = Tool.anyone(Mesh.context().get_consumer().id, '')
        self.cip = Tool.anyone(Mesh.context().get_consumer().ip, '')
        self.chost = Tool.anyone(Mesh.context().get_consumer().host, '')
        self.pdc = Tool.anyone(Mesh.context().get_provider().id, '')
        self.pip = Tool.anyone(Mesh.context().get_provider().ip, '')
        self.phost = Tool.anyone(Mesh.context().get_provider().host, '')
        self.urn = Mesh.context().get_urn()
        self.now = int(time.time() * 1000)

    def write(self, pattern: str, code: str):
        now = int(time.time() * 1000)
        log.info(
            f"{self.trace_id},"
            f"{self.span_id},"
            f"{Mesh.context().get_timestamp()},"
            f"{self.now},"
            f"{now - Mesh.context().get_timestamp()},"
            f"{now - self.now},"
            f"{self.mode},"
            f"{pattern},"
            f"{self.cdc},"
            f"{self.pdc},"
            f"{self.cip},"
            f"{self.pip},"
            f"{self.chost},"
            f"{self.phost},"
            f"{Tool.anyone(Mesh.context().get_attribute(Mesh.REMOTE), Tool.get_mesh_address().any())},"
            f"{self.urn},{code}")
