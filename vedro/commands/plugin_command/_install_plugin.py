import asyncio
from asyncio import create_subprocess_shell
from asyncio.streams import StreamReader
from typing import Any, Callable, Union

__all__ = ("install_plugin",)

CallbackType = Callable[[str], Any]


async def install_plugin(package: str, pip_args: str, *,
                         on_stdout: CallbackType, on_stderr: CallbackType) -> Union[int, None]:
    cmd = f"pip install {package} {pip_args}"

    proc = await create_subprocess_shell(cmd.strip(),
                                         stdout=asyncio.subprocess.PIPE,
                                         stderr=asyncio.subprocess.PIPE)
    await asyncio.gather(
        _read_stream(proc.stdout, on_stdout),
        _read_stream(proc.stderr, on_stderr)
    )

    await proc.wait()

    return proc.returncode


async def _read_stream(stream: Union[StreamReader, None], callback: CallbackType) -> None:
    if not stream:
        return

    while True:
        line = await stream.readline()
        if not line:
            break
        callback(line.decode())
