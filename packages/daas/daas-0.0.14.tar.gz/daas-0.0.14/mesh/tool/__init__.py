#
# Copyright (c) 2019, 2025, firmer.tech and/or its affiliates. All rights reserved.
# Firmer Corporation PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#

import inspect
import os
import random
import sys
from pathlib import Path
from typing import List, Any, Type, Dict

from mesh.macro import T, Compatible, URI, Addrs, System
from mesh.tool.objects import Objects
from mesh.tool.snowflake import UUID

__all__ = (
    "Objects",
    "Tool"
)


def init():
    """ init function """
    pass


class Tool:
    __uuid = UUID(random.randint(0, 31), random.randint(0, 31))

    @staticmethod
    def anyone(*args: str) -> str:
        if not args:
            return ""

        for arg in args:
            if arg and "" != arg:
                return arg

        return ""

    @staticmethod
    def ternary(expr: bool, left: T, right: T) -> T:
        if expr:
            return left
        return right

    @staticmethod
    def get_property(dft: str, name: List[str]) -> str:
        return System.environ().get_property(dft, name)

    @staticmethod
    def get_ip() -> str:
        return System.environ().get_ip()

    @staticmethod
    def get_hostname() -> str:
        return System.environ().get_hostname()

    @staticmethod
    def get_mesh_address() -> Addrs:
        return System.environ().get_mesh_address()

    @staticmethod
    def get_mesh_runtime() -> URI:
        return System.environ().get_mesh_runtime()

    @staticmethod
    def get_mesh_name() -> str:
        return System.environ().get_mesh_name()

    @staticmethod
    def get_mesh_mode() -> int:
        return int(System.environ().get_mesh_mode())

    @staticmethod
    def get_mesh_direct() -> str:
        return System.environ().get_mesh_direct()

    @staticmethod
    def get_max_channels() -> int:
        return System.environ().get_max_channels()

    @staticmethod
    def get_min_channels() -> int:
        return System.environ().get_min_channels()

    @staticmethod
    def get_proc() -> int:
        return System.environ().get_proc()

    @staticmethod
    def get_packet_size() -> int:
        return System.environ().get_packet_size()

    @staticmethod
    def required(*args: Any) -> bool:
        if not args:
            return False

        for arg in args:
            if arg is not None and "" != arg:
                continue
            return False

        return True

    @staticmethod
    def optional(v: Any) -> bool:
        return not Tool.required(v)

    @staticmethod
    def new_trace_id() -> str:
        return f"{System.environ().get_ip_hex()}{Tool.next_id()}"

    @staticmethod
    def new_span_id(span_id: str, index: int) -> str:
        if Tool.optional(span_id):
            return "0"
        if span_id.__len__() > 255:
            return "0"
        return f"{span_id}.{index}"

    @staticmethod
    def split(v: str, sep: str) -> [str]:
        if not v or "" == v:
            return []
        return v.split(sep)

    @staticmethod
    def get_declared_methods(reference: Type[T]) -> Dict[Type[T], List[Any]]:
        kinds: List[Type[T]] = []
        for k, v in vars(reference).items():
            if inspect.isclass(v) and issubclass(reference, v):
                kinds.append(v)
        if inspect.isabstract(reference):
            kinds.append(reference)
        methods: Dict[Type[T], List[Any]] = {}
        for kind in kinds:
            methods[kind] = []
            for method in inspect.getmembers(kind, inspect.isfunction):
                methods[kind].append(method[1])
            for method in inspect.getmembers(kind, inspect.ismethod):
                methods[kind].append(method[1])
        return methods

    @staticmethod
    def next_id() -> str:
        return Tool.__uuid.new_id()

    @staticmethod
    def get_origin(tp):
        return Compatible.get_origin(tp)

    @staticmethod
    def get_args(tp):
        return Compatible.get_args(tp)

    @staticmethod
    def pwd() -> str:
        """
        Returns the name of the project root directory.
        :return: Project root directory name
        """

        # stack trace history related to the call of this function
        frame_stack: [inspect.FrameInfo] = inspect.stack()

        # get info about the module that has invoked this function
        # (index=0 is always this very module, index=1 is fine as long this function is not called by some other
        # function in this module)
        frame_info: inspect.FrameInfo = frame_stack[1]

        # if there are multiple calls in the stacktrace of this very module, we have to skip those and take the first
        # one which comes from another module
        if frame_info.filename == __file__:
            for frame in frame_stack:
                if frame.filename != __file__:
                    frame_info = frame
                    break

        # path of the module that has invoked this function
        caller_path: str = frame_info.filename

        # absolute path of the of the module that has invoked this function
        caller_absolute_path: str = os.path.abspath(caller_path)

        # get the top most directory path which contains the invoker module
        paths: [str] = [p for p in sys.path if p in caller_absolute_path]
        paths.sort(key=lambda p: len(p))
        caller_root_path: str = paths[0]

        if not os.path.isabs(caller_path):
            # file name of the invoker module (eg: "mymodule.py")
            caller_module_name: str = Path(caller_path).name

            # this piece represents a subpath in the project directory
            # (eg. if the root folder is "myproject" and this function has ben called from myproject/foo/bar/mymodule.py
            # this will be "foo/bar")
            project_related_folders: str = caller_path.replace(os.sep + caller_module_name, '')

            # fix root path by removing the undesired subpath
            caller_root_path = caller_root_path.replace(project_related_folders, '')

        dir_name: str = Path(caller_root_path).name

        return dir_name

    @staticmethod
    def compare_version(x: str, v: str) -> int:
        """
        Is the version less than the appointed version.
        :param x:
        :param v: compared version
        :return: -1 true less than, 0 equals, 1 gather than
        """
        if not x or "" == x:
            return -1
        if not v or "" == v:
            return 1

        rvs = x.split(".")
        vs = v.split(".")
        for idx, value in enumerate(rvs):
            if vs.__len__() <= idx:
                return 0
            if vs[idx] == "*":
                continue
            if rvs[idx] > vs[idx]:
                return 1
            if rvs[idx] < vs[idx]:
                return -1
        return 0
