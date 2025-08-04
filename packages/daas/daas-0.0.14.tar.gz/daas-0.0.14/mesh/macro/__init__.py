#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from mesh.macro.ark import ark, T, A, B, C
from mesh.macro.binding import binding, Binding
from mesh.macro.cache import Cache
from mesh.macro.cause import Cause
from mesh.macro.codec import serializable
from mesh.macro.compatible import Compatible
from mesh.macro.env import Mode, Addrs, URI, System
from mesh.macro.hook import RuntimeHook
from mesh.macro.index import idx, Index
from mesh.macro.inspect import Returns, Parameters, Inspector, Stacktrace
from mesh.macro.loader import ServiceLoader
from mesh.macro.mpi import mpi, MPI, MethodProxy
from mesh.macro.mps import mps, MPS
from mesh.macro.proxy import Proxy, InvocationHandler
from mesh.macro.spi import spi, SPI
from mesh.macro.types import Types

__all__ = ("mpi",
           "mps",
           "binding",
           "idx",
           "spi",
           "serializable",
           "ark",
           "T",
           "A",
           "B",
           "C",
           "Index",
           "SPI",
           "Proxy",
           "InvocationHandler",
           "MPI",
           "MPS",
           "Binding",
           "ServiceLoader",
           "Types",
           "Cause",
           "Returns",
           "Parameters",
           "Inspector",
           "MethodProxy",
           "Compatible",
           "RuntimeHook",
           "Stacktrace",
           "Cache",
           ##
           "System",
           "URI",
           "Addrs",
           "Mode"
           )


def init():
    """ init function """
    pass
