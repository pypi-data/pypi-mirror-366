#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
from typing import Any

from mesh.cause import TimeoutException
from mesh.types import Reference
from mesh.macro import spi
from mesh.mpc.filter import Filter, Invoker, Invocation, CONSUMER
from mesh.mpc.invoker import Execution


@spi(name="robust", pattern=CONSUMER, priority=(1 << 32) - 1)
class RobustFilter(Filter):

    async def invoke(self, invoker: Invoker, invocation: Invocation) -> Any:
        execution: Execution[Reference] = invocation.get_execution()
        retries: int = min(execution.schema().retries, 3)
        for _ in range(retries - 1):
            try:
                return await invoker.run(invocation)
            except Exception as e:
                if not self.can_retry(e):
                    raise e
                if self.should_delay(e):
                    continue
        return await invoker.run(invocation)

    @staticmethod
    def can_retry(e: Exception) -> bool:
        """ Can retry """
        return isinstance(e, TimeoutException)

    @staticmethod
    def should_delay(e: Exception) -> bool:
        """ Should delay """
        return False
