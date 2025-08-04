#
# Copyright (c) 2019, 2023, ducesoft and/or its affiliates. All rights reserved.
# TRUSTBE PROPRIETARY/CONFIDENTIAL. Use is subject to license terms.
#
#
import asyncio
import os

import mesh


async def main():
    os.environ.setdefault("mesh.mode", str(1 << 6 | 1 << 11))
    os.environ.setdefault("mesh.proc", str(0))
    os.environ.setdefault("mesh.address", "10.43.245.145:8866")
    os.environ.setdefault("mesh.runtime", "192.168.31.11:8866")
    await mesh.start()
    await mesh.wait()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
