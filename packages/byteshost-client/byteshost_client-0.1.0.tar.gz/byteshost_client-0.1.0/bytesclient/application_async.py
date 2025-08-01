import asyncio
from urllib.parse import urlparse
import os

class Application:
    def __init__(self, url="http://127.0.0.1:65534", user="application-admin", key="TiKNBTCK.Tai16yo.", timeout=5):
        self.url = url
        self.user = user
        self.key = key
        self.timeout = timeout
        self.reader = None
        self.writer = None
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

        # Authenticate immediately after connecting
        if not await self._authenticate():
            raise ValueError("Authentication failed")

        self.id = self.get_project_id()
        if not self.id:
            raise ValueError("This program is not part of the application")

    def get_project_id(self):
        return os.environ.get("PROCESS_PROJECT_ID", None)

    async def send_message(self, message: str):
        self.writer.write(message.encode('utf-8'))
        await self.writer.drain()

    async def receive_message(self) -> str:
        data = await self.reader.read(1024)
        return data.decode('utf-8')

    async def _authenticate(self) -> bool:
        auth_message = f"AUTH {self.user} {self.key}\n"
        await self.send_message(auth_message)
        response = await self.receive_message()
        return response.strip().upper() == "OK"

    async def kill_project(self, project_id: str):
        message = f"killproject {project_id}\n"
        await self.send_message(message)
        return await self.receive_message()

    async def start_project(self, project_id: str):
        message = f"startproject {project_id}\n"
        await self.send_message(message)
        return await self.receive_message()

    async def restart_project(self, project_id: str):
        message = f"restartproject {project_id}\n"
        await self.send_message(message)
        return await self.receive_message()

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
