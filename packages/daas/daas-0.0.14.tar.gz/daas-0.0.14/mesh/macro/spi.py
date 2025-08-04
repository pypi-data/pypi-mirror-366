#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import inspect
from typing import Type, Any, Generic

from mesh.macro.ark import ark, T


class SPI(Generic[T]):

    def __init__(self, fn: T = None, name='', pattern='', priority=0, prototype=False):
        """
        Metadata annotation for Serial Peripheral Interface. Can be used with {@link ServiceLoader#load(Class)}
        or dependency injection at compile time and runtime time.
        """
        self.__ref__ = None
        self.name = name
        self.pattern = pattern
        self.priority = priority
        self.prototype = prototype
        if name != '':
            self.name = name
            return
        if fn is None:
            return
        if type(fn) is str:
            self.name = fn
            return
        self.name = str(type(fn))
        self.kind = fn

    def __call__(self, *args, **kwargs) -> T:
        if inspect.isfunction(args[0]):
            if not self.__ref__:
                def invoke(cls):
                    from mesh.macro import ServiceLoader
                    signature = inspect.signature(args[0])
                    return ServiceLoader.load(signature.return_annotation).get(self.name)

                self.__ref__ = invoke
            return self.__ref__
        if not hasattr(self, 'kind'):
            self.kind = args[0]
        self.kind.__spi__ = self
        ark.register(spi, self.name, self.kind, self)
        return self.kind

    @staticmethod
    def get_macro(kind: Type[Any]) -> "SPI":
        if hasattr(kind, '__spi__'):
            return kind.__spi__
        return SPI()


def spi(fn: T = None, *, name='', pattern='', priority=0, prototype=False):
    return SPI(fn, name, pattern, priority, prototype)
