import unittest
import base64
import socket
import subprocess
import sys
import time
import requests
import signal
import os


def _free_port():
    """Ask the OS for a port nobody is listening on."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class DocShieldIntegrationTest(unittest.TestCase):
    """Test that DocShield works in an actual running FastAPI application."""

    @classmethod
    def setUpClass(cls):
        """Start a test server in the background and wait until it answers."""
        cls.port = _free_port()
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "examples.manual_test:app", "--port", str(cls.port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        deadline = time.time() + 15
        while time.time() < deadline:
            if cls.process.poll() is not None:
                raise RuntimeError(f"Test server exited early: {cls.process.stderr.read().decode()}")
            try:
                requests.get(cls.base_url, timeout=0.5)
                return
            except requests.ConnectionError:
                time.sleep(0.2)
        cls.tearDownClass()
        raise RuntimeError("Test server did not start within 15 seconds")

    @classmethod
    def tearDownClass(cls):
        """Shut down the test server."""
        if cls.process and cls.process.poll() is None:
            os.killpg(os.getpgid(cls.process.pid), signal.SIGTERM)
            cls.process.wait()

    def get_auth_header(self, username, password):
        """Create HTTP Basic Auth header for testing."""
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}
    
    def test_docs_protected(self):
        """Test that docs endpoint requires authentication."""
        response = requests.get(f"{self.base_url}/docs")
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)
        self.assertEqual(response.headers["WWW-Authenticate"], "Basic")
    
    def test_redoc_protected(self):
        """Test that redoc endpoint requires authentication."""
        response = requests.get(f"{self.base_url}/redoc")
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)
        self.assertEqual(response.headers["WWW-Authenticate"], "Basic")
    
    def test_openapi_protected(self):
        """Test that openapi.json endpoint requires authentication."""
        response = requests.get(f"{self.base_url}/openapi.json")
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)
        self.assertEqual(response.headers["WWW-Authenticate"], "Basic")
    
    def test_valid_credentials(self):
        """Test that valid credentials allow access to docs endpoints."""
        headers = self.get_auth_header("admin", "password123")
        
        response = requests.get(f"{self.base_url}/docs", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        response = requests.get(f"{self.base_url}/openapi.json", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.headers["content-type"])
    
    def test_invalid_credentials(self):
        """Test that invalid credentials are rejected."""
        headers = self.get_auth_header("admin", "wrongpassword")
        response = requests.get(f"{self.base_url}/docs", headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)
        self.assertEqual(response.headers["WWW-Authenticate"], "Basic")


if __name__ == "__main__":
    unittest.main()