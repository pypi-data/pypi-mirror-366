#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from mesh.asm import *
from mesh.boost import *
from mesh.cause import *
from mesh.codec import *
from mesh.context import *
from mesh.log import *
from mesh.macro import *
from mesh.mpc import *
from mesh.psi import *

__all__ = (
    "mpi",
    "mps",
    "idx",
    "spi",
    "binding",
    "Codeable",
    "Cause",
    "Inspector",
    "Types",
    "ServiceLoader",
    ##
    "URN",
    "URNFlag",
    "Consumer",
    "Filter",
    "Invocation",
    "Provider",
    "ServiceProxy",
    "MeshKey",
    "Mesh",
    # cause
    "MeshException",
    "CompatibleException",
    "NotFoundException",
    "ValidationException",
    "Codec",
    # psi
    "Builtin",
    "Hodor",
    "Cache",
    "CipherEconomy",
    "CipherProvider",
    "ObjectProvider",
    "Cluster",
    "Commercialize",
    "Header",
    "Context",
    "RunMode",
    "Key",
    "Cryptor",
    "DataHouse",
    "Dispatcher",
    "Endpoint",
    "EndpointSticker",
    "Evaluator",
    "Graph",
    "KMS",
    "KV",
    "Licenser",
    "Locker",
    "Network",
    "Pipeline",
    "Publisher",
    "Registry",
    "Routable",
    "Savepoint",
    "Scheduler",
    "Sequence",
    "Subscriber",
    "Tokenizer",
    "TokenProvider",
    "Transporter",
    "FileSystem",
    "Workflow",
    #
    "Runtime",
    "MethodProxy",
    "Header",
)

__mooter__ = Mooter()


def init():
    asm.init()


async def start():
    await __mooter__.start()


async def refresh():
    await __mooter__.refresh()


async def stop():
    await __mooter__.stop()


async def wait():
    """
    Use signal handler to throw exception which can be caught to allow graceful exit.
    """
    await __mooter__.wait()
