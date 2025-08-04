#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from abc import abstractmethod, ABC

from mesh.macro.spi import spi


@spi("mesh")
class RuntimeHook(ABC):

    @abstractmethod
    async def start(self):
        """
         Trigger when mesh runtime is start.
        :return:
        """
        pass

    @abstractmethod
    async def stop(self):
        """
        Trigger when mesh runtime is stop.
        :return:
        """
        pass

    @abstractmethod
    async def refresh(self):
        """
        Trigger then mesh runtime context is refresh or metadata is refresh.
        :return:
        """
        pass

    @abstractmethod
    async def wait(self):
        """
        Wait for mesh runtime is terminal.
        :return:
        """
        pass
