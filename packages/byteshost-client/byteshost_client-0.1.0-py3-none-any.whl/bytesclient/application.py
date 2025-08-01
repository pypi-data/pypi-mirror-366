import socket
from urllib.parse import urlparse
import os

class Application:
    def __init__(self, url, user, key, timeout=5):
        self.url = url
        self.user = user
        self.key = key

        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port

        if host is None or port is None:
            raise ValueError("Invalid URL, must include host and port")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect((host, port))

        # Authenticate immediately after connecting
        if not self._authenticate():
            raise ValueError("Authentication failed")

        self.id = self.get_project_id()
        if not self.id:
            raise ValueError("This program is not part of the application")

    def get_project_id(self):
        return os.environ.get("PROCESS_PROJECT_ID", None)

    def send_message(self, message):
        self.socket.sendall(message.encode('utf-8'))

    def receive_message(self):
        data = self.socket.recv(1024)
        return data.decode('utf-8')

    def _authenticate(self):
        # Compose your authentication message format
        auth_message = f"AUTH {self.user} {self.key}"
        self.send_message(auth_message)
        response = self.receive_message()
        if response.strip().upper() == "OK":
            return True
        return False

    def kill_project(self, project_id):
        message = f"killproject {project_id}"
        self.send_message(message)
        response = self.receive_message()
        

    def start_project(self, project_id):
        message = f"startproject {project_id}"
        self.send_message(message)
        
    def restart_project(self, project_id):
        message = f"restartproject {project_id}"
        self.send_message(message)
        