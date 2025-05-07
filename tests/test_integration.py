import unittest
import base64
import subprocess
import time
import threading
import requests
import signal
import os

class DocShieldIntegrationTest(unittest.TestCase):
    """Test that DocShield works in an actual running FastAPI application."""

    @classmethod
    def setUpClass(cls):
        """Start a test server in the background."""
        cls.process = subprocess.Popen(
            ["uvicorn", "examples.manual_test:app", "--port", "8765"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
        # Give the server time to start
        time.sleep(2)
    
    @classmethod
    def tearDownClass(cls):
        """Shut down the test server."""
        if cls.process:
            os.killpg(os.getpgid(cls.process.pid), signal.SIGTERM)
            cls.process.wait()
    
    def get_auth_header(self, username, password):
        """Create HTTP Basic Auth header for testing."""
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}
    
    def test_docs_protected(self):
        """Test that docs endpoint requires authentication."""
        response = requests.get("http://localhost:8765/docs")
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)
        self.assertEqual(response.headers["WWW-Authenticate"], "Basic")
    
    def test_redoc_protected(self):
        """Test that redoc endpoint requires authentication."""
        response = requests.get("http://localhost:8765/redoc")
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)
        self.assertEqual(response.headers["WWW-Authenticate"], "Basic")
    
    def test_openapi_protected(self):
        """Test that openapi.json endpoint requires authentication."""
        response = requests.get("http://localhost:8765/openapi.json")
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)
        self.assertEqual(response.headers["WWW-Authenticate"], "Basic")
    
    def test_valid_credentials(self):
        """Test that valid credentials allow access to docs endpoints."""
        headers = self.get_auth_header("admin", "password123")
        
        response = requests.get("http://localhost:8765/docs", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        
        response = requests.get("http://localhost:8765/openapi.json", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.headers["content-type"])
    
    def test_invalid_credentials(self):
        """Test that invalid credentials are rejected."""
        headers = self.get_auth_header("admin", "wrongpassword")
        response = requests.get("http://localhost:8765/docs", headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)
        self.assertEqual(response.headers["WWW-Authenticate"], "Basic")


if __name__ == "__main__":
    unittest.main()