"""This file is part of the Flow project, which provides a client library for creating and sending Mermaid diagrams.
It includes functionality to send diagrams via HTTP to a specified API endpoint."""

import requests
import os


class HTTPSender:
    def __init__(self, api_url=None):
        # Default to local FastAPI server
        self.api_url = api_url or os.getenv(
            "MERMAID_API_URL", "http://localhost:8000/diagrams"
        )

    def detect_type(self, content: str) -> str:
        content = content.strip()
        if content.startswith("sequenceDiagram"):
            return "sequence"
        elif content.startswith("flowchart"):
            return "flowchart"
        return "unknown"

    def send(self, message: str):
        diagram_type = self.detect_type(message)
        payload = {"diagram_type": diagram_type, "content": message}
        response = requests.post(self.api_url, json=payload)

        if response.ok:
            print("✅ Diagram posted via HTTP")
        else:
            print(f"❌ HTTP error {response.status_code}: {response.text}")
