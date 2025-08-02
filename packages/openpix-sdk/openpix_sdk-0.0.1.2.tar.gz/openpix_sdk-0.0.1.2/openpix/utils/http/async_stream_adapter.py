from typing import AsyncIterator


class AsyncStreamAdapter:
    def __init__(self, async_iterator: AsyncIterator[bytes]) -> None:
        self.async_iterator = async_iterator
        self.buffer = b""
        self.offset = 0

    async def read(self, size: int = -1) -> bytes:
        if size == -1 or len(self.buffer) >= size:
            if size == -1:
                data = self.buffer
                self.buffer = b""
            else:
                data = self.buffer[self.offset : self.offset + size]
                self.offset += size
                if self.offset >= len(self.buffer):
                    self.buffer = b""
                    self.offset = 0
            return data

        while True:
            try:
                chunk = await anext(self.async_iterator)
                self.buffer += chunk
                if len(self.buffer) >= size:
                    data = self.buffer[self.offset : self.offset + size]
                    self.offset += size
                    if self.offset >= len(self.buffer):
                        self.buffer = b""
                        self.offset = 0
                    return data
            except StopAsyncIteration:
                data = self.buffer[self.offset :]
                self.buffer = b""
                self.offset = 0
                return data
