import asyncio
import json
from urllib.parse import urlparse
import os

class Application:
    def __init__(self, url="tcp://127.0.0.1:65534", user="application-admin", key="TiKNBTCK.Tai16yo.", timeout=5):
        self.url = url
        self.user = user
        self.key = key
        self.timeout = timeout
        self.reader = None
        self.writer = None
        self.buffer = ""
        self.id = None

    async def connect(self):
        parsed_url = urlparse(self.url)
        host = parsed_url.hostname
        port = parsed_url.port

        if host is None or port is None:
            raise ValueError("Invalid URL, must include host and port")

        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError("Connection timed out")

        if not await self._authenticate():
            raise ValueError("Authentication failed")

        self.id = self.get_project_id()
        if not self.id:
            raise ValueError("This program is not part of the application")

    def get_project_id(self):
        return os.environ.get("PROCESS_PROJECT_ID")

    async def send_message(self, message: str):
        """Sends a newline-terminated message."""
        self.writer.write((message + '\n').encode('utf-8'))
        await self.writer.drain()

    async def receive_json(self):
        """Reads a single JSON object line (delimited by newline)."""
        while '\n' not in self.buffer:
            chunk = await self.reader.read(1024)
            if not chunk:
                raise ConnectionError("Connection closed by server")
            self.buffer += chunk.decode("utf-8")

        line, self.buffer = self.buffer.split('\n', 1)

        try:
            return json.loads(line)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON received: {line}") from e

    async def _authenticate(self) -> bool:
        await self.send_message(f"AUTH {self.user} {self.key}")
        response = await self.receive_json()
        return response.get("success", False)

    async def kill_project(self, project_id: str):
        await self.send_message(f"killproject {project_id}")
        return await self.receive_json()

    async def start_project(self, project_id: str):
        await self.send_message(f"startproject {project_id}")
        return await self.receive_json()

    async def restart_project(self, project_id: str):
        await self.send_message(f"restartproject {project_id}")
        return await self.receive_json()

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
