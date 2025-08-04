#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from mesh.grpx.bindservice import GrpcBindableService
from mesh.grpx.channels import GrpcChannels
from mesh.grpx.consumer import GrpcConsumer
from mesh.grpx.interceptor import GrpcInterceptor, AsyncGrpcInterceptor
from mesh.grpx.marshaller import GrpcMarshaller
from mesh.grpx.provider import GrpcProvider

MPC = "/mpc/grpc"

__all__ = (
    "GrpcBindableService",
    "GrpcChannels",
    "GrpcConsumer",
    "GrpcInterceptor",
    "AsyncGrpcInterceptor",
    "GrpcMarshaller",
    "GrpcProvider",
)


def init():
    """ init function """
    pass
