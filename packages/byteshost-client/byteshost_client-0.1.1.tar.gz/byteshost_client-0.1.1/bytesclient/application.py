import socket
import json
from urllib.parse import urlparse
import os

class Application:
    def __init__(self, url, user, key, timeout=5):
        self.url = url
        self.user = user
        self.key = key
        self.buffer = ""

        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port

        if host is None or port is None:
            raise ValueError("Invalid URL, must include host and port")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect((host, port))

        # Authenticate immediately
        if not self._authenticate():
            raise ValueError("Authentication failed")

        self.id = self.get_project_id()
        if not self.id:
            raise ValueError("This program is not part of the application")

    def get_project_id(self):
        return os.environ.get("PROCESS_PROJECT_ID", None)

    def send_message(self, message: str):
        """Send a message, always newline-terminated."""
        self.socket.sendall((message + "\n").encode("utf-8"))

    def receive_json(self):
        """Receive one complete JSON object (newline-delimited)."""
        while '\n' not in self.buffer:
            data = self.socket.recv(1024)
            if not data:
                raise ConnectionError("Disconnected from server")
            self.buffer += data.decode('utf-8')

        line, self.buffer = self.buffer.split('\n', 1)
        return json.loads(line)

    def _authenticate(self):
        self.send_message(f"AUTH {self.user} {self.key}")
        response = self.receive_json()
        return response.get("success", False)

    def kill_project(self, project_id):
        self.send_message(f"killproject {project_id}")
        return self.receive_json()

    def start_project(self, project_id):
        self.send_message(f"startproject {project_id}")
        return self.receive_json()

    def restart_project(self, project_id):
        self.send_message(f"restartproject {project_id}")
        return self.receive_json()

    def close(self):
        self.socket.close()
