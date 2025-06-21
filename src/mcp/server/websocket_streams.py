"""
WebSocket stream adapters for MCP protocol.
Converts WebSocket to asyncio streams for MCP server compatibility.
"""

import asyncio
import json
from typing import AsyncIterator
import websockets
from websockets.server import WebSocketServerProtocol


class WebSocketReadStream:
    """Async read stream from WebSocket."""
    
    def __init__(self, websocket: WebSocketServerProtocol):
        self.websocket = websocket
        self._buffer = asyncio.Queue()
        self._closed = False
    
    async def __aiter__(self) -> AsyncIterator[bytes]:
        """Async iterator for reading from WebSocket."""
        try:
            async for message in self.websocket:
                if isinstance(message, str):
                    yield message.encode('utf-8')
                else:
                    yield message
        except websockets.exceptions.ConnectionClosed:
            self._closed = True
            return
    
    async def read(self, n: int = -1) -> bytes:
        """Read data from WebSocket."""
        try:
            message = await self.websocket.recv()
            if isinstance(message, str):
                return message.encode('utf-8')
            return message
        except websockets.exceptions.ConnectionClosed:
            self._closed = True
            return b''
    
    async def readline(self) -> bytes:
        """Read a line from WebSocket."""
        return await self.read()
    
    def at_eof(self) -> bool:
        """Check if stream is at end of file."""
        return self._closed


class WebSocketWriteStream:
    """Async write stream to WebSocket."""
    
    def __init__(self, websocket: WebSocketServerProtocol):
        self.websocket = websocket
        self._closed = False
    
    async def write(self, data: bytes) -> None:
        """Write data to WebSocket."""
        try:
            if isinstance(data, bytes):
                message = data.decode('utf-8')
            else:
                message = str(data)
            await self.websocket.send(message)
        except websockets.exceptions.ConnectionClosed:
            self._closed = True
    
    async def drain(self) -> None:
        """Drain the write buffer (no-op for WebSocket)."""
        pass
    
    def close(self) -> None:
        """Close the write stream."""
        self._closed = True
        # Don't close websocket here - let connection handler manage it
    
    async def wait_closed(self) -> None:
        """Wait for stream to close."""
        pass
    
    def is_closing(self) -> bool:
        """Check if stream is closing."""
        return self._closed


class WebSocketStreams:
    """WebSocket stream pair for MCP protocol."""
    
    def __init__(self, websocket: WebSocketServerProtocol):
        self.websocket = websocket
        self.read_stream = WebSocketReadStream(websocket)
        self.write_stream = WebSocketWriteStream(websocket)