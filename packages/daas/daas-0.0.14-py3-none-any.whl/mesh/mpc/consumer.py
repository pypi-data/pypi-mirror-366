#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

from abc import abstractmethod, ABC

from mesh.context import URN
from mesh.macro import spi
from mesh.mpc.invoker import Execution
from mesh.types import Reference


@spi(name="grpc")
class Consumer(ABC):
    HTTP = "http"
    GRPC = "grpc"
    TCP = "tcp"
    MQTT = "mqtt"

    """
    Service consumer with any protocol and codec.
    """

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def start(self):
        """
        Start the mesh broker.
        :return:
        """
        pass

    @abstractmethod
    async def consume(self, address: str, urn: URN, execution: Execution[Reference], inbound: bytes) -> bytes:
        """
        Consume the input payload.
        :param address: Remote address.
        :param urn: Actual uniform resource domain name.
        :param execution: Service reference.
        :param inbound: Input arguments.
        :return: Output payload
        """
        pass
